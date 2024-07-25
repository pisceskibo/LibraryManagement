# Thư viện Backend Python
from fastapi import  APIRouter, Depends, Request, Form, Query, Cookie, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import models
import jwt
import shutil
import os
from routers import function

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# Khởi chạy nhánh App
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Cấu hình đường dẫn lưu trữ avatar
UPLOAD_FOLDER = "static/media/avatars"



## 3. QUẢN LÝ NGƯỜI DÙNG
# Thêm admin (chỉ user.role == 2 thì mới thêm được quyền admin)
@router.post('/users/get_admin')
async def update_role(request: Request, finded_username: str = Form(), new_role: int = Form(), db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)

            if user.role == 2:
                user_update = db.query(models.User).filter(models.User.username == finded_username).first()
                user_update.role = new_role

                db.commit()
                db.refresh(user_update)
                
                return templates.TemplateResponse("accounts/change_admin.html", {"request": request, 
                                                                        "finded_username": finded_username, 
                                                                        "mean_star": mean_star, 
                                                                        "success_message": f"Cập nhật quyền thành công cho {finded_username}!"})
            else:
                return templates.TemplateResponse("errors/not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": f"Không có quyền thay đổi user/admin cho {finded_username}!"})

        except:
            return templates.TemplateResponse("errors/not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Page Not Found"})
    else:
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    
@router.get('/users/get_admin', response_class=HTMLResponse)
async def get_change_admin(request: Request, finded_username: Optional[str] = None, 
                           token: str = Cookie(None), db: Session = Depends(models.get_db)):
    if token:
        mean_star = function.get_mean_star(db)
        all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
        
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        user = function.get_user(db, username)
        
        # Logic thay đổi chức năng của user
        if user.role != 2:
            return templates.TemplateResponse("errors/not_permit_access.html", {"request": request, 
                                                                         "mean_star": mean_star, 
                                                                         "error": "Không có quyền thay đổi user/admin"})
        else:
            picked_student = function.get_user(db, finded_username)
            picked_this_role = picked_student.role
            return templates.TemplateResponse("accounts/change_admin.html", {
                "request": request, 
                "finded_username": finded_username,
                "picked_this_role": picked_this_role,
                "mean_star": mean_star,
                'all_category2': all_category2
                })
    else:
       return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                 "mean_star": mean_star, 
                                                                 "error": "Page Not Found"})
    

# Hiển thị thông tin chi tiết từng sinh viên
@router.get('/users/detail_student', response_class=HTMLResponse)
async def get_detail_user(request: Request, username_choice: Optional[str] = None, 
                          db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    # Logic xem thông tin học sinh chi tiết
    user_choice = db.query(models.User).filter((models.User.username == username_choice)).first()
         
    if user_choice:
        get_fullname_userchoice = user_choice.fullname
        get_email_userchoice = user_choice.email
        get_role_userchoice = user_choice.role
            
        return templates.TemplateResponse("students/student_detail.html", {
                "request": request, 
                "mean_star": mean_star,
                "username_choice": username_choice,
                "user": user_choice,
                "get_fullname_userchoice": get_fullname_userchoice,
                "get_email_userchoice": get_email_userchoice,
                "get_role_userchoice": get_role_userchoice,
                "all_category2": all_category2})
    else:
        # Không tìm thấy sinh viên này
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})


# Cập nhật chỉnh sửa lại thông tin người dùng
@router.post('/users/update_user')
async def update_user(request: Request, fullname: str = Form(), email: str = Form(), avatar: UploadFile = File(), 
                      db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)
            
            # Update lại thông tin người dùng hiện tại 
            user.fullname = fullname
            user.email = email

            # Xử lý upload avatar nếu có
            if avatar:
                if len(avatar.filename) != 0:
                    # Tạo tên file avatar dựa trên username và tên file gốc
                    avatar_filename = f"{username}_{avatar.filename}"

                    # Lưu file vào thư mục upload
                    file_path = os.path.join(UPLOAD_FOLDER, avatar_filename)
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(avatar.file, buffer)

                    # Lưu đường dẫn file avatar vào cơ sở dữ liệu
                    user.avatar = f"avatars/{avatar_filename}"
            
            db.commit()
            db.refresh(user)
            
            # Đã update thông tin user.username
            return templates.TemplateResponse("accounts/edit_avatar.html", {"request": request, 
                                                                   "user": user, 
                                                                   "mean_star": mean_star, 
                                                                   "success_message": "Cập nhật thông tin thành công!"})

        except:
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})

