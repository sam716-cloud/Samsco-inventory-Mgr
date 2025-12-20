import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxp-9EGQ8_hOJ32R0m3vAq9aVJdDBBD1EeYa2MGS-Q7YBGoz8yXdrmgHR9iEAEOOIkt/exec"

USERS = {
    "admin": ["1234", "관리자"],
    "samsco1": ["1111", "홍길동"]
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
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.7);
            z-index: 9999;
        }
        .error-border { border-color: #ef4444 !important; background-color: #fef2f2 !important; }
        .valid-border { border-color: #22c55e !important; background-color: #f0fdf4 !important; }
        /* 입력칸 포커스 시 테두리 제거 및 깔끔한 스타일 */
        input:focus { outline: none; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen font-sans antialiased">

    <div id="overlay" class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-900"></div>
    </div>

    <div id="toast" class="fixed top-0 left-0 w-full samsco-blue text-white py-3 text-center font-bold transform -translate-y-full transition-transform duration-300 z-50 shadow-md">
        등록이 완료되었습니다!
    </div>

    <div class="max-w-md mx-auto p-3">
        <div id="loginSection" class="bg-white mt-10 p-8 rounded-2xl shadow-xl border border-gray-100">
            <h1 class="text-2xl font-black text-center text-blue-900 mb-8 tracking-tighter uppercase">Samsco Login</h1>
            <input type="text" id="userId" placeholder="아이디" class="w-full p-4 mb-3 border rounded-xl">
            <input type="password" id="userPw" placeholder="비밀번호" class="w-full p-4 mb-8 border rounded-xl">
            <button onclick="login()" class="w-full samsco-blue text-white py-4 rounded-xl font-bold text-lg hover:shadow-lg transition-all">접속하기</button>
        </div>

        <div id="mainSection" class="hidden">
            <div class="flex justify-between items-center mb-3 bg-white p-3 rounded-xl shadow-sm border border-gray-100">
                <h2 class="text-lg font-bold text-blue-900 tracking-tighter">SAMSCO 입고</h2>
                <span id="userInfo" class="text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1 rounded-full"></span>
            </div>

            <div id="dynamicRows" class="space-y-1.5">
                </div>

            <button id="submitBtn" onclick="submitAll()" class="w-full samsco-blue text-white py-4 mt-5 rounded-xl font-bold text-lg shadow-lg active:scale-95 transition-all">일괄 전송하기</button>
            
            <div class="mt-6">
                <h3 class="font-bold text-gray-500 mb-2 text-[10px] uppercase tracking-widest px-1">최근 내역</h3>
                <div id="historyList" class="space-y-1.5"></div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = "";
        let validStatus = [false, false, false, false, false];
        const scriptUrl = "SCRIPT_URL_PLACEHOLDER";
        const userCredentials = USER_DATA_PLACEHOLDER;

        // 한 줄에 [품번] [상세정보] [수량]이 배치되도록 수정
        const rowsDiv = document.getElementById('dynamicRows');
        for(let i=1; i<=5; i++) {
            rowsDiv.innerHTML += `
                <div class="bg-white p-2 rounded-lg border border-gray-200 shadow-sm">
                    <div class="flex items-center gap-1.5">
                        <span class="text-[9px] font-bold text-gray-300 w-3">${i}</span>
                        <input type="text" placeholder="품번" oninput="checkPart(this, ${i-1})" 
                            class="part-input w-[100px] p-2 border rounded-md text-xs font-bold uppercase transition-colors">
                        
                        <div id="info-${i-1}" class="flex-1 text-[10px] text-gray-400 font-medium truncate px-1">
                            대기...
                        </div>

                        <input type="number" placeholder="수량" 
                            class="qty-input w-[60px] p-2 border rounded-md text-xs font-bold text-center">
                    </div>
                </div>
            `;
        }

        function login() {
            const id = document.getElementById('userId').value;
            const pw = document.getElementById('userPw').value;
            if(userCredentials[id] && userCredentials[id][0] === pw) {
                currentUser = userCredentials[id][1];
                document.getElementById('userInfo').innerText = currentUser;
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('mainSection').classList.remove('hidden');
            } else { alert("로그인 정보를 확인하세요."); }
        }

        async function checkPart(el, idx) {
            const val = el.value.trim();
            const infoDiv = document.getElementById(`info-${idx}`);
            
            if(val.length >= 8) {
                try {
                    const res = await fetch(scriptUrl + "?type=getInfo&part_number=" + val);
                    const infoText = await res.text();
                    
                    if(infoText.includes("❌")) {
                        el.classList.add('error-border');
                        el.classList.remove('valid-border');
                        infoDiv.innerText = "미등록 품번";
                        infoDiv.style.color = "#ef4444";
                        validStatus[idx] = false;
                    } else {
                        el.classList.add('valid-border');
                        el.classList.remove('error-border');
                        infoDiv.innerText = infoText; // 구글 시트의 상세정보 출력
                        infoDiv.style.color = "#16a34a";
                        validStatus[idx] = true;
                    }
                } catch(e) { infoDiv.innerText = "연결 오류"; }
            } else {
                el.classList.remove('error-border', 'valid-border');
                infoDiv.innerText = "입력 중...";
                infoDiv.style.color = "#94a3b8";
                validStatus[idx] = false;
            }
            updateSubmitButton();
        }

        function updateSubmitButton() {
            const parts = document.querySelectorAll('.part-input');
            let hasInvalid = false;
            parts.forEach((input, idx) => {
                if(input.value.trim().length > 0 && !validStatus[idx]) hasInvalid = true;
            });
            document.getElementById('submitBtn').disabled = hasInvalid;
            document.getElementById('submitBtn').style.opacity = hasInvalid ? "0.5" : "1";
        }

        async function submitAll() {
            const parts = document.querySelectorAll('.part-input');
            const qtys = document.querySelectorAll('.qty-input');
            let targets = [];

            for(let i=0; i<parts.length; i++) {
                if(parts[i].value.trim() && qtys[i].value.trim()) {
                    targets.push({p: parts[i].value, q: qtys[i].value, idx: i});
                }
            }

            if(targets.length === 0) return;

            document.getElementById('overlay').style.display = 'flex';

            for(const item of targets) {
                const uid = Date.now() + "-" + item.idx;
                await fetch(scriptUrl, {
                    method: 'POST', mode: 'no-cors',
                    body: JSON.stringify({
                        type: "submit", part_number: item.p, quantity: item.q, worker: currentUser, uid: uid
                    })
                });
                addHistory(item.p, item.q, uid);
            }

            parts.forEach((p, idx) => { 
                p.value = ''; 
                qtys[idx].value = ''; 
                document.getElementById(`info-${idx}`).innerText = "대기..."; 
                p.classList.remove('valid-border'); 
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
            list.insertAdjacentHTML('afterbegin', `
                <div id="${id}" class="flex justify-between items-center bg-white px-3 py-2 rounded-lg border text-[11px] shadow-sm">
                    <span class="font-bold">${part} <span class="text-gray-400 font-normal">(${qty}개)</span></span>
                    <button onclick="cancelItem('${uid}', '${id}')" class="text-red-400 font-bold hover:bg-red-50 px-2 py-1 rounded">취소</button>
                </div>
            `);
        }

        async function cancelItem(uid, divId) {
            if(!confirm("취소하시겠습니까?")) return;
            await fetch(scriptUrl, { method: 'POST', mode: 'no-cors', body: JSON.stringify({ type: "cancel", uid: uid }) });
            document.getElementById(divId).innerHTML = "<span class='text-gray-300 italic px-2'>취소됨</span>";
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    res_html = HTML_CONTENT.replace("SCRIPT_URL_PLACEHOLDER", GOOGLE_SCRIPT_URL)
    res_html = res_html.replace("USER_DATA_PLACEHOLDER", json.dumps(USERS))
    return res_html
