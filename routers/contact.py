# Thư viện Backend Python
from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session
import models
from routers import function

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Thư viện gửi mail phản hồi
import smtplib
from email.mime.text import MIMEText


# Khởi chạy nhánh App
router = APIRouter()
templates = Jinja2Templates(directory="templates")



## 6. GỬI EMAIL PHẢN HỒI
# Trang web gửi góp ý phản hồi tới email máy chủ
@router.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request, db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)
    all_category2 = db.query(models.Category).filter(models.Category.delete_flag != 1).all()
    
    return templates.TemplateResponse("contact.html", {"request": request, 
                                                       "mean_star": mean_star, 
                                                       "all_category2": all_category2})

@router.post("/contact")
async def sending_email(request: Request, sending_by_name: str = Form(), sending_by_email: str = Form(), sending_content: str = Form(), rate_star: int = Form(), db: Session = Depends(models.get_db)):
    mean_star = function.get_mean_star(db)

    # Lưu tỷ lệ đánh giá 
    customer_rating = models.OverviewRate(rated_email=sending_by_email, content=sending_content, rated_star=rate_star)
    db.add(customer_rating)
    db.commit()
    db.refresh(customer_rating)
    
    # Nội dung email
    subject = "Góp ý và đánh giá Project"
    email_from = "kibo0603@gmail.com"
    email_to = "tungtq2@rikkeisoft.com"
    
    body = f"""
    SUBJECT: GÓP Ý VÀ ĐÁNH GIÁ TỚI PROJECT from {sending_by_email} - {sending_by_name} \n
    Rating: {rate_star}
    
    Content:
    {sending_content}
    
    Xin chân thành cảm ơn!
    """

    # Tiếp tục thực hiện Logic gửi email
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = email_from
    message["To"] = email_to
    
    # Khởi tạo kết nối
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()       # Bật vùng an toàn lên
    
    # Login tài khoản email
    smtp_email_login = "kibo0603@gmail.com"
    smtp_password_login = "ftzhstecmczzlpmn"        # Mật khẩu mã hóa từ App Password
    server.login(smtp_email_login, smtp_password_login)
    
    # Gửi email
    server.sendmail(email_from, email_to, message.as_string())
    
    # Thoát exit
    server.quit()
    
    return templates.TemplateResponse("contact.html", {"request": request, 
                                                       "mean_star": mean_star,
                                                       "success_message": "Gửi email thành công!"})
