from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED

from app.customers.authentication.customer_authentication_router import (
    customer_auth_router,
)
from app.customers.authentication.customer_change_password_router import (
    customer_password_router,
)
from app.customers.cart.customer_cart_router import cart_router
from app.customers.customer_vendors.customer_vendors import customer_vendor_router
from app.customers.orders.customer_orders_router import customer_order_router
from app.vendors.authentication.change_password_router import vendor_password_router
from app.vendors.authentication.vendor_authentication_router import vendor_auth_router
from app.vendors.menu.menu_routes import (
    categories_router,
    menus_router,
    packaging_router,
)
from app.vendors.orders.orders_routes import order_router

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = exc.errors()
    field_names = [error["loc"][1] for error in errors]
    error_message = f"Validation error: fields {', '.join(field_names)} are required"
    return JSONResponse(
        status_code=400,
        content={
            "detail": {
                "success": False,
                "message": error_message,
            }
        },
    )


# Handle route not found (404)
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    if exc.status_code == HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=HTTP_404_NOT_FOUND,
            content={
                "detail": {
                    "success": False,
                    "message": "The requested route does not exist.",
                }
            },
        )
    elif exc.status_code == HTTP_405_METHOD_NOT_ALLOWED:
        return JSONResponse(
            status_code=HTTP_405_METHOD_NOT_ALLOWED,
            content={
                "detail": {
                    "success": False,
                    "message": f"Method {request.method} not allowed for this route.",
                }
            },
        )
    # Fallback for other HTTP exceptions
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "success": False,
                "message": exc.detail,
            }
        },
    )


# Vendor Routes
app.include_router(vendor_auth_router, prefix="/api")
app.include_router(vendor_password_router, prefix="/api")
app.include_router(menus_router, prefix="/api")
app.include_router(packaging_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(order_router, prefix="/api")


# Customer Routes
app.include_router(customer_auth_router, prefix="/api")
app.include_router(customer_password_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(customer_order_router, prefix="/api")
app.include_router(customer_vendor_router, prefix="/api")


# Rider Routes
# app.include_router(customer_auth_router, prefix="/api")
# app.include_router(customer_password_router, prefix="/api")
# app.include_router(cart_router, prefix="/api")
# app.include_router(customer_order_router, prefix="/api")
