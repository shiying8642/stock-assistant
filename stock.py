
import requests
from bs4 import BeautifulSoup
import os

# 要查詢的台灣股票
stocks = {
    "2330": "台積電",
    "2454": "聯發科",
    "2317": "鴻海"
}

# Yahoo 股市爬蟲
def get_stock_price(stock_id):
    url = f"https://tw.stock.yahoo.com/quote/{stock_id}.TW"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url, headers=headers, timeout=15
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    price_classes = [
        "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-down)",
        "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c)",
        "Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-up)"
    ]

    price_tag = soup.find("span", class_=price_classes)

    if price_tag:
        return price_tag.get_text(strip=True)

    return "無法取得股價"


# 整理股票資訊
def get_all_stocks():
    message = "📈 我的股票助手\n\n"

    for stock_id, name in stocks.items():
        try:
            price = get_stock_price(stock_id)
            message += f"{name}（{stock_id}）\n股價：{price}\n\n"
        except Exception as e:
            message += f"{name}（{stock_id}）\n查詢失敗：{e}\n\n"

    return message


# 傳送 Telegram 訊息
def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("尚未設定 Telegram，先顯示查詢結果：")
        print(message)
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message
        },
        timeout=15
    )

    response.raise_for_status()


# 執行股票助手
if __name__ == "__main__":
    result = get_all_stocks()
    print(result)
    send_telegram(result)
