# Thư viện Backend Python
from fastapi import APIRouter, Depends, Request, Form, Query, Cookie, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
import models
import jwt
import datetime
import shutil
import os
from routers import function
import uuid

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# Khởi chạy nhánh App
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Cấu hình đường dẫn lưu trữ file
UPLOAD_IMAGE_FOLDER = "static/media/books"
UPLOAD_PDF_FOLDER = "static/media/files"



## 2. CHỨC NĂNG QUẢN LÝ SÁCH - Thực hiện cách chức năng sử lý sách tương ứng với từng user
# Tạo sách mới khi có quyền User
@router.post('/books/create_book')
async def create_book(request: Request, id: str = Form(), category_id: str = Form(), 
                      title: str = Form(), author: str = Form(), year: int = Form(),  
                      quantity: int = Form(), book_image: UploadFile = File(), book_pdf: UploadFile = File(),
                      db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

    if token != "":
        # Decode
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            # Category tương ứng
            this_category = db.query(models.Category).filter(models.Category.category_id == category_id,
                                                            models.Category.delete_flag != 1).first()
            if this_category:
                category_taken = this_category.category_id
            else:
                category_taken = "default_category_id"
            

            # Ảnh và file cho sách
            book_image_path = None
            book_pdf_path = None

            if book_image:
                if len(book_image.filename) != 0:
                    # Tạo tên file book_image dựa trên book và tên file gốc
                    book_image_filename = f"{username}_{book_image.filename}"

                    # Lưu file vào thư mục upload
                    file_path_image_book = os.path.join(UPLOAD_IMAGE_FOLDER, book_image_filename)
                    with open(file_path_image_book, "wb") as buffer:
                        shutil.copyfileobj(book_image.file, buffer)

                    # Lưu đường dẫn file avatar vào cơ sở dữ liệu
                    book_image_path = f"books/{book_image_filename}"
            
            if book_pdf:
                if len(book_pdf.filename) != 0:
                    # Tạo tên file book_pdf dựa trên book và tên file gốc
                    book_pdf_filename = f"{username}_{book_pdf.filename}"

                    # Lưu file vào thư mục upload
                    file_path_image_book = os.path.join(UPLOAD_PDF_FOLDER, book_pdf_filename)
                    with open(file_path_image_book, "wb") as buffer:
                        shutil.copyfileobj(book_pdf.file, buffer)

                    # Lưu đường dẫn file avatar vào cơ sở dữ liệu
                    book_pdf_path = f"files/{book_pdf_filename}"

            # Thời gian xử lý sách
            insert_at = datetime.datetime.now()
            insert_id = username
            update_at = None
            update_id = None
            delete_at = None
            delete_id = None
            delete_flag = 0
            
            new_book = models.Book(username_id = username, id_book=id, title=title, author=author, year=year, 
                                category_id=category_taken, quantity_amount = quantity,
                                insert_at=insert_at, insert_id=insert_id, update_at=update_at, update_id=update_id,
                                delete_at=delete_at, delete_id=delete_id, delete_flag=delete_flag,
                                image_book=book_image_path, pdf_book=book_pdf_path)
            db.add(new_book)
            db.commit()
            db.refresh(new_book)
            return templates.TemplateResponse("books/add_book.html", {"request": request, 
                                                                "mean_star": mean_star, 
                                                                "success": "Book added successfully!"})
        except:
            return templates.TemplateResponse("books/add_book.html", {"request": request, 
                                                                "mean_star": mean_star, 
                                                                "error": "Nhập thiếu dữ liệu thông tin sách!"})
    else:
        # Chưa đăng nhập tài khoản
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Chưa có tài khoản đăng nhập!"})

@router.get('/books/create_book', response_class=HTMLResponse)
async def get_login(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        all_category = db.query(models.Category.category_id).filter(models.Category.delete_flag != 1).all()
        
        return templates.TemplateResponse("books/add_book.html", {"request": request, 
                                                            "all_category": all_category, 
                                                            "mean_star": mean_star, 
                                                            "all_category2": all_category2})
    else:
        # Chưa đăng nhập tài khoản
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star})
    
    
# Sắp xếp thứ tự sách theo lựu chọn id, title, year (Customer)
@router.get('/books/sort_books', response_class=HTMLResponse)
async def sort_books(bookview: int, choice: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    # Chức năng sắp xếp tất cả các sách
    if choice == "year":
        books = db.query(models.Book).order_by(models.Book.year)
    elif choice == "id":
        books = db.query(models.Book).order_by(models.Book.id_book)
    elif choice == "name":
        books = db.query(models.Book).order_by(models.Book.title)
    
    books = books.filter(models.Book.delete_flag != 1).all()
    total_books = db.query(models.Book).filter(models.Book.delete_flag == 0).count()

    return templates.TemplateResponse("books/sorting_book.html", {
        "request": request,
        "books": books,
        "total_books": total_books,
        "bookview": bookview,
        "mean_star": mean_star, 
        "all_category2": all_category2})


# Tìm kiếm sách (Customer)
@router.get('/books/search_book', response_class=HTMLResponse)
async def search_book(request: Request, bookview: int, searching: str, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    searching = searching.strip()       # Xóa các khoảng trắng dư thừa
   
    books = db.query(models.Book).filter(
        (models.Book.id_book.contains(searching)) | 
        (models.Book.title.contains(searching)) | 
        (models.Book.author.contains(searching)) | 
        (models.Book.year.contains(searching))
    )
    books = books.filter(models.Book.delete_flag != 1).order_by(models.Book.id_book).all()
    total_books = len(books)
    
    return templates.TemplateResponse("books/searching_book.html", {
        "request": request, 
        "books": books, 
        "bookview": bookview,
        "searching": searching,
        "total_books": total_books,
        "mean_star": mean_star,
        "all_category2": all_category2})


# Tìm kiếm sách theo category
@router.get('/books/booktype', response_class=HTMLResponse)
async def search_category_book(request: Request, searching: str, sortby: str = "id", 
                               db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    this_category_by_searching = db.query(models.Category).filter(models.Category.delete_flag != 1,
                                                                  models.Category.category_id == searching).first()

    searching = searching.strip()       # Xóa các khoảng trắng dư thừa
    
    books = db.query(models.Book).filter(
        (models.Book.category_id.contains(searching))
    )

    if sortby == "title":
        books = books.filter(models.Book.delete_flag != 1).order_by(models.Book.title).all()
    else:
        books = books.filter(models.Book.delete_flag != 1).order_by(models.Book.id_book).all()
    total_books = len(books)
    
    return templates.TemplateResponse("books/booktype.html", {
        "request": request, 
        "books": books, 
        "searching": searching,
        "total_books": total_books,
        "mean_star": mean_star,
        "this_category_by_searching": this_category_by_searching,
        "all_category2": all_category2})

    
# Chỉnh sửa sách đối với những sách của User (khác sách User tạo thì không thể sửa)
@router.post('/books/edit_book')
async def edit_book(request: Request, id: str = Form(), category_id: str = Form(), title: str = Form(), 
                    author: str = Form(), year: int = Form(), quantity: int = Form(), 
                    book_image: UploadFile = File(), book_pdf: UploadFile = File(), 
                    db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            user = function.get_user(db, username)
            if user.role != 2:
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

                # Chỉnh sửa ảnh và file sách
                if book_image and book_image.filename:
                    if len(book_image.filename) != 0:
                        # Tạo tên file book_image dựa trên book và tên file gốc
                        unique_suffix = f"{uuid.uuid4().hex[:8]}"
                        book_image_filename = f"{username}_{unique_suffix}_{book_image.filename}"

                        # Lưu file vào thư mục upload
                        file_path_image_book = os.path.join(UPLOAD_IMAGE_FOLDER, book_image_filename)
                        with open(file_path_image_book, "wb") as buffer:
                            shutil.copyfileobj(book_image.file, buffer)

                        # Lưu đường dẫn file avatar vào cơ sở dữ liệu
                        book.image_book = f"books/{book_image_filename}"
                
                if book_pdf and book_pdf.filename:
                    if len(book_pdf.filename) != 0:
                        # Tạo tên file book_pdf dựa trên book và tên file gốc
                        unique_suffix = f"{uuid.uuid4().hex[:8]}"
                        book_pdf_filename = f"{username}_{unique_suffix}_{book_pdf.filename}"

                        # Lưu file vào thư mục upload
                        file_path_image_book = os.path.join(UPLOAD_PDF_FOLDER, book_pdf_filename)
                        with open(file_path_image_book, "wb") as buffer:
                            shutil.copyfileobj(book_pdf.file, buffer)

                        # Lưu đường dẫn file avatar vào cơ sở dữ liệu
                        book.pdf_book= f"files/{book_pdf_filename}"
                
                db.commit()
                db.refresh(book)
                
                return templates.TemplateResponse("books/edit_book.html", {"request": request, 
                                                                     "book": book, 
                                                                     "mean_star": mean_star, 
                                                                     "success_message": "Sửa sách thành công!"})
            else:
                # Không có quyền sửa sách khác User hoặc Admin
                return templates.TemplateResponse("errors/not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Không có quyền sửa sách!"}) 
        except:
            # Đăng nhập sai 
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        # Chưa đăng nhập nên không vào được
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})

@router.get('/books/edit_book', response_class=HTMLResponse)
async def get_edit(request: Request, id: Optional[str] = None, 
                   token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        
        # Tất cả các thể loại sách
        all_category = db.query(models.Category.category_id).filter(models.Category.delete_flag != 1).all()
        
        # Logic chỉ sửa được những sách
        user = function.get_user(db, username)
        if user.role != 2:
            book = db.query(models.Book).filter((models.Book.username_id == username) & (models.Book.id_book == id)).first()
        else:
            book = db.query(models.Book).filter((models.Book.id_book == id)).first()
        
        if book:
            return templates.TemplateResponse("books/edit_book.html", {"request": request, 
                                                                 "book": book, 
                                                                 "all_category": all_category, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
        else:
            # Không thấy sách cần sửa
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                         "mean_star": mean_star, 
                                                                         "error": "Không thấy sách cần sửa!"})
    else:
        # Chưa đăng nhập tài khoản
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})


