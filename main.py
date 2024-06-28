# Thư viện Backend Python
from fastapi import FastAPI, Depends, Form, Query, Request, Cookie
from sqlalchemy.orm import Session
import models
from passlib.context import CryptContext
import jwt
import datetime
from typing import Optional

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

# Thư viện gửi mail phản hồi
import smtplib
from email.mime.text import MIMEText


# Cài đặt setting cho program
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")



## 1. ĐĂNG NHẬP VÀ ĐĂNG KÝ
# Tạo tài khoản
@app.post("/create_account", response_class=HTMLResponse)
async def create_account(request: Request, username: str = Form(), fullname: str = Form(), email: str = Form(), password: str = Form(), role: int = Form(), db: Session = Depends(models.get_db)):
    # Kiểm tra có trùng username không?
    user = get_user(db, username)
    
    if user:
        # Username đã tồn tại, cần chọn username khác
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists!"})
    else:    
        passwordHash = get_password_hash(password)
        new_user = models.User(username = username, fullname = fullname, email = email, password = passwordHash, role = role, delete_flag = 0)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return templates.TemplateResponse("register.html", {"request": request, "success": "Account created successfully!"})

@app.get('/create_account', response_class=HTMLResponse)
async def get_register(request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    return templates.TemplateResponse("register.html", {"request": request, "mean_star": mean_star})


# Kiểm tra password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

# Mã hóa mật khẩu
def get_password_hash(password):
    return pwd_context.hash(password)


# Chức năng login lấy token tương ứng
@app.post('/login')
async def login_account(request: Request, username: str = Form(), password: str = Form(), db: Session = Depends(models.get_db)):
    user = get_user(db, username)
    passwordCheck = verify_password(password, user.password)
    if user and passwordCheck and user.delete_flag != 1:
        encoded_jwt = jwt.encode({"username": username, 
                                  "password": passwordCheck}, "secret", algorithm="HS256")

        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="token", value=encoded_jwt)
        response.set_cookie(key="username", value=username)
        return response
    else:
        # Username hoặc Password bị sai
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials!"})

@app.get('/login', response_class=HTMLResponse)
async def get_login(request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    return templates.TemplateResponse("login.html", {"request": request, "mean_star": mean_star})


# Chức năng đăng xuất tài khoản
@app.get('/logout')
async def logout(request: Request):
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie('token')
    response.delete_cookie('username')
    return response


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

@app.get("/profile", response_class=HTMLResponse)
async def read_profile(request: Request, db: Session = Depends(models.get_db)):
    current_username = get_current_user(request)
    mean_star = get_mean_star(db)
    
    if current_username:
        # Lấy dữ liệu từ username
        user_logined = db.query(models.User).filter(models.User.username == current_username).first()
        get_fullname = user_logined.fullname
        get_email = user_logined.email
        get_role = user_logined.role
        
        return templates.TemplateResponse("profile.html", {
            "request": request, "current_username": current_username,
            "get_fullname": get_fullname,
            "get_email": get_email, 
            "get_role": get_role,
            "mean_star": mean_star})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "You are not logged in."})
    


