import csv
import os
import json
import random
from datetime import datetime
import requests

CSV_FILE = 'tools.csv'
API_KEY = os.environ.get("DEEPSEEK_API_KEY") 

def fetch_deep_analysis(tool_name):
    """
    V9.0 升级：获取深度优缺点分析，拒绝内容单薄
    """
    if not API_KEY:
        # 本地模拟数据
        return {
            "verdict": f"{tool_name} remains a strong contender in 2026.",
            "score": round(random.uniform(4.2, 4.9), 1),
            "pros": "Easy to use; Affordable; Great Support",
            "cons": "Limited advanced features; API limits; No mobile app"
        }

    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    
    # 核心：要求 AI 返回优缺点
    prompt = f"""Analyze '{tool_name}' for 2026. Return JSON:
    {{
        "verdict": "1 sentence summary",
        "score": 4.8,
        "pros": "Pro 1; Pro 2; Pro 3",
        "cons": "Con 1; Con 2; Con 3"
    }}"""
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        return json.loads(response.json()['choices'][0]['message']['content'])
    except:
        return {"verdict": "Data unavailable.", "score": 4.0, "pros": "", "cons": ""}

def main():
    print("🤖 深度分析机器人启动...")
    
    if not os.path.exists(CSV_FILE):
        print("❌ CSV not found")
        return

    rows = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    
    # 随机抽取 2 个进行深度更新 (省 Token)
    targets = random.sample(rows, min(2, len(rows)))
    
    for row in targets:
        print(f"🧠 深度分析: {row['tool_b']}...")
        data = fetch_deep_analysis(row['tool_b'])
        
        row['score_b'] = data['score']
        row['verdict'] = data['verdict'] # 更新点评
        
        # 自动填充/更新优缺点 (如果CSV里没有这些列，稍后写入时会自动忽略或需手动添加表头，建议手动先加好)
        row['pros_b'] = data['pros']
        row['cons_b'] = data['cons']

    # 写入
    if rows:
        fieldnames = rows[0].keys()
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print("✅ 数据深度增强完毕！")

if __name__ == "__main__":
    main()