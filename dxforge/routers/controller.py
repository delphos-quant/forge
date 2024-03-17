from fastapi import APIRouter, Request, HTTPException
from ..forge import Forge

router = APIRouter()
forge = Forge()


def get_controller(name: str):
    return forge.orchestrator.controllers.get(name, None)


@router.get("/")
async def get_status():
    return forge.orchestrator.status()


@router.get("/{controller}")
async def get_controller_status(controller: str):
    if not (controller := get_controller(controller)):
        raise HTTPException(status_code=404, detail="controller not found")

    status = await controller.status()
    return status


@router.get("/{controller}/{node}")
async def get_node_endpoints(controller: str,
                             node: str):
    if not (controller := get_controller(controller)):
        raise HTTPException(status_code=404, detail="controller not found")

    async with forge.client:
        response = await controller.get(node)
        return response.json()


@router.get("/{controller}/{node}/{endpoint}")
async def get_node_endpoints(controller: str,
                             node: str,
                             endpoint: str):
    if not (controller := get_controller(controller)):
        raise HTTPException(status_code=404, detail="controller not found")

    async with forge.client:
        response = await controller.get(node, endpoint=f"/{endpoint}")
        return response.json()


@router.post("/{controller}/{node}/{endpoint}")
async def get_node_endpoints(controller: str,
                             node: str,
                             endpoint: str,
                             request: Request):
    if not (controller := get_controller(controller)):
        raise HTTPException(status_code=404, detail="controller not found")

    data = await request.json()
    async with forge.client:
        response = await controller.post(node, endpoint=f"/{endpoint}", data=data)
        return response.json()