## 2. CHỨC NĂNG QUẢN LÝ SÁCH - Thực hiện cách chức năng sử lý sách tương ứng với từng user
# Tạo sách mới khi có quyền User
@app.post('/books/create_book')
async def create_book(request: Request, id: str = Form(), category_id: str = Form(), title: str = Form(), author: str = Form(), year: int = Form(),  quantity: int = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    if token != "":
        # Decode
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            this_category = db.query(models.Category).filter(models.Category.category_id == category_id and models.Category.delete_flag != 1).first()
            if this_category:
                category_taken = this_category.category_id
            else:
                category_taken = "default_category_id"
            
            # Thời gian xử lý sách
            insert_at = datetime.datetime.now()
            insert_id = username
            update_at = None
            update_id = None
            delete_at = None
            delete_id = None
            delete_flag = 0
            
            new_book = models.Book(username_id = username, id_book=id, title=title, author=author, year=year, category_id=category_taken, quantity_amount = quantity,
                                insert_at=insert_at, insert_id=insert_id, update_at=update_at, update_id=update_id,
                                delete_at=delete_at, delete_id=delete_id, delete_flag=delete_flag)
            db.add(new_book)
            db.commit()
            db.refresh(new_book)
            return templates.TemplateResponse("add_book.html", {"request": request, "success": "Book added successfully!"})
        except:
            return templates.TemplateResponse("add_book.html", {"request": request, "error": "Nhập thiếu dữ liệu thông tin sách!"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Chưa có tài khoản đăng nhập!"})

@app.get('/books/create_book', response_class=HTMLResponse)
async def get_login(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    if token:
        all_category = db.query(models.Category.category_id).filter(models.Category.delete_flag != 1).all()
        
        return templates.TemplateResponse("add_book.html", {"request": request, "all_category": all_category, "mean_star": mean_star})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request})
    
    
# Sắp xếp thứ tự sách theo lựu chọn id hoặc là năm (Customer)
@app.get('/books/sort_books', response_class=HTMLResponse)
async def sort_books(choice: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    # Chức năng tìm kiếm tất cả các sách
    if choice == "year":
        books = db.query(models.Book).order_by(models.Book.year)
    elif choice == "id":
        books = db.query(models.Book).order_by(models.Book.id_book)
    
    books = books.filter(models.Book.delete_flag != 1).all()
    total_books = db.query(models.Book).filter(models.Book.delete_flag == 0).count()

    return templates.TemplateResponse("sorting_book.html", {
        "request": request,
        "books": books,
        "total_books": total_books,
        "mean_star": mean_star})

# Tìm kiếm sách (Customer)
@app.get('/books/search_book', response_class=HTMLResponse)
async def search_book(searching: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    searching = searching.strip()       # Xóa các khoảng trắng dư thừa
    
    books = db.query(models.Book).filter(
        (models.Book.id_book.contains(searching)) | 
        (models.Book.title.contains(searching)) | 
        (models.Book.author.contains(searching)) | 
        (models.Book.year.contains(searching)) |
        (models.Book.category_id.contains(searching))
    )
    books = books.filter(models.Book.delete_flag != 1).all()
    total_books = len(books)
    
    return templates.TemplateResponse("searching_book.html", {
        "request": request, 
        "books": books, 
        "searching": searching,
        "total_books": total_books,
        "mean_star": mean_star})


# Gộp các chức năng tìm kiếm, sắp xếp, phân trang (đang hoàn thiện)
@app.get('/books/extension')
async def search_and_sort(searching_title_book: str = None, searching_author: str = None, searching_category: str = None,
                          searching: str = None, sortby: str = None, 
                          limit: int = Query(10, gt=0),  # Số lượng sách tối đa mỗi trang, mặc định là 5
                          offset: int = Query(0, ge=0),  # Vị trí bắt đầu của trang, mặc định là 0
                          db: Session = Depends(models.get_db)):
    query = db.query(models.Book).filter(models.Book.delete_flag == 0)
    
    # Chức năng tìm kiếm
    if searching_title_book:
        query = query.filter(models.Book.title == searching_title_book)
    if searching_author:
        query = query.filter(models.Book.author == searching_author)
    if searching_category:
        query = query.filter(models.Book.category_id == searching_category)
    
    if searching != None:
        query = query.filter(
            (models.Book.id_book.contains(searching)) | 
            (models.Book.title.contains(searching)) | 
            (models.Book.author.contains(searching)) | 
            (models.Book.year.contains(searching)) |
            (models.Book.category_id.contains(searching)))
    
    # Chức năng sắp xếp
    if sortby == "year":
        query = query.order_by(models.Book.year)
    elif sortby == "id":
        query = query.order_by(models.Book.id_book)
    
    # Chức năng phân trang
    books = query.offset(offset).limit(limit).all()
    
    return books

    
# Chỉnh sửa sách đối với những sách của User (khác sách User tạo thì không thể sửa)
@app.post('/books/edit_book')
async def edit_book(request: Request, id: str = Form(), category_id: str = Form(), title: str = Form(), author: str = Form(), year: int = Form(), quantity: int = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            user = get_user(db, username)
            if user.role == 0:
                book = db.query(models.Book).filter((models.Book.username_id == username) & (models.Book.id_book == id)).first()
            else:
                book = db.query(models.Book).filter((models.Book.id_book == id)).first()
                
            # Sửa sách
            if book:
                book.title = title
                book.author = author
                book.year = year
                book.quantity_amount = quantity
                book.category_id = category_id
                book.update_at = datetime.datetime.now()
                book.update_id = username
                
                db.commit()
                db.refresh(book)
                
                return templates.TemplateResponse("edit_book.html", {"request": request, "book": book, "success_message": "Sửa sách thành công!"})

            else:
                # Không có quyền sửa sách khác User hoặc Admin
                return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có quyền sửa sách!"}) 
        except:
            # Chưa đăng nhập nên không vào được
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})

@app.get('/books/edit_book', response_class=HTMLResponse)
async def get_edit(request: Request, id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    if token:
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        
        # Tất cả các thể loại sách
        all_category = db.query(models.Category.category_id).filter(models.Category.delete_flag != 1).all()
        
        # Logic chỉ sửa được những sách
        user = get_user(db, username)
        if user.role == 0:
            book = db.query(models.Book).filter((models.Book.username_id == username) & (models.Book.id_book == id)).first()
        else:
            book = db.query(models.Book).filter((models.Book.id_book == id)).first()
        
        if book:
            return templates.TemplateResponse("edit_book.html", {"request": request, "book": book, "all_category": all_category, "mean_star": mean_star})
        else:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có quyền sửa sách!"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})


# Xóa sách theo id có quyền admin và user tương ứng
@app.post('/books/delete_book')
async def delete_book(request: Request, id: str = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)
        
            book = db.query(models.Book).filter(models.Book.id_book == id)
            
            if user.role == 0:
                book = book.filter(models.Book.username_id == username)

            book = book.first()
            
            if book:
                book.delete_at = datetime.datetime.now()
                book.delete_id = username
                book.delete_flag = 1
                    
                # db.delete(book)
                db.commit()
                db.refresh(book)
                    
                return templates.TemplateResponse("delete_book.html", {"request": request, "book": book, "success_message": "Sách đã bị xóa!"})
            else:
                # Không có quyền xóa sách
                return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Page not found"})

        except:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})

@app.get('/books/delete_book', response_class=HTMLResponse)
async def get_delete(request: Request, id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    if token:
        book = db.query(models.Book).filter(models.Book.id_book == id).first()
        if book:
            return templates.TemplateResponse("delete_book.html", {"request": request, "book": book, "mean_star": mean_star})
        else:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})
        
        
# Đọc tất cả sách (kết hợp Logic phân trang)
@app.get('/books', response_class=HTMLResponse)
async def read_all_books(request: Request, page: int = Query(1, gt=0), page_size: int = Query(10, gt=0), db: Session = Depends(models.get_db)):       
    mean_star = get_mean_star(db)
     
    offset = (page - 1) * page_size
    books = db.query(models.Book).filter(models.Book.delete_flag == 0).offset(offset).limit(page_size).all()
    
    total_books = db.query(models.Book).filter(models.Book.delete_flag == 0).count()
    total_pages = (total_books + page_size - 1) // page_size  # Tính toán tổng số trang

    return templates.TemplateResponse("library.html", {
        "request": request,
        "books": books,
        "total_books": total_books,
        "page": page,
        "total_pages": total_pages, 
        "mean_star": mean_star
    })



## 3. QUẢN LÝ NGƯỜI DÙNG
# Thêm admin
@app.post('/users/get_admin')
async def update_role(request: Request, finded_username: str = Form(), new_role: int = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)

            if user.role == 2:
                user_update = db.query(models.User).filter(models.User.username == finded_username).first()
                user_update.role = new_role

                db.commit()
                db.refresh(user_update)
                
                return templates.TemplateResponse("change_admin.html", {"request": request, "finded_username": finded_username, "success_message": f"Cập nhật quyền thành công cho {finded_username}!"})
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": f"Không có quyền thay đổi user/admin cho {finded_username}!"})

        except:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})
    
