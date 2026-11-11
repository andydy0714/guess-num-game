import random
from flask import Flask, request, session


TEST_MODE = True  # 设置为True以启用测试模式，顯示目標數字

app = Flask(__name__)  # 創建 Flask 應用實例
app.secret_key = "secret" # 設置密鑰，用於加密 session

@app.route("/guess_num_game", methods=["GET", "POST"]) # 定義路由：當用戶訪問 /guess_num_game 時執行此函數
def guess_number():

        # 首次訪問時初始化 session,保存遊戲狀態
        if "target" not in session:  
            session["target"] = None  # 目標數字
            session["tries"] = 0      # 猜測次數
            session["max_num"] = None # 最大正整數
            session["message"] = "歡迎來到猜數字遊戲!请先设置最大正整数以開始遊戲。"

        # 用戶設置上限時執行
        if request.method == "POST" and "max_num" in request.form:
            try:
                max_num = int(request.form["max_num"]) # 將輸入轉為整數
                if max_num < 1:
                    raise ValueError
            except ValueError:
                session["message"] = "請輸入正整數！" # 輸入非法時提示
            else:  # 輸入合法時執行
                session["max_num"] = max_num # 保存上限
                session["target"] = random.randint(1, max_num) # 隨機生成目標數字
                session["tries"] = 0 # 重置猜測次數

                # 根據測試模式顯示提示
                if TEST_MODE:
                    session["test_mode"] = f"(測試模式已啟用，目標數字是 {session['target']})"
                else:
                    session["test_mode"] = f"(測試模式已禁用，目標數字是隱藏的)"

        # 用戶猜數字時執行
        if request.method == "POST" and "guess" in request.form:
            try:
                guess = int(request.form["guess"])  # 將猜測轉為整數
            except ValueError:
                session["message"] = "請輸入正整數！" # 輸入非法時提示
            else:  # 猜測輸入合法時執行                         
                max_num = session["max_num"] # 取出上限
                target = session["target"] # 取出目標數字
                session["tries"] += 1 # 猜測次數加一
                tries = session["tries"]  # 暫存次數用於顯示

                # 判斷猜測結果
                if guess < 1 or guess > max_num:
                    session["message"] = f"目標數字是1-{max_num}之間的整數！"
                elif guess < target:
                    session["message"] = "小了"
                elif guess > target:
                    session["message"] = "大了"
                else:
                    session["message"] = f"猜對了！數字是 {target} ，你猜了 {tries} 次 ，再次设置最大正整数以重新開始遊戲。"
                    session["target"] = None       # 清空目標數字
                    session["max_num"] = None      # 清掉上限
                    session["tries"] = 0           # 次数归零
                    session["test_mode"] = ""      # 清掉测试提示
        # 根據遊戲狀態顯示不同的表單
        if session["target"] is None: # 遊戲未開始或已結束,顯示設置上限表單
            form = "<form method='post'><input name='max_num' type='number'><button>開始</button></form>"
        else: # 遊戲進行中,顯示猜數字表單
            form = f"<form method='post'><input name='guess' type='number' placeholder='猜一个1-{session['max_num']}的整數'><button>猜</button></form>"
        
        return f"<h1>猜數字遊戲</h1><p>{session['message']}</p>{form}<p>{session.get('test_mode', '')}</p>" # 返回完整 HTML 頁面（標題 + 提示 + 表單 + 測試模式提示）

app.run(debug=True) # 啟動 Flask 應用，debug模式開啟