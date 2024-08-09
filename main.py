# Thư viện Backend Python
from fastapi import FastAPI

# Thư viện giao diện
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Thư viện nhánh con API
from routers import homepage, account, book, student, category, contact, borrow, comment, authority


# Cài đặt setting cho program
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Nối các đường dẫn bao gồm
app.include_router(homepage.router)
app.include_router(account.router)
app.include_router(book.router)
app.include_router(student.router)
app.include_router(category.router)
app.include_router(contact.router)
app.include_router(borrow.router)
app.include_router(comment.router)
app.include_router(authority.router)
