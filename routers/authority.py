# Thư viện Backend Python
from fastapi import APIRouter, Depends, Request, Cookie
from sqlalchemy.orm import Session
import models
import jwt
from routers import function

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# Khởi chạy nhánh App
router = APIRouter()
templates = Jinja2Templates(directory="templates")



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
                                                        "all_category2": all_category2,
                                                        })