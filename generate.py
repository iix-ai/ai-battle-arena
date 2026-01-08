import csv
import os
import json
import datetime
import random

# ==========================================
# 1. 帝国级配置 (Configuration)
# ==========================================
CSV_FILE = 'tools.csv'
OUTPUT_DIR = 'dist'
BASE_URL = 'https://compare.ii-x.com'
SITE_NAME = 'AI Tool Diff Engine'

# 多语言配置
LANGUAGES = {
    'en': {
        'flag': '🇺🇸', 'title': 'VS', 'price': 'Monthly Cost', 'winner': 'Winner', 
        'save': 'Yearly Savings', 'visit': 'Get Deal', 
        'calc_title': '💰 ROI Calculator', 'input_label': 'Team Size:', 'calc_btn': 'Calculate Savings',
        'email_title': 'Download Full 2026 AI Report', 'email_desc': 'Get the PDF with 50+ tool comparisons.', 'email_btn': 'Send to me',
        'related': '🔥 People Also Compare',
        'badge_value': '🏆 Best Value', 'badge_power': '🚀 Top Performance',
        'verdict_intro': 'Our Verdict:', 'verdict_value': 'Great for startups & freelancers.', 'verdict_power': 'Best for large enterprises.'
    },
    'es': {
        'flag': '🇪🇸', 'title': 'VS', 'price': 'Costo Mensual', 'winner': 'Ganador', 
        'save': 'Ahorro Anual', 'visit': 'Ver Oferta', 
        'calc_title': '💰 Calculadora ROI', 'input_label': 'Equipo:', 'calc_btn': 'Calcular', 
        'email_title': 'Descargar Reporte PDF', 'email_desc': 'Comparativa de 50 herramientas.', 'email_btn': 'Enviar',
        'related': '🔥 Comparaciones Relacionadas',
        'badge_value': '🏆 Mejor Valor', 'badge_power': '🚀 Máxima Potencia',
        'verdict_intro': 'Veredicto:', 'verdict_value': 'Ideal para startups.', 'verdict_power': 'Para grandes empresas.'
    },
    'de': {
        'flag': '🇩🇪', 'title': 'VS', 'price': 'Preis', 'winner': 'Gewinner', 
        'save': 'Sparen', 'visit': 'Webseite', 
        'calc_title': 'ROI-Rechner', 'input_label': 'Teamgröße:', 'calc_btn': 'Berechnen', 
        'email_title': 'Bericht herunterladen', 'email_desc': 'PDF mit 50+ Tools.', 'email_btn': 'Senden',
        'related': '🔥 Ähnliche Vergleiche',
        'badge_value': '🏆 Bester Wert', 'badge_power': '🚀 Top Leistung',
        'verdict_intro': 'Urteil:', 'verdict_value': 'Ideal für Startups.', 'verdict_power': 'Für große Unternehmen.'
    },
    'fr': {
        'flag': '🇫🇷', 'title': 'VS', 'price': 'Prix', 'winner': 'Gagnant', 
        'save': 'Économisez', 'visit': 'Visiter', 
        'calc_title': 'Calculateur ROI', 'input_label': 'Équipe :', 'calc_btn': 'Calculer', 
        'email_title': 'Télécharger le rapport', 'email_desc': 'PDF avec 50+ outils.', 'email_btn': 'Envoyer',
        'related': '🔥 Comparaisons Similaires',
        'badge_value': '🏆 Meilleure Valeur', 'badge_power': '🚀 Haute Performance',
        'verdict_intro': 'Verdict:', 'verdict_value': 'Idéal pour les startups.', 'verdict_power': 'Pour les grandes entreprises.'
    },
    'pt': {
        'flag': '🇧🇷', 'title': 'VS', 'price': 'Preço', 'winner': 'Vencedor', 
        'save': 'Economize', 'visit': 'Visitar', 
        'calc_title': 'Calculadora ROI', 'input_label': 'Equipe:', 'calc_btn': 'Calcular', 
        'email_title': 'Baixar Relatório', 'email_desc': 'PDF com 50+ ferramentas.', 'email_btn': 'Enviar',
        'related': '🔥 Também Comparado',
        'badge_value': '🏆 Melhor Valor', 'badge_power': '🚀 Desempenho Máximo',
        'verdict_intro': 'Veredito:', 'verdict_value': 'Ideal para startups.', 'verdict_power': 'Para grandes empresas.'
    }
}

# ==========================================
# 2. 核心功能模块
# ==========================================

def clean_price(price_str):
    """清洗价格数据"""
    try:
        return float(str(price_str).replace('$','').replace(',','').strip())
    except:
        return 0.0

