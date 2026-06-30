from sqladmin import ModelView
from wtforms import PasswordField, StringField

from app.core.security import hash_password
from app.models.user import User

class UserAdmin(ModelView, model=User):

    column_list = [User.id, User.email, User.name]

    form_columns = [
        "org",
        "name",
        "email",
        "role",
        "employee_no",
        "position",
        "aircraft_type",
        "medical_expires_at",
        "passport_expires_at",
        "license_expires_at",
    ]

    form_overrides = {
        "email": StringField,
    }

    # 2. Override scaffold_form to inject the custom field
    async def scaffold_form(self, *args, **kwargs):
        # Let sqladmin build the base form using the safe form_columns above
        BaseForm = await super().scaffold_form(*args, **kwargs)
        
        # Subclass the generated form to add our virtual field
        class CustomUserForm(BaseForm):
            password = PasswordField("Password")
            
        return CustomUserForm

    # 3. Handle the hashing before saving
    async def on_model_change(self, data, model, is_created, request):
        password = data.pop("password", None)
        
        if password:
            data["password_hash"] = hash_password(password) # Use your hashing utility here
