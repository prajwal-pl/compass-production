from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/github")
async def github_webhook(request: Request):
    # WIP: Add logic to receive GitHub webhooks
    # Events: push, pull_request, deployment
    return {"status": "accepted", "message": "GitHub webhook handler is a work in progress"}


@router.post("/kubernetes")
async def k8s_webhook():
    # WIP: Add logic to receive Kubernetes events
    # Events: pod_created, pod_failed, deployment_updated
    return {"status": "accepted", "message": "Kubernetes webhook handler is a work in progress"}


@router.post("/sentry")
async def sentry_webhook():
    # WIP: Add logic to receive Sentry error notifications
    return {"status": "accepted", "message": "Sentry webhook handler is a work in progress"}
