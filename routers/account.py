# Thư viện Backend Python
from fastapi import APIRouter, Depends, Form, Request, Cookie
from sqlalchemy.orm import Session
import models
import jwt
from routers import function

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse


# Khởi chạy nhánh App
router = APIRouter()
templates = Jinja2Templates(directory="templates")



## 1. ĐĂNG NHẬP VÀ ĐĂNG KÝ
# Tạo tài khoản
@router.post("/create_account", response_class=HTMLResponse)
async def create_account(request: Request, username: str = Form(), fullname: str = Form(), 
                         email: str = Form(), password: str = Form(), role: int = Form(), 
                         db: Session = Depends(models.get_db)):
    # Kiểm tra có trùng username không?
    user = function.get_user(db, username)
    mean_star = function.get_mean_star(db)    
    
    if user:
        # Username đã tồn tại, cần chọn username khác
        return templates.TemplateResponse("accounts/register.html", {"request": request, 
                                                            "mean_star": mean_star, 
                                                            "error": "Username already exists!"})
    else:    
        passwordHash = function.get_password_hash(password)
        new_user = models.User(username = username, fullname = fullname, email = email, 
                               password = passwordHash, role = role, delete_flag = 0)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return templates.TemplateResponse("accounts/register.html", {"request": request, 
                                                            "mean_star": mean_star, 
                                                            "success": "Account created successfully!"})

@router.get('/create_account', response_class=HTMLResponse)
async def get_register(request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    return templates.TemplateResponse("accounts/register.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2})


# Chức năng login lấy token tương ứng
@router.post('/login')
async def login_account(request: Request, username: str = Form(), password: str = Form(), 
                        db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)

    user = function.get_user(db, username)
    passwordCheck = function.verify_password(password, user.password)
    if user and passwordCheck and user.delete_flag != 1:
        encoded_jwt = jwt.encode({"username": username, 
                                  "password": passwordCheck}, "secret", algorithm="HS256")

        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="token", value=encoded_jwt)
        response.set_cookie(key="username", value=username)
        return response
    else:
        # Username hoặc Password bị sai
        return templates.TemplateResponse("accounts/login.html", {"request": request, 
                                                         "mean_star": mean_star, 
                                                         "error": "Invalid credentials!"})

@router.get('/login', response_class=HTMLResponse)
async def get_login(request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    return templates.TemplateResponse("accounts/login.html", {"request": request, 
                                                     "mean_star": mean_star, 
                                                     "all_category2": all_category2})


# Chức năng đăng xuất tài khoản
@router.get('/logout')
async def logout():
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie('token')
    response.delete_cookie('username')
    return response


# Thay đổi mật khẩu
@router.post('/change_password')
async def change_your_password(request: Request, old_password: str = Form(), new_password: str = Form(), enter_again_password: str = Form(),
                               token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)

            # Điều kiện thay đổi mật khẩu
            check_old = function.verify_password(old_password, user.password)
            check_old_new = old_password != new_password
            check_new_again = new_password == enter_again_password
            
            if check_old and check_old_new and check_new_again:
                hash_new_password = function.get_password_hash(new_password)
                user.password = hash_new_password

                db.commit()
                db.refresh(user)
        
                return templates.TemplateResponse("accounts/change_password.html", {"request": request, 
                                                        "username": username,
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        "success_message": "Đổi mật khẩu thành công!"
                                                        })
            else:
                return templates.TemplateResponse("accounts/change_password.html", {"request": request, 
                                                        "username": username,
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        "error_message": "Đổi mật khẩu không thành công!"
                                                        })
        except:
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        })
    else:
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        })

@router.get('/change_password', response_class=HTMLResponse)
async def change_password(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]

            return templates.TemplateResponse("accounts/change_password.html", {"request": request, 
                                                        "username": username,
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        })
        except:
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        })
    else:
        return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        })


# Trang cá nhân
@router.get("/profile", response_class=HTMLResponse)
async def read_profile(request: Request, db: Session = Depends(models.get_db)):
    current_username = function.get_current_user(request)
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    if current_username:
        # Lấy dữ liệu từ username
        user_logined = db.query(models.User).filter(models.User.username == current_username).first()
        get_fullname = user_logined.fullname
        get_email = user_logined.email
        get_role = user_logined.role
        
        return templates.TemplateResponse("accounts/profile.html", {
            "request": request, 
            "current_username": current_username,
            "user": user_logined,
            "get_fullname": get_fullname,
            "get_email": get_email, 
            "get_role": get_role,
            "mean_star": mean_star,
            "all_category2": all_category2})
    else:
        return templates.TemplateResponse("accounts/login.html", {"request": request, 
                                                         "mean_star": mean_star, 
                                                         "error": "You are not logged in."})
