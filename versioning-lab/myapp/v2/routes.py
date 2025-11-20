from fastapi import APIRouter

router = APIRouter(tags=["v2"])

@router.get("/items/{item_id}")
async def read_item_v2(item_id: int):
    return {
        "version": "v2",
        "item_id": item_id,
        "detail": "Enhanced data from v2"
    }
