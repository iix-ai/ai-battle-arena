import pandas as pd
from openai import OpenAI
import json
import os
import time

def enrich_data(raw_file, enriched_file):
    print("🧠 [Enricher] Checking data integrity...")
    
    if not os.path.exists(raw_file):
        print("❌ Error: Raw data file not found.")
        return

    try:
        df_raw = pd.read_csv(raw_file)
    except Exception as e:
        print(f"❌ Error reading raw file: {e}")
        return

    # 初始化 DataFrame，增加多语言列
    cols = list(df_raw.columns) + [
        'Pros', 'Cons', 'Verdict', 'Rating',
        'Pros_ES', 'Cons_ES', 'Verdict_ES', # 西班牙语
        'Pros_PT', 'Cons_PT', 'Verdict_PT'  # 葡萄牙语
    ]
    
    if os.path.exists(enriched_file) and os.path.getsize(enriched_file) > 0:
        try:
            df_enriched = pd.read_csv(enriched_file)
        except:
            df_enriched = pd.DataFrame(columns=cols)
    else:
        df_enriched = pd.DataFrame(columns=cols)

    # 确保列存在
    for col in cols:
        if col not in df_enriched.columns:
            df_enriched[col] = ""

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️ No DEEPSEEK_API_KEY found. Skipping.")
        return

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    data_changed = False

    for index, row in df_raw.iterrows():
        tool_name = str(row['Tool_Name'])
        if "!" in tool_name or "[" in tool_name or len(tool_name) < 2: continue

        # 检查是否已存在且有外语数据
        if tool_name in df_enriched['Tool_Name'].values:
            existing = df_enriched[df_enriched['Tool_Name'] == tool_name].iloc[0]
            # 如果英文和葡语都有了，就跳过
            if pd.notna(existing.get('Verdict')) and pd.notna(existing.get('Verdict_PT')):
                continue

        print(f"   🤖 AI Processing (Multi-lang): {tool_name}...")
        
        # 核弹级 Prompt：一次生成三种语言
        prompt = f"""
        Analyze software "{tool_name}". Return JSON with English(default), Spanish(_es), Portuguese(_pt):
        {{
            "pros": ["3 short pros EN"], "cons": ["3 short cons EN"], "verdict": "Verdict EN",
            "pros_es": ["3 pros ES"], "cons_es": ["3 cons ES"], "verdict_es": "Verdict ES",
            "pros_pt": ["3 pros PT"], "cons_pt": ["3 cons PT"], "verdict_pt": "Verdict PT",
            "rating": "4.7"
        }}
        JSON ONLY. No markdown.
        """
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat", messages=[{"role": "user", "content": prompt}], temperature=0.1
            )
            content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "")
            data = json.loads(content)
            
            new_row = row.copy()
            new_row['Rating'] = str(data.get('rating', '4.5'))
            
            # English
            new_row['Pros'] = " | ".join(data.get('pros', []))
            new_row['Cons'] = " | ".join(data.get('cons', []))
            new_row['Verdict'] = data.get('verdict', '')
            
            # Spanish
            new_row['Pros_ES'] = " | ".join(data.get('pros_es', []))
            new_row['Cons_ES'] = " | ".join(data.get('cons_es', []))
            new_row['Verdict_ES'] = data.get('verdict_es', '')
            
            # Portuguese
            new_row['Pros_PT'] = " | ".join(data.get('pros_pt', []))
            new_row['Cons_PT'] = " | ".join(data.get('cons_pt', []))
            new_row['Verdict_PT'] = data.get('verdict_pt', '')
            
            # 合并
            # 先删除旧的同名行（如果有）
            df_enriched = df_enriched[df_enriched['Tool_Name'] != tool_name]
            df_enriched = pd.concat([df_enriched, pd.DataFrame([new_row])], ignore_index=True)
            
            df_enriched.to_csv(enriched_file, index=False)
            data_changed = True
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

    if data_changed:
        print("✅ Multi-language data updated.")