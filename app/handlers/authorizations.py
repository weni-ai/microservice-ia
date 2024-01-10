import os
from fastapi import HTTPException


def token_verification(token: str):
    if os.environ.get("SENTENX_TOKEN") == token:
        return
    raise HTTPException(status_code=401, detail=[{"msg": str("Unauthorized")}])
