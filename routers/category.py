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



## 4. QUẢN LÝ THỂ LOẠI SÁCH
# Thêm thể loại sách mới
@router.post('/category_books/create_category')
async def create_category(request: Request, category_id: str = Form(), category_name: str = Form(), 
                          db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

    if token != "":
        # Decode
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)
            
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
            
                return templates.TemplateResponse("add_category.html", {"request": request, 
                                                                        "mean_star": mean_star, 
                                                                        "success": "Category created successfully!"})
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Không có quyền thêm thể loại sách!"})
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})

@router.get('/category_books/create_category', response_class=HTMLResponse)
async def get_create_category(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
            
        # Logic truy cập tới template tạo thể loại sách
        user = function.get_user(db, username)
        if user.role != 0:
            return templates.TemplateResponse("add_category.html", {"request": request, 
                                                                    "mean_star": mean_star, 
                                                                    "all_category2": all_category2})
        else:
            return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                         "mean_star": mean_star, 
                                                                         "error": "Không có quyền thêm sách!"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, "mean_star": mean_star})
    

# Cập nhật thông tin thể loại theo id_category
@router.post('/category_books/update_category')
async def update_category(request: Request, choice_category_id: str = Form(), new_category_name: str = Form(), 
                          token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            user = function.get_user(db, username)
            if user.role != 0:
                category = db.query(models.Category).filter(models.Category.category_id == choice_category_id).first()
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Không có quyền sửa sách!"})

            if category:
                category.category_name = new_category_name
                category.update_at = datetime.datetime.now()
                category.update_id = username
                
                db.commit()
                db.refresh(category)
                        
                return templates.TemplateResponse("edit_category.html", {
                        "request": request, 
                        "success": "Category updated successfully!",
                        "this_category": category,
                        "choice_category_id": choice_category_id,
                        "mean_star": mean_star
                    })
                
            else:
                # "Không có thể loại sách '{category.category_id}' cần thay đổi"
                return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                          "mean_star": mean_star, 
                                                                          "error": "Page Not Found"})
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page Not Found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    
@router.get('/category_books/update_category', response_class=HTMLResponse)
async def get_edit_category(request: Request, choice_category_id: Optional[str] = None, 
                            token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        try:        
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            
            # Logic chỉnh sửa thông tin cá nhân
            user = function.get_user(db, username)
            
            if user.role != 0:
                this_category = db.query(models.Category).filter(models.Category.category_id == choice_category_id, 
                                                                 models.Category.delete_flag == 0).first()
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Không có quyền sửa thể loại sách!"})
 
            if this_category:
                return templates.TemplateResponse("edit_category.html", {
                        "request": request, 
                        "user": user, 
                        "this_category": this_category,
                        "choice_category_id": choice_category_id, 
                        "mean_star": mean_star, 
                        "all-category2": all_category2})
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Không có thể loại sách này!"})
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page Not Found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    
    
# Xóa thể loại sách theo id_category (chỉ có role != 0 mới có quyền thực hiện)
@router.post('/category_books/delete_category')
async def delete_category(request: Request, deleted_category_id: str = Form(), 
                          token: str = Cookie(None), db: Session = Depends(models.get_db)):
    if token != "":
        mean_star = function.get_mean_star(db)
        
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)
        
            if user.role != 0:
                category_clear = db.query(models.Category).filter(models.Category.category_id == deleted_category_id).first()
                
                category_clear.delete_at = datetime.datetime.now()
                category_clear.delete_id = username
                category_clear.delete_flag = 1
                
                db.commit()
                db.refresh(category_clear)

                # return f"Thể loại {category_clear.category_id} đã bị xóa"
                return templates.TemplateResponse("delete_category.html", {
                    "request": request, 
                    "success_message": "Xóa thể loại thành công!", 
                    "user": user, 
                    "deleted_category_id": deleted_category_id,
                    "choiced_category": category_clear,
                    "mean_star": mean_star})
            else:
                return templates.TemplateResponse("not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Không có quyền xóa thể loại sách này!"})
        except:
            return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page Not Found"})
    else:
        return templates.TemplateResponse("error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})

@router.get('/category_books/delete_category', response_class=HTMLResponse)
async def get_delete(request: Request, deleted_category_id: Optional[str] = None, 
                     token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if token:
        choiced_category = db.query(models.Category).filter(models.Category.category_id == deleted_category_id).first()
        if choiced_category:
            return templates.TemplateResponse("delete_category.html", {"request": request, 
                                                                       "choiced_category": choiced_category, 
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


# Tìm kiếm thể loại sách
@router.get('/category_books/search_category', response_class=HTMLResponse)
async def search_category(searching: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
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
        "mean_star": mean_star,
        "all_category2": all_category2})


# Hiển thị tất cả các thể loại sách
@router.get('/category_books', response_class=HTMLResponse)
async def get_all_category(request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()    
    all_category = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    return templates.TemplateResponse("category_list.html", {"request": request, 
                                                             "all_category": all_category, 
                                                             "mean_star": mean_star, 
                                                             "all_category2": all_category2})
