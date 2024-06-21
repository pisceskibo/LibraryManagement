# Thư viện Backend Python
from fastapi import FastAPI, Depends, Form, Query, Request
from sqlalchemy.orm import Session
import models
from passlib.context import CryptContext
import jwt
import datetime

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


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
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})
    else:    
        passwordHash = get_password_hash(password)
        new_user = models.User(username = username, fullname = fullname, email = email, password = passwordHash, role = role, delete_flag = 0)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return templates.TemplateResponse("register.html", {"request": request, "success": "Account created successfully"})

@app.get('/create_account', response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


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
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get('/login', response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Chức năng đăng xuất tài khoản
@app.get('/logout')
async def logout(request: Request):
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie('token')
    response.delete_cookie('username')
    return response


# Trang cá nhân của tài khoản - Đang hoàn thiện
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
async def read_profile(request: Request):
    current_user = get_current_user(request)
    if current_user:
        return templates.TemplateResponse("profile.html", {"request": request, "username": current_user})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "You are not logged in."})
    



    
    
## 2. CHỨC NĂNG QUẢN LÝ SÁCH - Thực hiện cách chức năng sử lý sách tương ứng với từng user
# Tạo sách mới khi có quyền User
@app.post('/books/create_book')
async def create_book(encoded_jwt: str, id: str = Form(), title: str = Form(), author: str = Form(), year: int = Form(), category_id: str = Form(), quantity: int = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        # Decode
        try:
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
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
            return new_book
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"
    
# Sắp xếp thứ tự sách theo lựu chọn id hoặc là năm (Customer)
@app.get('/books/sort_books', response_class=HTMLResponse)
async def sort_books(choice: str, request: Request, db: Session = Depends(models.get_db)):
    if choice == "year":
        books = db.query(models.Book).order_by(models.Book.year)
    elif choice == "id":
        books = db.query(models.Book).order_by(models.Book.id_book)
    
    books = books.filter(models.Book.delete_flag != 1).all()

    return templates.TemplateResponse("sorting_book.html", {"request": request, "books": books})

# Tìm kiếm sách (Customer)
@app.get('/books/search_book', response_class=HTMLResponse)
async def search_book(searching: str, request: Request, db: Session = Depends(models.get_db)):
    books = db.query(models.Book).filter(
        (models.Book.id_book.contains(searching)) | 
        (models.Book.title.contains(searching)) | 
        (models.Book.author.contains(searching)) | 
        (models.Book.year.contains(searching)) |
        (models.Book.category_id.contains(searching))
    )
    books = books.filter(models.Book.delete_flag != 1).all()
    
    return templates.TemplateResponse("searching_book.html", {"request": request, "books": books, "searching": searching})


# Gộp hai chức năng tìm kiếm và sắp xếp và phân trang
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
@app.put('/books/edit_book')
async def edit_book(encoded_jwt: str, id: str = Form(), title: str = Form(), author: str = Form(), year: int = Form(), category_id: str = Form(), quantity: int = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            user = get_user(db, username)
            if user.role != 1:
                book = db.query(models.Book).filter((models.Book.username_id == username) & (models.Book.id_book == id)).first()
            else:
                book = db.query(models.Book).filter((models.Book.id_book == id)).first()
                

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
                return book
            else:
                return "Book not found"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
            
    else:
        return "Đăng nhập bị lỗi"

# Xóa sách theo id có quyền admin và user tương ứng
@app.delete('/books/delete_book')
async def delete_book(encoded_jwt: str, id: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
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
                    
                return "Sách đã bị xóa"
            else:
                return "Không có quyền xóa sách"

        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        # book = db.query(models.Book).filter((models.Book.username_id == username) & (models.Book.id_book != id)).first()    # Những cuốn sách còn lại
        return "Đăng nhập bị lỗi"
        
# Đọc tất cả sách
@app.get('/books', response_class=HTMLResponse)
async def read_all_books(request: Request, db: Session = Depends(models.get_db)):        
    books = db.query(models.Book).filter(models.Book.delete_flag != 1).all()

    return templates.TemplateResponse("library.html", {"request": request, "books": books})


## 3. QUẢN LÝ NGƯỜI DÙNG
# Thêm admin
@app.put('/users/get_admin')
async def update_role(encoded_jwt: str, finded_username: str = Form(), new_role: int = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)

            if user.role == 1:
                user_update = db.query(models.User).filter(models.User.username == finded_username).first()
                user_update.role = new_role

                db.commit()
                db.refresh(user_update)
                
                return f"Đã update quyền cho {finded_username}"
            else:
                return f"Không có quyền thay đổi cho {finded_username}"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"
    
# Cập nhật lại thông tin người dùng
@app.put('/users/update_user')
async def update_user(encoded_jwt: str, fullname: str = Form(), email: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)
            
            # Update lại thông tin người dùng hiện tại 
            user.fullname = fullname
            user.email = email
            
            db.commit()
            db.refresh(user)
            
            return f"Đã update thông tin {user.username}"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"

# Xóa người dùng theo username
@app.delete('/users/delete_username')
async def delete_username(encoded_jwt: str, deleted_username: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)
        
            if user.role == 1:
                user_clear = db.query(models.User).filter(models.User.username == deleted_username).first()

                if user_clear.role != 1:
                    user_clear.delete_flag = 1
                    
                    db.commit()
                    db.refresh(user_clear)
                    
                    return f"Người {user_clear.username} dùng đã bị xóa"
                else:
                    return "Không xóa được người dùng"
            else:
                return "Không có quyền xóa người dùng"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"

# Hiển thị tất cả danh sách người dùng
@app.get('/users')
async def get_all_users(db: Session = Depends(models.get_db)):
    all_users = db.query(models.User).filter(models.User.delete_flag != 1).all()
    return all_users


## 4. QUẢN LÝ THỂ LOẠI SÁCH
# Thêm thể loại sách mới
@app.post('/category_books/create_category')
async def create_category(encoded_jwt: str, category_id: str = Form(), category_name: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        # Decode
        try:
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = get_user(db, username)
            
            if user.role == 1:
                
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
                return new_category
            else:
                return "Không có quyền thêm thể loại"
            
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
    else:
        return "Đăng nhập bị lỗi"

# Cập nhật thông tin thể loại theo id_category
@app.put('/category_books/update_category')
async def update_category(encoded_jwt: str, category_id: str = Form(), new_category_name: str = Form(), db: Session = Depends(models.get_db)):
    if encoded_jwt != "":
        try:
            # Decode
            decodeJSON = jwt.decode(encoded_jwt, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            user = get_user(db, username)
            if user.role == 1:
                category = db.query(models.Category).filter(models.Category.category_id == category_id).first()

                if category:
                    category.category_name = new_category_name
                    category.update_at = datetime.datetime.now()
                    category.update_id = username
                    
                    db.commit()
                    db.refresh(category)
                    return category
                else:
                    return f"Không có thể loại sách '{category.category_id}' cần thay đổi"
        except:
            return "Sai tên đăng nhập hoặc mật khẩu"
            
    else:
        return "Đăng nhập bị lỗi"
        
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

# Hiển thị tất cả các thể loại sách
@app.get('/category_books')
async def get_all_category(db: Session = Depends(models.get_db)):
    all_category = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    return all_category


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
    

# Trang chủ giao diện
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Render template với dữ liệu đã cho
    return templates.TemplateResponse("home.html", {"request": request})

