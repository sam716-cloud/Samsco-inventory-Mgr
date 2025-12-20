import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

# 1. 관리자님의 구글 웹 앱 URL (수정 필수)
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzcZFITI2cO_3tC7wwfgMNu4h4oJyVMp766MjjVoScuwFkBJO85c6XommRWMaIjx7OP/exec"

# 2. 로그인 사용자 정보 (여기서 직접 수정하세요)
# {"아이디": ["비밀번호", "사용자이름"]} 형식입니다.
USERS = {
    "admin": ["1234", "관리자"],
    "samsco1": ["1111", "홍길동"],
    "samsco2": ["2222", "김철수"],
    "samsco3": ["3333", "이영희"],
    "samsco4": ["4444", "박민수"]
}

HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMSCO 통합관리</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .samsco-blue {{ background-color: #003366; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body class="bg-slate-100 min-h-screen flex items-center justify-center p-4">

    <div id="loginSection" class="w-full max-w-sm bg-white p-8 rounded-3xl shadow-2xl">
        <h1 class="text-2xl font-black text-center text-slate-800 mb-6 font-sans">SAMSCO LOGIN</h1>
        <input type="text" id="userId" placeholder="아이디" class="w-full p-4 mb-3 border-2 rounded-xl focus:outline-none focus:border-blue-500">
        <input type="password" id="userPw" placeholder="비밀번호" class="w-full p-4 mb-6 border-2 rounded-xl focus:outline-none focus:border-blue-500">
        <button onclick="login()" class="w-full samsco-blue text-white py-4 rounded-xl font-bold text-lg hover:opacity-90 transition-opacity">접속하기</button>
    </div>

    <div id="mainSection" class="w-full max-w-2xl bg-white p-6 rounded-3xl shadow-2xl hidden">
        <div class="flex justify-between items-center mb-6 border-b pb-4 font-sans">
            <h2 class="text-xl font-bold text-slate-800 tracking-tighter">SAMSCO INVENTORY</h2>
            <span id="userInfo" class="text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1 rounded-full"></span>
        </div>

        <div id="inputRows" class="space-y-4">
            <div id="dynamicRows"></div>
        </div>

        <button onclick="submitAll()" class="w-full samsco-blue text-white py-4 mt-6 rounded-xl font-bold text-lg shadow-lg active:scale-95 transition-all">일괄 전송하기</button>
        
        <div class="mt-8 border-t pt-4">
            <h3 class="font-bold text-slate-700 mb-3 text-sm">최근 전송 내역 (취소 가능)</h3>
            <div id="historyList" class="space-y-2 text-xs"></div>
        </div>
    </div>

    <script>
        let currentUser = "";
        const scriptUrl = '{GOOGLE_SCRIPT_URL}';
        const userCredentials = {json.dumps(USERS)};

        // 줄 생성 로직
        const rowsDiv = document.getElementById('dynamicRows');
        for(let i=1; i<=5; i++) {{
            rowsDiv.innerHTML += `
                <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 mb-3">
                    <div class="flex gap-2 mb-2">
                        <input type="text" placeholder="품번" oninput="checkPart(this, ${{i}})" class="part-input w-2/3 p-3 border rounded-lg text-sm font-bold uppercase focus:ring-2 focus:ring-blue-200 outline-none">
                        <input type="number" placeholder="수량" class="qty-input w-1/3 p-3 border rounded-lg text-sm font-bold focus:ring-2 focus:ring-blue-200 outline-none">
                    </div>
                    <div id="info-${{i}}" class="text-[11px] text-slate-400 font-medium ml-1">품번 8자리를 입력하세요.</div>
                </div>
            `;
        }}

        function login() {{
            const id = document.getElementById('userId').value;
            const pw = document.getElementById('userPw').value;
            if(userCredentials[id] && userCredentials[id][0] === pw) {{
                currentUser = userCredentials[id][1];
                document.getElementById('userInfo').innerText = currentUser + " 님";
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('mainSection').classList.remove('hidden');
            }} else {{
                alert("아이디 또는 비밀번호가 올바르지 않습니다.");
            }}
        }

        async function checkPart(el, idx) {{
            const val = el.value.trim();
            const infoDiv = document.getElementById(`info-${{idx}}`);
            if(val.length === 8) {{
                el.classList.add('border-green-500', 'bg-green-50');
                infoDiv.innerText = "조회 중...";
                try {{
                    const res = await fetch(scriptUrl, {{method:'POST', body: JSON.stringify({{type:'getInfo', part_number: val}})}});
                    infoDiv.innerText = await res.text();
                    infoDiv.classList.replace('text-slate-400', 'text-green-600');
                }} catch(e) {{ infoDiv.innerText = "조회 실패"; }}
            }} else {{
                el.classList.remove('border-green-500', 'bg-green-50');
                infoDiv.innerText = "8자리 입력 시 정보가 표시됩니다.";
                infoDiv.classList.replace('text-green-600', 'text-slate-400');
            }}
        }

        async function submitAll() {{
            const parts = document.querySelectorAll('.part-input');
            const qtys = document.querySelectorAll('.qty-input');
            let count = 0;

            for(let i=0; i<parts.length; i++) {{
                const pVal = parts[i].value.trim();
                const qVal = qtys[i].value.trim();
                if(pVal && qVal) {{
                    const uid = Date.now() + "-" + i;
                    try {{
                        await fetch(scriptUrl, {{method:'POST', body: JSON.stringify({{
                            type:'submit', part_number: pVal, quantity: qVal, worker: currentUser, uid: uid
                        }})}});
                        addHistory(pVal, qVal, uid);
                        parts[i].value = ''; qtys[i].value = '';
                        document.getElementById(`info-${{i+1}}`).innerText = "전송 완료";
                        count++;
                    }} catch(e) {{ alert("전송 오류 발생"); }}
                }
            }
            if(count > 0) alert(count + "건이 구글 시트에 기록되었습니다.");
        }

        function addHistory(part, qty, uid) {{
            const list = document.getElementById('historyList');
            const id = 'hist-' + uid;
            list.insertAdjacentHTML('afterbegin', `
                <div id="${{id}}" class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-100 shadow-sm mb-2">
                    <span><b>${{part}}</b> / ${{qty}}개</span>
                    <button onclick="cancelItem('${{uid}}', '${{id}}')" class="text-red-500 font-bold border border-red-50 px-3 py-1 rounded-lg hover:bg-red-50">취소</button>
                </div>
            `);
        }

        async function cancelItem(uid, divId) {{
            if(!confirm("이 전송 내역을 취소로 변경하시겠습니까?")) return;
            try {{
                await fetch(scriptUrl, {{method:'POST', body: JSON.stringify({{type:'cancel', uid: uid}})}});
                document.getElementById(divId).innerHTML = "<span class='text-slate-300 italic px-2'>취소됨 (구글 시트 반영 완료)</span>";
            }} catch(e) {{ alert("취소 처리 중 오류"); }}
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(): return HTML_CONTENT
