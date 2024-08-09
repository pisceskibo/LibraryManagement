# Xuất thư viện giao diện cửa sổ
import tkinter as tk
from tkinter import *
from chatbotai import classifier

# Chuyển đổi văn bản thành giọng nói
from gtts import gTTS
import io
import pygame
import webbrowser       # Truy cập tự động tới website

# Truy cập tới CSDL
from sqlalchemy.orm import Session
import models
from database import SessionLocal
from sqlalchemy import or_


# Tạo cửa số giao diện chính 
def chatbox(username=None):
    global root
    root = tk.Tk()
    root.title("Messenger")
    root.resizable(width=False, height=False)               # Không cho phép thay đổi kích thước
    root.configure(width=510, height=550, bg='#1C2341')     # Kích thước màu nền cửa sổ chính

    # Thiết kế tiêu đề chính
    tk.Label(root, bg='#12182B', fg='#6DFFE7', text="CHATBOT AI", font="Helvetica 13 bold", pady=10).place(relwidth=1)
    # Tiny divider
    tk.Label(root, width=450, bg='#394F46').place(relwidth=1, rely=0.07, relheight=0.012)

    # Text widget để hiển thị tin nhắn
    text = tk.Text(root, width=20, height=2, bg='#12182B', fg='#6DFFE7', font='Helvetica 14', padx=5, pady=5)
    text.place(relheight=0.745, relwidth=1, rely=0.08)
    text.configure(cursor='arrow', state=tk.DISABLED)

    ## Phần người dùng nhập liệu
    # Bottom label
    bottom_label = tk.Label(root, bg='#1C2341', height=80)
    bottom_label.place(relwidth=1, rely=0.825)

    # Message entry box
    message_entry = tk.Entry(bottom_label, bg='#394F46', fg='#6DFFE7', font='Helvetica 14')
    message_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
    message_entry.focus()

    # Send button
    send = tk.Button(bottom_label, text="Send", font="Helvetica 13 bold", width=20, bg="#55BEC0",
                     command=lambda: enter_message(None))
    send.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

    def enter_message(event):
        msg = message_entry.get()
        insert_message_username(msg, username if username else "User")

    def insert_message_username(msg, sender):
        # Nếu đầu vào rỗng
        if not msg:
            return
        t = get_response(msg)

        message_entry.delete(0, tk.END)
        text.configure(state=tk.NORMAL)
        
        # Insert user message aligned to right with background color and border
        text.tag_configure("user", justify='right', background="#55BEC0", foreground="#FFFFFF")
        user_msg = f"{sender}: {msg}"
        user_msg = f"{user_msg}\n{'─' * len(user_msg)}"  # Add a border effect
        text.insert(tk.END, user_msg + "\n", "user")

        # Insert bot response aligned to left with background color and border
        text.tag_configure("bot", justify='left', background="#394F46", foreground="#6DFFE7")
        bot_msg = f"Bot: {t}"
        bot_msg = f"{bot_msg}\n{'─' * len(bot_msg)}"  # Add a border effect
        text.insert(tk.END, bot_msg + "\n", "bot")
        
        text.configure(state=tk.DISABLED)
        text.see(tk.END)
        # Phát âm thanh sau khi hiển thị văn bản
        root.after(500, lambda: text_to_speech(t))

    # Đăng ký sự kiện để xử lý khi cửa sổ bị đóng
    root.protocol("WM_DELETE_WINDOW", root.quit)
    message_entry.bind("<Return>", enter_message)
    root.mainloop()


