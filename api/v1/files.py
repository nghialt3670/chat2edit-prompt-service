import traceback

from database.services.canvas_service import CanvasService
from database.services.user_service import UserService
from dependencies.authorization import clerk_validate_user
from dependencies.database import get_canvas_service, get_user_service
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/v1")


@router.get("/files/{file_id}", response_class=StreamingResponse)
async def get_file(
    file_id: str,
    user_service: UserService = Depends(get_user_service),
    canvas_service: CanvasService = Depends(get_canvas_service),
    clerk_user_id=Depends(clerk_validate_user),
):
    try:
        file_object = canvas_service.get(file_id)

        if file_object is None:
            raise HTTPException(404)

        user = user_service.find_by_clerk_user_id(clerk_user_id)
        if file_object.user_id != user.id:
            raise HTTPException(401)

        headers = {
            "Content-Disposition": f'attachment; filename="{file_object.filename}"'
        }
        return StreamingResponse(file_object, headers=headers)

    except HTTPException as e:
        raise e

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(500)