@app.get('/users/get_admin', response_class=HTMLResponse)
async def get_change_admin(request: Request, finded_username: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    if token:
        mean_star = get_mean_star(db)
        
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        user = get_user(db, username)
        
        # Logic thay đổi chức năng của user
        if user.role != 2:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có quyền thay đổi user/admin"})
        else:
            picked_student = get_user(db, finded_username)
            picked_this_role = picked_student.role
            return templates.TemplateResponse("change_admin.html", {
                "request": request, 
                "finded_username": finded_username,
                "picked_this_role": picked_this_role,
                "mean_star": mean_star
                })
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})
    

# Hiển thị thông tin từng sinh viên
@app.get('/users/detail_student', response_class=HTMLResponse)
async def get_detail_user(request: Request, username_choice: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    # Logic xem thông tin học sinh chi tiết
    user_choice = db.query(models.User).filter((models.User.username == username_choice)).first()
         
    if user_choice:
        get_fullname_userchoice = user_choice.fullname
        get_email_userchoice = user_choice.email
        get_role_userchoice = user_choice.role
            
        return templates.TemplateResponse("student_detail.html", {
                "request": request, 
                "mean_star": mean_star,
                "username_choice": username_choice,
                "get_fullname_userchoice": get_fullname_userchoice,
                "get_email_userchoice": get_email_userchoice,
                "get_role_userchoice": get_role_userchoice})
    else:
        # Không tìm thấy sinh viên này
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})

    
# Cập nhật lại thông tin người dùng
@app.post('/users/update_user')
async def update_user(request: Request, fullname: str = Form(), email: str = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)
            
            # Update lại thông tin người dùng hiện tại 
            user.fullname = fullname
            user.email = email
            
            db.commit()
            db.refresh(user)
            
            # Đã update thông tin user.username
            return templates.TemplateResponse("edit_avatar.html", {"request": request, "user": user, "success_message": "Cập nhật thông tin thành công!"})

        except:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})

    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})

