"""
商品分类路由 - Controller层
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category import CategoryService
from app.core.response import success_response
from app.dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/categories", tags=["商品分类管理"])


@router.post("", summary="添加分类")
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    category = CategoryService.create_category(db, data)
    return success_response(data={"id": category.id, "name": category.name}, message="创建分类成功")


@router.get("", summary="查询所有分类（含商品数量）")
def get_all_categories(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    categories = CategoryService.get_all_categories(db)
    return success_response(data=categories)


@router.put("/{category_id}", summary="修改分类")
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    category = CategoryService.update_category(db, category_id, data)
    return success_response(data={"id": category.id, "name": category.name}, message="修改分类成功")


@router.delete("/{category_id}", summary="删除分类")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    CategoryService.delete_category(db, category_id)
    return success_response(message="删除分类成功")
