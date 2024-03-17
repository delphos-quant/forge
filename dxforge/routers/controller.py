from fastapi import APIRouter
from ..forge import Forge


router = APIRouter()
forge = Forge()


@router.get("/")
async def status():
    return {"status": "ok"}
