import csv
import os
import json
import datetime

# =================配置区=================
CSV_FILE = 'tools.csv'
OUTPUT_DIR = 'dist'
SITE_NAME = 'Nexus AI Battle Arena'
SITE_URL = 'https://compare.ii-x.com' # 您的二级域名
# =======================================

def create_svg_chart(name_a, price_a, name_b, price_b):
    """
    黑科技：直接用代码生成 SVG 矢量价格对比图
    无需任何插件，加载速度 0 秒
    """
    try:
        pa = float(price_a)
        pb = float(price_b)
    except:
        return "" # 数据错误就不画图

    max_price = max(pa, pb) * 1.2 # 留点头部空间
    h_a = (pa / max_price) * 200
    h_b = (pb / max_price) * 200
    
    # 颜色逻辑：便宜的用绿色，贵的用红色 (视觉引导转化)
    color_a = "#22c55e" if pa < pb else "#ef4444"
    color_b = "#22c55e" if pb < pa else "#ef4444"

    svg = f'''
    <svg width="100%" height="250" viewBox="0 0 400 250" xmlns="http://www.w3.org/2000/svg" style="background:#f9fafb; border-radius:12px; padding:20px;">
        <!-- A柱 -->
        <rect x="50" y="{220 - h_a}" width="100" height="{h_a}" fill="{color_a}" rx="5" />
        <text x="100" y="{215 - h_a}" text-anchor="middle" font-family="sans-serif" font-weight="bold" fill="#374151">${pa}</text>
        <text x="100" y="240" text-anchor="middle" font-family="sans-serif" fill="#6b7280">{name_a}</text>
        
        <!-- B柱 -->
        <rect x="250" y="{220 - h_b}" width="100" height="{h_b}" fill="{color_b}" rx="5" />
        <text x="300" y="{215 - h_b}" text-anchor="middle" font-family="sans-serif" font-weight="bold" fill="#374151">${pb}</text>
        <text x="300" y="240" text-anchor="middle" font-family="sans-serif" fill="#6b7280">{name_b}</text>
        
        <!-- 标题 -->
        <text x="200" y="30" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#9ca3af">Monthly Price Comparison (Lower is Better)</text>
    </svg>
    '''
    return svg

def create_schema(row):
    """
    高端SEO：生成 JSON-LD 结构化数据
    让 Google 直接显示星级和价格
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"{row['tool_a']} vs {row['tool_b']}",
        "description": f"Detailed comparison: {row['tool_a']} (${row['price_a']}) vs {row['tool_b']} (${row['price_b']}). Winner: {row['winner']}.",
        "brand": {"@type": "Brand", "name": SITE_NAME},
        "review": {
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": row['score_a'], # 给我们推的那个打高分
                "bestRating": "5"
            },
            "author": {"@type": "Organization", "name": "Nexus AI Team"}
        }
    }
    return json.dumps(schema)

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            # 1. 生成核武器
            svg_chart = create_svg_chart(row['tool_a'], row['price_a'], row['tool_b'], row['price_b'])
            schema_json = create_schema(row)
            
            # 2. 渲染 HTML (SaaS 风格布局)
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{row['tool_a']} vs {row['tool_b']}: 2026 Pricing & Feature Battle</title>
    <meta name="description" content="Stop overpaying. See why {row['winner']} beats {row['tool_b']} in our exclusive 2026 data analysis.">
    <script type="application/ld+json">{schema_json}</script>
    <style>
        body {{ font-family: -apple-system, sans-serif; line-height: 1.5; color: #111; max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        h1 {{ font-size: 2.5rem; letter-spacing: -1px; margin-bottom: 10px; }}
        .badge {{ background: #f3f4f6; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; color: #666; }}
        .chart-box {{ margin: 40px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-radius: 12px; overflow: hidden; }}
        .cta-box {{ background: #111; color: white; padding: 30px; border-radius: 12px; text-align: center; margin-top: 40px; }}
        .btn {{ background: #D946EF; color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.2rem; display: inline-block; margin-top: 15px; }}
        .vs-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .vs-table td {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
        .winner-text {{ color: #22c55e; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <span class="badge">UPDATED: {datetime.date.today()}</span>
        <h1>{row['tool_a']} <span style="color:#ccc">vs</span> {row['tool_b']}</h1>
        <p>Data-driven comparison for smart founders.</p>
    </div>

    <!-- 动态 SVG 图表 -->
    <div class="chart-box">
        {svg_chart}
    </div>

    <!-- 核心对比表 -->
    <table class="vs-table">
        <tr>
            <td><strong>Monthly Price</strong></td>
            <td class="winner-text">${row['price_a']}</td>
            <td>${row['price_b']}</td>
        </tr>
        <tr>
            <td><strong>User Score</strong></td>
            <td>{row['score_a']}/5.0</td>
            <td>{row['score_b']}/5.0</td>
        </tr>
        <tr>
            <td><strong>Best Feature</strong></td>
            <td>{row['feature_a']}</td>
            <td>{row['feature_b']}</td>
        </tr>
    </table>

    <!-- 变现区 -->
    <div class="cta-box">
        <h2>🏆 The Winner: {row['winner']}</h2>
        <p>Save money without sacrificing features.</p>
        <a href="{row['link']}" class="btn">👉 Get {row['winner']} Deal</a>
        <p style="font-size:0.8rem; margin-top:15px; opacity:0.6">We verify prices daily. Affiliate links support our research.</p>
    </div>
</body>
</html>
            """
            
            # 3. 写入文件 (结构: dist/slug/index.html)
            slug_dir = os.path.join(OUTPUT_DIR, row['slug'])
            if not os.path.exists(slug_dir): os.makedirs(slug_dir)
            with open(os.path.join(slug_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)
            
            count += 1
            print(f"✅ [生成完毕] {row['slug']} - SVG图表已绘制 - Schema已注入")

    print(f"\n🎉 任务完成！共生成 {count} 个页面。准备上传 Cloudflare！")

if __name__ == "__main__":
    main()