# Cơ sở dữ liệu phản hồi
def get_response(msg):
    db: Session = SessionLocal()
    # Xử lý dữ liệu cần hỏi
    test_input_array = classifier.format_testcase(msg)
    classifier_data = classifier.naivebayes_searching_ai(test_input_array)
    msg_search = classifier.get_keyword_search(test_input_array)

    # Phản hồi theo từng trường hợp
    if classifier_data == "Library":
        # Tạo danh sách các điều kiện tìm kiếm
        search_conditions = []
        for keyword in msg_search:
            search_conditions.append(models.Book.id_book.contains(keyword))
            search_conditions.append(models.Book.title.contains(keyword))
            search_conditions.append(models.Book.author.contains(keyword))
            
        # Truy vấn sách với các điều kiện tìm kiếm kết hợp với toán tử OR
        books = db.query(models.Book).filter(
            or_(*search_conditions)).filter(models.Book.delete_flag != 1).order_by(models.Book.id_book).all()

        if len(books) == 0:
            response = "Bạn hãy vào mục Library để trải nghiệm nhiều hơn nha!"
        else:
            name_books = [book.title for book in books]
            join_searching = ",".join(name_books)
            response = f"Trong mục Library có những cuốn sách {join_searching} nên bạn có thể vào xem nhé!"
    
    elif classifier_data == "Student":
         # Tạo danh sách các điều kiện tìm kiếm cho sinh viên
        search_conditions = []
        for keyword in msg_search:
            search_conditions.append(models.User.username.contains(keyword))
            search_conditions.append(models.User.fullname.contains(keyword))

        # Truy vấn sinh viên với các điều kiện tìm kiếm kết hợp với toán tử OR
        students = db.query(models.User).filter(
            or_(*search_conditions)).filter(models.User.delete_flag != 1).order_by(models.User.username).all()

        if len(students) == 0:
            response = "Bạn hãy vào mục Student để tra cứu thông tin nha!"
        else:
            name_students = [student.username for student in students]
            join_searching = ",".join(name_students)
            response = f"Trong mục Student có những người liên quan như {join_searching} mà bạn muốn tìm!"

    elif classifier_data == "Type":
        # Tạo danh sách các điều kiện tìm kiếm cho loại tài nguyên
        search_conditions = []
        for keyword in msg_search:
            search_conditions.append(models.Category.category_id.contains(keyword))
            search_conditions.append(models.Category.category_name.contains(keyword))

        # Truy vấn loại tài nguyên với các điều kiện tìm kiếm kết hợp với toán tử OR
        categories = db.query(models.Category).filter(
            or_(*search_conditions)
        ).filter(models.Category.delete_flag != 1).order_by(models.Category.category_name).all()

        if not categories:
            response = "Bạn hãy vào mục Category để biết thêm chi tiết hơn nha!"
        else:
            name_categories = [category.category_name for category in categories]
            join_searching = ", ".join(name_categories)
            response = f"Trong mục Category có các thể loại như: {join_searching}. Bạn có thể vào xem chi tiết hơn nhé!"
    
    elif classifier_data == "Authority":
        response = "Bạn hãy vào mục Authory để biết thêm thông tin chi tiết hơn nha!"
        webbrowser.open("http://127.0.0.1:8000/authority")
    elif classifier_data == "Contact":
        response = "Bạn hãy vào mục Contact để gửi phản hồi nha!"
    else:
        response = "Tôi không hiểu ý bạn! Bạn hãy cung cấp thêm thông tin khác!"
    
    return response

# Hàm để chuyển văn bản thành âm thanh và phát nó
def text_to_speech(text):
    # Khởi tạo gTTS và tạo âm thanh từ văn bản
    tts = gTTS(text=text, lang='vi')
    # Tạo một luồng byte để lưu trữ dữ liệu âm thanh tạm thời
    fp = io.BytesIO()
    # Lưu âm thanh vào luồng byte
    tts.write_to_fp(fp)
    # Đặt con trỏ của luồng ở đầu
    fp.seek(0)
    
    # Khởi tạo pygame mixer
    pygame.mixer.init()
    # Tải âm thanh từ luồng byte vào pygame mixer
    pygame.mixer.music.load(fp, 'mp3')
    # Phát âm thanh
    pygame.mixer.music.play()
    
    # Chờ cho đến khi phát xong
    while pygame.mixer.music.get_busy():
        continue
