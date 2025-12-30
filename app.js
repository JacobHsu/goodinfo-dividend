/**
 * 股利一覽
 * 讀取各類股 CSV 並顯示殖利率 >= 5% 的股票
 */

// 類股清單
const INDUSTRIES = [
    '水泥工業', '食品工業', '塑膠工業', '紡織纖維', '電機機械',
    '電器電纜', '生技醫療業', '化學工業', '玻璃陶瓷', '造紙工業',
    '鋼鐵工業', '橡膠工業', '汽車工業', '電腦及週邊設備業', '半導體業',
    '電子零組件業', '其他電子業', '通信網路業', '資訊服務業', '建材營造業',
    '航運業', '觀光餐旅', '銀行業', '保險業', '金控業',
    '貿易百貨業', '光電業', '電子通路業', '證券業', '綠能環保',
    '數位雲端', '其他業', '運動休閒', '油電燃氣業', '居家生活',
    '文化創意業', '農業科技業', 'ETF'
];

// 全域狀態
let allData = {};
let currentIndustry = null;
let currentSort = { field: 'totalYield', ascending: false };

// 初始化
document.addEventListener('DOMContentLoaded', init);

async function init() {
    renderCategoryButtons();
    await loadAllData();
    updateDate();
    // 預設選擇 ETF
    selectIndustry('ETF');
}

// 渲染類股按鈕
function renderCategoryButtons() {
    const container = document.getElementById('categoryTable');
    container.innerHTML = INDUSTRIES.map(industry => `
        <button class="category-btn" data-industry="${industry}">
            ${industry}
            <span class="stock-count-badge">載入中...</span>
        </button>
    `).join('');
    
    container.addEventListener('click', (e) => {
        const btn = e.target.closest('.category-btn');
        if (btn) {
            const industry = btn.dataset.industry;
            selectIndustry(industry);
        }
    });
}

// 載入所有 CSV 資料
async function loadAllData() {
    for (const industry of INDUSTRIES) {
        try {
            const response = await fetch(`data/${encodeURIComponent(industry)}.csv`);
            const text = await response.text();
            const data = parseCSV(text);
            let filtered = filterHighYield(data);
            
            // 如果是 ETF，過濾掉代碼以 'B' 結尾的債券型 ETF
            if (industry === 'ETF') {
                filtered = filtered.filter(stock => !stock.code.endsWith('B'));
            }
            
            allData[industry] = filtered;
            
            // 更新按鈕上的數量
            const btn = document.querySelector(`[data-industry="${industry}"]`);
            if (btn) {
                btn.querySelector('.stock-count-badge').textContent = `${filtered.length} 檔`;
            }
        } catch (err) {
            console.error(`載入 ${industry} 失敗:`, err);
            allData[industry] = [];
        }
    }
}

// 解析 CSV
function parseCSV(text) {
    const lines = text.trim().split('\n');
    if (lines.length < 2) return [];
    
    // 解析標題行
    const headers = parseCSVLine(lines[0]);
    
    const data = [];
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue;
        const values = parseCSVLine(lines[i]);
        
        if (values.length < 10) continue;
        
        // 對應欄位 (根據 GoodInfo 匯出的格式)
        const stock = {
            code: values[0] || '',
            name: values[1] || '',
            date: values[2] || '',
            price: parseFloat(values[3]) || 0,
            change: values[4] || '',
            changePercent: values[5] || '',
            dividendYear: values[6] || '',
            frequency: values[7] || '',
            cashDividend: parseFloat(values[8]) || 0,
            stockDividend: parseFloat(values[9]) || 0,
            totalDividend: parseFloat(values[10]) || 0,
            exDividendPrice: values[11] || '',
            exDividendYield: parseFloat(values[12]) || 0,
            exRightsPrice: values[13] || '',
            exRightsYield: parseFloat(values[14]) || 0,
            totalYield: parseFloat(values[15]) || 0,
            exDividendDate: values[16] || '',
            exRightsDate: values[17] || '',
            paymentDate: values[18] || ''
        };
        
        data.push(stock);
    }
    
    return data;
}

