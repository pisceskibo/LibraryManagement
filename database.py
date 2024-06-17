from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Tạo database kết nối
DATABASE_URL = "sqlite:///./managebook.db"
# DATABASE_URL = "mysql+pymysql://admin:root123@localhost/managebook"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()