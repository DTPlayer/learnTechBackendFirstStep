from fastapi_jwt import JwtAccessBearer

from datetime import datetime, timedelta, timezone
from config import SECRET_KEY

from db.models import User


access_security = JwtAccessBearer(secret_key=SECRET_KEY, access_expires_delta=timedelta(days=7), auto_error=True)

async def create_jwt_token(user: User):
    subject = {
        'user_id': user.id,
        'iat': (datetime.now(tz=timezone.utc) + timedelta(days=7)).timestamp(),
    }

    jwt_token = access_security.create_access_token(subject=subject)

    return jwt_token, subject