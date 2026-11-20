from fastapi import  status, Header
from fastapi.responses import JSONResponse
from supabase_auth.errors import AuthApiError
from models import auth_model
from config.database import supabase


def signup(payload: auth_model.AuthRequest):
    if not payload.email or not payload.email.strip() or not payload.password or not payload.password.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required"},
        )

    try:
        res = supabase.auth.sign_up({
            "email": payload.email.strip(),
            "password": payload.password,
        })
        if not res.user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Sign up failed"},
            )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"user": res.user.model_dump(mode="json")},
        )
    except AuthApiError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": e.message},
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )

def login(payload: auth_model.AuthRequest):
    if not payload.email or not payload.email.strip() or not payload.password or not payload.password.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required"},
        )

    try:
        res = supabase.auth.sign_in_with_password({
            "email": payload.email.strip(),
            "password": payload.password,
        })
        if not res.session:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid login credentials"},
            )

        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "token_type": "bearer",
            "user": res.user.model_dump(mode="json") if res.user else None,
        }
    except AuthApiError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"},
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"},
        )

def get_protected_profile(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Access token required"},
        )

    token = authorization[len("Bearer "):].strip()
    if not token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Access token required"},
        )

    try:
        res = supabase.auth.get_user(token)
        if not res or not res.user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid or expired token"},
            )

        user = res.user
        return {
            "id": str(user.id),
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid or expired token"},
        )