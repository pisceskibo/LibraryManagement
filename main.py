# Thư viện Backend Python
from fastapi import FastAPI, Depends, Form, Request
from sqlalchemy.orm import Session
import models
import jwt
import datetime
from routers import function

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Thư viện nhánh 
from routers import account, book, student, category, contact


# Cài đặt setting cho program
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Nối các đường dẫn bao gồm
app.include_router(account.router)
app.include_router(book.router)
app.include_router(student.router)
app.include_router(category.router)
app.include_router(contact.router)


# Trang chủ giao diện (trang '/home')
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    # Render template với dữ liệu đã cho
    return templates.TemplateResponse("home.html", {"request": request, 
                                                    "mean_star": mean_star, 
                                                    "all_category2": all_category2})



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


## 6. NÂNG CẤP MƯỢN SÁCH (Logic mượn sách khác)
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
    
