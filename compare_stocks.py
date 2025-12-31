"""
交叉比對股東會紀念品與高殖利率股票
找出同時有紀念品又有高殖利率的股票
"""
import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'
GIFT_FILE = DATA_DIR / '股東會紀念品.csv'
HIGH_YIELD_FILE = DATA_DIR / 'high_yield_stocks.csv'
OUTPUT_FILE = DATA_DIR / 'gift_and_high_yield.csv'

def read_gift_stocks():
    """讀取有紀念品的股票代碼"""
    stocks = {}

    try:
        with open(GIFT_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row['股票代號'].strip()
                stocks[code] = {
                    'name': row['股票名稱'].strip(),
                    'gift': row['紀念品'].strip(),
                    'price': row['股價'].strip(),
                    'last_buy_date': row['最後買進日'].strip()
                }
    except FileNotFoundError:
        print(f'[!] 找不到檔案: {GIFT_FILE}')
        return {}
    except Exception as e:
        print(f'[!] 讀取股東會紀念品檔案錯誤: {e}')
        return {}

    return stocks

def read_high_yield_stocks():
    """讀取高殖利率股票代碼"""
    stocks = {}

    try:
        with open(HIGH_YIELD_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row['股票代號'].strip()
                stocks[code] = {
                    'name': row['股票名稱'].strip(),
                    'industry': row['產業'].strip(),
                    'price': row['股價'].strip(),
                    'cash_dividend': row['現金股利'].strip(),
                    'total_dividend': row['合計股利'].strip(),
                    'total_yield': row['殖利率(%)'].strip(),
                    'ex_dividend_date': row['除息日'].strip(),
                    'payment_date': row['發放日'].strip()
                }
    except FileNotFoundError:
        print(f'[!] 找不到檔案: {HIGH_YIELD_FILE}')
        return {}
    except Exception as e:
        print(f'[!] 讀取高殖利率股票檔案錯誤: {e}')
        return {}

    return stocks

def compare_and_export():
    """比對並匯出共同股票"""
    print('[*] 讀取股東會紀念品資料...')
    gift_stocks = read_gift_stocks()
    print(f'  [+] 找到 {len(gift_stocks)} 檔有紀念品的股票')

    print('\n[*] 讀取高殖利率股票資料...')
    high_yield_stocks = read_high_yield_stocks()
    print(f'  [+] 找到 {len(high_yield_stocks)} 檔高殖利率股票')

    # 找出共同的股票代碼
    common_codes = set(gift_stocks.keys()) & set(high_yield_stocks.keys())

    print(f'\n[*] 找到 {len(common_codes)} 檔共同股票（有紀念品 + 殖利率 >= 5%）\n')

    if not common_codes:
        print('[!] 沒有找到共同的股票')
        return

    # 整合資料
    results = []
    for code in sorted(common_codes):
        gift_info = gift_stocks[code]
        yield_info = high_yield_stocks[code]

        results.append({
            'code': code,
            'name': gift_info['name'],
            'industry': yield_info['industry'],
            'price': yield_info['price'],
            'gift': gift_info['gift'],
            'last_buy_date': gift_info['last_buy_date'],
            'cash_dividend': yield_info['cash_dividend'],
            'total_dividend': yield_info['total_dividend'],
            'total_yield': yield_info['total_yield'],
            'ex_dividend_date': yield_info['ex_dividend_date'],
            'payment_date': yield_info['payment_date']
        })

    # 依殖利率排序
    results.sort(key=lambda x: float(x['total_yield']), reverse=True)

    # 輸出到螢幕
    print('='*80)
    print(f"{'代號':<8} {'股票名稱':<12} {'殖利率':<8} {'紀念品':<20} {'最後買進日':<12}")
    print('='*80)

    for stock in results:
        print(f"{stock['code']:<8} {stock['name']:<12} {stock['total_yield']:>6}% {stock['gift']:<20} {stock['last_buy_date']:<12}")

    # 匯出 CSV
    print(f'\n[*] 匯出至 {OUTPUT_FILE.name}...')

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = [
            '股票代號', '股票名稱', '產業', '股價', '紀念品', '最後買進日',
            '現金股利', '合計股利', '殖利率(%)', '除息日', '發放日'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        for stock in results:
            writer.writerow({
                '股票代號': stock['code'],
                '股票名稱': stock['name'],
                '產業': stock['industry'],
                '股價': stock['price'],
                '紀念品': stock['gift'],
                '最後買進日': stock['last_buy_date'],
                '現金股利': stock['cash_dividend'],
                '合計股利': stock['total_dividend'],
                '殖利率(%)': stock['total_yield'],
                '除息日': stock['ex_dividend_date'],
                '發放日': stock['payment_date']
            })

    print('\n' + '='*80)
    print(f'[+] 完成！共找到 {len(results)} 檔股票（有紀念品 + 殖利率 >= 5%）')
    print(f'  檔案: {OUTPUT_FILE}')
    print('='*80)

if __name__ == '__main__':
    compare_and_export()