# Xóa sách theo id có quyền admin và user tương ứng
@router.post('/books/delete_book')
async def delete_book(request: Request, id: str = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)
        
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
                    
                return templates.TemplateResponse("books/delete_book.html", {"request": request, 
                                                                       "book": book, 
                                                                       "mean_star": mean_star, 
                                                                       "success_message": "Sách đã bị xóa!"})
            else:
                # Không có quyền xóa sách
                return templates.TemplateResponse("errors/not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
        except:
            # Xóa sách không hợp lệ (thông tin sai)
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        # Chưa đăng nhập tài khoản
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})

@router.get('/books/delete_book', response_class=HTMLResponse)
async def get_delete(request: Request, id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        book = db.query(models.Book).filter(models.Book.id_book == id).first()
        if book:
            return templates.TemplateResponse("books/delete_book.html", {"request": request, 
                                                                   "book": book, 
                                                                   "mean_star": mean_star, 
                                                                   "all_category2": all_category2})
        else:
            # Không thấy sách cần xóa
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        # Chưa đăng nhập tài khoản
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})


# Hiển thị chi tiết thông tin từng cuốn sách (bao gồm cả Comment)
@router.get('/books/detail_book', response_class=HTMLResponse)
async def get_book_detail(request: Request, token: str = Cookie(None), choice_book: Optional[str] = None, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    this_book_mean_star = function.get_mean_star_for_book(choice_book, db)

    # Logic xem thông tin chi tiết từng loại sách
    this_book_choice = db.query(models.Book).filter(models.Book.id_book == choice_book,
                                                    models.Book.delete_flag == 0).first()
    
    # Hiển thị các bình luận và đánh giá cho sách
    this_comment_book = db.query(models.CommentBook, models.User).join(
        models.User, models.CommentBook.username_id == models.User.username).filter(
            models.CommentBook.book_id == choice_book,
            models.CommentBook.delete_flag == False
    ).order_by(desc(models.CommentBook.insert_at)).all()
    
    if this_book_choice:
        if token:
            try:
                # Decode
                decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
                username = decodeJSON["username"]
                user = function.get_user(db, username)

                # Kiểm tra sách xem người dùng này đang mượn không
                this_user_borrow = db.query(models.BorrowBook).filter(models.BorrowBook.username_id == username,
                                                                      models.BorrowBook.book_id == choice_book,
                                                                      models.BorrowBook.status == 1).all()
                
                if this_user_borrow != []:
                    this_user_borrow = this_user_borrow[0]
                    return templates.TemplateResponse("books/book_detail.html", {
                        "request": request, 
                        "user": user,
                        "mean_star": mean_star,
                        "all_category2": all_category2,
                        "this_book_choice": this_book_choice,
                        "this_user_borrow": this_user_borrow,
                        "this_comment_book": this_comment_book,
                        "this_book_mean_star": this_book_mean_star})
                else:
                    return templates.TemplateResponse("books/book_detail.html", {
                        "request": request, 
                        "user": user,
                        "mean_star": mean_star,
                        "all_category2": all_category2,
                        "this_book_choice": this_book_choice, 
                        "this_comment_book": this_comment_book,
                        "this_book_mean_star": this_book_mean_star})
            except:
                # Đăng nhập bị sai
                return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
        else:
            return templates.TemplateResponse("books/book_detail.html", {
                    "request": request, 
                    "mean_star": mean_star,
                    "all_category2": all_category2,
                    "this_book_choice": this_book_choice,
                    "this_comment_book": this_comment_book,
                    "this_book_mean_star": this_book_mean_star})
    else:
        # Không tìm thấy sách này
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})

