# Thư viện Backend Python
from fastapi import APIRouter, Depends, Request, Form, Query, Cookie
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



## 2. CHỨC NĂNG QUẢN LÝ SÁCH - Thực hiện cách chức năng sử lý sách tương ứng với từng user
# Tạo sách mới khi có quyền User
@router.post('/books/create_book')
async def create_book(request: Request, id: str = Form(), category_id: str = Form(), title: str = Form(), author: str = Form(), year: int = Form(),  quantity: int = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

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
            return templates.TemplateResponse("add_book.html", {"request": request, 
                                                                "mean_star": mean_star, 
                                                                "success": "Book added successfully!"})
        except:
            return templates.TemplateResponse("add_book.html", {"request": request, 
                                                                "mean_star": mean_star, 
                                                                "error": "Nhập thiếu dữ liệu thông tin sách!"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Chưa có tài khoản đăng nhập!"})

@router.get('/books/create_book', response_class=HTMLResponse)
async def get_login(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        all_category = db.query(models.Category.category_id).filter(models.Category.delete_flag != 1).all()
        
        return templates.TemplateResponse("add_book.html", {"request": request, 
                                                            "all_category": all_category, 
                                                            "mean_star": mean_star, 
                                                            "all_category2": all_category2})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star})
    
    
# Sắp xếp thứ tự sách theo lựu chọn id, title, year (Customer)
@router.get('/books/sort_books', response_class=HTMLResponse)
async def sort_books(bookview: int, choice: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    # Chức năng tìm kiếm tất cả các sách
    if choice == "year":
        books = db.query(models.Book).order_by(models.Book.year)
    elif choice == "id":
        books = db.query(models.Book).order_by(models.Book.id_book)
    elif choice == "name":
        books = db.query(models.Book).order_by(models.Book.title)
    
    books = books.filter(models.Book.delete_flag != 1).all()
    total_books = db.query(models.Book).filter(models.Book.delete_flag == 0).count()

    return templates.TemplateResponse("sorting_book.html", {
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
    books = books.filter(models.Book.delete_flag != 1).all()
    total_books = len(books)
    
    return templates.TemplateResponse("searching_book.html", {
        "request": request, 
        "books": books, 
        "bookview": bookview,
        "searching": searching,
        "total_books": total_books,
        "mean_star": mean_star,
        "all_category2": all_category2})


# Tìm kiếm sách theo category
@router.get('/books/booktype', response_class=HTMLResponse)
async def search_category_book(request: Request, searching: str, sortby: str = "id", db: Session = Depends(models.get_db)):
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
    
    return templates.TemplateResponse("booktype.html", {
        "request": request, 
        "books": books, 
        "searching": searching,
        "total_books": total_books,
        "mean_star": mean_star,
        "this_category_by_searching": this_category_by_searching,
        "all_category2": all_category2})


# Gộp các chức năng tìm kiếm, sắp xếp, phân trang (đang hoàn thiện)
@router.get('/books/extension')
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
@router.post('/books/edit_book')
async def edit_book(request: Request, id: str = Form(), category_id: str = Form(), title: str = Form(), author: str = Form(), year: int = Form(), quantity: int = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            user = function.get_user(db, username)
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
                
                return templates.TemplateResponse("edit_book.html", {"request": request, 
                                                                     "book": book, 
                                                                     "mean_star": mean_star, 
                                                                     "success_message": "Sửa sách thành công!"})
            else:
                # Không có quyền sửa sách khác User hoặc Admin
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Không có quyền sửa sách!"}) 
        except:
            # Chưa đăng nhập nên không vào được
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})

@router.get('/books/edit_book', response_class=HTMLResponse)
async def get_edit(request: Request, id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
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
        if user.role == 0:
            book = db.query(models.Book).filter((models.Book.username_id == username) & (models.Book.id_book == id)).first()
        else:
            book = db.query(models.Book).filter((models.Book.id_book == id)).first()
        
        if book:
            return templates.TemplateResponse("edit_book.html", {"request": request, 
                                                                 "book": book, 
                                                                 "all_category": all_category, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
        else:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                         "mean_star": mean_star, 
                                                                         "error": "Không có quyền sửa sách!"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
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
                    
                return templates.TemplateResponse("delete_book.html", {"request": request, 
                                                                       "book": book, 
                                                                       "mean_star": mean_star, 
                                                                       "success_message": "Sách đã bị xóa!"})
            else:
                # Không có quyền xóa sách
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})

        except:
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})

@router.get('/books/delete_book', response_class=HTMLResponse)
async def get_delete(request: Request, id: Optional[str] = None, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        book = db.query(models.Book).filter(models.Book.id_book == id).first()
        if book:
            return templates.TemplateResponse("delete_book.html", {"request": request, 
                                                                   "book": book, 
                                                                   "mean_star": mean_star, 
                                                                   "all_category2": all_category2})
        else:
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})
        
        
# Đọc tất cả sách (kết hợp Logic phân trang)
@router.get('/books', response_class=HTMLResponse)
async def read_all_books(request: Request, bookview: int, page: int = Query(1, gt=0), page_size: int = Query(10, gt=0), page_size2: int = Query(12, gt = 0), db: Session = Depends(models.get_db)):       
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if bookview == 0: 
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
            "mean_star": mean_star,
            "bookview": bookview, 
            "all_category2": all_category2
        })
    else:
        # Hiển thị view ảnh chung ở template khác
        offset = (page - 1) * page_size2
        books = db.query(models.Book).filter(models.Book.delete_flag == 0).offset(offset).limit(page_size2).all()
        
        total_books = db.query(models.Book).filter(models.Book.delete_flag == 0).count()
        total_pages = (total_books + page_size2 - 1) // page_size2  # Tính toán tổng số trang

        return templates.TemplateResponse("library_view.html", {
            "request": request,
            "books": books,
            "total_books": total_books,
            "page": page,
            "total_pages": total_pages, 
            "mean_star": mean_star,
            "bookview": bookview, 
            "all_category2": all_category2
        })