import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing(app):
    """Distributed tracking for the app. Creates/configures a tracer provider,
    sets the exported endpoint, adds a span processor, instruments FastAPI."""
    
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT","http://localhost:4317")

    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)
    otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()

    tracer = trace.get_tracer(__name__)
    return tracer