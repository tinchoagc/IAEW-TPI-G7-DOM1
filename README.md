# Sistema de Gestión de Turnos - Salud Ambulatoria (TPI G2)

Trabajo Práctico Integrador para la materia **Ingeniería de Aplicaciones Web (IAEW) - 2025**.

Este proyecto implementa una solución de backend completa para la reserva de turnos médicos, utilizando una arquitectura de microservicios contenerizada. Cumple con patrones de diseño modernos, seguridad delegada (OAuth2), comunicación asincrónica (RabbitMQ) y observabilidad completa (OpenTelemetry).

> **Estado del Proyecto:** Etapa 2 (Finalizada)
> **Versión:** `v1.0.0` > **Fecha de entrega:** 27/11/2025

---

## 🏗️ Arquitectura en 1 Vistazo

El sistema sigue el modelo **C4**. A continuación se muestra el **Diagrama de Contenedores**, que describe la interacción entre la API, la Base de Datos, el Broker de Mensajería, el Worker y los servicios externos.

![Arquitectura C2](docs/img/c2_containers.png)

_(Puede consultar los diagramas de Contexto y Componentes detallados en la carpeta `/docs`)_

---

## ⚙️ Requisitos y Ejecución Local

### 1. Requisitos Previos

- **Docker Desktop** (v4.0 o superior).
- **4GB de RAM** libres asignadas a Docker.
- **Puertos libres:** `8000` (API), `8080` (Keycloak), `3000` (Grafana), `16686` (Jaeger), `5432` (Postgres), `15672` (RabbitMQ).

### 2. Variables de Entorno

El proyecto incluye un archivo de ejemplo con valores por defecto funcionales para entorno local.

```bash
cp .env.example .env
```

### 3. Cómo levantar el sistema

El sistema está diseñado para levantarse con un solo comando.

**Opción A (Script Automático - Recomendado):**
Limpia contenedores previos y reconstruye todo desde cero.

```bash
./run.sh
```

**Opción B (Manual con Docker Compose):**

```bash
docker-compose up -d --build
```

_Orden de inicio sugerido:_ Postgres/RabbitMQ/Keycloak (Healthchecks) -> API -> Worker -> Observabilidad.

---

## 🔐 Usuarios y Credenciales de Prueba

El sistema se autoconfigura con los siguientes accesos (Seed Data) para facilitar la corrección:

