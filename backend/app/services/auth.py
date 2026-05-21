"""
认证Service - 登录校验、JWT生成
"""
from sqlalchemy.orm import Session
from app.models.category import Admin
from app.core.security import verify_password, create_access_token, hash_password
from app.core.exceptions import UnauthorizedException, NotFoundException
from app.core.config import settings


class AuthService:

    @staticmethod
    def login(db: Session, username: str, password: str) -> dict:
        """
        管理员登录：校验用户名密码，返回JWT令牌
        """
        admin = db.query(Admin).filter(Admin.username == username).first()
        if not admin:
            raise UnauthorizedException("用户名或密码错误")
        if not verify_password(password, admin.password):
            raise UnauthorizedException("用户名或密码错误")
        # 生成JWT令牌
        token = create_access_token(data={"sub": str(admin.id), "role": admin.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_HOURS * 3600
        }

    @staticmethod
    def init_admin(db: Session):
        """
        初始化管理员账号（系统启动时调用，若不存在则创建）
        账号: admin  密码: admin123
        """
        existing = db.query(Admin).filter(Admin.username == "admin").first()
        if not existing:
            admin = Admin(
                username="admin",
                password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("✅ 已自动创建管理员账号: admin / admin123")