def create_svg_chart(name_a, price_a, name_b, price_b):
    """生成 SVG 图表 (修复版：拆分赋值，防止Tuple报错)"""
    pa = clean_price(price_a)
    pb = clean_price(price_b)
    
    if pa == 0 and pb == 0: 
        return ""

    max_h = max(pa, pb) * 1.2
    
    # 核心修复：强制转float，并拆行写，杜绝逗号隐患
    h_a = float((pa / max_h) * 200)
    h_b = float((pb / max_h) * 200)
    
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
    """生成多语言结构化数据"""
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

def generate_internal_links(all_rows, current_slug, lang, texts):
    """生成内链"""
    others = [r for r in all_rows if r['slug'] != current_slug]
    if not others: return ""
    
    # 防止样本不足报错
    sample_size = min(6, len(others))
    if sample_size == 0: return ""
    
    picks = random.sample(others, sample_size)
    
    prefix = "" if lang == 'en' else f"/{lang}"
    
    links_html = f'<div class="internal-links"><h3>{texts["related"]}</h3><div class="links-grid">'
    for p in picks:
        links_html += f'<a href="{prefix}/{p["slug"]}/">{p["tool_a"]} vs {p["tool_b"]}</a>'
    links_html += '</div></div>'
    return links_html

def generate_sitemap_and_robots(urls):
    """生成 Sitemap 和 Robots"""
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        sitemap += f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{datetime.date.today()}</lastmod>\n    <changefreq>daily</changefreq>\n  </url>\n'
    sitemap += '</urlset>'
    with open(os.path.join(OUTPUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap)
    
    robots = f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml"
    with open(os.path.join(OUTPUT_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(robots)
    print("✅ [SEO] sitemap.xml & robots.txt Generated")

def determine_verdict(row, texts):
    """智能裁决逻辑"""
    pa = clean_price(row['price_a'])
    pb = clean_price(row['price_b'])
    price_diff = abs(pa - pb)
    
    if pa < pb:
        badge = texts['badge_value']
        reason = f"{texts['save']} <strong>${price_diff * 12}</strong>/year. {texts['verdict_value']}"
        winner_class = "winner-value"
    else:
        badge = texts['badge_power']
        reason = texts['verdict_power']
        winner_class = "winner-power"
        
    return badge, reason, winner_class, price_diff * 12

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    try:
        all_rows = list(csv.DictReader(open(CSV_FILE, 'r', encoding='utf-8')))
    except:
        print("❌ CSV Not Found!")
        return

    generated_urls = [BASE_URL]
    
    target_langs = ['en', 'es', 'de', 'fr', 'pt']

    for lang in target_langs:
        print(f"🌍 Building: {lang.upper()}")
        texts = LANGUAGES.get(lang, LANGUAGES['en'])
        
        lang_dir = os.path.join(OUTPUT_DIR, lang) if lang != 'en' else OUTPUT_DIR
        if not os.path.exists(lang_dir): os.makedirs(lang_dir)
        
        index_links = ""

        for row in all_rows:
            badge, reason, win_class, yearly_save = determine_verdict(row, texts)
            svg_chart = create_svg_chart(row['tool_a'], row['price_a'], row['tool_b'], row['price_b'])
            schema_json = create_schema(row, lang)
            
            prefix = "" if lang == 'en' else f"/{lang}"
            internal_links = generate_internal_links(all_rows, row['slug'], lang, texts)
            
            slug = row['slug']
            page_dir = os.path.join(lang_dir, slug)
            if not os.path.exists(page_dir): os.makedirs(page_dir)
            
            full_url = f"{BASE_URL}{prefix}/{slug}/"
            generated_urls.append(full_url)

            index_links += f'''<a href="{prefix}/{slug}/" class="card"><div class="card-head">{row['tool_a']} <span style="opacity:0.5">vs</span> {row['tool_b']}</div><div class="card-badge">{badge}</div></a>'''

            html = f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{row['tool_a']} vs {row['tool_b']} | {SITE_NAME}</title>
    <meta name="description" content="{texts['title']}: {row['tool_a']} vs {row['tool_b']}. {texts['winner']}: {row['winner']}.">
    <script type="application/ld+json">{schema_json}</script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #000; --accent: #2563eb; --bg: #f8fafc; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: #1e293b; margin: 0; padding-bottom: 50px; line-height: 1.6; }}
        .nav {{ background: white; padding: 15px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-weight: 900; font-size: 1.2rem; text-decoration: none; color: var(--primary); }}
        .btn-login {{ font-size: 0.9rem; color: #64748b; text-decoration: none; font-weight: 600; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin: 40px 0; }}
        .badge {{ background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 99px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }}
        h1 {{ font-size: 2.5rem; letter-spacing: -1px; margin: 15px 0; }}
        .chart-box {{ margin: 40px 0; }}
        .verdict-box {{ padding: 25px; border-radius: 12px; margin: 30px 0; border-left: 5px solid; }}
        .winner-value {{ background: #f0fdf4; border-color: #22c55e; }} 
        .winner-power {{ background: #fdf2f8; border-color: #db2777; }} 
        .verdict-title {{ font-weight: 800; font-size: 1.2rem; margin-bottom: 10px; display: block; }}
        .calculator {{ background: #1e293b; color: white; padding: 30px; border-radius: 16px; margin: 40px 0; box-shadow: 0 20px 40px rgba(0,0,0,0.2); }}
        .calc-flex {{ display: flex; gap: 20px; align-items: flex-end; }}
        .calc-input {{ flex: 1; }}
        .calc-input label {{ display: block; font-size: 0.9rem; margin-bottom: 8px; opacity: 0.8; }}
        .calc-input input {{ width: 100%; padding: 12px; border-radius: 8px; border: none; font-size: 1.1rem; }}
        .calc-res {{ font-size: 1.5rem; font-weight: 800; color: #4ade80; margin-top: 20px; display: none; }}
        .vs-table {{ width: 100%; background: white; border-radius: 12px; border-collapse: collapse; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        .vs-table td {{ padding: 20px; border-bottom: 1px solid #f1f5f9; }}
        .cta-box {{ text-align: center; margin-top: 50px; }}
        .btn-main {{ background: var(--accent); color: white; padding: 18px 40px; border-radius: 12px; text-decoration: none; font-weight: 700; font-size: 1.2rem; display: inline-block; transition: 0.2s; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2); }}
        .email-box {{ background: #fff; border: 2px dashed #cbd5e1; padding: 30px; border-radius: 12px; margin-top: 50px; text-align: center; }}
        .email-input {{ padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1; width: 60%; margin-right: 10px; }}
        .email-btn {{ padding: 10px 20px; background: #0f172a; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }}
        .internal-links {{ margin-top: 60px; padding-top: 30px; border-top: 2px solid #e2e8f0; }}
        .links-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }}
        .links-grid a {{ background: white; padding: 10px 15px; border-radius: 6px; text-decoration: none; color: #475569; font-size: 0.9rem; border: 1px solid #e2e8f0; transition: 0.2s; }}
        .links-grid a:hover {{ border-color: var(--accent); color: var(--accent); }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="/" class="logo">⚡ {SITE_NAME}</a>
        <div><span style="margin-right: 15px">{texts['flag']}</span><a href="#" class="btn-login">Log In</a></div>
    </nav>
    <div class="container">
        <div class="header">
            <span class="badge">Live Data 2026</span>
            <h1>{row['tool_a']} <span style="color:#cbd5e1">vs</span> {row['tool_b']}</h1>
            <p>Data-driven analysis for decision makers.</p>
        </div>
        
        <div class="chart-box">{svg_chart}</div>
        
        <div class="verdict-box {win_class}">
            <span class="verdict-title">{badge}</span>
            <p>{texts['verdict_intro']} <strong>{reason}</strong></p>
        </div>

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
                const yearlySave = {yearly_save};
                const total = (yearlySave / 12) * months;
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').innerText = '{texts['save']} $' + total.toFixed(0) + '!';
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

        <div class="email-box">
            <h3>{texts['email_title']}</h3>
            <p>{texts['email_desc']}</p>
            <form onsubmit="alert('Thank you! Report sent.'); return false;">
                <input type="email" placeholder="Email" class="email-input" required>
                <button type="submit" class="email-btn">{texts['email_btn']}</button>
            </form>
        </div>

        {internal_links}
    </div>
</body>
</html>
            """
            
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)

        lang_home_html = f"""<!DOCTYPE html><html lang="{lang}"><head><meta charset="UTF-8"><title>{SITE_NAME} ({lang.upper()})</title><style>body{{font-family:sans-serif;max-width:900px;margin:0 auto;padding:40px;background:#f8fafc}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:15px}}.card{{background:white;padding:20px;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:inherit;display:block}}.card:hover{{border-color:#2563eb}}.card-head{{font-weight:bold;margin-bottom:5px}}.card-badge{{font-size:0.8rem;color:#22c55e;font-weight:600}}</style></head><body><h1>⚡ {SITE_NAME} [{texts['flag']}]</h1><div class="grid">{index_links}</div></body></html>"""
        with open(os.path.join(lang_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(lang_home_html)

    generate_sitemap_and_robots(generated_urls)
    print("\n🚀 [V7.2 稳健版] 生成完成。无元组错误。")

if __name__ == "__main__":
    main()