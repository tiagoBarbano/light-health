# 🩺 light-health

**light-health** é uma biblioteca Python **leve, assíncrona e framework-agnostic** para expor endpoints de *health check* e *management* no estilo **Spring Boot Actuator**, usando **ASGI nativo** e **msgspec** para máxima performance e baixo overhead.

> 🎯 Ideal para microsserviços, plataformas internas, sidecars e runtimes customizados.

---

## ✨ Principais características

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

🔹 **Runtime (execução)**
  - ASGI puro
  - Sem dependência de framework
  - Ideal para produção

🔹 **Contrato (documentação)**
  - Pode ser exposto via FastAPI
  - Usado apenas para Swagger / OpenAPI

---

## 📁 Estrutura da lib

```
light_health/
├── asgi/
│   ├── health.py        # Health / readiness / liveness
│   └── management.py   # Loggers / Env
├── checks/
│   ├── base.py
│   ├── mongo.py
│   ├── redis.py
│   └── http.py
├── registry.py         # Registro de checks
├── status.py           # Status + agregação
├── management_models.py
└── __init__.py
```

🩺 Health Checks
Tipos suportados
Tipo	Endpoint
Liveness	/health/liveness
Readiness	/health/readiness
Full	/health
🧱 Criando checks
Exemplo: MongoDB
from light_health.checks.mongo import MongoHealthCheck

mongo_check = MongoHealthCheck(
    name="mongo",
    uri="mongodb://localhost:27017",
)

Exemplo: Redis
from light_health.checks.redis import RedisHealthCheck

redis_check = RedisHealthCheck(
    name="redis",
    url="redis://localhost:6379",
)

Exemplo: Serviço HTTP
from light_health.checks.http import HttpHealthCheck

http_check = HttpHealthCheck(
    name="billing-api",
    url="https://billing/health",
)

🗂️ Registry de checks
from light_health.registry import HealthRegistry

registry = HealthRegistry()
registry.register(mongo_check)
registry.register(redis_check)
registry.register(http_check)


O registry:

Executa checks em paralelo

Agrega status

Controla timeout e falhas

🚀 Usando com FastAPI
from fastapi import FastAPI
from light_health.asgi.health import HealthASGIApp
from light_health.asgi.management import ManagementASGIApp

app = FastAPI()

app.mount("/health", HealthASGIApp(registry))
app.mount("/management", ManagementASGIApp())


Endpoints disponíveis:

GET /health
GET /health/liveness
GET /health/readiness

GET /management/loggers
POST /management/loggers/update
GET /management/env
POST /management/env/update

📘 Swagger / OpenAPI

Como os endpoints são ASGI puros, eles não aparecem automaticamente no Swagger.

✅ Solução recomendada

Criar rotas “espelho” apenas para documentação:

from light_health.management_models import LoggerUpdate, EnvUpdate

@app.post("/management/loggers/update", include_in_schema=True)
def update_logger_doc(payload: LoggerUpdate):
    """Atualiza o nível de um logger"""
    pass


👉 O FastAPI usa isso apenas para gerar o OpenAPI.
👉 A execução real continua no ASGI.

⚙️ Management Endpoints
🔹 Loggers
Listar loggers
GET /management/loggers


Resposta:

{
  "root": "INFO",
  "uvicorn.error": "WARNING"
}

Atualizar nível
POST /management/loggers/update

{
  "level": "DEBUG",
  "logger_name": "uvicorn.error"
}

🔹 Environment variables
Listar env
GET /management/env

Atualizar env
POST /management/env/update

{
  "key": "FEATURE_X",
  "value": "true"
}

🚨 Segurança (IMPORTANTE)

⚠️ Nunca exponha /management publicamente

Boas práticas:

Expor apenas em rede interna

Proteger via:

mTLS

Auth ASGI

NetworkPolicy (K8s)

Desabilitar /env em produção

Mesma recomendação do Spring Actuator.

🧩 Extensibilidade
Criar um check customizado
from light_health.checks.base import HealthCheck, HealthStatus

class MyCheck(HealthCheck):
    async def check(self) -> HealthStatus:
        return HealthStatus.up(details={"custom": "ok"})

⚡ Performance

msgspec para serialização

Async IO

Execução paralela dos checks

Overhead mínimo

Ideal para:

APIs de alta escala

Runtimes com pouco CPU/memória

Sidecars

🗺️ Roadmap

 Auth ASGI

 Metrics (Prometheus)

 Feature flags

 Info endpoint

 Profiles (dev / prod)

🧠 Filosofia

Health e management são infra, não aplicação.

Essa lib foi pensada para:

Não acoplar frameworks

Ser reutilizável

Escalar com governança

📄 Licença

MIT