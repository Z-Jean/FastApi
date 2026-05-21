"""
用户Service - 业务逻辑层，封装CRUD核心逻辑
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import NotFoundException, BadRequestException


class UserService:

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        """创建用户（检查邮箱是否已存在）"""
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise BadRequestException("该邮箱已被注册")
        user = User(**data.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_all_users(db: Session) -> list[User]:
        """查询所有用户（按创建时间倒序）"""
        return db.query(User).order_by(desc(User.created_at)).all()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """根据ID查询用户，不存在则抛出404"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException(f"ID为{user_id}的用户不存在")
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
        """修改用户信息"""
        user = UserService.get_user_by_id(db, user_id)
        update_data = data.model_dump(exclude_unset=True)
        # 如果修改了邮箱，检查是否重复
        if "email" in update_data:
            existing = db.query(User).filter(
                User.email == update_data["email"],
                User.id != user_id
            ).first()
            if existing:
                raise BadRequestException("该邮箱已被其他用户使用")
        for key, value in update_data.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """删除用户"""
        user = UserService.get_user_by_id(db, user_id)
        db.delete(user)
        db.commit()
        return True
