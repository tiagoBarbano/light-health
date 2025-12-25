import asyncio
from typing import Dict, Callable, Awaitable

from light_health.status import (
    HealthState,
    HealthCheckResult,
    HealthResponse,
)


class AsyncHealthRegistry:
    def __init__(self):
        self._liveness: Dict[str, Callable[[], Awaitable[HealthCheckResult]]] = {}
        self._readiness: Dict[str, Callable[[], Awaitable[HealthCheckResult]]] = {}

    def register_liveness(self, name: str, check):
        self._liveness[name] = check

    def register_readiness(self, name: str, check):
        self._readiness[name] = check

    async def liveness(self) -> HealthResponse:
        return await self._run(self._liveness)

    async def readiness(self) -> HealthResponse:
        return await self._run(self._readiness)

    async def _run(self, checks) -> HealthResponse:
        tasks = {
            name: asyncio.create_task(self._safe(check))
            for name, check in checks.items()
        }

        results: Dict[str, HealthCheckResult] = {}
        overall = HealthState.UP

        for name, task in tasks.items():
            result = await task
            results[name] = result
            if result.status is HealthState.DOWN:
                overall = HealthState.DOWN

        return HealthResponse(status=overall, checks=results)

    async def _safe(self, check) -> HealthCheckResult:
        try:
            return await check()
        except Exception as e:
            return HealthCheckResult(
                status=HealthState.DOWN,
                details={"error": str(e)},
            )
