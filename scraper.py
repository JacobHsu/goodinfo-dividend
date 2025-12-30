"""
GoodInfo 股利資料爬蟲 (並行版本)
使用多執行緒同時抓取多個類股以提升速度
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import csv
import urllib.parse
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MAX_WORKERS = 4  # 同時運行的瀏覽器數量

def get_industry_data(driver, industry):
    """抓取單一類股的股利資料"""
    encoded = urllib.parse.quote(industry)
    url = f'https://goodinfo.tw/tw/StockList.asp?MARKET_CAT=%E5%85%A8%E9%83%A8&INDUSTRY_CAT={encoded}&SHEET=%E8%82%A1%E5%88%A9%E6%94%BF%E7%AD%96%E7%99%BC%E6%94%BE%E5%B9%B4%E5%BA%A6&SHEET2=%E8%82%A1%E5%88%A9%E5%88%86%E6%B4%BE%E8%88%87%E9%99%A4%E6%AC%8A%2F%E6%81%AF%E5%83%B9%E6%AE%96%E5%88%A9%E7%8E%87&RPT_TIME=%E6%9C%80%E6%96%B0%E8%B3%87%E6%96%99'
    
    driver.get(url)
    time.sleep(3)  # 縮短等待時間
    
    table = driver.find_element(By.ID, 'tblStockList')
    rows = table.find_elements(By.TAG_NAME, 'tr')
    
    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'th') + row.find_elements(By.TAG_NAME, 'td')
        row_data = [c.text.strip().replace('\n', ' ') for c in cells]
        if any(row_data):
            data.append(row_data)
    
    return data

def save_to_csv(data, industry):
    """存成 CSV 檔案"""
    output_path = os.path.join(DATA_DIR, f'{industry}.csv')
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return len(data) - 1

def scrape_single_industry(industry):
    """抓取單一類股（獨立執行緒使用）"""
    start_time = time.time()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-images')  # 不載入圖片加速
    
    driver = None
    try:
        print(f'  🚀 開始抓取 {industry}...')
        driver = webdriver.Chrome(options=options)
        data = get_industry_data(driver, industry)
        count = save_to_csv(data, industry)
        duration = time.time() - start_time
        print(f'  ✅ {industry} 完成，{count} 檔，耗時: {duration:.2f} 秒')
        return {
            'industry': industry,
            'count': count,
            'duration': duration,
            'success': True
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f'  ❌ {industry} 錯誤: {e}')
        return {
            'industry': industry,
            'count': 0,
            'duration': duration,
            'success': False,
            'error': str(e)
        }
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def scrape_industries_parallel(industries, max_workers=MAX_WORKERS):
    """並行抓取多個類股"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_single_industry, industry): industry 
                   for industry in industries}
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    return results

if __name__ == '__main__':
    # 重新抓取资讯服务业
    industries = ['資訊服務業']
    
    total_start = time.time()
    print(f'開始並行抓取 {len(industries)} 個類股（最多同時 {MAX_WORKERS} 個）...\n')
    
    results = scrape_industries_parallel(industries)
    
    total_duration = time.time() - total_start
    
    # 統計結果
    print('\n' + '='*60)
    success_count = sum(1 for r in results if r['success'])
    total_stocks = sum(r['count'] for r in results if r['success'])
    
    print(f'全部完成!')
    print(f'  成功: {success_count}/{len(industries)} 個類股')
    print(f'  總股票數: {total_stocks} 檔')
    print(f'  總耗時: {total_duration:.2f} 秒')
    print(f'  平均每類股: {total_duration/len(industries):.2f} 秒')
    print('='*60)
