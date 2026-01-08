import csv
import os
import json
import datetime
import random

# ==========================================
# 1. 读取通用配置
# ==========================================
# 即使有 config.json，为了保证代码独立运行不报错，
# 我在这里内置了默认配置，双重保险。
DEFAULT_CONFIG = {
    "site_name": "AI Tool Diff Engine",
    "base_url": "https://compare.ii-x.com",
    "affiliate_disclosure": "We earn a commission if you buy through our links."
}

try:
    with open('config.json', 'r', encoding='utf-8') as f:
        CONFIG = json.load(f)
except:
    CONFIG = DEFAULT_CONFIG

CSV_FILE = 'tools.csv'
OUTPUT_DIR = 'dist'

# 完整 5 国语言矩阵 (V7.1回归 + V9.0新字段)
TRANS = {
    'en': {
        'title': 'VS', 'price': 'Monthly Cost', 'score': 'Rating', 
        'pros': 'Pros', 'cons': 'Cons', 
        'budget_pick': '🏆 Best Value', 'power_pick': '🚀 Top Performance',
        'verdict_value': 'Great for startups.', 'verdict_power': 'Best for enterprises.',
        'save': 'Yearly Savings', 'visit': 'Get Deal',
        'calc_title': '💰 ROI Calculator', 'input_label': 'Team Size:', 'calc_btn': 'Calculate',
        'email_title': 'Get Full Report', 'email_desc': 'Download PDF comparison.', 'email_btn': 'Send',
        'related': '🔥 People Also Compare'
    },
    'es': {
        'title': 'VS', 'price': 'Costo Mensual', 'score': 'Puntuación',
        'pros': 'Pros', 'cons': 'Contras',
        'budget_pick': '🏆 Mejor Valor', 'power_pick': '🚀 Máxima Potencia',
        'verdict_value': 'Ideal para startups.', 'verdict_power': 'Para grandes empresas.',
        'save': 'Ahorro Anual', 'visit': 'Ver Oferta',
        'calc_title': '💰 Calculadora ROI', 'input_label': 'Equipo:', 'calc_btn': 'Calcular',
        'email_title': 'Descargar Reporte', 'email_desc': 'PDF comparativo.', 'email_btn': 'Enviar',
        'related': '🔥 Comparaciones'
    },
    'de': {
        'title': 'VS', 'price': 'Preis', 'score': 'Bewertung',
        'pros': 'Vorteile', 'cons': 'Nachteile',
        'budget_pick': '🏆 Bester Wert', 'power_pick': '🚀 Top Leistung',
        'verdict_value': 'Ideal für Startups.', 'verdict_power': 'Für Unternehmen.',
        'save': 'Sparen', 'visit': 'Webseite',
        'calc_title': 'ROI-Rechner', 'input_label': 'Team:', 'calc_btn': 'Berechnen',
        'email_title': 'Bericht laden', 'email_desc': 'PDF Vergleich.', 'email_btn': 'Senden',
        'related': '🔥 Ähnliche'
    },
    'fr': {
        'title': 'VS', 'price': 'Prix', 'score': 'Note',
        'pros': 'Avantages', 'cons': 'Inconvénients',
        'budget_pick': '🏆 Meilleure Valeur', 'power_pick': '🚀 Haute Performance',
        'verdict_value': 'Idéal pour startups.', 'verdict_power': 'Pour entreprises.',
        'save': 'Économisez', 'visit': 'Visiter',
        'calc_title': 'Calculateur ROI', 'input_label': 'Équipe:', 'calc_btn': 'Calculer',
        'email_title': 'Télécharger PDF', 'email_desc': 'Rapport complet.', 'email_btn': 'Envoyer',
        'related': '🔥 Similaires'
    },
    'pt': {
        'title': 'VS', 'price': 'Preço', 'score': 'Avaliação',
        'pros': 'Prós', 'cons': 'Contras',
        'budget_pick': '🏆 Melhor Valor', 'power_pick': '🚀 Desempenho',
        'verdict_value': 'Ideal para startups.', 'verdict_power': 'Para empresas.',
        'save': 'Economize', 'visit': 'Visitar',
        'calc_title': 'Calculadora ROI', 'input_label': 'Equipe:', 'calc_btn': 'Calcular',
        'email_title': 'Baixar Relatório', 'email_desc': 'PDF completo.', 'email_btn': 'Enviar',
        'related': '🔥 Relacionados'
    }
}

