import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from dependencies.keys import get_clerk_public_key

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def clerk_validate_user(
    token: str = Security(oauth2_scheme),
    public_key: str = Depends(get_clerk_public_key),
) -> str:
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        user_id = payload.get("sub")
        return user_id

    except PyJWTError:
        raise HTTPException(401)

    except Exception:
        raise HTTPException(500)
