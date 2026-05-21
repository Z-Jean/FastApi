"""
数据库测试数据填充脚本
运行: cd backend && venv\Scripts\python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, Category, Product


def seed():
    db = SessionLocal()
    try:
        # =====================
        # 1. 添加测试用户
        # =====================
        users_data = [
            {"name": "张三", "age": 28, "email": "zhangsan@example.com"},
            {"name": "李四", "age": 35, "email": "lisi@example.com"},
            {"name": "王五", "age": 42, "email": "wangwu@example.com"},
            {"name": "赵六", "age": 25, "email": "zhaoliu@example.com"},
            {"name": "孙七", "age": 31, "email": "sunqi@example.com"},
        ]

        for u in users_data:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user = User(**u)
                db.add(user)
                print(f"  + 添加用户: {u['name']}")

        # =====================
        # 2. 添加商品分类
        # =====================
        categories_data = [
            {"name": "数码电子"},
            {"name": "服装鞋帽"},
            {"name": "食品饮料"},
            {"name": "图书音像"},
            {"name": "家居用品"},
        ]

        added_categories = []
        for c in categories_data:
            existing = db.query(Category).filter(Category.name == c["name"]).first()
            if not existing:
                cat = Category(**c)
                db.add(cat)
                db.flush()
                added_categories.append(cat)
                print(f"  + 添加分类: {c['name']}")
            else:
                added_categories.append(existing)
                print(f"  - 分类已存在: {c['name']}")

        db.commit()  # 确保分类ID已生成

        # =====================
        # 3. 添加商品
        # =====================
        products_data = [
            {"name": "iPhone 15 Pro", "price": 8999.00, "category_id": added_categories[0].id},
            {"name": "MacBook Air M3", "price": 9999.00, "category_id": added_categories[0].id},
            {"name": "AirPods Pro 2", "price": 1899.00, "category_id": added_categories[0].id},
            {"name": "Nike 运动鞋", "price": 699.00, "category_id": added_categories[1].id},
            {"name": "Adidas T恤", "price": 299.00, "category_id": added_categories[1].id},
            {"name": "茅台飞天53度", "price": 1499.00, "category_id": added_categories[2].id},
            {"name": "农夫山泉24瓶装", "price": 35.00, "category_id": added_categories[2].id},
            {"name": "Python编程书籍", "price": 79.00, "category_id": added_categories[3].id},
            {"name": "小米台灯", "price": 169.00, "category_id": added_categories[4].id},
        ]

        for p in products_data:
            existing = db.query(Product).filter(Product.name == p["name"]).first()
            if not existing:
                prod = Product(**p)
                db.add(prod)
                print(f"  + 添加商品: {p['name']}")
            else:
                print(f"  - 商品已存在: {p['name']}")

        db.commit()
        print("\n测试数据填充完成!")

    except Exception as e:
        db.rollback()
        print(f"\n发生错误: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 40)
    print("开始填充测试数据...")
    print("=" * 40)
    seed()