# Chức năng bình luận sách cho Users (bao gồm cả xem chi tiết sách)
@router.post('/books/detail_book')
async def comment_this_book(request: Request,  
                            choice_book: str = Form(), 
                            description: str = Form(),
                            star_book: int = Form(),
                            token: str = Cookie(None),
                            db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)

    if token != "":
        # Decode
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]

            new_comment = models.CommentBook(username_id=username, book_id=choice_book,
                                             description_reviewer=description, rate_book=star_book, 
                                             insert_at=datetime.datetime.now(),
                                             update_at=None, delete_at=None, delete_flag=False)
            
            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)
    
            return RedirectResponse(url=f"/books/detail_book?choice_book={choice_book}", status_code=303)
        except:
            # Không có quyền truy cập trang
            return templates.TemplateResponse("errors/not_permit_access.html", {"request": request, 
                                                                            "mean_star": mean_star, 
                                                                            "error": "Page not found"})
    else:
        # Không có tài khoản nên không thể bình luận sách
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})

        
# Đọc tất cả sách (kết hợp Logic phân trang)
@router.get('/books', response_class=HTMLResponse)
async def read_all_books(request: Request, bookview: int, page: int = Query(1, gt=0), page_size: int = Query(10, gt=0), page_size2: int = Query(12, gt = 0), db: Session = Depends(models.get_db)):       
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if bookview == 0: 
        offset = (page - 1) * page_size
        books = db.query(models.Book).filter(models.Book.delete_flag == 0).order_by(models.Book.id_book).offset(offset).limit(page_size).all()
        
        total_books = db.query(models.Book).filter(models.Book.delete_flag == 0).count()
        total_pages = (total_books + page_size - 1) // page_size  # Tính toán tổng số trang

        return templates.TemplateResponse("books/library.html", {
            "request": request,
            "books": books,
            "total_books": total_books,
            "page": page,
            "total_pages": total_pages, 
            "mean_star": mean_star,
            "bookview": bookview, 
            "all_category2": all_category2
        })
    else:
        # Hiển thị view ảnh chung ở template khác
        offset = (page - 1) * page_size2
        books = db.query(models.Book).filter(models.Book.delete_flag == 0).order_by(models.Book.id_book).offset(offset).limit(page_size2).all()
        
        total_books = db.query(models.Book).filter(models.Book.delete_flag == 0).count()
        total_pages = (total_books + page_size2 - 1) // page_size2  # Tính toán tổng số trang

        return templates.TemplateResponse("books/library_view.html", {
            "request": request,
            "books": books,
            "total_books": total_books,
            "page": page,
            "total_pages": total_pages, 
            "mean_star": mean_star,
            "bookview": bookview, 
            "all_category2": all_category2
        })
