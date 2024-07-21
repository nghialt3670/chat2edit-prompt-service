import traceback
from typing import List, Literal

from database.services import ConvService, UserService
from dependencies.authorization import clerk_validate_user
from dependencies.database import get_conv_service, get_user_service
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")


class SettingsResponse(BaseModel):
    theme: Literal["dark", "light"]


class ConvResponse(BaseModel):
    id: str
    title: str


class UserResponse(BaseModel):
    settings: SettingsResponse
    convs: List[ConvResponse]


@router.get("/users/me", response_model=UserResponse)
async def get_user_details(
    clerk_user_id: str = Depends(clerk_validate_user),
    user_service: UserService = Depends(get_user_service),
    conv_service: ConvService = Depends(get_conv_service),
):
    try:
        user = user_service.find_by_clerk_user_id(clerk_user_id)
        if not user:
            user = user_service.create_with_clerk_user_id(clerk_user_id)
            return UserResponse(
                user_id=str(user.id),
                settings=SettingsResponse(theme=user.settings.theme),
                convs=[],
            )

        convs = conv_service.find_by_user_id(user.id)
        return UserResponse(
            settings=SettingsResponse(theme=user.settings.theme),
            convs=[ConvResponse(id=str(conv.id), title=conv.title) for conv in convs],
        )

    except Exception:
        print(traceback.format_exc())
        raise HTTPException(500)
