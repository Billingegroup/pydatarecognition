from typing import Optional
from starlette.requests import Request
from fastapi import HTTPException


# Try to get the logged in user
async def get_user(request: Request) -> Optional[dict]:
    user = request.session.get('user', None)
    if user is not None:
        return user
    else:
        raise HTTPException(status_code=403, detail='Please return to home screen and log in.')

    return None