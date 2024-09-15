from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
load_dotenv()

security = HTTPBearer()


async def auth_middleware(request: Request, call_next):
    """
    Authentication Middleware.

    This middleware function validates the JWT token provided in the Authorization header of the request.
    It decodes the token using the secret key from the environment variables.
    
    - If the token is valid, the payload is stored in the request's state as 'user' for later use in the application.
    - If the token is invalid or expired, it raises a 403 Forbidden HTTP exception.
    
    After processing the authentication, it passes the request to the next handler in the chain.

    Parameters:
    - **request**: The incoming HTTP request.
    - **call_next**: The next middleware or route handler in the request chain.

    Returns:
    - The response from the next handler, or an error if token validation fails.
    """
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv(
    "SecretJwt"), algorithms=["HS256"])
        request.state.user = payload
    except JWTError:
        raise HTTPException(
            status_code=403, detail="Token is invalid or expired")
    response = await call_next(request)
    return response


async def auth_middleware_email_return(request: Request):
    """
    Middleware to extract email from JWT token.

    This function extracts the JWT token from the Authorization header, decodes it using the secret key, 
    and returns the email (stored in the "sub" field) associated with the token.

    - If the token is invalid or expired, it raises a 403 Forbidden HTTP exception.
    - If another error occurs, it raises a 404 error.

    Parameters:
    - **request**: The incoming HTTP request.

    Returns:
    - The email from the token payload.
    """
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv(
    "SecretJwt"), algorithms=["HS256"])
        return str(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=403, detail="Token is invalid or expired")
    except Exception as e:
        raise HTTPException(status_code=404, detail="Some error")


async def verify_admin_token(request: Request):
    """
    Middleware to verify if the user is an admin.

    This function extracts the JWT token from the Authorization header, decodes it, 
    and checks if the user is an admin (by validating the 'sub' field in the token).
    
    - If the 'sub' field does not contain the admin identifier ("admin_statefree"), it raises a 403 Forbidden error.
    - If the token is invalid or expired, it raises a 403 error.
    - If another error occurs, it raises a 404 error.

    Parameters:
    - **request**: The incoming HTTP request.

    Returns:
    - If the token is valid and the user is an admin, the decoded token is stored in `request.state.user`.
    """
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv(
    "SecretJwt"), algorithms=["HS256"])
        if payload.get("sub") != "admin_statefree":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        request.state.user = payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token is invalid or expired"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="Some error")
