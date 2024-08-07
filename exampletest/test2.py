# 1. CẬP NHẬT MÃ NHẬN DIỆN GIỌNG NÓI
import speech_recognition as sr

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Tôi: ", end='')
        audio = r.listen(source, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio, language="vi-VN")
            print(text)
            return text
        except sr.UnknownValueError:
            print("Không nhận diện được giọng nói.")
            return None
        except sr.RequestError:
            print("Lỗi kết nối.")
            return None


# 2. CẬP NHẬT MÃ FASTAPI
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from chatbotai import classifier

app = FastAPI()

class VoiceInput(BaseModel):
    keyword: str

@app.post("/search_voice")
async def search_voice(request: Request):
    # Nhận giọng nói từ người dùng
    audio_text = get_audio()  # Gọi hàm để nhận giọng nói
    if audio_text:
        # Tiến hành phân loại và chuyển trang
        test_input_array = classifier.format_testcase(audio_text)
        if test_input_array == []:
            return RedirectResponse(url="/", status_code=303)
        
        label_for_test = classifier.naivebayes_searching_ai(test_input_array)

        if label_for_test == "Library":
            return RedirectResponse(url="/books?bookview=0", status_code=303)
        elif label_for_test == "Student":
            return RedirectResponse(url="/users?view=0", status_code=303)
        elif label_for_test == "Type":
            return RedirectResponse(url="/category_books", status_code=303)
        elif label_for_test == "Authority":
            return RedirectResponse(url="/authority", status_code=303)
        elif label_for_test == "Contact":
            return RedirectResponse(url="/contact", status_code=303)
        else:
            return RedirectResponse(url="/", status_code=303)
    else:
        return RedirectResponse(url="/", status_code=303)


""" Thêm vào file HTML
<form action="/search_voice" method="post">
    <button type="submit">Tìm kiếm bằng giọng nói</button>
</form>
"""