@router.get('/users/update_user', response_class=HTMLResponse)
async def get_edit_user(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    if token:
        mean_star = function.get_mean_star(db)
        all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
        
        # Decode
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        
        # Logic chỉnh sửa thông tin cá nhân
        user = function.get_user(db, username)
        
        if user:
            return templates.TemplateResponse("accounts/edit_avatar.html", {"request": request, 
                                                                   "user": user, 
                                                                   "mean_star": mean_star, 
                                                                   "all_category2": all_category2})
        else:
            return templates.TemplateResponse("errors/not_permit_access.html", {"request": request, 
                                                                         "mean_star": mean_star, 
                                                                         "error": "Không có quyền thay đổi trang cá nhân!"})
    else:
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page Not Found"})
    
    
# Xóa người dùng theo username
@router.post('/users/delete_username')
async def delete_username(request: Request, db: Session = Depends(models.get_db), token: str = Cookie(None)):
    mean_star = function.get_mean_star(db)

    if token != "":
        try:
            # Decode
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)
        
            user.delete_flag = 1            
            db.commit()
            db.refresh(user)
                    
            return templates.TemplateResponse("accounts/delete_account.html", {"request": request, 
                                                                      "user": user, 
                                                                      "mean_star": mean_star, 
                                                                      "success_message": "Xóa tài khoản thành công!"})
        except:
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})

@router.get('/users/delete_username', response_class=HTMLResponse)
async def get_delete(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    if token:
        mean_star = function.get_mean_star(db)
        all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
        
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        user = function.get_user(db, username)
        
        if user:
            return templates.TemplateResponse("accounts/delete_account.html", {"request": request, 
                                                                      "user": user, 
                                                                      "mean_star": mean_star, 
                                                                      "all_category2": all_category2})
        else:
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                      "mean_star": mean_star, 
                                                                      "error": "Page not found"})
    else:
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                                  "mean_star": mean_star, 
                                                                  "error": "Page not found"})
    
        
# Tìm kiếm sinh viên (Customer)
@router.get('/users/search_students', response_class=HTMLResponse)
async def search_student(searching: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    searching = searching.strip()       # Xóa các khoảng trắng dư thừa
    
    students = db.query(models.User).filter(
        (models.User.username.contains(searching)) | 
        (models.User.fullname.contains(searching))
    )
    students = students.filter(models.User.delete_flag != 1).order_by(models.User.username).all()
    total_students = len(students)
    
    return templates.TemplateResponse("students/searching_users.html", {
        "request": request, 
        "students": students, 
        "searching": searching,
        "total_students": total_students,
        "mean_star": mean_star, 
        "all_category2": all_category2})


# Lọc sinh viên theo quyền hạn
@router.get('/users/sort_user', response_class=HTMLResponse)
async def search_student_role(choice: str, request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    # Chức năng tìm kiếm tất cả các sách
    if choice == "SuperAdmin":
        this_user = db.query(models.User).filter(models.User.role == 2)
    elif choice == "Admin":
        this_user = db.query(models.User).filter(models.User.role == 1)
    elif choice == "User":
        this_user = db.query(models.User).filter(models.User.role == 0)
    
    this_user = this_user.filter(models.User.delete_flag != 1).order_by(models.User.username).all()
    total_this_user = len(this_user)

    return templates.TemplateResponse("students/student_role.html", {
        "request": request,
        "this_user": this_user,
        "total_this_user": total_this_user,
        "mean_star": mean_star, 
        "all_category2": all_category2})


# Hiển thị tất cả danh sách người dùng (kết hợp phân trang)
@router.get('/users', response_class=HTMLResponse)
async def get_all_users(request: Request, page: int = Query(1, gt=0), page_size: int = Query(8, gt=0), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    offset = (page - 1) * page_size
    all_users = db.query(models.User).filter(models.User.delete_flag == 0).order_by(models.User.username).offset(offset).limit(page_size).all()
    
    total_users = db.query(models.User).filter(models.User.delete_flag == 0).count()
    total_pages = (total_users + page_size - 1) // page_size    # Tinh tổng số trang sẽ có
    
    return templates.TemplateResponse("students/student_list.html", {
        "request": request, 
        "all_users": all_users, 
        "mean_star": mean_star,
        "page": page,
        "total_users": total_users,
        "total_pages": total_pages, 
        "all_category2": all_category2})
