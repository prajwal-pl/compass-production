import express from 'express';
import { googleAuthHandler, loginHandler, profileHandler, registerHandler } from '../controllers/auth';
import { authMiddleware } from '../middleware/auth-middleware';

const router = express.Router()

router.post("/register", registerHandler)

router.post("/login", loginHandler)

router.get("/me", authMiddleware, profileHandler)

router.get("/google-auth", googleAuthHandler)

export default router