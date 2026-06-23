from jose import JWTError
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.errors import AuthenticationError
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.enums import UserRole
from app.repositories import user_repo
from app.services import auth_service


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()

        # SQLAdmin calls this field "username"; users enter their email.
        email = str(form.get("username", "")).strip()
        password = str(form.get("password", ""))

        with SessionLocal() as db:
            try:
                result = auth_service.login(
                    db,
                    email=email,
                    password=password,
                    ip=request.client.host if request.client else None,
                    device_info={"client": "sqladmin"},
                )
            except AuthenticationError:
                return False

            # Authentication succeeded, but SQLAdmin requires authorization too.
            if result["user"]["role"] != UserRole.admin.value:
                auth_service.logout(
                    db,
                    raw_refresh_token=result["refresh_token"],
                )
                return False

        request.session.update(
            {
                "admin_access_token": result["access_token"],
                "admin_refresh_token": result["refresh_token"],
            }
        )
        return True

    async def authenticate(self, request: Request) -> bool:
        access_token = request.session.get("admin_access_token")

        if not access_token:
            return False

        try:
            payload = decode_access_token(access_token)
        except JWTError:
            # Transparently renew an expired access token using the existing
            # refresh-session system.
            refresh_token = request.session.get("admin_refresh_token")
            if not refresh_token:
                request.session.clear()
                return False

            with SessionLocal() as db:
                try:
                    result = auth_service.refresh(
                        db,
                        raw_refresh_token=refresh_token,
                    )
                except AuthenticationError:
                    request.session.clear()
                    return False

            access_token = result["access_token"]
            request.session["admin_access_token"] = access_token

            try:
                payload = decode_access_token(access_token)
            except JWTError:
                request.session.clear()
                return False

        try:
            user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError):
            request.session.clear()
            return False

        # The database is authoritative. This makes role changes and soft
        # deletion take effect immediately, even with an existing token.
        with SessionLocal() as db:
            user = user_repo.get_by_id(db, user_id)

            if user is None or user.role != UserRole.admin:
                request.session.clear()
                return False

            request.state.admin_user_id = user.id
            request.state.admin_org_id = user.org_id

        return True

    async def logout(self, request: Request) -> bool:
        refresh_token = request.session.get("admin_refresh_token")

        try:
            if refresh_token:
                with SessionLocal() as db:
                    auth_service.logout(
                        db,
                        raw_refresh_token=refresh_token,
                    )
        finally:
            request.session.clear()

        return True