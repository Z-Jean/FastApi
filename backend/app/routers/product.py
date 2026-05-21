"""
商品路由 - Controller层
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product import ProductService
from app.core.response import success_response
from app.dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/products", tags=["商品管理"])


@router.get("", summary="获取商品列表")
def get_products(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    products = ProductService.get_all_products(db)
    return success_response(
        data=[ProductResponse.model_validate(p) for p in products]
    )


@router.post("", summary="添加商品")
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    product = ProductService.create_product(db, data)
    return success_response(
        data=ProductResponse.model_validate(product),
        message="添加商品成功"
    )


@router.get("/category/{category_id}", summary="根据分类ID查询商品列表")
def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    products = ProductService.get_products_by_category(db, category_id)
    return success_response(
        data=[ProductResponse.model_validate(p) for p in products]
    )


@router.put("/{product_id}", summary="修改商品")
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    product = ProductService.update_product(db, product_id, data)
    return success_response(
        data=ProductResponse.model_validate(product),
        message="修改商品成功"
    )


@router.delete("/{product_id}", summary="删除商品")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin)
):
    ProductService.delete_product(db, product_id)
    return success_response(message="删除商品成功")
