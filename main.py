from fastapi import FastAPI,Request
from fastapi.openapi.utils import get_openapi
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from starlette.responses import JSONResponse

from auth_routes import auth_router
from debt_route import debt_router
from schema import JWTSettings

from models import Users, Debt
app = FastAPI()
app.include_router(auth_router)
app.include_router(debt_router)


@AuthJWT.load_config
def get_config():
    return JWTSettings()
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title="Debt API", version="1.0.0", routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi