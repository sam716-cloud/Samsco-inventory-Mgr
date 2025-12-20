import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# 관리자님의 구글 앱스 스크립트 주소
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzcZFITI2cO_3tC7wwfgMNu4h4oJyVMp766MjjVoScuwFkBJO85c6XommRWMaIjx7OP/exec"

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMSCO 재고관리 시스템</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f1f5f9; font-family: 'Apple SD Gothic Neo', sans-serif; }
        .samsco-blue { background-color: #003366; }
        .transition-all { transition: all 0.3s ease; }
    </style>
</head>
<body class="flex flex-col items-center min-h-screen p-4 space-y-6">
    <div class="w-full max-w-md bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
        <div class="samsco-blue p-6 text-white text-center">
            <h1 class="text-2xl font-extrabold tracking-tight">SAMSCO</h1>
            <p class="text-blue-200 text-sm mt-1 font-medium">실시간 입고 등록</p>
        </div>
        
        <form id="stockForm" class="p-6 space-y-4">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">📦 품번 (8자리)</label>
                <input type="text" id="part_number" required placeholder="품번 입력" 
                    class="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:outline-none transition-all text-lg">
                <p id="length_hint" class="text-xs mt-1 text-gray-400 font-medium">현재 글자 수: 0 / 8</p>
            </div>
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">🔢 수량</label>
                <input type="number" id="quantity" required placeholder="0" 
                    class="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all text-lg">
            </div>
            <button type="button" onclick="submitData()"
                class="w-full samsco-blue hover:bg-blue-800 text-white font-bold py-4 rounded-2xl text-lg shadow-lg transform active:scale-95 transition-all">
                데이터 전송하기
            </button>
        </form>
    </div>

    <div class="w-full max-w-md bg-white rounded-3xl shadow-lg p-6 border border-gray-100">
        <h2 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
            <span class="mr-2">📝</span> 최근 전송 내역
        </h2>
        <div id="historyList" class="space-y-3">
            <p class="text-sm text-gray-400 text-center py-4">아직 전송한 내역이 없습니다.</p>
        </div>
    </div>

    <script>
        const partInput = document.getElementById('part_number');
        const hint = document.getElementById('length_hint');
        const historyList = document.getElementById('historyList');

        partInput.addEventListener('input', (e) => {
            const len = e.target.value.length;
            hint.innerText = `현재 글자 수: ${len} / 8`;
            if (len === 8) {
                partInput.classList.remove('border-gray-200');
                partInput.classList.add('border-green-500', 'bg-green-50');
            } else {
                partInput.classList.remove('border-green-500', 'bg-green-50');
                partInput.classList.add('border-gray-200');
            }
        });

        async function submitData(isCancel = false, cancelPart = '', cancelQty = 0, elementId = '') {
            const part = isCancel ? cancelPart : partInput.value;
            const qty = isCancel ? -cancelQty : document.getElementById('quantity').value;
            
            if(!part || !qty) { alert("품번과 수량을 확인해주세요."); return; }

            try {
                const response = await fetch('/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: new URLSearchParams({ 'part_number': part, 'quantity': qty })
                });

                if(response.ok) {
                    if(!isCancel) {
                        addHistory(part, qty);
                        partInput.value = '';
                        document.getElementById('quantity').value = '';
                        partInput.classList.remove('border-green-500', 'bg-green-50');
                        partInput.classList.add('border-gray-200');
                        hint.innerText = "현재 글자 수: 0 / 8";
                        alert("전송 완료!");
                    } else {
                        document.getElementById(elementId).innerHTML = `<div class="w-full text-center py-2 text-red-500 font-bold bg-red-50 rounded-xl border border-red-100 italic">취소 처리됨 (-${cancelQty})</div>`;
                    }
                }
            } catch (e) { alert("연결 오류 발생"); }
        }

        function addHistory(part, qty) {
            if(historyList.innerHTML.includes("아직 전송한 내역이 없습니다")) historyList.innerHTML = '';
            const id = 'item-' + Date.now();
            const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const itemHtml = `
                <div id="${id}" class="flex items-center justify-between p-4 bg-gray-50 rounded-2xl border border-gray-100 transition-all">
                    <div>
                        <div class="font-bold text-gray-800">${part}</div>
                        <div class="text-xs text-gray-500">${time} · ${qty}개</div>
                    </div>
                    <button onclick="submitData(true, '${part}', ${qty}, '${id}')" 
                        class="text-xs font-bold text-red-500 border border-red-200 px-3 py-1 rounded-lg hover:bg-red-50">
                        취소하기
                    </button>
                </div>`;
            historyList.insertAdjacentHTML('afterbegin', itemHtml);
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
    async with httpx.AsyncClient() as client:
        await client.post(GOOGLE_SCRIPT_URL, json={"part_number": part_number, "quantity": quantity})
    return {"status": "success"}
