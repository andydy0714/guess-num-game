import random


class BettingEngine:
    MIN_MAX_NUM = 1
    MAX_MAX_NUM = 3200
    MAX_GUESSES = 5

    def __init__(self, bet=100, bank=0):
        self.bet = bet
        self.bank = bank
        self.stake = 0
        self.target = None
        self.max_num = None
        self.tries = 0
        self.multiplier = 1
        self.in_round = False

    def deposit(self, amount):  #存錢
        if self.in_round:
            raise ValueError("回合進行中，不能操作銀行")
        if amount <= 0 or amount > self.bet:
            raise ValueError("金額非法")
        self.bet -= amount
        self.bank += amount

    def withdraw(self, amount): #取錢
        if self.in_round:
            raise ValueError("回合進行中，不能操作銀行")
        if amount <= 0 or amount > self.bank:
            raise ValueError("金額非法")
        self.bank -= amount
        self.bet += amount

    def start_round(self, max_num):
        if self.in_round:
            raise ValueError("上一局還沒結束")
        if not (self.MIN_MAX_NUM <= max_num <= self.MAX_MAX_NUM):
            raise ValueError("上限超出範圍")
        if self.bet <= 0:
            raise ValueError("賭注不能為0")

        self.max_num = max_num
        self.stake = self.bet
        self.target = random.randint(1, max_num)
        self.tries = 0
        self.multiplier = max_num / 32
        self.in_round = True

    def guess(self, guess):
        """返回 (結果字串, 是否結束)"""
        if not self.in_round:
            raise ValueError("沒有進行中的回合")

        self.tries += 1

        if guess == self.target:
            winnings = int(self.stake * (1 + self.multiplier))
            self.bet = winnings
            self.in_round = False
            return f"猜對了！數字是 {self.target}，你贏了 {winnings}", True

        if self.tries >= self.MAX_GUESSES:
            self.bet = 0
            self.in_round = False
            if self.bet == 0 and self.bank == 0: # 破產檢查：賭注和銀行都為 0 時，送 100 賭注
                self.bet = 100
                return f"次數用盡，數字是 {self.target}，你輸了全部賭注 {self.stake}，請重新設置上限（因為你破產了，送你 100 賭注！）", True
            else:    
                return f"次數用盡，數字是 {self.target}，你輸了全部賭注 {self.stake}，請重新設置上限", True

        if guess < self.target:
            return f"小了，你猜的是 {guess}（剩 {self.MAX_GUESSES - self.tries} 次）", False
        else:
            return f"大了，你猜的是 {guess}（剩 {self.MAX_GUESSES - self.tries} 次）", False

    def to_dict(self):
        return {
            "bet": self.bet, "bank": self.bank, "stake": self.stake,
            "target": self.target, "max_num": self.max_num,
            "tries": self.tries, "multiplier": self.multiplier,
            "in_round": self.in_round,
        }

    @classmethod
    def from_dict(cls, d):
        e = cls(bet=d.get("bet", 100), bank=d.get("bank", 0))
        e.stake = d.get("stake", 0)
        e.target = d.get("target")
        e.max_num = d.get("max_num")
        e.tries = d.get("tries", 0)
        e.multiplier = d.get("multiplier", 1)
        e.in_round = d.get("in_round", False)
        return e