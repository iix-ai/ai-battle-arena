import pandas as pd
from openai import OpenAI
import json
import os
import time

def enrich_data(raw_file, enriched_file):
    print("🧠 [Enricher] Checking data integrity...")
    
    # 1. 检查原始数据是否存在
    if not os.path.exists(raw_file):
        print("❌ Error: Raw data file not found.")
        return

    # 读取原始数据 (Raw)
    try:
        df_raw = pd.read_csv(raw_file)
    except Exception as e:
        print(f"❌ Error reading raw file: {e}")
        return

    # 2. 智能读取缓存 (修复 EmptyDataError)
    # 只有当文件存在 且 大小大于0 时，才尝试读取
    if os.path.exists(enriched_file) and os.path.getsize(enriched_file) > 0:
        try:
            df_enriched = pd.read_csv(enriched_file)
            print("   ✅ Loaded existing enriched data cache.")
        except pd.errors.EmptyDataError:
            print("   ⚠️ Enriched file is empty. Creating new one.")
            df_enriched = pd.DataFrame(columns=list(df_raw.columns) + ['Pros', 'Cons', 'Verdict'])
    else:
        print("   🆕 No cache found. Creating new enriched dataframe.")
        df_enriched = pd.DataFrame(columns=list(df_raw.columns) + ['Pros', 'Cons', 'Verdict'])

    # 3. 检查 API Key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("⚠️ No DEEPSEEK_API_KEY found in environment secrets.")
        print("   -> Skipping AI enrichment to prevent crash.")
        # 如果没有Key，直接把原始数据保存过去，保证后续步骤有文件可用
        if not os.path.exists(enriched_file) or os.path.getsize(enriched_file) == 0:
            df_raw.to_csv(enriched_file, index=False)
        return

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # 4. 开始处理数据
    data_changed = False # 标记是否有新数据写入

    for index, row in df_raw.iterrows():
        tool_name = str(row['Tool_Name'])
        
        # 过滤掉垃圾数据 (比如 Excel 截图里的 ![Awesome]...)
        if "!" in tool_name or "[" in tool_name or len(tool_name) < 2:
            continue

        # 检查缓存：如果这个工具已经处理过且 Verdict 不为空，跳过
        if 'Tool_Name' in df_enriched.columns and tool_name in df_enriched['Tool_Name'].values:
            existing_rows = df_enriched[df_enriched['Tool_Name'] == tool_name]
            if not existing_rows.empty and pd.notna(existing_rows.iloc[0].get('Verdict')):
                continue

        print(f"   🤖 AI Processing: {tool_name}...")
        
        # 修改 prompt
        prompt = f"""
        Analyze software "{tool_name}". Return JSON with:
        "pros": ["pro1", "pro2", "pro3"],
        "cons": ["con1", "con2", "con3"],
        "verdict": "Best for X",
        "rating": "4.x" 
        (Provide a realistic rating between 4.0 and 4.9 based on user sentiment. e.g. "4.7")
        JSON ONLY. No markdown.
        """
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            content = response.choices[0].message.content.strip()
            # 清理可能存在的 markdown 标记
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
            
            data = json.loads(content)
            
            # 定位或新增行
            # 这里简单处理：直接在 df_enriched 里追加或更新
            # 为了代码简单，我们直接把当前 row 复制并添加 AI 字段
            new_row = row.copy()
            new_row['Pros'] = " | ".join(data.get('pros', []))
            new_row['Cons'] = " | ".join(data.get('cons', []))
            new_row['Verdict'] = data.get('verdict', '')
            new_row['Rating'] = data.get('rating', '4.5') # 新增这一行
            
            # 将新行转为 DataFrame 并合并
            df_enriched = pd.concat([df_enriched, pd.DataFrame([new_row])], ignore_index=True)
            
            # 实时保存 (防止超时丢失)
            df_enriched.to_csv(enriched_file, index=False)
            data_changed = True
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ Failed to enrich {tool_name}: {e}")

    # 再次去重保存，确保整洁
    if data_changed:
        df_enriched.drop_duplicates(subset=['Tool_Name'], keep='last', inplace=True)
        df_enriched.to_csv(enriched_file, index=False)
        print("✅ Enrichment update complete.")
    else:
        print("✅ No new data needed enrichment.")