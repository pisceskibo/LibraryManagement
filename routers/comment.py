# Thư viện Backend Python
from fastapi import APIRouter, Depends, Request, Form, Cookie
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



# CHỨC NĂNG PHỤC VỤ CHO BÌNH LUẬN SÁCH
# Chỉnh sửa comment
@router.post('/books/comment_edit')
async def edit_comment(request: Request, id_choice: int = Form(), description: str = Form(), rate: int = Form(),
                       token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)

            your_comment_choice = db.query(models.CommentBook).filter(
                models.CommentBook.id == id_choice,
                models.CommentBook.delete_flag == False).all()
            
            if your_comment_choice == []:
                return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
            else:
                
                your_comment_choice = your_comment_choice[0]
                your_comment_choice.description_reviewer = description
                your_comment_choice.rate_book = rate
                your_comment_choice.update_at = datetime.datetime.now()

                db.commit()
                db.refresh(your_comment_choice)

                return templates.TemplateResponse("edit_comment.html", {"request": request, 
                                                                 "user": user,
                                                                 "your_comment_choice": your_comment_choice, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2,
                                                                 "success_message": "Sửa bình luận thành công!"})

        except:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    
@router.get('/books/comment_edit', response_class=HTMLResponse)
async def get_edit_comment(request: Request, id_choice: Optional[int] = None,
                           token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)

            your_comment_choice = db.query(models.CommentBook).filter(
                models.CommentBook.id == id_choice,
                models.CommentBook.delete_flag == False).all()

            if len(your_comment_choice) == 0:
                return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                         "mean_star": mean_star, 
                                                                         "error": "Không thấy bình luận cần sửa!"})
            else:
                your_comment_choice = your_comment_choice[0]

                return templates.TemplateResponse("edit_comment.html", {"request": request, 
                                                                 "user": user,
                                                                 "your_comment_choice": your_comment_choice, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
        except:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    

# Xóa comment
@router.post('/books/comment_delete')
async def delete_comment(request: Request, id_choice: int = Form(), 
                         token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)

            your_comment_choice = db.query(models.CommentBook).filter(
                models.CommentBook.id == id_choice,
                models.CommentBook.delete_flag == False).all()

            if len(your_comment_choice) == 0:
                return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                         "mean_star": mean_star, 
                                                                         "error": "Không thấy bình luận cần xóa!"})
            else:
                your_comment_choice = your_comment_choice[0]
                your_comment_choice.delete_at = datetime.datetime.now()
                your_comment_choice.delete_flag = True

                db.commit()
                db.refresh(your_comment_choice)

                return templates.TemplateResponse("delete_comment.html", {"request": request, 
                                                                 "user": user,
                                                                 "your_comment_choice": your_comment_choice, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2,
                                                                 "success_message": "Xóa bình luận thành công!"})
        except:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})

@router.get('/books/comment_delete', response_class=HTMLResponse)
async def get_delete_comment(request: Request, id_choice: Optional[int] = None, 
                             token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)

            your_comment_choice = db.query(models.CommentBook).filter(
                models.CommentBook.id == id_choice,
                models.CommentBook.delete_flag == False).all()

            if len(your_comment_choice) == 0:
                return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                         "mean_star": mean_star, 
                                                                         "error": "Không thấy bình luận cần xóa!"})
            else:
                your_comment_choice = your_comment_choice[0]

                return templates.TemplateResponse("delete_comment.html", {"request": request, 
                                                                 "user": user,
                                                                 "your_comment_choice": your_comment_choice, 
                                                                 "mean_star": mean_star, 
                                                                 "all_category2": all_category2})
        except:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page not found"})
    else: 
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    