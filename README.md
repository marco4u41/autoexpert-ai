# 🚗 AutoExpert AI — Asistente Automotriz Inteligente con RAG y Tool Calling

[![CI](https://img.shields.io/github/actions/workflow/status/aledash3/autoexpert-ai/ci.yml?branch=main&style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/aledash3/autoexpert-ai/actions)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-Nemotron--3--Ultra-FF6B35?style=for-the-badge&logo=openai&logoColor=white)](https://openrouter.ai/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Pytest-345%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
![Licencia](https://img.shields.io/badge/Licencia-Acad%C3%A9mica%20y%20Educativa-blue?style=for-the-badge)

---

## 📌 Descripción General

**AutoExpert AI** es una aplicación *full-stack* que combina una base de datos vehicular estructurada (20,000+ vehículos, 47,000+ registros de mercado) con un **agente de IA conversacional** capaz de:

- **Recomendar** vehículos filtrando por marca, presupuesto, tipo, combustible y uso —respetando estrictamente las restricciones del usuario—
- **Comparar** modelos mediante tablas interactivas con análisis cualitativo (uso, confort, desempeño, confiabilidad)
- **Diagnosticar** orientativamente problemas mecánicos a partir de síntomas reportados
- **Persistir** conversaciones privadas, garage virtual (hasta 10 vehículos/usuario) y preferencias en PostgreSQL
- **Exponer** analíticas de uso y mercado a través de un dashboard en tiempo real

El sistema implementa **RAG (Retrieval-Augmented Generation)** sobre datos propios + **Tool Calling** estructurado, orquestados por un agente multi-capacidad con clasificación de intención, gestión de contexto persistente y *follow-up* inteligente.

---

## 🎯 Objetivos

### Objetivo General
Construir un asistente automotriz conversacional *production-ready* que demuestre integración de LLM con bases de datos relacionales, arquitectura de agentes, *prompt engineering* avanzado y despliegue full-stack.

### Objetivos Específicos
1. **Arquitectura de Agente**: Implementar orquestador con clasificación de intención (RECOMMENDATION | COMPARISON | DIAGNOSIS | GENERAL), *tool calling* tipado y registro de capacidades extensible.
2. **RAG Estructurado**: Consultas SQL parametrizadas (`search_vehicles`, `get_vehicle_details`, `get_model_info`, `get_brand_info`) inyectadas como bloques de contexto en *system prompt*.
3. **Gestión de Contexto**: Perfil de usuario persistente (presupuesto, uso, terreno, marcas mencionadas, síntomas, vehículos en garage) + historial de conversación con *sliding window*.
4. **Seguimiento Inteligente**: Detección automática de campos faltantes críticos/importantes/complementarios y generación de preguntas de seguimiento contextualizadas.
5. **Frontend Reactivo**: Streaming token-a-token, UI *glassmorphism* responsive, estado global con Zustand, validación Zod.
6. **Calidad y Observabilidad**: Cobertura de tests backend (pytest) + frontend (Vitest/RTL), linting estricto, migraciones versionadas (Alembic), health checks.

---

## 🧠 Arquitectura del Agente IA

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT ORCHESTRATOR                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Intent       │  │ Context      │  │ Capability Registry  │  │
│  │ Classifier   │  │ Manager      │  │ (Recommendation,     │  │
│  │ (keyword +   │  │ (UserProfile │  │  Comparison,         │  │
│  │  heuristics) │  │  + History)  │  │  Diagnosis)          │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │             │
│         ▼                 ▼                      ▼             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              AUTOMOTIVE AGENT TOOL (Interface)            │  │
│  │  search_vehicles  │  get_vehicle_details  │ get_model_info │  │
│  │  get_brand_info   │  list_brands            │ health_check │  │
│  └──────────────────────────┬────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │           POSTGRESQL (vehicles_master, brands,            │  │
│  │            vehicle_market_stats, users, conversations)    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OPENROUTER (Nemotron-3-Ultra)              │
│  System Prompt = Base + Context Block + Capability Enhancement  │
│  + Follow-up Instructions (jinja2 templates)                    │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de una petición
1. **Clasificación de intención** → `IntentClassifier` (keywords + heurísticas de presupuesto/terreno/motor)
2. **Construcción de contexto** → `ContextManager` recupera perfil + histórico → `UserContext`
3. **Búsqueda automotriz** → `AutomotiveAgentTool` ejecuta queries SQL según intención → bloques de datos formateados
4. **Ensamblaje de prompt** → `PromptLoader` renderiza plantillas Jinja2 (base + enhancement + follow-up)
5. **LLM Streaming** → `OpenRouterProvider` envía *system prompt* + *history* + *user message* → tokens SSE
6. **Persistencia** → Guarda `user_message`, `assistant_message`, actualiza `conversation.updated_at`

---

## 📊 Base de Conocimiento (Dataset)

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| `vehicles_master` | ~20,036 | Vehículos agregados por (marca, modelo, año) con stats de precio, odómetro, combustible, transmisión, tipo, carrocería, cilindros, consumo, confianza de mercado |
| `vehicle_market_stats` | ~47,030 | Estadísticas por (marca, modelo): años disponibles, listados totales, precio medio/mediano global, modo de combustible/transmisión/tracción/tipo |
| `brands` | ~N | Resumen por fabricante: conteo de modelos, años, listados, precio medio |
| `users` | — | Autenticación (JWT en cookies httpOnly) |
| `conversations` | — | Historial privado por usuario |
| `messages` | — | Turnos de conversación (user/assistant) |
| `user_profiles` | — | Panel físico (presupuesto, terreno, motor, uso, familia, preferencias) |
| `user_garage_vehicles` | — | Garage virtual (máx. 10/usuario) |

**Fuente**: Datos de listados públicos de vehículos (EE. UU.) agregados y anonimizados.

---

## ⚙️ Stack Tecnológico

| Capa | Tecnología | Versión | Rol |
|------|------------|---------|-----|
| **Frontend** | React + TypeScript + Vite | 18.3 / 5.6 / 6.0 | SPA, SSR-ready |
| **Estilos** | TailwindCSS | 3.4 | Utility-first, glassmorphism |
| **Estado** | Zustand | 5.0 | Stores reactivos (auth, chat, garage, analytics) |
| **Validación** | Zod | 3.24 | Schemas runtime + DX |
| **Testing FE** | Vitest + React Testing Library | 4.1 / 16.3 | Unit + integration |
| **Backend** | FastAPI (async) | 0.115+ | API REST + SSE streaming |
| **ORM** | SQLAlchemy 2.0 (async) | 2.0+ | Mapeo tipado, sessions async |
| **Migraciones** | Alembic | 1.14+ | Versionado de esquema |
| **DB Driver** | asyncpg | 0.30+ | PostgreSQL async |
| **Validación** | Pydantic v2 | 2.6+ | Request/response schemas |
| **Auth** | JWT + bcrypt | — | Cookies httpOnly, SameSite=Lax |
| **IA** | OpenRouter SDK (HTTP) | — | Nemotron-3-Ultra-550B (free tier) |
| **Testing BE** | pytest + httpx | — | API + unit + integration |
| **Contenedores** | Docker / Docker Compose | — | Dev + Prod ready |

---

## 🚀 Puesta en Marcha

### Prerrequisitos
| Herramienta | Versión mínima | Verificación |
|-------------|----------------|--------------|
| Git | 2.x | `git --version` |
| Python | 3.13+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| PostgreSQL | 14+ | `psql --version` |
| Docker (opcional) | 24+ | `docker --version` |

---

### Opción A: Docker Compose (Recomendado - Un comando)

```bash
# 1. Clonar
git clone https://github.com/<tu-usuario>/autoexpert-ai.git
cd autoexpert-ai

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales (ver sección Variables de Entorno)

# 3. Levantar todo (PostgreSQL + Backend + Frontend)
docker compose up --build -d

# 4. Verificar
curl http://localhost:8000/health   # {"status":"ok"}
# Frontend: http://localhost:5173
```

> **Nota**: El `docker-compose.yml` incluye healthchecks, volúmenes para BD y hot-reload en ambos servicios.

---

### Opción B: Instalación Manual (Desarrollo local)

#### 1. Base de datos PostgreSQL
```sql
-- Con usuario admin (postgres)
CREATE DATABASE autoexpert_db;
-- Usuario/contraseña por defecto en .env.example: postgres / admin1234
```

#### 2. Backend
```powershell
cd backend

# Entorno virtual
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Dependencias
python -m pip install --upgrade pip
pip install -e .
pip install -e ".[dev]"

# Migraciones
alembic upgrade head

# Servidor
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 3. Frontend (otra terminal)
```powershell
cd frontend
npm install
npm run dev
```

#### 4. URLs de desarrollo
| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://127.0.0.1:8000 |
| Swagger Docs | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/health |

---

## 🔧 Variables de Entorno

### Backend (`backend/.env`)
```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_DB=autoexpert_db

# OpenRouter (obtener key en https://openrouter.ai/keys)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Backend
APP_ENV=development
DEBUG=true
JWT_SECRET=clave-secreta-super-larga-y-aleatoria-64-chars-minimo

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

> **Fallback SQLite**: Si `POSTGRES_HOST` y `POSTGRES_USER` están vacíos, usa `backend/database/chatbot.db` automáticamente.

### Frontend
No requiere `.env`. El proxy de Vite (`vite.config.ts`) redirige `/api/*` → `http://localhost:8000`.

---

## 🧪 Testing y Calidad

El proyecto implementa una suite integral de **345 pruebas automatizadas** que validan la lógica de orquestación del agente, clasificación de intenciones, RAG con PostgreSQL y validaciones de API:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-9.1.1, pluggy-1.6.0
rootdir: autoexpert-ai
collected 367 items

backend/tests/test_agent.py ............................................ [ 19%]
backend/tests/test_analytics.py ...................ssssssss............. [ 39%]
backend/tests/test_auth.py ............................................. [ 58%]
backend/tests/test_automotive.py ....................................... [ 78%]
backend/tests/test_chat.py ............................................. [ 98%]
backend/tests/test_garage.py .......                                     [100%]

======================== 345 passed, 22 skipped in 11.30s =====================
```

### Backend
```bash
cd backend
python -m pytest tests/ -q --cov=app --cov-report=term-missing
```
- **Cobertura objetivo**: ≥ 85%
- Tests: API (auth, chat, garage, analytics, automotive), dominio (agente, intenciones, herramientas), repositorios, migraciones.

### Frontend
```bash
cd frontend
npm run typecheck      # TypeScript strict
npm run lint           # ESLint + React hooks
npm run test           # Vitest (unit + integration)
npm run test:watch     # Modo watch
npm run build          # Build producción (verifica tipos + bundle)
```

---

## 📦 Migraciones (Alembic)

```bash
cd backend
.\.venv\Scripts\Activate.ps1

alembic current          # Migración aplicada
alembic heads            # Última disponible
alembic upgrade head     # Aplicar pendientes
alembic revision --autogenerate -m "descripción"
alembic downgrade -1     # Revertir una
alembic downgrade base   # Revertir todo (⚠️ pérdida de datos)
```

---

## 🐳 Despliegue en Producción

### Checklist Pre-Deploy
- [ ] `APP_ENV=production` / `DEBUG=false`
- [ ] `JWT_SECRET` = string aleatorio 64+ chars (no valor por defecto)
- [ ] `POSTGRES_*` apuntan a instancia gestionada (RDS, Supabase, Neon, Railway)
- [ ] `OPENROUTER_API_KEY` válida con cuota suficiente
- [ ] `CORS_ORIGINS` = solo dominio frontend (ej. `["https://autoexpert.ai"]`)
- [ ] `alembic upgrade head` ejecutado contra BD de producción
- [ ] HTTPS + Reverse Proxy (Nginx/Caddy) + Certificado SSL
- [ ] Cookies `Secure` + `SameSite=none` (config en `auth.py` según `APP_ENV`)
- [ ] Logs sin secretos (revisar `backend.log`)

### Backend (Docker)
```dockerfile
# Dockerfile.backend (multi-stage)
FROM python:3.13-slim AS builder
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Frontend (Build Estático)
```bash
cd frontend
npm run build
# Output en dist/ → servir con Nginx, Vercel, Netlify, Cloudflare Pages
# Configurar rewrite: /api/* → https://api.tudominio.com
```

---

## 🔍 Solución de Problemas Comunes

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| `ECONNREFUSED` en `/api/*` | Backend no levantado | `docker compose up -d` o `uvicorn` en puerto 8000 |
| `401 Unauthorized` en `/auth/me` | Cookie no enviada / CORS | Verificar `CORS_ORIGINS` + acceder via `localhost:5173` (no IP) |
| `psycopg2.OperationalError` | PostgreSQL down / credenciales | `systemctl status postgresql` / revisar `.env` |
| Migración `NotNullViolation` | Columna nueva sin default | Editar migración: `server_default=sa.false()` + `op.execute("UPDATE ...")` |
| Streaming se corta | Timeout OpenRouter / red | Aumentar `timeout` en `httpx.AsyncClient` (openrouter.py) |
| `ModuleNotFoundError: psycopg2` | Falta driver en venv | `pip install psycopg2-binary` |

---

## 🔐 Seguridad

- `.env` en `.gitignore` — **nunca** commitear secretos
- `.env.example` solo con placeholders
- Passwords: **bcrypt** (cost 12)
- Sesiones: **JWT** (HS256) en cookies `httpOnly`, `SameSite=Lax`, `Secure` en prod
- CORS: restringido a `CORS_ORIGINS`
- Validación estricta: **Pydantic v2** en todos los endpoints
- Rate limiting: *(pendiente — ver roadmap)*

---

## 🗺️ Roadmap / Próximos Pasos

- [ ] **Rate limiting** (`slowapi` + Redis) en `/api/chat`
- [ ] **Evaluaciones automáticas del agente** (golden set + métricas: intent accuracy, tool call correctness, hallucination rate)
- [ ] **Observabilidad**: OpenTelemetry + Prometheus + Grafana (latencia, tokens, errores)
- [ ] **Tests E2E** (Playwright): login → chat → recomendación → garage → comparación → dashboard
- [ ] **Búsqueda semántica** (pgvector) sobre descripciones de vehículos
- [ ] **Multi-idioma** (i18n) — arquitectura lista, solo diccionarios
- [ ] **PWA** (service worker, manifest, offline-first para garage)
- [ ] **Admin panel** (gestión usuarios, métricas, auditoría)

---

## 👨‍💻 Autores

Este proyecto fue desarrollado de forma colaborativa por:

* **Carlos Alejandro Coronel Quilachamin** — [@coronelq](https://github.com/coronelq)
* **David Alejandro Cruz Palacios** — [@aledash3](https://github.com/aledash3)
* **Dilan Andres Delgado Salgado** — [@Dilan-D-S](https://github.com/Dilan-D-S)
* **Marco Antonio Espinoza Huanga** — [@marco4u41](https://github.com/marco4u41)

Carrera de Ingeniería en Ciencias de la Computación  
Asignatura de Inteligencia Artificial — Sexto Semestre  
**Universidad Politécnica Salesiana (UPS)**  
Quito, Ecuador

---

## 📜 Licencia

Este proyecto fue desarrollado con fines estrictamente académicos y educativos en la **Universidad Politécnica Salesiana (UPS)**.

Todos los derechos reservados conforme a las normativas de desarrollo académico e institucional. Prohibido su uso comercial no autorizado.
