
import os
import requests
from bs4 import BeautifulSoup

# 要查詢的股票代號
STOCKS = ["2330.TW"]

# 從 GitHub Secrets 讀取 Telegram 設定
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def get_stock_price(stock_code):
    url = f"https://tw.stock.yahoo.com/quote/{stock_code}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    price_tag = soup.find(
        "span",
        class_=lambda c: c and "Fz(32px)" in c and "Fw(b)" in c
    )

    if price_tag is None:
        raise ValueError(
            f"找不到 {stock_code} 的股價，可能是 Yahoo 網頁格式已變更"
        )

    return price_tag.get_text(strip=True)


def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError(
            "找不到 Telegram Bot Token 或 Chat ID，請檢查 GitHub Secrets"
        )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(
        url,
        data=data,
        timeout=20
    )

    result = response.json()

    if not response.ok or not result.get("ok"):
        raise RuntimeError(
            f"Telegram 傳送失敗：{result.get('description', result)}"
        )

    print("Telegram 訊息傳送成功！")


def main():
    messages = ["📈 台股股價通知"]

    for stock_code in STOCKS:
        try:
            price = get_stock_price(stock_code)
            messages.append(
                f"{stock_code}：{price} 元"
            )
        except Exception as error:
            messages.append(
                f"{stock_code}：取得股價失敗\n{error}"
            )

    message = "\n".join(messages)
    print(message)

    send_telegram(message)
    print("Telegram 訊息傳送完成！")


if __name__ == "__main__":
    main()
