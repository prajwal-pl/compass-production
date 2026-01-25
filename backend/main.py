from fastapi import FastAPI
import api.auth as auth
import api.ai as ai
import api.services as services
import api.deployments as deployments
import api.dependencies as dependencies
import api.docs as docs
import api.integrations as integrations
import api.metrics as metrics
import api.templates as templates
import api.webhooks as webhooks
import api.search as search

app = FastAPI(
    title="Compass - AI-Native Internal Developer Portal",
    description="An AI-powered platform for managing services, deployments, and developer documentation",
    version="0.1.0"
)

# Include all API routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(services.router, prefix="/services", tags=["services"])
app.include_router(deployments.router, prefix="/deployments", tags=["deployments"])
app.include_router(dependencies.router, prefix="/dependencies", tags=["dependencies"])
app.include_router(docs.router, prefix="/docs", tags=["docs"])
app.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(templates.router, prefix="/templates", tags=["templates"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(search.router, prefix="/search", tags=["search"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to Compass - AI-Native Internal Developer Portal"}
