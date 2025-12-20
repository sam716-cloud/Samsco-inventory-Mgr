import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

# 1. 관리자님의 구글 웹 앱 URL (배포 후 주소 확인 필수)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxp-9EGQ8_hOJ32R0m3vAq9aVJdDBBD1EeYa2MGS-Q7YBGoz8yXdrmgHR9iEAEOOIkt/exec"

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMSCO 통합관리</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .samsco-blue { background-color: #003366; }
        .hidden { display: none; }
    </style>
</head>
<body class="bg-slate-100 min-h-screen flex items-center justify-center p-4">

    <div id="loginSection" class="w-full max-w-sm bg-white p-8 rounded-3xl shadow-2xl">
        <h1 class="text-2xl font-black text-center text-slate-800 mb-6 font-sans uppercase">Samsco Login</h1>
        <input type="text" id="userId" placeholder="아이디" class="w-full p-4 mb-3 border-2 rounded-xl focus:outline-none focus:border-blue-500">
        <input type="password" id="userPw" placeholder="비밀번호" class="w-full p-4 mb-6 border-2 rounded-xl focus:outline-none focus:border-blue-500">
        <button onclick="login()" class="w-full samsco-blue text-white py-4 rounded-xl font-bold text-lg">접속하기</button>
    </div>

    <div id="mainSection" class="w-full max-w-2xl bg-white p-6 rounded-3xl shadow-2xl hidden">
        <div class="flex justify-between items-center mb-6 border-b pb-4">
            <h2 class="text-xl font-bold text-slate-800 uppercase tracking-tighter">Samsco Inventory</h2>
            <span id="userInfo" class="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full"></span>
        </div>

        <div id="dynamicRows" class="space-y-4"></div>

        <button onclick="submitAll()" class="w-full samsco-blue text-white py-4 mt-6 rounded-xl font-bold text-lg shadow-lg active:scale-95 transition-all">일괄 전송하기</button>
        
        <div class="mt-8 border-t pt-4">
            <h3 class="font-bold text-slate-700 mb-3 text-sm">📝 최근 전송 내역 (취소 가능)</h3>
            <div id="historyList" class="space-y-2 text-xs"></div>
        </div>
    </div>

    <script>
        let currentUser = "";
        const scriptUrl = "SCRIPT_URL_PLACEHOLDER";
        const userCredentials = USER_DATA_PLACEHOLDER;

        // 입력 행 생성
        const rowsDiv = document.getElementById('dynamicRows');
        for(let i=1; i<=5; i++) {
            rowsDiv.innerHTML += `
                <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 mb-3">
                    <div class="flex gap-2 mb-2">
                        <input type="text" placeholder="품번" oninput="checkPart(this, ${i})" class="part-input w-2/3 p-3 border rounded-lg text-sm font-bold uppercase outline-none focus:ring-2 focus:ring-blue-200">
                        <input type="number" placeholder="수량" class="qty-input w-1/3 p-3 border rounded-lg text-sm font-bold outline-none focus:ring-2 focus:ring-blue-200">
                    </div>
                    <div id="info-${i}" class="text-[11px] text-slate-400 font-medium ml-1 italic">품번 8자리를 입력하세요.</div>
                </div>
            `;
        }

        function login() {
            const id = document.getElementById('userId').value;
            const pw = document.getElementById('userPw').value;
            if(userCredentials[id] && userCredentials[id][0] === pw) {
                currentUser = userCredentials[id][1];
                document.getElementById('userInfo').innerText = currentUser + " 님";
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('mainSection').classList.remove('hidden');
            } else { alert("아이디/비밀번호 오류"); }
        }

        async function checkPart(el, idx) {
            const val = el.value.trim();
            const infoDiv = document.getElementById(`info-${idx}`);
            if(val.length === 8) {
                el.classList.add('border-green-500', 'bg-green-50');
                infoDiv.innerText = "조회 중...";
                try {
                    // 중요: JSON 형식을 엄격하게 지켜서 전송
                    const response = await fetch(scriptUrl, {
                        method: 'POST',
                        mode: 'no-cors', // CORS 문제 방지
                        headers: { 'Content-Type': 'text/plain' },
                        body: JSON.stringify({ type: "getInfo", part_number: val })
                    });
                    
                    // no-cors 모드에서는 응답 내용을 직접 읽을 수 없으므로 
                    // 실제 운영 시에는 이 부분을 구글 앱스 스크립트와 다시 맞춰야 함
                    // 하지만 관리자님의 시연을 위해 더 확실한 fetch 방식으로 재구성함
                    const realRes = await fetch(scriptUrl + "?type=getInfo&part_number=" + val);
                    const infoText = await realRes.text();
                    infoDiv.innerText = infoText;
                    infoDiv.style.color = "#16a34a";
                } catch(e) { infoDiv.innerText = "정보 로드 실패"; }
            } else {
                el.classList.remove('border-green-500', 'bg-green-50');
                infoDiv.innerText = "품번 8자리를 입력하세요.";
                infoDiv.style.color = "#94a3b8";
            }
        }

        async function submitAll() {
            const parts = document.querySelectorAll('.part-input');
            const qtys = document.querySelectorAll('.qty-input');
            let count = 0;

            for(let i=0; i<parts.length; i++) {
                const pVal = parts[i].value.trim();
                const qVal = qtys[i].value.trim();
                if(pVal && qVal) {
                    const uid = Date.now() + "-" + i;
                    await fetch(scriptUrl, {
                        method: 'POST',
                        mode: 'no-cors',
                        body: JSON.stringify({
                            type: "submit", part_number: pVal, quantity: qVal, worker: currentUser, uid: uid
                        })
                    });
                    addHistory(pVal, qVal, uid);
                    parts[i].value = ''; qtys[i].value = '';
                    document.getElementById(`info-${i+1}`).innerText = "전송 완료";
                    count++;
                }
            }
            if(count > 0) alert(count + "건 전송 완료!");
        }

        function addHistory(part, qty, uid) {
            const list = document.getElementById('historyList');
            const id = 'hist-' + uid;
            list.insertAdjacentHTML('afterbegin', `
                <div id="${id}" class="flex justify-between items-center bg-white p-3 rounded-xl border mb-2 shadow-sm">
                    <span><b>${part}</b> / ${qty}개</span>
                    <button onclick="cancelItem('${uid}', '${id}')" class="text-red-500 font-bold border border-red-50 px-3 py-1 rounded-lg hover:bg-red-50">취소</button>
                </div>
            `);
        }

        async function cancelItem(uid, divId) {
            if(!confirm("취소하시겠습니까?")) return;
            await fetch(scriptUrl, {
                method: 'POST',
                mode: 'no-cors',
                body: JSON.stringify({ type: "cancel", uid: uid })
            });
            document.getElementById(divId).innerHTML = "<span class='text-slate-300 italic px-2'>취소 요청됨</span>";
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
