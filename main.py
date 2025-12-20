import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

# 1. 관리자님의 구글 웹 앱 URL (배포 후 주소 확인 필수)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzcZFITI2cO_3tC7wwfgMNu4h4oJyVMp766MjjVoScuwFkBJO85c6XommRWMaIjx7OP/exec"

# 2. 로그인 사용자 정보
USERS = {
    "admin": ["1234", "관리자"],
    "samsco1": ["1111", "홍길동"],
    "samsco2": ["2222", "김철수"]
}

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SAMSCO Inventory</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .samsco-blue { background-color: #003366; }
        .hidden { display: none; }
        #overlay {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.7); z-index: 9999; cursor: not-allowed;
        }
        .error-border { border-color: #ef4444 !important; background-color: #fef2f2 !important; }
        .valid-border { border-color: #22c55e !important; background-color: #f0fdf4 !important; }
        #toast {
            position: fixed; top: 0; left: 0; width: 100%; background: #003366; color: white;
            padding: 12px; text-align: center; font-weight: bold; transform: translateY(-100%);
            transition: transform 0.3s; z-index: 10000;
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen font-sans antialiased text-slate-900">

    <div id="overlay" class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-900"></div>
    </div>

    <div id="toast">등록이 완료되었습니다!</div>

    <div class="max-w-md mx-auto p-4">
        <div id="loginSection" class="bg-white mt-10 p-8 rounded-2xl shadow-xl border border-gray-100">
            <h1 class="text-2xl font-black text-center text-blue-900 mb-8 uppercase tracking-tighter">Samsco Login</h1>
            <input type="text" id="userId" placeholder="아이디" class="w-full p-4 mb-3 border rounded-xl outline-none focus:ring-2 focus:ring-blue-500">
            <input type="password" id="userPw" placeholder="비밀번호" class="w-full p-4 mb-8 border rounded-xl outline-none focus:ring-2 focus:ring-blue-500">
            <button onclick="login()" class="w-full samsco-blue text-white py-4 rounded-xl font-bold text-lg">접속하기</button>
        </div>

        <div id="mainSection" class="hidden">
            <div class="flex justify-between items-center mb-4 bg-white p-3 rounded-xl shadow-sm border border-gray-100">
                <h2 class="text-lg font-bold text-blue-900 tracking-tighter uppercase">Samsco Inout</h2>
                <span id="userInfo" class="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full"></span>
            </div>

            <div id="dynamicRows" class="space-y-2"></div>

            <button id="submitBtn" onclick="submitAll()" disabled style="opacity: 0.4" 
                class="w-full samsco-blue text-white py-4 mt-6 rounded-xl font-bold text-lg shadow-lg active:scale-95 transition-all">
                일괄 전송하기
            </button>
            
            <div class="mt-8 border-t pt-4">
                <h3 class="font-bold text-gray-400 mb-3 text-[10px] uppercase tracking-widest px-1">최근 전송 내역</h3>
                <div id="historyList" class="space-y-2"></div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = "";
        let validStatus = [false, false, false, false, false];
        let searchTimers = [null, null, null, null, null];
        const scriptUrl = "SCRIPT_URL_PLACEHOLDER";
        const userCredentials = USER_DATA_PLACEHOLDER;

        // 콤팩트 디자인 행 생성
        const rowsDiv = document.getElementById('dynamicRows');
        for(let i=1; i<=5; i++) {
            rowsDiv.innerHTML += `
                <div class="bg-white p-3 rounded-xl border border-gray-100 shadow-sm">
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-bold text-gray-300 w-3">${i}</span>
                        <input type="text" placeholder="품번" oninput="handleInput(${i-1}, this)" 
                            class="part-input w-[130px] p-2 border-2 rounded-lg text-sm font-bold uppercase outline-none transition-all">
                        <input type="number" placeholder="수량" oninput="updateSubmitButton()"
                            class="qty-input w-[70px] p-2 border-2 rounded-lg text-sm font-bold outline-none flex-1">
                    </div>
                    <div id="info-${i-1}" class="text-[11px] text-gray-400 mt-1.5 ml-7 font-medium truncate">4자리 이상 입력 시 조회</div>
                </div>
            `;
        }

        function login() {
            const id = document.getElementById('userId').value;
            const pw = document.getElementById('userPw').value;
            if(userCredentials[id] && userCredentials[id][0] === pw) {
                currentUser = userCredentials[id][1];
                document.getElementById('userInfo').innerText = currentUser + "님";
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('mainSection').classList.remove('hidden');
                updateSubmitButton(); // 로그인 직후 버튼 상태 초기화
            } else { alert("로그인 정보를 확인하세요."); }
        }

        function handleInput(idx, el) {
            clearTimeout(searchTimers[idx]);
            const val = el.value.trim();
            const infoDiv = document.getElementById(\`info-\${idx}\`);

            if(val.length >= 4) {
                infoDiv.innerText = "조회 중...";
                searchTimers[idx] = setTimeout(() => {
                    checkPart(val, idx, el);
                }, 500);
            } else {
                el.classList.remove('error-border', 'valid-border');
                infoDiv.innerText = "4자리 이상 입력 시 조회";
                infoDiv.style.color = "#94a3b8";
                validStatus[idx] = false;
                updateSubmitButton();
            }
        }

        async function checkPart(val, idx, el) {
            const infoDiv = document.getElementById(\`info-\${idx}\`);
            try {
                const res = await fetch(scriptUrl + "?type=getInfo&part_number=" + val);
                const infoText = await res.text();
                
                if(infoText.includes("❌")) {
                    el.classList.add('error-border');
                    el.classList.remove('valid-border');
                    infoDiv.innerText = infoText;
                    infoDiv.style.color = "#ef4444";
                    validStatus[idx] = false;
                } else {
                    el.classList.add('valid-border');
                    el.classList.remove('error-border');
                    infoDiv.innerText = infoText;
                    infoDiv.style.color = "#16a34a";
                    validStatus[idx] = true;
                }
            } catch(e) { 
                infoDiv.innerText = "통신오류 (URL 확인)"; 
            }
            updateSubmitButton();
        }

        // 버튼 활성화 로직 강화
        function updateSubmitButton() {
            const parts = document.querySelectorAll('.part-input');
            const qtys = document.querySelectorAll('.qty-input');
            let canSubmit = false;
            let hasError = false;

            parts.forEach((input, idx) => {
                const pVal = input.value.trim();
                const qVal = qtys[idx].value.trim();

                if (pVal.length > 0 || qVal.length > 0) {
                    // 품번이 유효하지 않거나 수량이 없으면 에러
                    if (!validStatus[idx] || qVal.length === 0) {
                        hasError = true;
                    } else {
                        canSubmit = true; // 유효한 세트가 하나라도 있음
                    }
                }
            });

            const btn = document.getElementById('submitBtn');
            if (canSubmit && !hasError) {
                btn.disabled = false;
                btn.style.opacity = "1";
            } else {
                btn.disabled = true;
                btn.style.opacity = "0.4";
            }
        }

        async function submitAll() {
            const parts = document.querySelectorAll('.part-input');
            const qtys = document.querySelectorAll('.qty-input');
            let items = [];

            for(let i=0; i<parts.length; i++) {
                if(parts[i].value.trim() && qtys[i].value.trim()) {
                    items.push({p: parts[i].value.trim(), q: qtys[i].value.trim(), idx: i});
                }
            }
            if(items.length === 0) return;

            document.getElementById('overlay').style.display = 'flex';

            for(const item of items) {
                const uid = Date.now() + "-" + item.idx;
                await fetch(scriptUrl, {
                    method: 'POST', mode: 'no-cors',
                    body: JSON.stringify({
                        type: "submit", part_number: item.p, quantity: item.q, worker: currentUser, uid: uid
                    })
                });
                addHistory(item.p, item.q, uid);
            }

            // 초기화
            parts.forEach((p, idx) => {
                p.value = ''; qtys[idx].value = '';
                document.getElementById(\`info-\${idx}\`).innerText = "4자리 이상 입력 시 조회";
                p.classList.remove('valid-border', 'error-border');
            });
            validStatus = [false, false, false, false, false];
            updateSubmitButton();
            document.getElementById('overlay').style.display = 'none';
            showToast();
        }

        function showToast() {
            const toast = document.getElementById('toast');
            toast.style.transform = 'translateY(0)';
            setTimeout(() => { toast.style.transform = 'translateY(-100%)'; }, 3000);
        }

        function addHistory(part, qty, uid) {
            const list = document.getElementById('historyList');
            const id = 'hist-' + uid;
            list.insertAdjacentHTML('afterbegin', \`
                <div id="\${id}" class="flex justify-between items-center bg-white px-3 py-2 rounded-lg border text-[11px] shadow-sm animate-pulse">
                    <span class="font-bold text-slate-700">\${part} <span class="text-gray-400 font-normal">(\${qty}개)</span></span>
                    <button onclick="cancelItem('\${uid}', '\${id}')" class="text-red-400 font-bold hover:bg-red-50 px-2 py-1 rounded">취소</button>
                </div>
            \`);
            setTimeout(() => { document.getElementById(id).classList.remove('animate-pulse'); }, 1000);
        }

        async function cancelItem(uid, divId) {
            if(!confirm("해당 항목을 취소하시겠습니까?")) return;
            await fetch(scriptUrl, { method: 'POST', mode: 'no-cors', body: JSON.stringify({ type: "cancel", uid: uid }) });
            document.getElementById(divId).innerHTML = "<span class='text-gray-300 italic px-2'>취소됨</span>";
        }
    </script>
</body>
</html>
