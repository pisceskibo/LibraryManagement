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

# Thư viện nhánh con API
from routers import account, book, student, category, contact, borrow, comment


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
app.include_router(borrow.router)
app.include_router(comment.router)


# Trang chủ giao diện (trang '/home')
@app.get("/", response_class=HTMLResponse)
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
