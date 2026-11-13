> 下注引擎（Betting Engine）

### 1.資金
玩家有兩個餘額：
  `balance`（本金 / 賭注池） | 可以用於下注的餘額 |
  `bank`（銀行） | 已存入、不參與下注的安全餘額 |
  初始值：`balance = 100`，`bank = 0`。
銀行只有兩個操作，且只允許在沒有進行中的回合時執行（狀態 `SETUP`）
  存入 `amount`：`balance -= amount`，`bank += amount`
  取出 `amount`：`bank -= amount`，`balance += amount`
金額必須是正整數，且不能超過對應餘額。

### 2. 一局的流程
1. 玩家在開始頁輸入上限 `max_num`（記為 `N`）。
2. 校驗：`MIN_MAX_NUM <= N <= MAX_MAX_NUM`，且 `balance > 0`。
3. 開局時鎖定全部本金作為賭注：`stake = balance`
4. 生成 `target = random.randint(1, N)`
5. 根據 `N` 計算本局倍率 `m = M(N)`，開局後固定不變。
6. 玩家最多猜 `G = 5` 次：
   猜中：結算為 `balance =(stake × (1 + m))`，回合結束，回到開始頁；
   5 次都沒猜中：`balance = 0`，回合結束，回到開始頁。
7. 回合結束後玩家重新設置上限，開始下一局。

### 3. 現在代碼的改動方式
寫一個獨立的 BettingEngine 類 `betting_engine.py`，實例存進 session