// 解析單行 CSV (處理引號)
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current.trim());
    
    return result;
}

// 過濾殖利率 >= 5%
function filterHighYield(data) {
    return data.filter(stock => stock.totalYield >= 5);
}

// 選擇類股
function selectIndustry(industry) {
    currentIndustry = industry;
    
    // 更新按鈕狀態
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.industry === industry);
    });
    
    // 更新標題
    document.getElementById('currentCategory').textContent = industry;
    
    // 顯示資料
    renderStockTable();
}

// 渲染股票表格
function renderStockTable() {
    let data = allData[currentIndustry] || [];
    
    // 如果是 ETF，過濾掉代碼以 'B' 結尾的債券型 ETF
    if (currentIndustry === 'ETF') {
        data = data.filter(stock => !stock.code.endsWith('B'));
    }
    
    // 過濾掉現金股利為 0 的股票
    data = data.filter(stock => stock.cashDividend > 0);
    
    const sortedData = sortData(data);
    
    document.getElementById('stockCount').textContent = sortedData.length;
    
    const tbody = document.getElementById('stockTableBody');
    
    if (sortedData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="no-data">沒有殖利率 ≥ 5% 的股票</td></tr>`;
        return;
    }
    
    tbody.innerHTML = sortedData.map(stock => `
        <tr>
            <td><a class="stock-link" href="https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID=${stock.code}" target="_blank">${stock.code}</a></td>
            <td>${stock.name}</td>
            <td>${stock.price.toFixed(2)}</td>
            <td>${stock.frequency}</td>
            <td>${stock.cashDividend.toFixed(2)}</td>
            <td style="${stock.stockDividend > 0 ? 'font-weight: bold;' : ''}">${stock.stockDividend.toFixed(2)}</td>
            <td>${stock.totalDividend.toFixed(2)}</td>
            <td class="${getYieldClass(stock.totalYield)}">${stock.totalYield.toFixed(2)}%</td>
            <td>${stock.exDividendDate}</td>
            <td>${stock.paymentDate}</td>
        </tr>
    `).join('');
}

// 排序資料
function sortData(data) {
    return [...data].sort((a, b) => {
        let valA = a[currentSort.field];
        let valB = b[currentSort.field];
        
        // 數字比較
        if (typeof valA === 'number' && typeof valB === 'number') {
            return currentSort.ascending ? valA - valB : valB - valA;
        }
        
        // 字串比較
        valA = String(valA);
        valB = String(valB);
        return currentSort.ascending ? valA.localeCompare(valB) : valB.localeCompare(valA);
    });
}

// 殖利率樣式
function getYieldClass(yield_val) {
    if (yield_val >= 8) return 'yield-high';
    if (yield_val >= 6) return 'yield-medium';
    return 'yield-low';
}

// 更新日期
function updateDate() {
    const today = new Date();
    document.getElementById('updateDate').textContent = 
        `${today.getFullYear()}/${String(today.getMonth() + 1).padStart(2, '0')}/${String(today.getDate()).padStart(2, '0')}`;
}

// 表頭排序點擊
document.addEventListener('click', (e) => {
    if (e.target.closest('th[data-sort]')) {
        const th = e.target.closest('th');
        const field = th.dataset.sort;
        
        if (currentSort.field === field) {
            currentSort.ascending = !currentSort.ascending;
        } else {
            currentSort.field = field;
            currentSort.ascending = false;
        }
        
        // 更新排序指示器
        document.querySelectorAll('.stock-table th').forEach(header => {
            const indicator = header.querySelector('.sort-indicator');
            if (header.dataset.sort === field) {
                indicator.textContent = currentSort.ascending ? '▲' : '▼';
                header.classList.add('highlight');
            } else {
                indicator.textContent = '';
                header.classList.remove('highlight');
            }
        });
        
        if (currentIndustry) {
            renderStockTable();
        }
    }
});
