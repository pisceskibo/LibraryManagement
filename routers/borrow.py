# Thư viện Backend Python
from fastapi import APIRouter, Depends, Form, Request, Cookie
from sqlalchemy.orm import Session
from typing import Optional
import models
import jwt
import datetime
from routers import function

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# Khởi chạy nhánh App
router = APIRouter()
templates = Jinja2Templates(directory="templates")



## 5. QUẢN LÝ MƯỢN TRẢ SÁCH
# Mượn sách
@router.post('/books/borrow_book')
async def borrowing_book(request: Request, borrow_book_id: str = Form(), token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)
            
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
                  
                return templates.TemplateResponse("book_borrow.html", {"request": request, 
                                                                 "user": user,
                                                                 "borrowed_book": borrowed_book,
                                                                 "new_borrow_book": new_borrow_book,
                                                                 "success_message": "Mượn sách thành công!",
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
            else:
                # Không tồn tại sách trong thư viện
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    
@router.get('/books/borrow_book', response_class=HTMLResponse)
async def get_borrowing_book(request: Request, borrow_book_id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        borrowed_book = db.query(models.Book).filter(models.Book.id_book == borrow_book_id).first()
    
        return templates.TemplateResponse("book_borrow.html", {"request": request, 
                                                                 "borrowed_book": borrowed_book, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    

# Gửi trả sách
@router.post('/books/restore_book')
async def restore_bookstore(request: Request, borrow_book_id: str = Form(), token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            find_book_to_restore = db.query(models.BorrowBook).filter(models.BorrowBook.book_id == borrow_book_id,
                                                                      models.BorrowBook.status == 1,
                                                                      models.BorrowBook.username_id == username).all()

            if find_book_to_restore != []:
                find_book_to_restore = find_book_to_restore[0]
                find_book_to_restore.borrow_actual = datetime.datetime.now()
                
                book_in_library = db.query(models.Book).filter(models.Book.id_book == borrow_book_id).first()
                book_in_library.quantity_amount += 1
                find_book_to_restore.status = 0
                
                db.commit()
                db.refresh(find_book_to_restore)

                # f"{username} đã trả sách {find_book_to_restore}"
                return templates.TemplateResponse("book_restore.html", {"request": request, 
                                                                 "restored_book": find_book_to_restore, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2,
                                                                 "success_message": "Trả sách thành công!"})
            else:
                # return "Sách này chưa được mượn"
                print("Lỗi")
                return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
        except:
            # return "Sai tên đăng nhập hoặc mật khẩu"
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    else:
        # return "Đăng nhập bị lỗi"
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})

@router.get('/books/restore_book', response_class=HTMLResponse)
async def get_restore_book(request: Request, borrow_book_id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        
        restored_book = db.query(models.BorrowBook).filter(models.BorrowBook.book_id == borrow_book_id,
                                                           models.BorrowBook.status == 1,
                                                           models.BorrowBook.username_id == username).first()
        
        return templates.TemplateResponse("book_restore.html", {"request": request, 
                                                                 "restored_book": restored_book, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})


# Hiển thị những sách đang mượn
@router.get('/books/all_borrowed_book', response_class=HTMLResponse)
async def show_all_borrowed_book(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        user = function.get_user(db, username)

        if user.role != 2:
            borrowing_book = (db.query(models.BorrowBook, models.BorrowBook.book_id, models.Book.title,
                                    models.BorrowBook.borrow_at, models.BorrowBook.borrow_predict)
                            .join(models.Book, models.BorrowBook.book_id == models.Book.id_book)
                            .filter(models.BorrowBook.username_id == username, models.BorrowBook.status == 1)
                            .order_by(models.BorrowBook.book_id)
                            .all())
            
            current_time = datetime.datetime.now()
            total_borrowing_books = len(borrowing_book)

            return templates.TemplateResponse("book_borrowing.html", {"request": request, 
                                                                    "borrowing_book": borrowing_book,
                                                                    "total_borrowing_books": total_borrowing_books,
                                                                    "current_time": current_time, 
                                                                    "user": user,
                                                                    "mean_star": mean_star, 
                                                                    "all_category2": all_category2})
        else:
            # Hiển thị lịch sử mượn trả sách (chỉ có SuperAdmin có quyền theo dõi)
            all_borrowed_books = db.query(models.BorrowBook).filter(models.BorrowBook.status == 1).order_by(models.BorrowBook.borrow_at).all()
            total_borrowed_books = len(all_borrowed_books)
            current_time = datetime.datetime.now()

            return templates.TemplateResponse("book_borrowing.html", {"request": request, 
                                                                    "borrowed_book": all_borrowed_books,
                                                                    "total_borrowed_books": total_borrowed_books,
                                                                    "user": user,
                                                                    "current_time": current_time,
                                                                    "mean_star": mean_star, 
                                                                    "all_category2": all_category2})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})


# Hiển thị những sách của mình
@router.get('/books/all_my_books', response_class=HTMLResponse)
async def show_all_my_book(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]

        my_book = db.query(models.Book).filter(models.Book.insert_id == username,
                                               models.Book.delete_flag == 0).order_by(models.Book.id_book).all()
        
        total_my_book = len(my_book)
        
        return templates.TemplateResponse("bookme.html", {"request": request, 
                                                                 "my_book": my_book,
                                                                 "total_my_book": total_my_book, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})


# Tự động trả sách cho user đó (dành cho SuperAdmin)
@router.post('/books/restore_book_user')
async def restore_bookstore(request: Request, username_res: str = Form(), borrow_book_id: str = Form(), token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)
            
            if user.role == 2:
                find_book_to_restore = db.query(models.BorrowBook).filter(models.BorrowBook.book_id == borrow_book_id,
                                                                        models.BorrowBook.status == 1,
                                                                        models.BorrowBook.username_id == username_res).all()
                # Có tìm thấy sách cần trả không?
                if find_book_to_restore != []:
                    find_book_to_restore = find_book_to_restore[0]
                    find_book_to_restore.borrow_actual = datetime.datetime.now()
                    book_in_library = db.query(models.Book).filter(models.Book.id_book == borrow_book_id).first()
                    book_in_library.quantity_amount += 1
                    find_book_to_restore.status = 0

                    db.commit()
                    db.refresh(find_book_to_restore)

                    return templates.TemplateResponse("book_restore_username.html", {"request": request, 
                                                                    "restored_book": find_book_to_restore, 
                                                                    "mean_star": mean_star, 
                                                                    "all_category2": all_category2,
                                                                    "success_message": "Trả sách thành công!"})
                else:
                    # return "Sách này chưa được mượn"
                    print("Lỗi")
                    return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                    "mean_star": mean_star, 
                                                                    "error": "Page Not Found"})
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
        except:
            # return "Sai tên đăng nhập hoặc mật khẩu"
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    else:
        # return "Đăng nhập bị lỗi"
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})

@router.get('/books/restore_book_user', response_class=HTMLResponse)
async def get_restore_book(request: Request, username_res: str, borrow_book_id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        user = function.get_user(db, username)

        if user.role == 2:
            restored_book = db.query(models.BorrowBook).filter(models.BorrowBook.book_id == borrow_book_id,
                                                           models.BorrowBook.status == 1,
                                                           models.BorrowBook.username_id == username_res).first()
        
            return templates.TemplateResponse("book_restore_username.html", {"request": request, 
                                                                 "restored_book": restored_book, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
        else:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})



# Hiển thị lịch sử mượn trả sách (chỉ có SuperAdmin có quyền theo dõi)
@router.get('/books/borrows')
async def show_all_borrowed(db: Session = Depends(models.get_db)):
    all_borrowed_books = db.query(models.BorrowBook).all()
    return all_borrowed_books

# Kiểm tra trạng thái sách (đang mượn và chưa được mượn)
@router.get('/books/show_status_books')
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
    