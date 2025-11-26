# app/observability.py
import os
import time
import logging
from uuid import uuid4
from contextvars import ContextVar
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def _setup_json_logging():
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        json_ensure_ascii=False,
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


def setup_opentelemetry(app):
    service_name = os.getenv("OTEL_SERVICE_NAME", "sistema-turnos-api")
    # Mantenemos el puerto 4318 (HTTP) que fue la solución ganadora
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4318/v1/traces")

    # 1. Configurar Proveedor
    resource = Resource.create(attributes={"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # 2. Configurar Exportador OTLP (HTTP)
    # Ya no necesitamos el ConsoleExporter (los logs) porque ya vimos que funciona en Jaeger
    try:
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    except Exception as e:
        print(f"❌ Error configurando OpenTelemetry: {e}")

    # 3. Instrumentar FastAPI
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider, excluded_urls="metrics,health,docs,openapi.json")
    _setup_json_logging()

# --- Métricas Prometheus (Igual que siempre) ---
REQUEST_COUNT = Counter("http_requests_total", "Total de peticiones HTTP", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Duración de la petición en segundos", ["method", "endpoint"])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        rid = request.headers.get("x-request-id") or str(uuid4())
        request_id_ctx.set(rid)
        request.state.request_id = rid
        start_time = time.time()
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            process_time = time.time() - start_time
            if path not in ["/metrics", "/health", "/docs", "/openapi.json"]:
                REQUEST_COUNT.labels(method=method, endpoint=path, status=status_code).inc()
                REQUEST_LATENCY.labels(method=method, endpoint=path).observe(process_time)
        response.headers["X-Request-ID"] = rid
        return response

def metrics_endpoint(request: Request):
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)