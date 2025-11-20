from fastapi import APIRouter

router = APIRouter(tags=["v1"])

@router.get("/items/{item_id}")
async def read_item_v1(item_id: int):
    return {
        "version": "v1",
        "item_id": item_id,
        "detail": "Data from v1"
    }
