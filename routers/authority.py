# Thư viện Backend Python
from fastapi import APIRouter, Depends, Request, Cookie, Form, UploadFile, File
from sqlalchemy.orm import Session
import models
import jwt
import datetime
import os
import shutil
from routers import function

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# Khởi chạy nhánh App
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Cấu hình đường dẫn lưu trữ ảnh chuyển khoản
UPLOAD_IMAGE_FOLDER = "static/media/contributions"



# TRANG CHỦ TÁC GIẢ
@router.get('/authority', response_class=HTMLResponse)
async def get_infor_authority(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
        username = decodeJSON["username"]
        user = function.get_user(db, username)

        return templates.TemplateResponse("references/authority.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        "user": user
                                                        })
    else:    
        # Render template với dữ liệu đã cho
        return templates.TemplateResponse("references/authority.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2
                                                        })
    

# TẠO YÊU CẦU GIA NHẬP ADMIN
@router.post('/authority')
async def join_admin(request: Request, username_require: str = Form(), contributor_admin: UploadFile = File(),
                     token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)
            username_require = username

            # Kiểm tra xem User đã tạo yêu cầu chưa
            search_require = db.query(models.JoinAdmin).filter(
                models.JoinAdmin.username_id == username_require,
                models.JoinAdmin.status == 0).all()
            
            if len(search_require) > 0:
                # return f"{username_require} đã gửi yêu cầu trước đó (đang chờ xét duyệt)"
                return templates.TemplateResponse("references/authority.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        "user": user,
                                                        "message_success": f"{username_require} đã gửi yêu cầu trước đó rồi!"
                                                        })
            else:
                contributor_image = None
                if contributor_admin:
                    if len(contributor_admin.filename) != 0:
                        # Tạo tên file 
                        contributor_image_name = f"contributor_{username_require}"
                        
                        # Lưu file vào thư mục upload
                        image_path_contribution = os.path.join(UPLOAD_IMAGE_FOLDER, contributor_image_name)
                        with open(image_path_contribution, "wb") as buffer:
                            shutil.copyfileobj(contributor_admin.file, buffer)

                        # Lưu đường dẫn file image_contributor vào cơ sở dữ liệu
                        contributor_image = f"contributions/{contributor_image_name}"

                new_requirement = models.JoinAdmin(
                    username_id = username_require,
                    image_contribution = contributor_image,
                    inserted_at = datetime.datetime.now(),
                    updated_at = None,
                    status = 0)

                db.add(new_requirement)
                db.commit()
                db.refresh(new_requirement)

                # Gửi yêu cầu thành công
                return templates.TemplateResponse("references/authority.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        "user": user,
                                                        "message_success": f"{username_require} gửi yêu cầu thành công!"
                                                        })
        except:
            return templates.TemplateResponse("errors/error_template.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2,
                                                        })
    else:
        return templates.TemplateResponse("references/authority.html", {"request": request, 
                                                        "mean_star": mean_star, 
                                                        "all_category2": all_category2
                                                        })


# DANH SÁCH CÁC YÊU CẦU GIA NHẬP ADMIN
@router.get('/authority/requirements', response_class=HTMLResponse)
async def get_requirement_list(request: Request, token: str = Cookie(None), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()

    if token:
        try:
            decodeJSON = jwt.decode(token, "secret", algorithms=["HS256"])
            username = decodeJSON["username"]
            user = function.get_user(db, username)

            if user.role != 2:
                return templates.TemplateResponse("errors/not_permit_access.html", {"request": request, 
                                                                             "mean_star": mean_star, 
                                                                             "error": "Không có quyền truy cập trang!"}) 
            else:
                list_requirement = (
                    db.query(
                    models.JoinAdmin.username_id, 
                    models.User.fullname,
                    models.User.email,
                    models.JoinAdmin.inserted_at,
                    models.JoinAdmin.image_contribution
                )
                .join(models.User, models.JoinAdmin.username_id == models.User.username)
                .filter(models.JoinAdmin.status == 0).order_by(models.JoinAdmin.inserted_at).all())
                
                total_users = len(list_requirement)
                
                return templates.TemplateResponse("students/student_require.html", {"request": request, 
                                                                             "list_requirement": list_requirement,
                                                                             "total_users": total_users,
                                                                             "mean_star": mean_star, 
                                                                             "all_category2": all_category2}) 
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
    