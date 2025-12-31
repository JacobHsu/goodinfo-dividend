"""
匯出所有產業中殖利率 >= 5% 的股票清單
整合所有類股資料並過濾符合條件的股票
"""
import csv
import os
from pathlib import Path

# 黑名單: 去年沒發股利的股票代碼
# 與 app.js 保持同步
DIVIDEND_BLACKLIST = [
    '1806',  # 冠軍 - 2024 年沒發股利
]

# 產業清單（與 app.js 保持同步）
INDUSTRIES = [
    'ETF', '水泥工業', '食品工業', '塑膠工業', '紡織纖維', '電機機械',
    '電器電纜', '生技醫療業', '化學工業', '玻璃陶瓷', '造紙工業',
    '鋼鐵工業', '橡膠工業', '汽車工業', '電腦及週邊設備業', '半導體業',
    '電子零組件業', '其他電子業', '通信網路業', '資訊服務業', '建材營造業',
    '航運業', '觀光餐旅', '銀行業', '保險業', '金控業',
    '貿易百貨業', '光電業', '電子通路業', '證券業', '綠能環保',
    '數位雲端', '其他業', '運動休閒', '油電燃氣業', '居家生活',
    '文化創意業', '農業科技業'
]

DATA_DIR = Path(__file__).parent / 'data'
OUTPUT_FILE = DATA_DIR / 'high_yield_stocks.csv'

def parse_csv_line(line):
    """解析 CSV 單行（處理引號）"""
    result = []
    current = ''
    in_quotes = False

    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            result.append(current.strip())
            current = ''
        else:
            current += char

    result.push(current.strip())
    return result

def read_industry_csv(csv_path):
    """讀取單一產業 CSV 並回傳符合條件的股票"""
    stocks = []

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader)  # 跳過標題列

            for row in reader:
                if len(row) < 16:
                    continue

                try:
                    # 解析資料（對應 app.js 的欄位結構）
                    code = row[0].strip()
                    name = row[1].strip()
                    price = float(row[3]) if row[3] else 0
                    cash_dividend = float(row[8]) if row[8] else 0
                    stock_dividend = float(row[9]) if row[9] else 0
                    total_dividend = float(row[10]) if row[10] else 0
                    total_yield = float(row[15]) if row[15] else 0

                    # 過濾條件（與 app.js 邏輯相同）
                    # 1. 殖利率 >= 5%
                    if total_yield < 5:
                        continue

                    # 2. 現金股利 > 0
                    if cash_dividend <= 0:
                        continue

                    # 3. 不在黑名單中
                    if code in DIVIDEND_BLACKLIST:
                        continue

                    # 4. ETF 類別過濾債券型（代碼結尾為 'B'）
                    industry_name = csv_path.stem
                    if industry_name == 'ETF' and code.endswith('B'):
                        continue

                    stocks.append({
                        'industry': industry_name,
                        'code': code,
                        'name': name,
                        'price': price,
                        'frequency': row[7],
                        'cash_dividend': cash_dividend,
                        'stock_dividend': stock_dividend,
                        'total_dividend': total_dividend,
                        'total_yield': total_yield,
                        'ex_dividend_date': row[16],
                        'payment_date': row[18]
                    })

                except (ValueError, IndexError) as e:
                    continue

    except FileNotFoundError:
        print(f'[!] 找不到檔案: {csv_path}')
    except Exception as e:
        print(f'[!] 讀取 {csv_path.name} 時發生錯誤: {e}')

    return stocks

def export_high_yield_stocks():
    """匯出所有高殖利率股票"""
    all_stocks = []

    print('[*] 開始讀取所有產業資料...\n')

    for industry in INDUSTRIES:
        csv_path = DATA_DIR / f'{industry}.csv'
        stocks = read_industry_csv(csv_path)
        all_stocks.extend(stocks)

        if stocks:
            print(f'  [+] {industry}: {len(stocks)} 檔')
        else:
            print(f'  [ ] {industry}: 0 檔')

    # 依殖利率排序（由高到低）
    all_stocks.sort(key=lambda x: x['total_yield'], reverse=True)

    # 寫入 CSV
    print(f'\n[*] 匯出至 {OUTPUT_FILE.name}...')

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = [
            '產業', '股票代號', '股票名稱', '股價', '發放頻率',
            '現金股利', '股票股利', '合計股利', '殖利率(%)',
            '除息日', '發放日'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for stock in all_stocks:
            writer.writerow({
                '產業': stock['industry'],
                '股票代號': stock['code'],
                '股票名稱': stock['name'],
                '股價': f"{stock['price']:.2f}",
                '發放頻率': stock['frequency'],
                '現金股利': f"{stock['cash_dividend']:.2f}",
                '股票股利': f"{stock['stock_dividend']:.2f}",
                '合計股利': f"{stock['total_dividend']:.2f}",
                '殖利率(%)': f"{stock['total_yield']:.2f}",
                '除息日': stock['ex_dividend_date'],
                '發放日': stock['payment_date']
            })

    print(f'\n' + '='*60)
    print(f'[+] 匯出完成！')
    print(f'  總共: {len(all_stocks)} 檔股票（殖利率 >= 5%）')
    print(f'  檔案: {OUTPUT_FILE}')
    print('='*60)

if __name__ == '__main__':
    export_high_yield_stocks()
