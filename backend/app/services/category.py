"""
分类Service - 业务逻辑层
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException


class CategoryService:

    @staticmethod
    def create_category(db: Session, data: CategoryCreate) -> Category:
        """创建分类（检查名称是否重复）"""
        existing = db.query(Category).filter(Category.name == data.name).first()
        if existing:
            raise BadRequestException("分类名称已存在")
        category = Category(name=data.name)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_all_categories(db: Session) -> list:
        """查询所有分类（含商品数量）"""
        categories = db.query(Category).all()
        result = []
        for cat in categories:
            product_count = db.query(func.count(Product.id)).filter(
                Product.category_id == cat.id
            ).scalar()
            result.append({
                "id": cat.id,
                "name": cat.name,
                "product_count": product_count,
                "created_at": cat.created_at
            })
        return result

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Category:
        """根据ID查询分类"""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise NotFoundException(f"ID为{category_id}的分类不存在")
        return category

    @staticmethod
    def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
        """修改分类"""
        category = CategoryService.get_category_by_id(db, category_id)
        # 检查名称是否和其他分类重复
        existing = db.query(Category).filter(
            Category.name == data.name,
            Category.id != category_id
        ).first()
        if existing:
            raise BadRequestException("分类名称已存在")
        category.name = data.name
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """
        删除分类（若该分类下有商品，禁止删除）
        """
        category = CategoryService.get_category_by_id(db, category_id)
        product_count = db.query(func.count(Product.id)).filter(
            Product.category_id == category_id
        ).scalar()
        if product_count > 0:
            raise ForbiddenException(f"该分类下有{product_count}个商品，禁止删除")
        db.delete(category)
        db.commit()
        return True
