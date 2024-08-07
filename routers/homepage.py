# Thư viện Backend Python
from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
import models
from routers import function
from chatbotai import classifier

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse


# Khởi chạy nhánh App
router = APIRouter()
templates = Jinja2Templates(directory="templates")



# Trang chủ giao diện (trang '/home')
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    all_book = db.query(models.Book).filter(models.Book.delete_flag != 1).all()
    all_student = db.query(models.User).filter(models.User.delete_flag != 1).all()
    new_created_book = db.query(models.Book).filter(models.Book.delete_flag != 1).all()[-1] 

    bestseller_id, bestseller_name, count_view = function.bestsellerbook(db)
    all_highest_book = function.highestbook(db)
    chart_books = function.chartplotseeing(db)
    
    # Render template với dữ liệu đã cho
    return templates.TemplateResponse("home.html", {"request": request, 
                                                    "mean_star": mean_star, 
                                                    "all_category2": all_category2,
                                                    "all_book": all_book,
                                                    "all_student": all_student,
                                                    "bestseller_id": bestseller_id,
                                                    "bestseller_name": bestseller_name,
                                                    "count_view": count_view,
                                                    "all_highest_book": all_highest_book,
                                                    "new_created_book": new_created_book,
                                                    "chart_books": chart_books
                                                    })

# Chuyển trang với chế độ AI
@router.post("/", response_class=HTMLResponse)
async def classifier_search(keyword: str = Form(None), db: Session = Depends(models.get_db)):
    if keyword:
        # Mô hình hóa phân loại văn bản
        test_input_array = classifier.format_testcase(keyword)
       
        if test_input_array == []:
            return RedirectResponse(url="/", status_code=303)
        
        label_for_test = classifier.naivebayes_searching_ai(test_input_array)
        keyword = keyword.strip()

        if label_for_test == "Library":
            books = db.query(models.Book).filter(
                (models.Book.id_book.contains(keyword)) | 
                (models.Book.title.contains(keyword)) | 
                (models.Book.author.contains(keyword)) | 
                (models.Book.year.contains(keyword))
            ).filter(models.Book.delete_flag != 1).order_by(models.Book.id_book).all()

            if len(books) == 0:
                return RedirectResponse(url="/books?bookview=0", status_code=303)
            else:
                return RedirectResponse(url=f"/books/search_book?bookview=0&searching={keyword}", status_code=303)
            
        elif label_for_test == "Student":
            students = db.query(models.User).filter(
                (models.User.username.contains(keyword)) | 
                (models.User.fullname.contains(keyword))
            ).filter(models.User.delete_flag != 1).order_by(models.User.username).all()

            if len(students) == 0:
                return RedirectResponse(url="/users?view=0", status_code=303)
            else:
                return RedirectResponse(url=f"/users/search_students?view=0&searching={keyword}", status_code=303)
            
        elif label_for_test == "Type":
            searching_category = db.query(models.Category).filter(
                (models.Category.category_id.contains(keyword)) | 
                (models.Category.category_name.contains(keyword))
            ).filter(models.Category.delete_flag != 1).all()

            if len(searching_category) == 0:
                return RedirectResponse(url="/category_books", status_code=303)
            else:
                return RedirectResponse(url=f"/category_books/search_category?searching={keyword}", status_code=303)
            
        elif label_for_test == "Authority":
            return RedirectResponse(url="/authority", status_code=303)
        elif label_for_test == "Contact":
            return RedirectResponse(url="/contact", status_code=303)
        else:
            return RedirectResponse(url="/", status_code=303)
    else:
        return RedirectResponse(url="/", status_code=303)