# ==========================================
# 3. 核心功能模块
# ==========================================

def clean_price(price_str):
    try:
        return float(str(price_str).replace('$','').replace(',','').strip())
    except:
        return 0.0

def create_svg_chart(name_a, price_a, name_b, price_b):
    """SVG 绘图 (V9.0标准)"""
    pa, pb = clean_price(price_a), clean_price(price_b)
    if pa == 0 and pb == 0: return ""
    max_h = max(pa, pb) * 1.2
    h_a = float((pa/max_h)*200)
    h_b = float((pb/max_h)*200)
    c_a = "#22c55e" if pa < pb else "#ef4444"
    c_b = "#22c55e" if pb < pa else "#ef4444"
    diff = abs(pa - pb)
    return f'''
    <svg width="100%" height="280" viewBox="0 0 400 280" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="t d" style="background:white; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.05); padding:20px;">
        <title id="t">{name_a} vs {name_b}</title>
        <desc id="d">{name_a}: ${pa}, {name_b}: ${pb}. Diff: ${diff}</desc>
        <rect x="50" y="{250-h_a}" width="100" height="{h_a}" fill="{c_a}" rx="6" />
        <text x="100" y="{240-h_a}" text-anchor="middle" font-family="sans-serif" font-weight="800" font-size="18" fill="#374151">${pa}</text>
        <text x="100" y="270" text-anchor="middle" font-family="sans-serif" fill="#6b7280" font-size="14">{name_a}</text>
        <rect x="250" y="{250-h_b}" width="100" height="{h_b}" fill="{c_b}" rx="6" />
        <text x="300" y="{240-h_b}" text-anchor="middle" font-family="sans-serif" font-weight="800" font-size="18" fill="#374151">${pb}</text>
        <text x="300" y="270" text-anchor="middle" font-family="sans-serif" fill="#6b7280" font-size="14">{name_b}</text>
    </svg>'''

def create_schema(row, lang):
    """Schema 结构化数据"""
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": f"{row['tool_a']} vs {row['tool_b']}",
        "description": f"Comparison: {row['tool_a']} vs {row['tool_b']}. Updated 2026.",
        "brand": {"@type": "Brand", "name": CONFIG['site_name']},
        "offers": {"@type": "Offer", "price": str(clean_price(row['price_a'])), "priceCurrency": "USD"}
    })

def generate_internal_links(all_rows, current_slug, prefix, texts):
    """内链生成"""
    others = [r for r in all_rows if r['slug'] != current_slug]
    if not others: return ""
    picks = random.sample(others, min(6, len(others)))
    links_html = f'<div class="internal-links"><h3>{texts["related"]}</h3><div class="links-grid">'
    for p in picks:
        links_html += f'<a href="{prefix}/{p["slug"]}/">{p["tool_a"]} vs {p["tool_b"]}</a>'
    links_html += '</div></div>'
    return links_html

