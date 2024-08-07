# Thư viện Backend Python (đang phát triển thêm ý tưởng)
from fastapi import APIRouter, Depends, Form, Query
from sqlalchemy.orm import Session
import models
import jwt
import datetime


# Khởi chạy nhánh App
router = APIRouter()


# 1. CHỨC NĂNG HIỂN THỊ SÁCH
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


# 2. CHỨC NĂNG MƯỢN SÁCH
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


## 3. NÂNG CẤP MƯỢN SÁCH (Logic mượn sách khác)
# Mượn sách có thời gian truyền vào
@router.post('/books/borrow_final')
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
@router.put('/books/restore_final')
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
    