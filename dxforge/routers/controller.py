from fastapi import APIRouter, Request, HTTPException
from ..forge import Forge

router = APIRouter()
forge = Forge()


def get_controller(name: str):
    return forge.orchestrator.controllers.get(name, None)


@router.get("/")
async def get_status():
    running = {controller_name: [] for controller_name in forge.orchestrator.controllers}
    stopped = {controller_name: [] for controller_name in forge.orchestrator.controllers}
    status = await forge.orchestrator.status()
    for controller_name, controller_status in status.items():
        for node_name, node_status in controller_status.items():
            if node_status == "running":
                running[controller_name].append(node_name)
            else:
                stopped[controller_name].append(node_name)
    return {"running": running, "stopped": stopped}


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
