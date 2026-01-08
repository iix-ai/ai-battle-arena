import csv
import os
import json
import datetime

# ==========================================
# 1. 帝国级配置 (Empire Configuration)
# ==========================================
CSV_FILE = 'tools.csv'
OUTPUT_DIR = 'dist'
BASE_URL = 'https://compare.ii-x.com' # 您的最终域名
SITE_NAME = 'AI Tool Diff Engine'

# 支持的语言矩阵 (流量扩大5倍)
LANGUAGES = {
    'en': {'flag': '🇺🇸', 'title': 'Comparison', 'price': 'Price', 'winner': 'Winner', 'save': 'Save', 'visit': 'Visit Site', 'calc_title': 'ROI Calculator: How much will you save?', 'input_label': 'Months to use:', 'calc_btn': 'Calculate Savings'},
    'es': {'flag': '🇪🇸', 'title': 'Comparación', 'price': 'Precio', 'winner': 'Ganador', 'save': 'Ahorra', 'visit': 'Visitar Sitio', 'calc_title': 'Calculadora ROI: ¿Cuánto ahorrarás?', 'input_label': 'Meses de uso:', 'calc_btn': 'Calcular Ahorro'},
    'de': {'flag': '🇩🇪', 'title': 'Vergleich', 'price': 'Preis', 'winner': 'Gewinner', 'save': 'Sparen', 'visit': 'Webseite', 'calc_title': 'ROI-Rechner: Wie viel sparen Sie?', 'input_label': 'Nutzungsmonate:', 'calc_btn': 'Ersparnis berechnen'},
    'fr': {'flag': '🇫🇷', 'title': 'Comparaison', 'price': 'Prix', 'winner': 'Gagnant', 'save': 'Économisez', 'visit': 'Visiter', 'calc_title': 'Calculateur ROI : Combien économiserez-vous ?', 'input_label': 'Mois d\'utilisation :', 'calc_btn': 'Calculer'},
    'pt': {'flag': '🇧🇷', 'title': 'Comparação', 'price': 'Preço', 'winner': 'Vencedor', 'save': 'Economize', 'visit': 'Visitar', 'calc_title': 'Calculadora ROI: Quanto você vai economizar?', 'input_label': 'Meses de uso:', 'calc_btn': 'Calcular Economia'}
}

# ==========================================
# 2. 核心功能模块
# ==========================================

def clean_price(price_str):
    """清洗价格数据，确保是纯数字"""
    try:
        return float(str(price_str).replace('$','').replace(',','').strip())
    except:
        return 0.0

def create_svg_chart(name_a, price_a, name_b, price_b):
    """生成带有语义化标签的高端 SVG 图表"""
    pa, pb = clean_price(price_a), clean_price(price_b)
    if pa == 0 and pb == 0: return ""

    max_h = max(pa, pb) * 1.2
    h_a, h_b = (pa/max_h)*200, (pb/max_h)*200
    c_a = "#22c55e" if pa < pb else "#ef4444"
    c_b = "#22c55e" if pb < pa else "#ef4444"
    
    diff = abs(pa - pb)
    
    return f'''
    <svg width="100%" height="280" viewBox="0 0 400 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" style="background:white; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.05); padding:20px;">
        <title id="title">Price Chart: {name_a} vs {name_b}</title>
        <desc id="desc">Visual comparison showing {name_a} at ${pa} and {name_b} at ${pb}. Difference is ${diff}.</desc>
        <rect x="50" y="{250 - h_a}" width="100" height="{h_a}" fill="{c_a}" rx="6" />
        <text x="100" y="{240 - h_a}" text-anchor="middle" font-family="sans-serif" font-weight="800" font-size="18" fill="#374151">${pa}</text>
        <text x="100" y="270" text-anchor="middle" font-family="sans-serif" fill="#6b7280" font-size="14">{name_a}</text>
        <rect x="250" y="{250 - h_b}" width="100" height="{h_b}" fill="{c_b}" rx="6" />
        <text x="300" y="{240 - h_b}" text-anchor="middle" font-family="sans-serif" font-weight="800" font-size="18" fill="#374151">${pb}</text>
        <text x="300" y="270" text-anchor="middle" font-family="sans-serif" fill="#6b7280" font-size="14">{name_b}</text>
    </svg>
    '''

