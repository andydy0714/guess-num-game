import random
import requests
from flask import Flask, request, session, render_template
from betting_engine import BettingEngine


TEST_MODE = True  # 设置为True以启用测试模式，顯示目標數字

app = Flask(__name__)  # 創建 Flask 應用實例
app.secret_key = "secret" # 設置密鑰，用於加密 session

@app.route("/guess_num_game", methods=["GET", "POST"]) # 定義路由：當用戶訪問 /guess_num_game 時執行此函數
def guess_number():

        # 首次訪問時初始化 session,保存遊戲狀態
        if "engine" not in session:
            session["engine"] = BettingEngine().to_dict()  # 初始化引擎（存字典）
            session["message"] = "歡迎來到猜數字遊戲!请先设置最大正整数以開始遊戲。"

        # 從 session 還原引擎對象
        engine = BettingEngine.from_dict(session["engine"])

        # 用戶設置上限時執行
        if request.method == "POST" and "max_num" in request.form:
            try:
                max_num = int(request.form["max_num"]) # 將輸入轉為整數
                if max_num < 1:
                    raise ValueError
            except ValueError:
                session["message"] = "請輸入正整數！" # 輸入非法時提示
            else:  # 輸入合法時執行
                try:
                    engine.start_round(max_num)  # 引擎開局：鎖定賭注、生成目標數字、計算倍率
                except ValueError as e:
                    session["message"] = str(e)
                else:
                    session["message"] = f"遊戲開始！上限 {max_num}，本局賭注 {engine.stake}，倍率 {engine.multiplier:.2f}"

                    # 根據測試模式顯示提示
                    if TEST_MODE:
                        session["test_mode"] = f"(測試模式已啟用，目標數字是 {engine.target})"
                    else:
                        session["test_mode"] = f"(測試模式已禁用，目標數字是隱藏的)"

        # 用戶猜數字時執行
        if request.method == "POST" and "guess" in request.form:
            try:
                guess = int(request.form["guess"])  # 將猜測轉為整數
            except ValueError:
                session["message"] = "請輸入正整數！" # 輸入非法時提示
            else:  # 猜測輸入合法時執行                         
                try:
                    msg, finished = engine.guess(guess)  # 引擎判斷結果
                except ValueError as e:
                    session["message"] = str(e)
                else:
                    session["message"] = msg
                    if finished:
                        session["test_mode"] = ""  # 清掉测试提示

        # 銀行操作
        if request.method == "POST" and "bank_amount" in request.form:
            # 第一步：转换（格式错误）
            try:
                amount = int(request.form["bank_amount"])
            except ValueError:
                session["message"] = "請輸入正整數！"
            else:
                # 第二步：引擎校验（业务错误）
                try:
                    if request.form.get("action") == "deposit":
                        engine.deposit(amount)
                        session["message"] = f"存入 {amount} 成功，賭注池：{engine.bet}，銀行：{engine.bank}"
                    else:
                        engine.withdraw(amount)
                        session["message"] = f"取出 {amount} 成功，賭注池：{engine.bet}，銀行：{engine.bank}"
                except ValueError as e:
                    session["message"] = str(e)   # 引擎的中文提示（"金額非法"等）

        session["engine"] = engine.to_dict()  # 把引擎狀態存回 session              

        return render_template(
            "game.html",
            message=session["message"],
            target=engine.target if engine.in_round else None,
            max_num=engine.max_num,
            test_mode=session.get("test_mode", ""),
            bet=engine.bet,
            bank=engine.bank,
        )  # 返回完整 HTML 頁面（標題 + 提示 + 表單 + 測試模式提示）

#AI 背景生成（硅基流动 Kolors）
@app.route("/generate_bg", methods=["POST"])
def generate_bg():
    """接收前端描述，調用硅基流动的 Kolors 模型生成背景圖片。"""
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return {"error": "請輸入背景描述"}, 400

    api_key = "sk-aopzgmvcuzfkflvipmaizwimcricrrjwyxqkucrllfgovsee"  #API Key
    url = "https://api.siliconflow.cn/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "Kwai-Kolors/Kolors",
        "prompt": prompt,
        "image_size": "1024x1024",
        "num_inference_steps": 20,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        # 硅基流动返回格式：{"images": [{"url": "..."}]}
        image_url = result["images"][0]["url"]
        return {"url": image_url}
    except requests.exceptions.Timeout:
        return {"error": "生成超時，請稍後再試"}, 504
    except requests.exceptions.HTTPError as e:
        # 常見：429（超過每分鐘 2 張的限制）
        if resp.status_code == 429:
            return {"error": "生成太頻繁，每分鐘最多 2 張，請稍後再試"}, 429
        return {"error": f"API 錯誤：{resp.status_code}"}, 502
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)  # 啟動 Flask 應用，debug模式開啟
