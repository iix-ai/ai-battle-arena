import json
import os
from src.enricher import enrich_data
from src.visualizer import generate_charts
from src.generator import generate_pages

def main():
    # 确保目录存在
    os.makedirs('data/images', exist_ok=True)
    
    with open('config.json', 'r') as f:
        config = json.load(f)

    # 1. AI 注入 (读取 raw, 输出 enriched)
    enrich_data('data/tools_raw.csv', 'data/tools_enriched.csv')
    
    # 2. 生成图片 (读取 enriched, 输出到 data/images)
    generate_charts('data/tools_enriched.csv', 'data/images', config)
    
    # 3. 生成网页 (读取 enriched 和 images, 输出到 public)
    generate_pages('data/tools_enriched.csv', config)

if __name__ == "__main__":
    main()