@app.get('/users/update_user', response_class=HTMLResponse)
async def get_edit_user(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    if token:
        mean_star = get_mean_star(db)
        
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        
        # Logic chỉnh sửa thông tin cá nhân
        user = get_user(db, username)
        
        if user:
            return templates.TemplateResponse("edit_avatar.html", {"request": request, "user": user, "mean_star": mean_star})
        else:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có quyền thay đổi trang cá nhân!"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})
    
    
# Xóa người dùng theo username
@app.post('/users/delete_username')
async def delete_username(request: Request, db: Session = Depends(models.get_db), token: str = Cookie(None)):
    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)
        
            user.delete_flag = 1            
            db.commit()
            db.refresh(user)
                    
            return templates.TemplateResponse("delete_account.html", {"request": request, "user": user, "success_message": "Xóa tài khoản thành công!"})
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})

@app.get('/users/delete_username', response_class=HTMLResponse)
async def get_delete(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    if token:
        mean_star = get_mean_star(db)
        
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        user = get_user(db, username)
        
        if user:
            return templates.TemplateResponse("delete_account.html", {"request": request, "user": user, "mean_star": mean_star})
        else:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})
    
        
# Tìm kiếm sinh viên (Customer)
@app.get('/users/search_students', response_class=HTMLResponse)
async def search_student(searching: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    searching = searching.strip()       # Xóa các khoảng trắng dư thừa
    
    students = db.query(models.User).filter(
        (models.User.username.contains(searching)) | 
        (models.User.fullname.contains(searching))
    )
    students = students.filter(models.User.delete_flag != 1).all()
    total_students = len(students)
    
    return templates.TemplateResponse("searching_users.html", {
        "request": request, 
        "students": students, 
        "searching": searching,
        "total_students": total_students,
        "mean_star": mean_star})

# Hiển thị tất cả danh sách người dùng (kết hợp phân trang)
@app.get('/users', response_class=HTMLResponse)
async def get_all_users(request: Request, page: int = Query(1, gt=0), page_size: int = Query(8, gt=0), db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    offset = (page - 1) * page_size
    all_users = db.query(models.User).filter(models.User.delete_flag == 0).offset(offset).limit(page_size).all()
    
    total_users = db.query(models.User).filter(models.User.delete_flag == 0).count()
    total_pages = (total_users + page_size - 1) // page_size    # Tinh tổng số trang sẽ có
    
    return templates.TemplateResponse("student_list.html", {
        "request": request, 
        "all_users": all_users, 
        "mean_star": mean_star,
        "page": page,
        "total_users": total_users,
        "total_pages": total_pages})



## 4. QUẢN LÝ THỂ LOẠI SÁCH
# Thêm thể loại sách mới
@app.post('/category_books/create_category')
async def create_category(request: Request, category_id: str = Form(), category_name: str = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    if token != "":
        # Decode
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)
            
            # Chỉ có role != 0 mới thêm được thể loại mới
            if user.role != 0:               
                # Thời gian xử lý thể loại
                insert_at = datetime.datetime.now()
                insert_id = username
                update_at = None
                update_id = None
                delete_at = None
                delete_id = None
                delete_flag = 0
                
                new_category = models.Category(category_id=category_id, category_name=category_name, 
                                            insert_at=insert_at, insert_id=insert_id, update_at=update_at, update_id=update_id,
                                            delete_at=delete_at, delete_id=delete_id, delete_flag=delete_flag)
                
                db.add(new_category)
                db.commit()
                db.refresh(new_category)
            
                return templates.TemplateResponse("add_category.html", {"request": request, "success": "Category created successfully!"})
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có quyền thêm thể loại sách"})
            
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page not found"})

@app.get('/category_books/create_category', response_class=HTMLResponse)
async def get_create_category(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    if token:
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
            
        # Logic chỉnh sửa thông tin cá nhân
        user = get_user(db, username)
        if user.role != 0:
            return templates.TemplateResponse("add_category.html", {"request": request, "mean_star": mean_star})
        else:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có quyền thêm sách!"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request})
    

# Cập nhật thông tin thể loại theo id_category
@app.post('/category_books/update_category')
async def update_category(request: Request, choice_category_id: str = Form(), new_category_name: str = Form(), token: str = Cookie(None), db: Session = Depends(models.get_db)):
    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            user = get_user(db, username)
            if user.role != 0:
                category = db.query(models.Category).filter(models.Category.category_id == choice_category_id).first()
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có quyền sửa sách!"})

            if category:
                category.category_name = new_category_name
                category.update_at = datetime.datetime.now()
                category.update_id = username
                
                db.commit()
                db.refresh(category)
                        
                return templates.TemplateResponse("edit_category.html", {
                        "request": request, 
                        "success": "Category update successfully!",
                        "this_category": category,
                        "choice_category_id": choice_category_id
                    })
                
            else:
                # "Không có thể loại sách '{category.category_id}' cần thay đổi"
                return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})
    
@app.get('/category_books/update_category', response_class=HTMLResponse)
async def get_edit_category(request: Request, choice_category_id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    if token:
        try:        
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            # Logic chỉnh sửa thông tin cá nhân
            user = get_user(db, username)
            
            if user.role != 0:
                this_category = db.query(models.Category).filter(models.Category.category_id == choice_category_id, models.Category.delete_flag == 0).first()
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có quyền sửa thể loại sách!"})
 
            if this_category:
                return templates.TemplateResponse("edit_category.html", {
                        "request": request, 
                        "user": user, 
                        "this_category": this_category,
                        "choice_category_id": choice_category_id, "mean_star": mean_star})

            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, "error": "Không có thể loại sách này!"})
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})

    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "error": "Page Not Found"})
    
    
        
