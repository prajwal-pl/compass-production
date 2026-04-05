import asyncio
import os
import time
from typing import Any

try:
    from redis.asyncio import Redis, from_url
except Exception:  # pragma: no cover - fallback path when redis is not installed
    Redis = None
    from_url = None


class SecurityStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._redis_url = os.getenv("REDIS_URL")
        self._redis: Any = None

        # In-memory fallback stores for local development or test environments.
        self._revoked_access_tokens: dict[str, int] = {}
        self._used_refresh_tokens: dict[str, int] = {}
        self._rate_limits: dict[str, tuple[int, int]] = {}
        self._auth_failures: dict[str, tuple[int, int]] = {}
        self._auth_lockouts: dict[str, int] = {}

        if self._redis_url and from_url:
            self._redis = from_url(self._redis_url, encoding="utf-8", decode_responses=True)

    @staticmethod
    def _now_ts() -> int:
        return int(time.time())

    @staticmethod
    def _lockout_state_key(scope: str, key: str) -> str:
        return f"auth:lockout:state:{scope}:{key}"

    @staticmethod
    def _lockout_failure_key(scope: str, key: str) -> str:
        return f"auth:lockout:failures:{scope}:{key}"

    async def _cleanup_memory_state(self) -> None:
        now = self._now_ts()
        self._revoked_access_tokens = {
            key: exp for key, exp in self._revoked_access_tokens.items() if exp > now
        }
        self._used_refresh_tokens = {
            key: exp for key, exp in self._used_refresh_tokens.items() if exp > now
        }
        self._rate_limits = {
            key: value for key, value in self._rate_limits.items() if value[1] > now
        }
        self._auth_failures = {
            key: value for key, value in self._auth_failures.items() if value[1] > now
        }
        self._auth_lockouts = {
            key: exp for key, exp in self._auth_lockouts.items() if exp > now
        }

    async def revoke_access_token(self, token_fingerprint: str, token_exp_ts: int) -> None:
        ttl = max(1, token_exp_ts - self._now_ts())

        if self._redis:
            await self._redis.set(f"auth:revoked:access:{token_fingerprint}", "1", ex=ttl)
            return

        async with self._lock:
            await self._cleanup_memory_state()
            self._revoked_access_tokens[token_fingerprint] = token_exp_ts

    async def is_access_token_revoked(self, token_fingerprint: str) -> bool:
        if self._redis:
            return bool(await self._redis.exists(f"auth:revoked:access:{token_fingerprint}"))

        async with self._lock:
            await self._cleanup_memory_state()
            return token_fingerprint in self._revoked_access_tokens

    async def consume_refresh_token_jti(self, jti: str, token_exp_ts: int) -> bool:
        ttl = max(1, token_exp_ts - self._now_ts())

        if self._redis:
            was_set = await self._redis.set(
                f"auth:used:refresh:{jti}",
                "1",
                nx=True,
                ex=ttl,
            )
            return bool(was_set)

        async with self._lock:
            await self._cleanup_memory_state()
            if jti in self._used_refresh_tokens:
                return False
            self._used_refresh_tokens[jti] = token_exp_ts
            return True

    async def hit_rate_limit(
        self,
        scope: str,
        key: str,
        max_attempts: int,
        window_seconds: int,
    ) -> tuple[bool, int, int]:
        now = self._now_ts()
        window_bucket = now // window_seconds
        reset_at = (window_bucket + 1) * window_seconds
        retry_after = max(1, reset_at - now)
        redis_key = f"auth:ratelimit:{scope}:{key}:{window_bucket}"

        if self._redis:
            attempts = await self._redis.incr(redis_key)
            if attempts == 1:
                await self._redis.expire(redis_key, window_seconds)

            allowed = attempts <= max_attempts
            remaining = max(0, max_attempts - attempts)
            return allowed, remaining, retry_after

        memory_key = redis_key
        async with self._lock:
            await self._cleanup_memory_state()
            attempts, expires_at = self._rate_limits.get(memory_key, (0, reset_at))

            if expires_at <= now:
                attempts = 0
                expires_at = reset_at

            attempts += 1
            self._rate_limits[memory_key] = (attempts, expires_at)

            allowed = attempts <= max_attempts
            remaining = max(0, max_attempts - attempts)
            return allowed, remaining, max(1, expires_at - now)

    async def get_lockout_status(self, scope: str, key: str) -> tuple[bool, int]:
        state_key = self._lockout_state_key(scope, key)

        if self._redis:
            ttl = await self._redis.ttl(state_key)
            if isinstance(ttl, int) and ttl > 0:
                return True, ttl
            if ttl == -1:
                return True, 60
            return False, 0

        async with self._lock:
            await self._cleanup_memory_state()
            lockout_exp_ts = self._auth_lockouts.get(state_key)
            if not lockout_exp_ts:
                return False, 0

            retry_after = max(1, lockout_exp_ts - self._now_ts())
            return True, retry_after

    async def register_auth_failure(
        self,
        scope: str,
        key: str,
        threshold: int,
        failure_window_seconds: int,
        lockout_seconds: int,
    ) -> tuple[bool, int]:
        state_key = self._lockout_state_key(scope, key)
        failure_key = self._lockout_failure_key(scope, key)

        if self._redis:
            lockout_ttl = await self._redis.ttl(state_key)
            if isinstance(lockout_ttl, int) and lockout_ttl > 0:
                return True, lockout_ttl

            attempts = await self._redis.incr(failure_key)
            if attempts == 1:
                await self._redis.expire(failure_key, failure_window_seconds)

            if attempts >= threshold:
                await self._redis.set(state_key, "1", ex=lockout_seconds)
                await self._redis.delete(failure_key)
                return True, lockout_seconds

            return False, max(0, threshold - attempts)

        async with self._lock:
            await self._cleanup_memory_state()
            now = self._now_ts()
            lockout_exp_ts = self._auth_lockouts.get(state_key)
            if lockout_exp_ts and lockout_exp_ts > now:
                return True, max(1, lockout_exp_ts - now)

            attempts, expires_at = self._auth_failures.get(
                failure_key,
                (0, now + failure_window_seconds),
            )
            if expires_at <= now:
                attempts = 0
                expires_at = now + failure_window_seconds

            attempts += 1
            if attempts >= threshold:
                self._auth_lockouts[state_key] = now + lockout_seconds
                self._auth_failures.pop(failure_key, None)
                return True, lockout_seconds

            self._auth_failures[failure_key] = (attempts, expires_at)
            return False, max(0, threshold - attempts)

    async def clear_auth_failures(self, scope: str, key: str) -> None:
        failure_key = self._lockout_failure_key(scope, key)

        if self._redis:
            await self._redis.delete(failure_key)
            return

        async with self._lock:
            await self._cleanup_memory_state()
            self._auth_failures.pop(failure_key, None)

    async def clear_test_state(self) -> None:
        async with self._lock:
            self._revoked_access_tokens.clear()
            self._used_refresh_tokens.clear()
            self._rate_limits.clear()
            self._auth_failures.clear()
            self._auth_lockouts.clear()


security_store = SecurityStore()
