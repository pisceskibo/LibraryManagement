# Thư viện xây dựng Models
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Text
from database import Base, engine, SessionLocal
from sqlalchemy.orm import relationship


# Model User
class User(Base):
    __tablename__ = 'users'
    username = Column(String(30), primary_key=True, unique=True, index=True)
    fullname = Column(String(100), index=True)
    email = Column(String(100), index=True)
    password = Column(String(100), index=True)
    role = Column(Integer, index=True)
    delete_flag = Column(Integer, index=True)
    avatar = Column(String(500), index=True, nullable=True)     # Trường thông tin avatar
    
    # Tạo mối quan hệ giữa hai bảng
    books = relationship("Book", back_populates="user")
    comments = relationship("CommentBook", back_populates="usercomment")
    join_requests = relationship('JoinAdmin', back_populates='user')
    
    
# Model sách
class Book(Base):
    __tablename__ = 'books'
    username_id = Column(String(30), ForeignKey('users.username'), nullable=False)
    id_book = Column(String(30), primary_key=True, unique=True, index=True)         # Số thứ tự sách
    title = Column(String(100), index=True)      # Tiêu đề sách
    author = Column(String(100), index=True)     # Tác giả
    year = Column(Integer)                  # Năm xuất bản
    
    # Số lượng sách tương ứng
    quantity_amount = Column(Integer, index=True, default=0)
    
    # Thể loại
    category_id = Column(String(10), ForeignKey('category.category_id'), nullable=False)
    
    # Các chức năng thêm, sửa, xóa
    insert_at = Column(DateTime, index=True)
    insert_id = Column(String(30), index=True)
    update_at = Column(DateTime,index=True)
    update_id = Column(String(30), index=True)
    delete_at = Column(DateTime,index=True)
    delete_id = Column(String(30), index=True)
    delete_flag = Column(Integer, index=True)

    # Thông tin thêm về ảnh và file PDF
    image_book = Column(String(100), index=True, nullable=True)         # Đường dẫn tới ảnh của sách
    pdf_book = Column(String(100), index=True, nullable=True)           # Đường dẫn tới file PDF của sách
    

    # Tạo mối liên hệ giữa các bảng
    user = relationship("User", back_populates="books")
    category = relationship("Category", back_populates="category_books")
    borrows = relationship("BorrowBook", back_populates="book_borrow")
    borrowfinal = relationship("BorrowBookFinal", back_populates="book_borrow_final")
    comments = relationship("CommentBook", back_populates="book")


# Model Category
class Category(Base):
    __tablename__ = 'category'
    category_id = Column(String(10), primary_key=True, index=True)
    category_name = Column(String(50), index=True)
    
     # Các chức năng thêm, sửa, xóa thể loại
    insert_at = Column(DateTime, index=True)
    insert_id = Column(String(30), index=True)
    update_at = Column(DateTime,index=True)
    update_id = Column(String(30), index=True)
    delete_at = Column(DateTime,index=True)
    delete_id = Column(String(30), index=True)
    delete_flag = Column(Integer, index=True)
    
    # Tạo mối liên hệ giữa hai bảng
    category_books = relationship("Book", back_populates="category")
    
    # Phương thức toString()
    def __str__(self):
        return self.category_id
    
    
# Model BorrowBook
class BorrowBook(Base):
    __tablename__ = 'borrow'
    id = Column(Integer, primary_key=True, autoincrement=True)          # Khóa chính mới
    book_id = Column(String(30), ForeignKey('books.id_book'), nullable=False)
    username_id = Column(String(50), index=True)
    borrow_at = Column(DateTime, index=True)
    borrow_predict = Column(DateTime, index=True)
    borrow_actual = Column(DateTime, index=True)
    status = Column(Integer, index=True, default=0)
    
    # Tạo mối liên hệ giữa 2 bảng
    book_borrow = relationship("Book", back_populates="borrows")
    
    
# Model BorrowBookFinal
class BorrowBookFinal(Base):
    __tablename__ = 'finalborrow'
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(String(30), ForeignKey('books.id_book'), nullable=False)
    username_id = Column(String(50), index=True)
    borrow_at = Column(Date, index=True)
    borrow_predict = Column(Date, index=True)
    borrow_actual = Column(Date, index=True)
    
    # Tại mối liên hệ giữa 2 bảng
    book_borrow_final = relationship("Book", back_populates="borrowfinal")


# Model CommentBook
class CommentBook(Base):
    __tablename__ = 'commentbook'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Khóa chính mới cho bảng
    username_id = Column(String(30), ForeignKey('users.username'), nullable=False, index=True)
    book_id = Column(String(30), ForeignKey('books.id_book'), nullable=False, index=True)
    description_reviewer = Column(Text, nullable=False, index=True)
    rate_book = Column(Integer, nullable=False, index=True)

    # Sửa và xóa bình luận
    insert_at = Column(DateTime, index=True)
    update_at = Column(DateTime, index=True)
    delete_at = Column(DateTime, index=True)
    delete_flag = Column(Boolean, index=True)

    # Tạo mối liên kết giữa các bảng
    usercomment = relationship("User", back_populates="comments")
    book = relationship("Book", back_populates="comments")


# Model JoinAdmin (bảng yêu cầu Admin)
class JoinAdmin(Base):
    __tablename__ = 'joinadmin'
    id = Column(Integer, primary_key=True, autoincrement=True)          # Khóa chính mới cho bảng
    username_id = Column(String(30), ForeignKey('users.username'), nullable=False, index=True)
    image_contribution = Column(String(100), index=True, nullable=True)         # Lưu thông tin chuyển khoản

    # Update
    inserted_at = Column(DateTime, index=True)      # Thời gian tạo yêu cầu (User)
    updated_at = Column(DateTime, index=True)       # Thời gian update quyền (SuperAdmin)
    status = Column(Boolean, index=True)            # Trạng thái đã đổi           

    # Tạo liên kết giữa các bảng
    user = relationship('User', back_populates='join_requests')


# Model OverviewRate (tỷ lệ đánh giá sao)
class OverviewRate(Base):
    __tablename__ = 'ratetable'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rated_email = Column(String(100), index=True)
    content = Column(Text, nullable=False, index=True)
    rated_star = Column(Integer)


Base.metadata.create_all(bind=engine)

# Kết nối tới cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