# Xóa thể loại sách theo id_category
@app.delete('/category_books/delete_category')
async def delete_category(encoded_jwt: str, deleted_category_id: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)
        
            if user.role == 1:
                category_clear = db.query(models.Category).filter(models.Category.category_id == deleted_category_id).first()
                
                category_clear.delete_at = datetime.datetime.now()
                category_clear.delete_id = username
                category_clear.delete_flag = 1
                
                db.commit()
                db.refresh(category_clear)

                return f"Thể loại {category_clear.category_id} đã bị xóa"
            else:
                return "Không xóa được thể loại sách"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"



# Tìm kiếm thể loại sách
@app.get('/category_books/search_category', response_class=HTMLResponse)
async def search_category(searching: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    searching = searching.strip()       # Xóa các khoảng trắng dư thừa
    
    searching_category = db.query(models.Category).filter(
        (models.Category.category_id.contains(searching)) | 
        (models.Category.category_name.contains(searching))
    )
    searching_category = searching_category.filter(models.Category.delete_flag != 1).all()
    total_searching_category = len(searching_category)
    
    return templates.TemplateResponse("searching_category.html", {
        "request": request, 
        "searching_category": searching_category, 
        "searching": searching,
        "total_searching_category": total_searching_category,
        "mean_star": mean_star})
    
# Hiển thị tất cả các thể loại sách
@app.get('/category_books', response_class=HTMLResponse)
async def get_all_category(request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    all_category = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    return templates.TemplateResponse("category_list.html", {"request": request, "all_category": all_category, "mean_star": mean_star})




## 5. QUẢN LÝ MƯỢN TRẢ SÁCH
# Mượn sách
@app.post('/books/borrow_book')
async def borrowing_book(encoded_jwt: str, borrow_book_id: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            borrowed_book = db.query(models.Book).filter(models.Book.id_book == borrow_book_id).first()
            if borrowed_book:
                borrowed_book_id = borrow_book_id
                borrowed_book_username = username
                borrowed_book_at = datetime.datetime.now()
                borrowed_book_predict = borrowed_book_at + datetime.timedelta(days=10)  # Dự đoán ngày trả là sau 10 ngày
                borrowed_book_actual = None
                
                if borrowed_book.quantity_amount > 0:
                    borrowed_status = 1
                    borrowed_book.quantity_amount -= 1
                else:
                    return f"Đã hết sách {borrow_book_id}"     
                
                new_borrow_book = models.BorrowBook(book_id = borrowed_book_id, username_id=borrowed_book_username,
                                                    borrow_at=borrowed_book_at, borrow_predict=borrowed_book_predict, borrow_actual=borrowed_book_actual,
                                                    status=borrowed_status)     
                
                db.add(new_borrow_book)
                db.commit()
                db.refresh(new_borrow_book)
                  
                return new_borrow_book
            else:
                return "Không tồn tại sách này trong thư viện"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"
    
# Gửi trả sách
@app.put('/books/restore_book')
async def restore_bookstore(encoded_jwt: str, borrow_book_id: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            find_book_to_restore = db.query(models.BorrowBook).filter(models.BorrowBook.book_id == borrow_book_id)
            find_book_to_restore = find_book_to_restore.filter(models.BorrowBook.status == 1) 
            find_book_to_restore = find_book_to_restore.filter(models.BorrowBook.username_id == username).first()
            
            if find_book_to_restore:
                find_book_to_restore.borrow_actual = datetime.datetime.now()
                
                book_in_library = db.query(models.Book).filter(models.Book.id_book == borrow_book_id).first()
                book_in_library.quantity_amount += 1
                find_book_to_restore.status = 0
                
                db.commit()
                db.refresh(find_book_to_restore)
                
                return f"{username} đã trả sách {find_book_to_restore}"
            else:
                return "Sách này chưa được mượn"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"

# Kiểm tra trạng thái sách (đang mượn và chưa được mượn)
@app.get('/books/show_status_books')
async def show_status(encoded_jwt: str, looking_for_book: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            query_status = db.query(models.BorrowBook).filter(models.BorrowBook.book_id == looking_for_book,
                                                              models.BorrowBook.username_id == username).order_by(models.BorrowBook.id.desc()).first()
            if query_status:
                # return query_status
                if query_status.status == 1:
                    return f"Sách có mã {looking_for_book} đang được mượn"
                else:
                    return f"Sách có mã {looking_for_book} chưa được mượn"
            else:
                return f"Sách có mã {looking_for_book} chưa được mượn"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"
    
# Hiển thị lịch sử mượn trả sách
@app.get('/books/borrows')
async def show_all_borrowed(db: Session = Depends(models.get_db)):
    all_borrowed_books = db.query(models.BorrowBook).all()
    return all_borrowed_books


## 6. NÂNG CẤP MƯỢN SÁCH 
# Mượn sách có thời gian truyền vào
@app.post('/books/borrow_final')
async def borrow_final_book(encoded_jwt: str, borrow_book_id: str = Form(), borrow_start: str = Form(), borrow_delta: int = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            borrowed_book = db.query(models.Book).filter(models.Book.id_book == borrow_book_id).first()
            if borrowed_book:
                if borrowed_book.quantity_amount > 0:
                    borrowed_book_id = borrow_book_id
                    borrowed_book_username = username
                    
                    try:
                        start = borrow_start.split("/")
                        
                        borrowed_book_at = datetime.date(int(start[2]), int(start[1]), int(start[0]))
                        borrowed_book_predict = borrowed_book_at + datetime.timedelta(days = borrow_delta)
                        borrowed_book_actual = None
                        
                        new_borrow_book = models.BorrowBookFinal(book_id = borrowed_book_id, username_id=borrowed_book_username,
                                                    borrow_at=borrowed_book_at, borrow_predict=borrowed_book_predict, borrow_actual=borrowed_book_actual)
                        
                        
                        ## Sách được tham chiếu
                        reference_book = db.query(models.BorrowBookFinal).filter(models.BorrowBookFinal.book_id == borrow_book_id,
                                                                                 models.BorrowBookFinal.borrow_actual == None).order_by(models.BorrowBookFinal.borrow_at).all()
                        
                        # Logic về ngày
                        if reference_book:
                            count_time = 0
                            for i in range(len(reference_book)):
                                if reference_book[i].borrow_at < borrowed_book_at < reference_book[i].borrow_predict or reference_book[i].borrow_at < borrowed_book_predict < reference_book[i].borrow_predict:
                                    count_time += 1
                                
                            if count_time <= borrowed_book.quantity_amount:
                                borrowed_book.quantity_amount -= 1
                            else:
                                return f"Kho mã sách {borrow_book_id} hết hàng"
                            
                        
                        else:
                            if borrowed_book.quantity_amount > 0:
                                borrowed_book.quantity_amount -= 1
                            else:
                                return f"Đã hết sách {borrow_book_id}"
                        
                        db.add(new_borrow_book)
                        db.commit()
                        db.refresh(new_borrow_book)
                        
                        return new_borrow_book
        
                    except:
                        return "Thời gian mượn không hợp lệ"
                else:
                    return f"Đã hết sách {borrow_book_id}"
            else:
                return "Không tồn tại sách này trong thư viện"
            
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"
    
# Gửi trả lại sách
@app.put('/books/restore_final')
async def restore_final_book(encoded_jwt: str, borrow_book_id: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            find_book_to_restore = db.query(models.BorrowBookFinal).filter(
                models.BorrowBookFinal.book_id == borrow_book_id, 
                models.BorrowBookFinal.username_id == username,
                models.BorrowBookFinal.borrow_actual == None
            ).order_by(models.BorrowBookFinal.borrow_at).first()
            
            if find_book_to_restore:
                find_book_to_restore.borrow_actual = datetime.date.today()
                
                book_in_library = db.query(models.Book).filter(models.Book.id_book == borrow_book_id).first()
                book_in_library.quantity_amount += 1
                
                db.commit()
                db.refresh(find_book_to_restore)
                
                return f"{username} đã trả sách {find_book_to_restore}"
            else:
                return 'Sách này chưa được mượn'
        except:
            return "Sai tên đằng nhập hoặc mật khẩu"
    else:
        return  "Đăng nhập bị lỗi"
    
    

## 7. MỘT SỐ TÍNH NĂNG ĐẶC BIỆT KHÁC
# Tính số star trung bình
def get_mean_star(db: Session):
    all_star = db.query(models.OverviewRate.rated_star).all()
    total_star = sum([star[0] for star in all_star])
    star_count = len(all_star)
    mean_star = round(total_star / star_count, 1) if star_count > 0 else 0.0
    return mean_star    

# Trang chủ giao diện
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    # Render template với dữ liệu đã cho
    return templates.TemplateResponse("home.html", {"request": request, "mean_star": mean_star})


# Trang web gửi góp ý phản hồi tới email máy chủ
@app.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request, db: Session = Depends(models.get_db)):
    mean_star = get_mean_star(db)
    
    return templates.TemplateResponse("contact.html", {"request": request, "mean_star": mean_star})

@app.post("/contact")
async def sending_email(request: Request, sending_by_name: str = Form(), sending_by_email: str = Form(), sending_content: str = Form(), rate_star: int = Form(), db: Session = Depends(models.get_db)):
    # Lưu tỷ lệ đánh giá để tính tỷ lệ
    customer_rating = models.OverviewRate(rated_email=sending_by_email, rated_star=rate_star)
    db.add(customer_rating)
    db.commit()
    db.refresh(customer_rating)
    
    # Nội dung email
    subject = "Góp ý và đánh giá Project"
    email_from = "kibo0603@gmail.com"
    email_to = "tungtq2@rikkeisoft.com"
    
    body = f"""
    SUBJECT: GÓP Ý VÀ ĐÁNH GIÁ TỚI PROJECT from {sending_by_email} - {sending_by_name} \n
    Rating: {rate_star}
    
    Content:
    {sending_content}
    
    Xin chân thành cảm ơn!
    """

    # Tiếp tục thực hiện Logic gửi email
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = email_from
    message["To"] = email_to
    
    # Khởi tạo kết nối
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()       # Bật vùng an toàn lên
    
    # Login tài khoản email
    smtp_email_login = "kibo0603@gmail.com"
    smtp_password_login = "qbkcynrqpegqbman"        # Mật khẩu mã hóa từ App Password
    server.login(smtp_email_login, smtp_password_login)
    
    # Gửi email
    server.sendmail(email_from, email_to, message.as_string())
    
    # Thoát exit
    server.quit()
    
    return templates.TemplateResponse("contact.html", {"request": request, "success_message": "Gửi email thành công!"})
