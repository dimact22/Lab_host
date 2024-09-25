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

    Validates the JWT token provided in the Authorization header of the request.
    If the token is valid, stores the payload in the request's state as 'user'.
    If invalid or expired, raises a 403 Forbidden HTTP exception.
    
    Parameters:
    - **request**: The incoming HTTP request.
    - **call_next**: The next middleware or route handler in the request chain.

    Returns:
    - The response from the next handler, or an error if token validation fails.
    """
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        # Decode the JWT token
        payload = jwt.decode(token, os.getenv("SecretJwt"), algorithms=["HS256"])
        request.state.user = payload  # Store payload in request state
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired.")
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Authentication error: {str(e)}")
    
    response = await call_next(request)
    return response

async def auth_middleware_email_return(request: Request):
    """
    Extracts email from JWT token.

    Decodes the JWT token and returns the email (stored in the "sub" field).
    Raises a 403 Forbidden if the token is invalid or expired.

    Parameters:
    - **request**: The incoming HTTP request.

    Returns:
    - The email from the token payload.
    """
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("SecretJwt"), algorithms=["HS256"])
        return str(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error retrieving email: {str(e)}")

async def verify_admin_token(request: Request):
    """
    Verifies if the user is an admin.

    Decodes the JWT token and checks if the user is an admin 
    by validating the 'sub' field. Raises 403 if not authorized.

    Parameters:
    - **request**: The incoming HTTP request.

    Returns:
    - If the token is valid and the user is an admin, stores the payload in `request.state.user`.
    """
    try:
        credentials: HTTPAuthorizationCredentials = await security(request)
        token = credentials.credentials
        payload = jwt.decode(token, os.getenv("SecretJwt"), algorithms=["HS256"])
        
        # Check if the user is an admin
        if payload.get("sub") != "admin_statefree":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized.")
        
        request.state.user = payload  # Store the payload for further use
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is invalid or expired.")
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Authorization error: {str(e)}")
