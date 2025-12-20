from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# 임시 저장소 (서버 재시작하면 날아감)
data_store = []

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        < title>입고 등록</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .box {
                background: white;
                padding: 30px;
                border-radius: 10px;
                width: 320px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }
            h2 {
                text-align: center;
                margin-bottom: 20px;
            }
            input, button {
                width: 100%;
                padding: 10px;
                margin-bottom: 12px;
                font-size: 16px;
            }
            button {
                background: #2d7ff9;
                color: white;
                border: none;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>입고 등록</h2>
            <form action="/submit" method="post">
                <input type="text" name="item_code" placeholder="품번" required>
                <input type="number" name="quantity" placeholder="수량" required>
                <button type="submit">등록</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/submit", response_class=HTMLResponse)
def submit(item_code: str = Form(...), quantity: int = Form(...)):
    data_store.append({
        "item_code": item_code,
        "quantity": quantity
    })

    print("현재 데이터:", data_store)

    return """
    <script>
        alert("등록 완료!");
        window.location.href = "/";
    </script>
    """
