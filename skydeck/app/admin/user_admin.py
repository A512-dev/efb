from wtforms import StringField
from sqladmin import ModelView

from app.models.user import User
from passlib.hash import bcrypt

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.name]

    form_columns = [
        "org",
        "name",
        "email",
        "password_hash",   # virtual field
        "role",
        "employee_no",
        "position",
        "aircraft_type",
        "medical_expires_at",
        "passport_expires_at",
        "license_expires_at",
    ]

    form_overrides = {
        "email": StringField
    }


    # from wtforms import PasswordField
    # form_extra_fields = {
    #     "password": PasswordField("Password")
    # }
    
    # async def on_model_change(self, data, model, is_created, request):
    #     password = data.get("password")

    #     if password:
    #         model.password_hash = bcrypt.hash(password)
