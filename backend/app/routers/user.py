"""
用户路由 - Controller层，处理HTTP请求
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user import UserService
from app.core.response import success_response
from app.dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.post("", summary="创建用户")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)   # JWT守卫保护
):
    user = UserService.create_user(db, data)
    return success_response(data=UserResponse.model_validate(user), message="创建用户成功")


@router.get("", summary="查询所有用户")
def get_all_users(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    users = UserService.get_all_users(db)
    return success_response(data=[UserResponse.model_validate(u) for u in users])


@router.get("/{user_id}", summary="查询单个用户")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    user = UserService.get_user_by_id(db, user_id)
    return success_response(data=UserResponse.model_validate(user))


@router.put("/{user_id}", summary="修改用户信息")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    user = UserService.update_user(db, user_id, data)
    return success_response(data=UserResponse.model_validate(user), message="修改用户成功")


@router.delete("/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    UserService.delete_user(db, user_id)
    return success_response(message="删除用户成功")