def create_schema(row, lang):
    """生成多语言结构化数据，霸占 Google 结果位"""
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"{row['tool_a']} vs {row['tool_b']}",
        "description": f"{LANGUAGES[lang]['title']}: {row['tool_a']} vs {row['tool_b']}. {LANGUAGES[lang]['winner']}: {row['winner']}.",
        "brand": {"@type": "Brand", "name": SITE_NAME},
        "review": {"@type": "Review", "reviewRating": {"@type": "Rating", "ratingValue": "4.9", "bestRating": "5"}, "author": {"@type": "Organization", "name": SITE_NAME}},
        "offers": {"@type": "Offer", "price": str(clean_price(row['price_a'])), "priceCurrency": "USD"}
    }
    return json.dumps(schema)

def generate_sitemap(urls):
    """自动生成 sitemap.xml，主动喂给 Google"""
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        sitemap += f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{datetime.date.today()}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    sitemap += '</urlset>'
    with open(os.path.join(OUTPUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap)
    print("✅ [SEO] sitemap.xml Generated")

# ==========================================
# 3. 页面生成主逻辑
# ==========================================
def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    all_rows = []
    generated_urls = []

    # 读取数据
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_rows.append(row)
    except:
        print("❌ CSV Not Found!")
        return

    # 循环语言 -> 循环数据 -> 生成页面
    for lang, texts in LANGUAGES.items():
        print(f"🌍 Starting build for language: {lang.upper()}")
        
        # 语言子目录
        lang_dir = os.path.join(OUTPUT_DIR, lang) if lang != 'en' else OUTPUT_DIR # 英语在根目录
        if not os.path.exists(lang_dir): os.makedirs(lang_dir)

        # 生成该语言的首页索引
        index_links = ""
        
        for row in all_rows:
            # 数据处理
            pa, pb = clean_price(row['price_a']), clean_price(row['price_b'])
            diff = abs(pa - pb)
            winner_tool = row['winner']
            
            # 生成各个组件
            svg_chart = create_svg_chart(row['tool_a'], row['price_a'], row['tool_b'], row['price_b'])
            schema_json = create_schema(row, lang)
            
            # 路径处理
            slug = row['slug']
            page_dir = os.path.join(lang_dir, slug)
            if not os.path.exists(page_dir): os.makedirs(page_dir)
            
            # 收集 Sitemap URL
            full_url = f"{BASE_URL}/{slug}/" if lang == 'en' else f"{BASE_URL}/{lang}/{slug}/"
            generated_urls.append(full_url)

            # 首页链接卡片
            index_links += f'''
            <a href="{slug}/" class="card">
                <div class="card-head">{row['tool_a']} <span style="opacity:0.5">vs</span> {row['tool_b']}</div>
                <div class="card-win">{texts['winner']}: {row['winner']}</div>
            </a>'''

            # === HTML 模版 (SaaS 级 + 交互计算器) ===
            html = f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{row['tool_a']} vs {row['tool_b']} | {SITE_NAME}</title>
    <meta name="description" content="{texts['title']}: {row['tool_a']} vs {row['tool_b']}. Live data analysis.">
    <script type="application/ld+json">{schema_json}</script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #000; --accent: #2563eb; --bg: #f8fafc; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: #1e293b; margin: 0; padding-bottom: 50px; }}
        .nav {{ background: white; padding: 15px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-weight: 900; font-size: 1.2rem; text-decoration: none; color: var(--primary); }}
        .btn-login {{ font-size: 0.9rem; color: #64748b; text-decoration: none; font-weight: 600; }}
        
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin: 40px 0; }}
        .badge {{ background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 99px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }}
        h1 {{ font-size: 2.8rem; letter-spacing: -1px; margin: 15px 0; }}
        
        /* 交互计算器样式 */
        .calculator {{ background: #1e293b; color: white; padding: 30px; border-radius: 16px; margin: 40px 0; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }}
        .calc-flex {{ display: flex; gap: 20px; align-items: flex-end; }}
        .calc-input {{ flex: 1; }}
        .calc-input label {{ display: block; font-size: 0.9rem; margin-bottom: 8px; opacity: 0.8; }}
        .calc-input input {{ width: 100%; padding: 12px; border-radius: 8px; border: none; font-size: 1.1rem; }}
        .calc-res {{ font-size: 1.5rem; font-weight: 800; color: #4ade80; margin-top: 20px; display: none; }}
        
        .chart-box {{ margin: 40px 0; }}
        .vs-table {{ width: 100%; background: white; border-radius: 12px; border-collapse: collapse; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        .vs-table td {{ padding: 20px; border-bottom: 1px solid #f1f5f9; }}
        .vs-table tr:last-child td {{ border-bottom: none; }}
        
        .cta-box {{ text-align: center; margin-top: 50px; }}
        .btn-main {{ background: var(--accent); color: white; padding: 18px 40px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 1.2rem; display: inline-block; transition: 0.2s; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2); }}
        .btn-main:hover {{ transform: translateY(-2px); box-shadow: 0 15px 30px rgba(37, 99, 235, 0.3); }}
    </style>
</head>
<body>
    <!-- SaaS 伪装导航栏 -->
    <nav class="nav">
        <a href="/" class="logo">⚡ {SITE_NAME}</a>
        <div>
            <span style="margin-right: 15px">{texts['flag']}</span>
            <a href="#" class="btn-login">Log In</a>
        </div>
    </nav>

    <div class="container">
        <div class="header">
            <span class="badge">Live Data 2026</span>
            <h1>{row['tool_a']} <span style="color:#cbd5e1">vs</span> {row['tool_b']}</h1>
            <p>Data-driven analysis for decision makers.</p>
        </div>

        <div class="chart-box">
            {svg_chart}
        </div>

        <!-- 核心武器：JS 交互计算器 -->
        <div class="calculator">
            <h3>🧮 {texts['calc_title']}</h3>
            <div class="calc-flex">
                <div class="calc-input">
                    <label>{texts['input_label']}</label>
                    <input type="number" id="months" value="12" min="1">
                </div>
                <button onclick="calculate()" style="background:#4ade80; color:#064e3b; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer">{texts['calc_btn']}</button>
            </div>
            <div id="result" class="calc-res"></div>
        </div>

        <script>
            function calculate() {{
                const months = document.getElementById('months').value;
                const diff = {diff};
                const total = diff * months;
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').innerText = '{texts['save']} $' + total + '!';
            }}
        </script>

        <table class="vs-table">
            <tr><td><strong>{texts['price']}</strong></td><td style="color:var(--accent); font-weight:bold">${row['price_a']}</td><td>${row['price_b']}</td></tr>
            <tr><td><strong>Score</strong></td><td>{row['score_a']}/5.0</td><td>{row['score_b']}/5.0</td></tr>
            <tr><td><strong>Feature</strong></td><td>{row['feature_a']}</td><td>{row['feature_b']}</td></tr>
        </table>

        <div class="cta-box">
            <h2 style="margin-bottom: 20px">{texts['winner']}: {row['winner']}</h2>
            <a href="{row['link']}" class="btn-main">👉 {texts['visit']} {row['winner']}</a>
            <p style="margin-top:20px; font-size:0.8rem; color:#94a3b8">Official Affiliate Partner</p>
        </div>
    </div>
</body>
</html>
            """
            
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)

        # 生成该语言的首页
        lang_home_html = f"""<!DOCTYPE html><html lang="{lang}"><head><meta charset="UTF-8"><title>{SITE_NAME} ({lang.upper()})</title><style>body{{font-family:sans-serif;max-width:800px;margin:0 auto;padding:40px;background:#f8fafc}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:15px}}.card{{background:white;padding:20px;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:inherit;display:block}}.card:hover{{border-color:#2563eb}}.card-head{{font-weight:bold;margin-bottom:5px}}.card-win{{font-size:0.8rem;color:#22c55e}}</style></head><body><h1>🌐 {SITE_NAME} [{texts['flag']}]</h1><div class="grid">{index_links}</div></body></html>"""
        with open(os.path.join(lang_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(lang_home_html)

    # 最后生成 Sitemap
    generate_sitemap(generated_urls)
    print("\n🚀 [帝国版] 构建完成！多语言 + 计算器 + Sitemap 已就绪。")

if __name__ == "__main__":
    main()