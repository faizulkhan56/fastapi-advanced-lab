from fastapi import APIRouter
import sys
import os

# Add versioning-lab directory to path to import utils
versioning_lab_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if versioning_lab_dir not in sys.path:
    sys.path.insert(0, versioning_lab_dir)

from utils.logger import logger
from utils.exception import CustomException

router = APIRouter(tags=["v2"])

@router.get("/items/{item_id}")
async def read_item_v2(item_id: int):
    try:
        logger.info(f"V2 endpoint called for item_id: {item_id}")
        return {
            "version": "v2",
            "item_id": item_id,
            "detail": "Enhanced data from v2"
        }
    except Exception as e:
        logger.error(f"Error in v2 read_item: {str(e)}")
        raise CustomException(f"V2 endpoint error: {str(e)}", sys)
