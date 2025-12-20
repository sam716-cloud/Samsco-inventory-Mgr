import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# 관리자님의 구글 앱스 스크립트 주소 (보내주신 주소입니다)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzcZFITI2cO_3tC7wwfgMNu4h4oJyVMp766MjjVoScuwFkBJO85c6XommRWMaIjx7OP/exec"

# 현장용 입력 화면 디자인 (SAMSCO 버전)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMSCO 재고관리 시스템</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f8fafc; font-family: 'Apple SD Gothic Neo', sans-serif; }
        .samsco-blue { background-color: #003366; }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden border border-gray-100">
        <div class="samsco-blue p-8 text-white text-center">
            <h1 class="text-3xl font-extrabold tracking-tight">SAMSCO</h1>
            <p class="text-blue-200 mt-2 font-medium">실시간 입고 등록 시스템</p>
        </div>
        
        <form id="stockForm" class="p-8 space-y-6">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-2">📦 품번 (Item Number)</label>
                <input type="text" id="part_number" required placeholder="예: SH-1234" 
                    class="w-full px-4 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all text-lg">
            </div>
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-2">🔢 수량 (Quantity)</label>
                <input type="number" id="quantity" required placeholder="0" 
                    class="w-full px-4 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all text-lg">
            </div>
            <button type="button" onclick="submitData()"
                class="w-full samsco-blue hover:bg-blue-800 text-white font-bold py-5 rounded-2xl text-xl shadow-lg transform active:scale-95 transition-all">
                데이터 전송하기
            </button>
        </form>
        <div id="status" class="px-8 pb-6 text-center font-bold hidden"></div>
    </div>

    <script>
        async function submitData() {
            const part_number = document.getElementById('part_number').value;
            const quantity = document.getElementById('quantity').value;
            const statusDiv = document.getElementById('status');
            
            if(!part_number || !quantity) { alert("품번과 수량을 입력해주세요."); return; }

            statusDiv.innerText = "⏳ 전송 중...";
            statusDiv.className = "px-8 pb-6 text-center text-blue-600 font-bold";
            statusDiv.classList.remove('hidden');

            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: new URLSearchParams({ 'part_number': part_number, 'quantity': quantity })
                });

                if(response.ok) {
                    statusDiv.innerText = "✅ 구글 시트 저장 완료!";
                    statusDiv.className = "px-8 pb-6 text-center text-green-600 font-bold";
                    document.getElementById('part_number').value = '';
                    document.getElementById('quantity').value = '';
                } else {
                    throw new Error();
                }
            } catch (e) {
                statusDiv.innerText = "❌ 전송 실패. 다시 시도해주세요.";
                statusDiv.className = "px-8 pb-6 text-center text-red-600 font-bold";
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_CONTENT

@app.post("/submit")
async def handle_form(part_number: str = Form(...), quantity: int = Form(...)):
    # 구글 시트로 데이터 쏘기
    async with httpx.AsyncClient() as client:
        data = {"part_number": part_number, "quantity": quantity}
        await client.post(GOOGLE_SCRIPT_URL, json=data)
    return {"status": "success"}
