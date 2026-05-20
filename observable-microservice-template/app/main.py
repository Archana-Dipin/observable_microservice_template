import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app import __version__
from app.logging_config import setup_logging
from app.metrics import metrics_middleware
from app.models import HealthResponse, Item, ItemCreate
from app.store import store
from app.tracing import setup_tracing

logger = setup_logging()
logger.info("Test message from startup")
app = FastAPI()
tracer = setup_tracing(app)

app.middleware("http")(metrics_middleware)
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Created a unique request ID for the incoming request, stores it so downstream code can log 
    with the same ID, logs request start/completion with path , method ,status and duration"""
    start_time = time.time()
    request_id = str(uuid4())
    request.state.request_id= request_id
    logger.info(
        "Requested started",
        extra = {
            "request_id":request_id,
            "method":request.method,
            "path": request.url.path,
        },
    )
    response = await call_next(request)
    duration_ms = (time.time()-start_time)*1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Request-Time"] = f"{duration_ms:.2f}ms"
    logger.info(
        "Request completed",
        extra = {
            "request_id":request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms,2),
        },
    )
    return response

@app.get("/")
def read_root():
    """root check"""
    return {"status":"ok"}

@app.post("/items",response_model = Item, status_code=201)
def create_item(payload: ItemCreate, request: Request):
    """Accepts ItemCreate JSON , calls store.create_item() and returns the newly created Item"""
    request_id = getattr(request.state, "request_id", None)
    with tracer.start_as_current_span("create_item_handler") as span:
        span.set_attribute("request.id", request_id)
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.route", request.url.path)
        span.set_attribute("item.status", payload.status.value)
        logger.info(
            "Creating item",
            extra ={
                "request_id": request_id,
                "method" : request.method,
                "path": request.url.path,
                "item_name": payload.name,
            },
        )
        item = store.create_item(payload)
        span.set_attribute("item_id", str(item.id))
        logger.info(
            "Item created",
            extra = {
                "request_id" : request_id,
                "item_id": str(item.id),

                },
        )
    return item

@app.get("/items", response_model=list[Item])
def list_items(request:Request):
    """returns full list of items"""
    request_id = getattr(request.state, "request_id", None)
    with tracer.start_as_current_span("list_items_handler") as span:
        span.set_attribute("request.id", request_id)
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.route", request.url.path)
        items = store.list_items()
        span.set_attribute("items.count",len(items))
        logger.info(
            "Listing items",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                },
        )
        return items

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id:str, request:Request):
    """Extracts item_id from the URL path and fetches from the store and raises exception if not found"""
    request_id = getattr(request.state, "request_id", None)
    with tracer.start_as_current_span("get_item_handler") as span:
        span.set_attribute("request.id", request_id)
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.route", request.url.path)
        span.set_attribute("item.id",item_id)
        logger.info(
            "Getting item",
            extra = {
                "request_id": request_id,
                "method" : request.method,
                "path": request.url.path,
                "item_id": item_id,
                },
        )
        item = store.get_item(item_id)
        if not item:
            logger.warning(
                "Item not found",
                extra = {
                    "request_id":request_id,
                    "item_id":item_id,
                    },
            )
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(
            "Item retrieved",
            extra = {
                "request_id": request_id,
                "item_id":item_id,
                },
        )
        return item

@app.delete("/items/{item_id}")
def delete_item(item_id:str, request:Request):
    """Calls store.delete_item() and returns true if the item existed and deleted else raise exception or success message."""
    request_id = getattr(request.state, "request_id", None)
    with tracer.start_as_current_span("delete_item_handler") as span:
        span.set_attribute("request.id", request_id)
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.route", request.url.path)
        span.set_attribute("item.id", item_id)
        logger.info(
            "Deleting item",
            extra = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "item_id": item_id,
            },
        )
        success = store.delete_item(item_id)
        if not success:
            logger.info(
                "Dele failed, item not found",
                extra= {
                    "request_id":request_id,
                    "item_id": item_id,
                },
            )
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(
            "Item deketed",
            extra = {
                "request_id": request_id,
                "item_id": item_id,
            },
        )
        return {"message":f"Item {item_id} deleted successfully"}

@app.get("/health/live", response_model=HealthResponse)
def live():
    """check app process up and running"""
    return HealthResponse(
        status = "live ok",
        service = "observable-microservice",
        version=__version__,)
@app.get("/health/read", response_model=HealthResponse)
def read():
    """check app ready to handle traffic"""
    return HealthResponse(
        status = "ready ok",
        service = "observable-microservice",
        version=__version__,)
@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    data = generate_latest()
    return Response(content=data, media_type = CONTENT_TYPE_LATEST)
