import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzcZFITI2cO_3tC7wwfgMNu4h4oJyVMp766MjjVoScuwFkBJO85c6XommRWMaIjx7OP/exec"

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMSCO 창고입고 입력 시스템</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f8fafc; font-family: 'Apple SD Gothic Neo', sans-serif; }
        .samsco-blue { background-color: #003366; }
        /* 부드러운 색상 변화를 위한 효과 */
        .transition-all { transition: all 0.3s ease; }
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
                <label class="block text-sm font-bold text-gray-700 mb-2">📦 품번 (8자리 권장)</label>
                <input type="text" id="part_number" required placeholder="품번 입력" 
                    class="w-full px-4 py-4 rounded-xl border-2 border-gray-200 focus:outline-none transition-all text-lg">
                <p id="length_hint" class="text-xs mt-2 text-gray-400 font-medium">현재 글자 수: 0 / 8</p>
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
        const partInput = document.getElementById('part_number');
        const hint = document.getElementById('length_hint');

        // 실시간 글자 수 체크 로직
        partInput.addEventListener('input', function(e) {
            const length = e.target.value.length;
            hint.innerText = `현재 글자 수: ${length} / 8`;

            if (length === 8) {
                partInput.classList.replace('border-gray-200', 'border-green-500');
                partInput.classList.add('bg-green-50');
                hint.classList.replace('text-gray-400', 'text-green-600');
            } else {
                partInput.classList.remove('border-green-500', 'bg-green-50');
                partInput.classList.add('border-gray-200');
                hint.classList.replace('text-green-600', 'text-gray-400');
            }
        });

        async function submitData() {
            const part_number = partInput.value;
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
                    statusDiv.innerText = "✅ 저장 완료!";
                    statusDiv.className = "px-8 pb-6 text-center text-green-600 font-bold";
                    partInput.value = '';
                    document.getElementById('quantity').value = '';
                    // 입력 초기화 시 색상도 초기화
                    partInput.classList.remove('border-green-500', 'bg-green-50');
                    partInput.classList.add('border-gray-200');
                    hint.innerText = "현재 글자 수: 0 / 8";
                } else { throw new Error(); }
            } catch (e) {
                statusDiv.innerText = "❌ 전송 실패";
                statusDiv.className = "px-8 pb-6 text-center text-red-600 font-bold";
            }
        }
    </script>
</body>
</html>
