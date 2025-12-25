from fastapi import FastAPI
import uvicorn
from pymongo import AsyncMongoClient
import redis.asyncio as redis

from light_health.asgi.base import HealthStatus,HealthCheck
from light_health.asgi.management import ManagementASGIApp
from light_health.asgi.health import HealthASGIApp
from light_health.registry import AsyncHealthRegistry
from light_health.status import HealthCheckResult, HealthState
from light_health.checks.mongo import mongo_health_check
from light_health.checks.redis import redis_health_check
from light_health.checks.http import http_health_check

mongo = AsyncMongoClient("mongodb://localhost:27017")
redis_client = redis.Redis(host="localhost", password="redis1234", port=6379)

registry = AsyncHealthRegistry()

async def process_alive():
    return HealthCheckResult(status=HealthState.UP)

registry.register_liveness("process", process_alive)
registry.register_readiness("mongo", mongo_health_check(mongo))
registry.register_readiness("redis", redis_health_check(redis_client))
registry.register_readiness(
    "external-api",
    http_health_check("https://httpbin.org/status/200"),
)

class MyCheck(HealthCheck):
    async def check(self) -> HealthStatus:
        return HealthStatus.up(details={"test_custom": "ok"})
    
registry_test = AsyncHealthRegistry()
registry_test.register_readiness("custom", MyCheck().check)

app = FastAPI()
app.mount("/actuator", HealthASGIApp(registry))
app.mount("/test", HealthASGIApp(registry_test))
app.mount("/management", ManagementASGIApp())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
