import pandas as pd
from openai import OpenAI
import json
import os
import time

def enrich_data(raw_file, enriched_file):
    print("🧠 [Enricher] Checking data integrity...")
    
    # 读取原始数据
    if not os.path.exists(raw_file):
        print("❌ Error: Raw data file not found.")
        return

    df_raw = pd.read_csv(raw_file)
    
    # 读取已有的丰富数据（缓存），如果不存在则创建一个空的
    if os.path.exists(enriched_file):
        df_enriched = pd.read_csv(enriched_file)
    else:
        df_enriched = pd.DataFrame(columns=list(df_raw.columns) + ['Pros', 'Cons', 'Verdict'])

    # 找出哪些是新工具 (在 Raw 里有，在 Enriched 里没有的)
    # 这里做简单的全量覆盖逻辑演示，但在生产环境建议做增量更新
    # 为了简化 GitHub Action 流程，这里我们假设每次 raw 变动都需要重新检查
    
    # ⚠️ 关键：从环境变量获取 Key，绝不要写死！
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️ No API Key found in environment. Skipping AI enrichment.")
        # 如果没有 Key (比如本地测试没配)，就直接把 raw 复制过去，避免报错
        if not os.path.exists(enriched_file):
             df_raw.to_csv(enriched_file, index=False)
        return

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # 遍历每一行
    for index, row in df_raw.iterrows():
        tool_name = row['Tool_Name']
        
        # 检查是否已经处理过 (避免重复烧钱)
        if tool_name in df_enriched['Tool_Name'].values:
            existing_row = df_enriched[df_enriched['Tool_Name'] == tool_name].iloc[0]
            if pd.notna(existing_row.get('Verdict')):
                print(f"   ⏭️ Skipping {tool_name} (Already enriched)")
                continue

        print(f"   🤖 AI Processing: {tool_name}...")
        
        prompt = f"""
        Analyze software "{tool_name}". Return JSON with:
        "pros": ["pro1", "pro2", "pro3"],
        "cons": ["con1", "con2", "con3"],
        "verdict": "Best for X"
        JSON ONLY.
        """
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            data = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", ""))
            
            # 更新/写入数据
            df_enriched.loc[index, 'Tool_Name'] = tool_name
            df_enriched.loc[index, 'Price'] = row['Price']
            df_enriched.loc[index, 'Monthly_Visits'] = row['Monthly_Visits'] # 假设你有这个列
            df_enriched.loc[index, 'Pros'] = " | ".join(data['pros'])
            df_enriched.loc[index, 'Cons'] = " | ".join(data['cons'])
            df_enriched.loc[index, 'Verdict'] = data['verdict']
            
            # 实时保存
            df_enriched.to_csv(enriched_file, index=False)
            time.sleep(1) # 避免速率限制
            
        except Exception as e:
            print(f"   ❌ Failed to enrich {tool_name}: {e}")

    print("✅ Enrichment complete.")