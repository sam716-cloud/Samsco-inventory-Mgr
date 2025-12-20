from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# 현장용 입력 화면 디자인 (HTML)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMCO 재고관리 시스템</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f8fafc; font-family: 'Apple SD Gothic Neo', sans-serif; }
        .samco-blue { background-color: #003366; } /* 삼현철강 느낌의 짙은 네이비 */
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
        <div class="samco-blue p-8 text-white text-center">
            <h1 class="text-3xl font-extrabold tracking-tight">SAMCO</h1>
            <p class="text-blue-200 mt-2 font-medium">실시간 입고 등록 시스템</p>
        </div>
        
        <form action="/submit" method="post" class="p-8 space-y-6">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-2">📦 품번 (Item Number)</label>
                <input type="text" name="part_number" required placeholder="예: SH-1234" 
                    class="w-full px-4 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all text-lg">
            </div>
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-2">🔢 수량 (Quantity)</label>
                <input type="number" name="quantity" required placeholder="0" 
                    class="w-full px-4 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all text-lg">
            </div>
            <button type="submit" 
                class="w-full samco-blue hover:bg-blue-800 text-white font-bold py-5 rounded-2xl text-xl shadow-lg transform active:scale-95 transition-all">
                데이터 전송하기
            </button>
        </form>
        <div class="bg-gray-50 p-4 text-center">
            <p class="text-xs text-gray-400">© 2024 SAMHYUN STEEL. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_CONTENT

@app.post("/submit")
async def handle_form(part_number: str = Form(...), quantity: int = Form(...)):
    # 여기서 나중에 엑셀 저장이나 DB 저장을 할 거예요!
    # 지금은 일단 잘 받았다는 메시지만 보여줍니다.
    return f"""
    <div style="text-align:center; padding:50px; font-family:sans-serif;">
        <h2 style="color:#003366;">✅ 전송 완료!</h2>
        <p>품번: {part_number} / 수량: {quantity}</p>
        <a href="/" style="display:inline-block; margin-top:20px; padding:10px 20px; background:#003366; color:white; text-decoration:none; border-radius:5px;">돌아가기</a>
    </div>
    """
