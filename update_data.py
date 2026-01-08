import csv
import os
import json
import random
from datetime import datetime
import requests

CSV_FILE = 'tools.csv'
# GitHub Actions 会自动注入这个环境变量
API_KEY = os.environ.get("DEEPSEEK_API_KEY") 

def fetch_market_intel(tool_name):
    """
    高端玩法：调用 AI 作为“软爬虫”，获取最新市场评价和价格波动
    """
    if not API_KEY:
        # 本地测试如果没有Key，返回模拟数据
        return f"Updated analysis for {tool_name} in 2026.", round(random.uniform(4.0, 5.0), 1)

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a Tech Market Analyst. Return JSON only."},
            {"role": "user", "content": f"Provide a 1-sentence verdict on '{tool_name}' for 2026. And give a rating (0.0-5.0). Format: {{\"verdict\": \"...\", \"score\": 4.8}}"}
        ],
        "stream": False
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        res_json = response.json()
        content = json.loads(res_json['choices'][0]['message']['content'])
        return content.get('verdict', 'Good tool'), content.get('score', 4.5)
    except:
        return "High demand tool.", 4.5

def main():
    print("🤖 机器人启动：开始扫描市场数据...")
    
    rows = []
    # 1. 读取旧数据
    if not os.path.exists(CSV_FILE):
        print("CSV not found.")
        return

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # 2. 智能更新 (模拟市场变化)
    # 每次随机更新 2 个工具的数据，模拟真实波动，且节省 Token
    if rows:
        targets = random.sample(rows, min(2, len(rows)))
        
        for row in targets:
            print(f"🔄 更新数据: {row['tool_b']}...")
            new_verdict, new_score = fetch_market_intel(row['tool_b'])
            # 更新 CSV 里的数据
            row['score_b'] = new_score
            # 在 feature 里追加更新标记，证明网站是活的
            base_feature = row['feature_b'].split(' (')[0]
            row['feature_b'] = f"{base_feature} (Checked {datetime.now().strftime('%m/%d')})"

        # 3. 写入文件
        fieldnames = rows[0].keys()
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        print("✅ 数据更新完毕！")
    else:
        print("CSV is empty.")

if __name__ == "__main__":
    main()