from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def auth_middleware(request: Request, call_next):
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = jwt.decode(token, "test", algorithms=["HS256"])
        request.state.user = payload
    except JWTError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Token is invalid or expired"}
        )

    response = await call_next(request)
    return response