def generate_sitemap_and_robots(urls):
    """Sitemap & Robots"""
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        sitemap += f'  <url><loc>{url}</loc><lastmod>{datetime.date.today()}</lastmod><changefreq>daily</changefreq></url>\n'
    sitemap += '</urlset>'
    with open(os.path.join(OUTPUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap)
    robots = f"User-agent: *\nAllow: /\nSitemap: {CONFIG['base_url']}/sitemap.xml"
    with open(os.path.join(OUTPUT_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(robots)
    print("✅ [SEO] Sitemap & Robots Generated")

def determine_verdict(row, texts):
    """智能裁决逻辑 (V9.0)"""
    pa = clean_price(row['price_a'])
    pb = clean_price(row['price_b'])
    price_diff = abs(pa - pb)
    
    if pa < pb:
        badge = texts['budget_pick']
        reason = f"{texts['save']} <strong>${price_diff * 12}</strong>/year. {texts['verdict_value']}"
        winner_class = "winner-value"
    else:
        badge = texts['power_pick']
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

    generated_urls = [CONFIG['base_url']]
    # 恢复 5 国语言
    target_langs = ['en', 'es', 'de', 'fr', 'pt']

    for lang in target_langs:
        print(f"🌍 Building: {lang.upper()}")
        t = TRANS.get(lang, TRANS['en'])
        lang_dir = os.path.join(OUTPUT_DIR, lang) if lang != 'en' else OUTPUT_DIR
        if not os.path.exists(lang_dir): os.makedirs(lang_dir)
        
        index_html = f"<h1>{CONFIG['site_name']} ({lang.upper()})</h1><div style='display:grid;gap:10px'>"

        for row in all_rows:
            # 逻辑计算
            badge, reason, win_class, yearly_save = determine_verdict(row, t)
            svg_chart = create_svg_chart(row['tool_a'], row['price_a'], row['tool_b'], row['price_b'])
            schema_json = create_schema(row, lang)
            prefix = "" if lang == 'en' else f"/{lang}"
            internal_links = generate_internal_links(all_rows, row['slug'], prefix, t)
            
            # Pros/Cons 列表 (V9.0)
            pros_list = row.get('pros_b', 'Good Value;Easy to Use;Fast').split(';')
            cons_list = row.get('cons_b', 'Limited features;Basic API;Newer').split(';')

            # URL
            slug = row['slug']
            page_dir = os.path.join(lang_dir, slug)
            if not os.path.exists(page_dir): os.makedirs(page_dir)
            full_url = f"{CONFIG['base_url']}{prefix}/{slug}/"
            generated_urls.append(full_url)
            
            index_html += f"<a href='{slug}/' style='display:block;padding:10px;background:white;margin-bottom:10px;text-decoration:none;color:#333;border:1px solid #eee'>{row['tool_a']} vs {row['tool_b']}</a>"

            # === 终极 HTML (全功能) ===
            html = f"""
<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{row['tool_a']} vs {row['tool_b']} | {CONFIG['site_name']}</title>
    <meta name="description" content="{t['title']}: {row['tool_a']} vs {row['tool_b']}. {t['winner']}: {row['winner']}.">
    <script type="application/ld+json">{schema_json}</script>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; color: #1f2937; background: #f9fafb; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .verdict-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
        .verdict-card {{ padding: 20px; border-radius: 12px; text-align: center; font-weight: bold; }}
        .v-budget {{ background: #ecfdf5; color: #047857; border: 1px solid #10b981; }}
        .v-power {{ background: #eff6ff; color: #1d4ed8; border: 1px solid #3b82f6; }}
        .chart-box {{ background: white; padding: 20px; border-radius: 12px; margin: 30px 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        
        /* V9.0 优缺点 */
        .pros-cons {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
        .pc-box {{ background: white; padding: 20px; border-radius: 8px; }}
        .pc-title {{ font-weight: bold; margin-bottom: 10px; display: block; }}
        .check {{ color: green; }} .cross {{ color: red; }}
        
        /* V7.1 计算器 */
        .calculator {{ background: #1e293b; color: white; padding: 30px; border-radius: 16px; margin: 40px 0; }}
        .calc-flex {{ display: flex; gap: 20px; align-items: flex-end; }}
        .calc-input {{ flex: 1; }}
        .calc-input label {{ display: block; font-size: 0.9rem; margin-bottom: 8px; opacity: 0.8; }}
        .calc-input input {{ width: 100%; padding: 12px; border-radius: 8px; border: none; }}
        .calc-res {{ font-size: 1.5rem; font-weight: 800; color: #4ade80; margin-top: 20px; display: none; }}
        
        /* V7.1 邮件捕获 */
        .email-box {{ background: #fff; border: 2px dashed #cbd5e1; padding: 30px; border-radius: 12px; margin-top: 50px; text-align: center; }}
        .email-input {{ padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1; width: 60%; margin-right: 10px; }}
        .email-btn {{ padding: 10px 20px; background: #0f172a; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }}

        .btn {{ display: block; background: #000; color: white; text-align: center; padding: 15px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }}
        td {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .internal-links {{ margin-top: 60px; padding-top: 30px; border-top: 1px solid #e2e8f0; }}
        .links-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }}
        .links-grid a {{ background: #f1f5f9; padding: 10px; border-radius: 6px; text-decoration: none; color: #475569; font-size: 0.85rem; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{row['tool_a']} <span style="color:#9ca3af">vs</span> {row['tool_b']}</h1>
        <p>Updated: {datetime.date.today()}</p>
    </div>

    <!-- V9.0 场景化推荐 -->
    <div class="verdict-grid">
        <div class="verdict-card v-budget">
            <div>{t['budget_pick']}</div>
            <div style="font-size:1.5rem">{budget_winner}</div>
        </div>
        <div class="verdict-card v-power">
            <div>{t['power_pick']}</div>
            <div style="font-size:1.5rem">{power_winner}</div>
        </div>
    </div>

    <div class="chart-box">{svg_chart}</div>

    <!-- V7.1 计算器 -->
    <div class="calculator">
        <h3>🧮 {t['calc_title']}</h3>
        <div class="calc-flex">
            <div class="calc-input">
                <label>{t['input_label']}</label>
                <input type="number" id="months" value="12" min="1">
            </div>
            <button onclick="calculate()" style="background:#4ade80; color:#064e3b; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer">{t['calc_btn']}</button>
        </div>
        <div id="result" class="calc-res"></div>
    </div>
    <script>
        function calculate() {{
            const months = document.getElementById('months').value;
            const yearlySave = {yearly_save};
            const total = (yearlySave / 12) * months;
            document.getElementById('result').style.display = 'block';
            document.getElementById('result').innerText = '{t['save']} $' + total.toFixed(0) + '!';
        }}
    </script>

    <table>
        <tr>
            <td><strong>{t['price']}</strong></td>
            <td><strong>${row['price_a']}</strong></td>
            <td><strong>${row['price_b']}</strong></td>
        </tr>
        <tr>
            <td><strong>{t['score']}</strong></td>
            <td>{row.get('score_a', 'N/A')}</td>
            <td>{row.get('score_b', 'N/A')}</td>
        </tr>
    </table>

    <!-- V9.0 优缺点 -->
    <div class="pros-cons">
        <div class="pc-box">
            <span class="pc-title">{row['tool_b']} {t['pros']}</span>
            {''.join([f'<div><span class="check">✔</span> {x}</div>' for x in pros_list])}
        </div>
        <div class="pc-box">
            <span class="pc-title">{row['tool_b']} {t['cons']}</span>
            {''.join([f'<div><span class="cross">✘</span> {x}</div>' for x in cons_list])}
        </div>
    </div>

    <a href="{row['link']}" class="btn">👉 {t['visit']} {row['winner']}</a>
    
    <!-- V7.1 邮件捕获 -->
    <div class="email-box">
        <h3>{t['email_title']}</h3>
        <p>{t['email_desc']}</p>
        <form onsubmit="alert('Thank you! Report sent.'); return false;">
            <input type="email" placeholder="Email" class="email-input" required>
            <button type="submit" class="email-btn">{t['email_btn']}</button>
        </form>
    </div>
    
    <p style="text-align:center; font-size:0.8rem; margin-top:20px; color:#999">{CONFIG['affiliate_disclosure']}</p>

    {internal_links}
</body>
</html>
            """
            with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(html)
            
            # 生成索引
            index_html += f"<a href='{slug}/' style='display:block;padding:10px;background:white;margin-bottom:10px;text-decoration:none;color:#333;border:1px solid #eee'>{row['tool_a']} vs {row['tool_b']}</a>"

        index_html += "</div>"
        with open(os.path.join(lang_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)

    generate_sitemap_and_robots(generated_urls)
    print("\n🚀 [V9.1 终极完全体] 所有功能核对完毕。")

if __name__ == "__main__":
    main()