from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.models
from app.routes.internal_product_routes import router as internal_products_router
from app.routes.market_routes import router as market_router
from app.routes.product_routes import router as product_router
from app.routes.seller_orders import router as orders_router
from app.schemas.response import ApiError, ApiResponse

app = FastAPI(title="Seller Backend Unified")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            data=None, errors=[ApiError(code=str(exc.status_code), message=exc.detail)], meta={}
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ApiResponse(
            data=None,
            errors=[
                ApiError(
                    code="VALIDATION_ERROR",
                    message="Validation failed",
                    meta={"details": exc.errors()},
                )
            ],
            meta={},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            data=None,
            errors=[ApiError(code="INTERNAL_ERROR", message="Internal server error")],
            meta={},
        ).model_dump(),
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market_router)
app.include_router(product_router)
app.include_router(orders_router)
app.include_router(internal_products_router)
