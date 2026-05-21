"""
商品Service - 业务逻辑层
"""
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate
from app.core.exceptions import NotFoundException, BadRequestException


class ProductService:

    @staticmethod
    def get_all_products(db: Session) -> list[Product]:
        """获取所有商品（联表查询分类名称）"""
        products = db.query(Product).all()
        return products

    @staticmethod
    def create_product(db: Session, data: ProductCreate) -> Product:
        """创建商品（校验分类是否存在）"""
        category = db.query(Category).filter(Category.id == data.category_id).first()
        if not category:
            raise BadRequestException(f"分类ID {data.category_id} 不存在")
        product = Product(**data.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Product:
        """根据ID查询商品，不存在则抛出404"""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundException(f"ID为{product_id}的商品不存在")
        return product

    @staticmethod
    def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
        """修改商品（校验分类是否存在）"""
        product = ProductService.get_product_by_id(db, product_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException("请至少提供一个要修改的字段")
        if "category_id" in update_data:
            category = db.query(Category).filter(
                Category.id == update_data["category_id"]
            ).first()
            if not category:
                raise BadRequestException(f"分类ID {update_data['category_id']} 不存在")
        for key, value in update_data.items():
            setattr(product, key, value)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """删除商品"""
        product = ProductService.get_product_by_id(db, product_id)
        db.delete(product)
        db.commit()
        return True

    @staticmethod
    def get_products_by_category(db: Session, category_id: int) -> list[Product]:
        """根据分类ID查询商品列表（联表查询）"""
        # 先检查分类是否存在
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise NotFoundException(f"ID为{category_id}的分类不存在")
        products = db.query(Product).filter(Product.category_id == category_id).all()
        return products
