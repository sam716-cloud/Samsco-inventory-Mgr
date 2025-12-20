import httpx
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import json
import os

app = FastAPI()

# 1. 관리자님의 구글 웹 앱 URL
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyssor-HyMsgS0WnTq-zSuZenffT-xKDO3nFyIUZj4FagC7eqno2k-JnRd2491MlnvD/exec"

# 2. 로그인 사용자 정보
USERS = {
    "admin": ["1234", "관리자"],
    "임성민": ["1296", "임성민"]
}

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Samsco 창고 입고 등록 시스템</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
        body { font-family: 'Noto Sans KR', sans-serif; }
        
        .samsco-blue { background-color: #003366; }
        .hidden { display: none; }
        #overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,255,255,0.7); z-index: 9999; }
        .error-border { border-color: #ef4444 !important; background-color: #fef2f2 !important; }
        .valid-border { border-color: #22c55e !important; background-color: #f0fdf4 !important; }
        input:focus { outline: none; border-color: #003366 !important; }
        input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
        
        /* 추천 목록 스타일 */
        .suggest-box { 
            position: absolute; top: 100%; left: 0; z-index: 100; 
            background: white; border: 1px solid #d1d5db; border-radius: 0.375rem; 
            width: 130px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); display: none; 
            max-height: 200px; overflow-y: auto; 
        }
        .suggest-item { padding: 8px 10px; font-size: 11px; cursor: pointer; border-bottom: 1px solid #f3f4f6; font-weight: bold; color: #334155; }
        .suggest-item:last-child { border-bottom: none; }
        .suggest-item:hover { background-color: #f1f5f9; color: #003366; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen font-sans antialiased text-gray-900">

    <div id="overlay" class="flex items-center justify-center"><div class="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-900"></div></div>
    <div id="toast" class="fixed top-0 left-0 w-full samsco-blue text-white py-3 text-center font-bold transform -translate-y-full transition-transform duration-300 z-50 shadow-md">등록이 완료되었습니다!</div>

    <div class="max-w-md mx-auto p-3">
        <div id="loginSection" class="bg-white mt-10 p-8 rounded-2xl shadow-xl border border-gray-100">
            <h1 class="text-2xl font-black text-center text-blue-900 mb-8 tracking-tighter uppercase">Samsco Login</h1>
            <input type="text" id="userId" placeholder="아이디" class="w-full p-4 mb-3 border rounded-xl focus:ring-2 focus:ring-blue-500">
            <input type="password" id="userPw" placeholder="비밀번호" class="w-full p-4 mb-8 border rounded-xl focus:ring-2 focus:ring-blue-500">
            <button onclick="login()" class="w-full samsco-blue text-white py-4 rounded-xl font-bold text-lg hover:bg-blue-800 transition-all">접속하기</button>
        </div>

        <div id="mainSection" class="hidden">
            <div class="flex justify-between items-center mb-2 bg-white p-2.5 rounded-xl shadow-sm border border-gray-100">
                <h2 class="text-md font-bold text-blue-900 tracking-tighter truncate mr-2">SAMSCO 창고 입고 등록 시스템</h2>
                <span id="userInfo" class="text-[11px] font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full whitespace-nowrap"></span>
            </div>

            <div id="dynamicRows" class="space-y-1"></div>

            <button id="submitBtn" onclick="submitAll()" disabled style="opacity: 0.5;" 
                class="w-full samsco-blue text-white py-2 mt-2.5 rounded-xl font-bold text-md shadow-md active:scale-95 transition-all">일괄 전송하기</button>
            
            <p class="text-[12px] text-slate-600 mt-1 px-1 text-center font-medium">
                ※ 시스템 오류나 품번 조회 불가 시, <span class="font-bold text-slate-600 underline">생산관리팀</span>에 문의해 주세요.
            </p>

            <div class="mt-3 border-t pt-3 border-gray-200">
                <h3 class="font-bold text-gray-400 mb-2 text-[10px] uppercase tracking-widest px-1">최근 내역</h3>
                <div id="historyList" class="space-y-1"></div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = "";
        let validStatus = [false, false, false, false, false];
        let searchTimer = null;
        const scriptUrl = "SCRIPT_URL_PLACEHOLDER";
        const userCredentials = USER_DATA_PLACEHOLDER;

        const rowsDiv = document.getElementById('dynamicRows');
        for(let i=1; i<=5; i++) {
            rowsDiv.innerHTML += `
                <div class="bg-white p-1.5 rounded-lg border border-gray-200 shadow-sm relative">
                    <div class="flex items-center gap-1">
                        <span class="text-[13px] font-bold text-gray-400 w-3">${i}</span>
                        <div class="relative">
                            <input type="text" id="part-${i-1}" placeholder="품번/뒷자리" maxlength="15" autocomplete="off"
                                oninput="handleInput(this, ${i-1})" 
                                class="part-input w-[95px] p-1.5 border rounded-md text-[13px] font-bold uppercase transition-colors">
                            <div id="suggest-${i-1}" class="suggest-box"></div>
                        </div>
                        
                        <div id="info-${i-1}" class="flex-1 text-[15px] font-bold text-slate-600 truncate px-1 italic">0/8</div>

                        <div class="flex items-center border rounded-md bg-gray-50 overflow-hidden">
                            <button onclick="adjustQty(${i-1}, -1)" class="px-2 py-1 text-gray-400 font-bold border-r hover:bg-gray-100">-</button>
                            <input type="number" id="qty-${i-1}" placeholder="0" 
                                class="qty-input w-[40px] py-1 text-[13px] font-bold text-center outline-none bg-transparent">
                            <button onclick="adjustQty(${i-1}, 1)" class="px-2 py-1 text-gray-400 font-bold border-l hover:bg-gray-100">+</button>
                        </div>
                    </div>
                </div>
            `;
        }

        function adjustQty(idx, val) {
            const input = document.getElementById(`qty-${idx}`);
            let current = parseInt(input.value) || 0;
            if (current + val >= 0) input.value = current + val;
        }

        function login() {
            const id = document.getElementById('userId').value;
            const pw = document.getElementById('userPw').value;
            if(userCredentials[id] && userCredentials[id][0] === pw) {
                currentUser = userCredentials[id][1];
                document.getElementById('userInfo').innerText = currentUser + "님";
                document.getElementById('loginSection').classList.add('hidden');
                document.getElementById('mainSection').classList.remove('hidden');
            } else { alert("로그인 정보를 확인하세요."); }
        }

        function handleInput(el, idx) {
            const val = el.value.trim();
            const suggestBox = document.getElementById(`suggest-${idx}`);
            const infoDiv = document.getElementById(`info-${idx}`);

            validStatus[idx] = false;
            updateSubmitButton();
            el.classList.remove('valid-border', 'error-border');
            
            infoDiv.innerText = `${val.length}/8`;
            infoDiv.style.color = "#94a3b8"; 

            if (searchTimer) clearTimeout(searchTimer);

            if (val.length < 3) {
                suggestBox.style.display = 'none';
                if(val.length === 0) infoDiv.innerText = "0/8";
                return;
            }

            if (val.length >= 8) {
                suggestBox.style.display = 'none';
                checkPart(el, idx);
                return;
            }

            searchTimer = setTimeout(async () => {
                try {
                    const sRes = await fetch(scriptUrl + "?type=search&query=" + val);
                    const list = await sRes.json();
                    if (list.length > 0 && el.value.trim() === val) {
                        suggestBox.innerHTML = list.map(item => `<div class="suggest-item" onclick="selectSuggest('${item}', ${idx})">${item}</div>`).join('');
                        suggestBox.style.display = 'block';
                    } else { suggestBox.style.display = 'none'; }
                } catch(e) { suggestBox.style.display = 'none'; }

                checkPart(el, idx);
            }, 300);
        }

        function selectSuggest(fullPart, idx) {
            const input = document.getElementById(`part-${idx}`);
            input.value = fullPart;
            document.getElementById(`suggest-${idx}`).style.display = 'none';
            checkPart(input, idx);
        }

        async function checkPart(el, idx) {
            const val = el.value.trim();
            const infoDiv = document.getElementById(`info-${idx}`);
            const len = val.length;

            if(len >= 3) {
                infoDiv.innerText = `조회 중... ${len}/8`;
                try {
                    const res = await fetch(scriptUrl + "?type=getInfo&part_number=" + val);
                    const infoText = await res.text();
                    
                    if(el.value.trim() !== val) return; 

                    if(infoText.includes("❌")) {
                        if(len >= 8) el.classList.add('error-border');
                        infoDiv.innerText = `미등록 ${len}/8`;
                        infoDiv.style.color = "#ef4444";
                        validStatus[idx] = false;
                    } else {
                        el.classList.add('valid-border');
                        infoDiv.innerText = infoText;
                        infoDiv.style.color = "#15803d"; 
                        validStatus[idx] = true;
                        document.getElementById(`suggest-${idx}`).style.display = 'none';
                    }
                } catch(e) { infoDiv.innerText = `연결 오류 ${len}/8`; }
            }
            updateSubmitButton();
        }

        function updateSubmitButton() {
            const parts = document.querySelectorAll('.part-input');
            let hasContent = false;
            let hasInvalid = false;
            parts.forEach((input, idx) => {
                const val = input.value.trim();
                if(val.length > 0) {
                    hasContent = true;
                    if(!validStatus[idx]) hasInvalid = true;
                }
            });
            const btn = document.getElementById('submitBtn');
            if(hasContent && !hasInvalid) {
                btn.disabled = false; btn.style.opacity = "1";
            } else {
                btn.disabled = true; btn.style.opacity = "0.5";
            }
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
                    body: JSON.stringify({ type: "submit", part_number: item.p, quantity: item.q, worker: currentUser, uid: uid })
                });
                addHistory(item.p, item.q, uid);
            }
            parts.forEach((p, idx) => { 
                p.value = ''; qtys[idx].value = ''; 
                document.getElementById(`info-${idx}`).innerText = "0/8"; 
                p.classList.remove('valid-border', 'error-border'); 
                validStatus[idx] = false;
            });
            updateSubmitButton();
            document.getElementById('overlay').style.display = 'none';
            showToast();
        }

        function showToast() {
            const toast = document.getElementById('toast');
            toast.style.transform = 'translateY(0)';
            setTimeout(() => { toast.style.transform = 'translateY(-100%)'; }, 3000);
        }

        // [수정] 취소 버튼 생성 시 this 전달 추가
        function addHistory(part, qty, uid) {
            const list = document.getElementById('historyList');
            const id = 'hist-' + uid;
            list.insertAdjacentHTML('afterbegin', `
                <div id="${id}" class="flex justify-between items-center bg-white px-3 py-1.5 rounded-lg border text-[10px] shadow-sm">
                    <span class="font-bold text-gray-700">${part} <span class="text-gray-400 font-normal">(${qty}개)</span></span>
                    <button onclick="cancelItem('${uid}', '${id}', this)" class="text-red-400 font-bold hover:bg-red-50 px-2 py-0.5 rounded border border-red-100">취소</button>
                </div>
            `);
        }

        // [수정] 취소 버튼 즉시 비활성화 처리
        async function cancelItem(uid, divId, btn) {
            if(!confirm("취소하시겠습니까?")) return;
            
            // 버튼 즉시 비활성화 (중복 클릭 방지)
            btn.disabled = true;
            btn.style.opacity = "0.5";
            btn.innerText = "처리중";

            await fetch(scriptUrl, { method: 'POST', mode: 'no-cors', body: JSON.stringify({ type: "cancel", uid: uid }) });
            document.getElementById(divId).innerHTML = "<span class='text-gray-300 italic px-2 text-[9px]'>전송 취소됨</span>";
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    html = HTML_CONTENT.replace(
        "SCRIPT_URL_PLACEHOLDER", GOOGLE_SCRIPT_URL
    ).replace(
        "USER_DATA_PLACEHOLDER", json.dumps(USERS, ensure_ascii=False)
    )
    return html

# Render 배포 실행용
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
