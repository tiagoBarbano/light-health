
# 🩺 light-health

**light-health** é uma biblioteca Python **leve, assíncrona e framework-agnostic** para expor endpoints de *health check* e *management* no estilo **Spring Boot Actuator**, usando **ASGI nativo** e **msgspec** para máxima performance e baixo overhead.

> 🎯 Ideal para microsserviços, plataformas internas, sidecars e runtimes customizados.

---

## ✨ Principais Características

- ✅ **ASGI puro** (sem dependência de FastAPI, Starlette ou Django)
- ⚡ **Assíncrono**
- 🧱 **Extensível via registry**
- 🚀 **Alta performance com msgspec**
- 🔌 **Plugável em qualquer framework ASGI**
- 🩺 Health, Readiness e Liveness
- ⚙️ Management endpoints (loggers, env)
- 📘 Compatível com Swagger/OpenAPI via adapter

---

## 📦 Instalação

```bash
pip install light-health
```

---

## 🧠 Conceito

Inspirado no Spring Actuator, a lib separa claramente:

- **Runtime (execução):** ASGI puro, sem dependência de framework, ideal para produção
- **Contrato (documentação):** Pode ser exposto via FastAPI, usado apenas para Swagger/OpenAPI

---

## 📁 Estrutura da Lib

```text
light_health/
├── asgi/
│   ├── health.py        # Health / readiness / liveness
│   ├── management.py    # Loggers / Env
│   ├── management_models.py
├── checks/
│   ├── mongo.py
│   ├── redis.py
│   └── http.py
├── registry.py         # Registro de checks
├── status.py           # Status + agregação
└── __init__.py
```

---

## 🚀 Exemplo de Uso

```python
from fastapi import FastAPI
import uvicorn
from pymongo import AsyncMongoClient
import redis.asyncio as redis

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

app = FastAPI()
app.mount("/actuator", HealthASGIApp(registry))
app.mount("/management", ManagementASGIApp())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Endpoints disponíveis:**

## 🩺 Health Checks

| Tipo      | Endpoint               |
|-----------|------------------------|
| Liveness  | /{root_path}/liveness  |
| Readiness | /{root_path}/readiness |
| Health    | /{root_path}/health    |
| UP        | /{root_path}/up        |

## 🩺 Management

| Tipo           | Endpoint                    |
|----------------|-----------------------------|
| loggers        | /{root_path}/loggers        |
| loggers update | /{root_path}/loggers/update |
| env            | /{root_path}/env            |
| env update     | /{root_path}/env/update     |


## 📘 Swagger / OpenAPI

Como os endpoints são ASGI puros, eles não aparecem automaticamente no Swagger.

**Solução recomendada:** criar rotas “espelho” apenas para documentação:

```python
from light_health.management_models import LoggerUpdate, EnvUpdate

@app.post("/management/loggers/update", include_in_schema=True)
def update_logger_doc(payload: LoggerUpdate):
    """Atualiza o nível de um logger"""
    pass
```

> O FastAPI usa isso apenas para gerar o OpenAPI. A execução real continua no ASGI.

---

## ⚙️ Management Endpoints

### 🔹 Loggers

- **Listar loggers:**
  - `GET /management/loggers`
  - Resposta:
    ```json
    {
      "root": "INFO",
      "uvicorn.error": "WARNING"
    }
    ```
- **Atualizar nível:**
  - `POST /management/loggers/update`
  - Payload:
    ```json
    {
      "level": "DEBUG",
      "logger_name": "uvicorn.error"
    }
    ```

### 🔹 Environment variables

- **Listar env:**
  - `GET /management/env`
- **Atualizar env:**
  - `POST /management/env/update`
  - Payload:
    ```json
    {
      "key": "FEATURE_X",
      "value": "true"
    }
    ```

---

## 🚨 Segurança (IMPORTANTE)

⚠️ Nunca exponha `/management` publicamente!

**Boas práticas:**
- Expor apenas em rede interna
- Proteger via:
  - mTLS
  - Auth ASGI
  - NetworkPolicy (K8s)
- Desabilitar `/env` em produção
- Mesma recomendação do Spring Actuator

---

## 🧩 Extensibilidade

**Criar um check customizado:**
```python
from light_health.checks.base import HealthCheck, HealthStatus

class MyCheck(HealthCheck):
    async def check(self) -> HealthStatus:
        return HealthStatus.up(details={"custom": "ok"})
```

---

## ⚡ Performance

- msgspec para serialização
- Async IO
- Execução paralela dos checks
- Overhead mínimo

Ideal para:
- APIs de alta escala
- Runtimes com pouco CPU/memória
- Sidecars

---

## 🗺️ Roadmap

- Auth ASGI
- Metrics (Prometheus)
- Feature flags
- Info endpoint
- Profiles (dev / prod)

---

## 🧠 Filosofia

Health e management são infra, não aplicação.

Essa lib foi pensada para:
- Não acoplar frameworks
- Ser reutilizável
- Escalar com governança

---

## 📄 Licença

MIT