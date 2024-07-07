# Thư viện cho các hàm chức năng khác
from fastapi import Request
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import jwt


# Kiểm tra password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Mã hóa mật khẩu
def get_password_hash(password):
    return pwd_context.hash(password)


# Thông tin đối tượng của username
def get_user(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Trang cá nhân của tài khoản
def get_current_user(request: Request):
    token = request.cookies.get("token")
    if token:
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])
            username = payload.get("username")
            if username is None:
                return None
            return username
        except jwt.PyJWTError:
            return None
    return None


# Tính số star trung bình
def get_mean_star(db: Session):
    all_star = db.query(models.OverviewRate.rated_star).all()
    total_star = sum([star[0] for star in all_star])
    star_count = len(all_star)
    mean_star = round(total_star / star_count, 1) if star_count > 0 else 0.0
    return mean_star  