| Servicio             | URL                                                        | Usuario    | Password | Rol/Descripción                       |
| :------------------- | :--------------------------------------------------------- | :--------- | :------- | :------------------------------------ |
| **API Swagger**      | [http://localhost:8000/docs](http://localhost:8000/docs)   | -          | -        | Documentación interactiva             |
| **Keycloak**         | [http://localhost:8080/admin](http://localhost:8080/admin) | `admin`    | `admin`  | Gestión de Identidad                  |
| **Grafana**          | [http://localhost:3000](http://localhost:3000)             | `admin`    | `admin`  | Dashboard de Métricas                 |
| **RabbitMQ**         | [http://localhost:15672](http://localhost:15672)           | `guest`    | `guest`  | Panel del Broker                      |
| **Jaeger**           | [http://localhost:16686](http://localhost:16686)           | -          | -        | Trazas Distribuidas                   |
| **Usuario Staff**    | (Vía API/Postman)                                          | `roman123` | `123456` | Médico/Admin (Rol `app_professional`) |
| **Usuario Paciente** | (Vía API/Postman)                                          | `lio`      | `123`    | Paciente (Rol `app_patient`)          |

---

## 🧪 Pruebas y Validación

### 1. Colección de Postman (Automatizada)

Se incluye una colección completa con scripts de pre-request, variables de entorno dinámicas y validaciones de test para cubrir el flujo de negocio (Login -> Crear Paciente -> Crear Turno -> Confirmar).

- **Ubicación:** [`tests/postman/`](tests/postman/)
- **Archivos:** Importar `turnos_collection.json` y `turnos_environment.json`.

### 2. Prueba de Carga (Stress Test)

Se realizó una prueba de estrés para validar la estabilidad del sistema bajo concurrencia.

> **Resultados de Performance:**
> Se ejecutó una prueba de carga utilizando **Postman Performance Runner** simulando **20 usuarios concurrentes (Virtual Users)** con un perfil de carga fijo durante 1 minuto sobre el endpoint crítico de agenda (`GET /appointments/me/agenda`).
>
> - **Throughput:** ~17 req/s (1,130 peticiones totales).
> - **Latencia Promedio:** 28ms.
> - **Tasa de Error:** 0.00%.
>
> **Conclusión:** El sistema demuestra alta estabilidad y tiempos de respuesta bajos bajo condiciones de concurrencia media, validando la eficiencia del stack FastAPI + PostgreSQL en entorno contenerizado.

_(Ver reporte completo en `docs/img/load_test_report.png`)_

---

## 👁️ Observabilidad (OpenTelemetry)

El sistema implementa trazabilidad y métricas completas.

1.  **Dashboard de Métricas (Grafana):**
    - Acceder a `localhost:3000`.
    - Observar paneles de: **Throughput** (RPM), **Latencia p95** y **Error Rate**.
2.  **Trazas Distribuidas (Jaeger):**
    - Acceder a `localhost:16686`.
    - Permite ver el "Waterfall" correlacionando API + Base de Datos en cada request.

---

## ⚡ Flujos Asincrónicos e Integración

### Asincronía (RabbitMQ + Worker)

El sistema desacopla el envío de notificaciones críticas.

1.  **Disparo:** Crear un turno (`POST /appointments`).
2.  **Efecto:** La API responde 201 inmediatamente. Se publica evento `AppointmentCreated`.
3.  **Validación:** Ver logs del worker (`docker logs worker_turnos`) procesando el mensaje.

### Integración Externa (Webhook)

Notificación de cambios de estado a terceros.

1.  **Disparo:** Confirmar un turno (`PATCH /appointments/{id}/status?status=CONFIRMED`).
2.  **Efecto:** El sistema envía un POST firmado (HMAC) a la `WEBHOOK_URL` configurada.
3.  **Simulación:** Configurar `WEBHOOK_URL` apuntando a [Webhook.site](https://webhook.site) para ver el payload en vivo.

---

## 🧱 Decisiones Arquitectónicas (ADRs)

Documentación resumida de las decisiones técnicas.

### ADR 0001 – Estilo de API (REST + OpenAPI)

- **Decisión:** Implementar API REST con FastAPI.
- **Justificación:** Estándar de industria, fácil integración y testing. Cumple requisito OpenAPI 3.1.

### ADR 0002 – Base de Datos (PostgreSQL)

- **Decisión:** PostgreSQL 16.
- **Justificación:** Robustez ACID, soporte JSONB y amplia comunidad.

### ADR 0003 – Broker de Mensajes (RabbitMQ)

- **Decisión:** RabbitMQ.
- **Justificación:** Mensajería AMQP confiable, ideal para despliegues locales con Docker.

### ADR 0004 – Seguridad (OAuth2 + JWT)

- **Decisión:** Keycloak.
- **Justificación:** Delegación de autenticación (RBAC) para no manejar contraseñas y permitir escalabilidad.

### ADR 0005 – Integración Externa (Webhook)

- **Decisión:** Webhook firmado (HMAC).
- **Justificación:** Mecanismo ligero y estándar para notificar eventos a terceros sin acoplamiento.

### ADR 0006 – Contenerización (Docker Compose)

- **Decisión:** Docker Compose.
- **Justificación:** Orquestación completa del entorno para garantizar reproducibilidad en cualquier máquina.

---

## 🔮 Limitaciones y Mejoras Futuras

- **Frontend:** Desarrollo de una interfaz de usuario (React/Next.js) consumiendo esta API.
- **Kubernetes:** Migrar de Docker Compose a K8s (Helm Charts) para alta disponibilidad.
- **CI/CD:** Implementar GitHub Actions para testing y despliegue automático.
- **BFF:** Implementar un Backend For Frontend para optimizar la carga de datos en móviles.

---

### 📦 Entrega

- **Versión:** `v1.0.0`
- **Commit Hash:** [PEGAR_TU_HASH_AQUI]
