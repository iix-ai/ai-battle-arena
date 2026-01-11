import pandas as pd
import os
import shutil
import datetime
import itertools
import json

# ===========================
# 天道 pSEO 核动力引擎 V4.5 (资产全保留版)
# 核心功能：GA注入 + Favicon + 排列组合 + Sitemap
# ===========================

def load_config():
    # 默认配置
    config = {
        "site_name": "SaaS Battle Arena",
        "domain": "https://compare.ii-x.com",
        "hero_title": "Software Comparisons 2026",
        "description": "Unbiased side-by-side comparisons of top SaaS tools.",
        "primary_color": "#2563eb",
        "year": "2026",
        "google_analytics_id": "G-XXXXXX", # 默认ID，会从文件读取覆盖
        "icon": "⚔️"
    }
    
    # 尝试读取 config.json
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                config.update(loaded)
        except Exception as e:
            print(f"⚠️ Config Error: {e}")
            
    return config

CONFIG = load_config()

# SVG 图标生成 (保留旧资产)
FAVICON_SVG = f'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>{CONFIG.get("icon", "⚡")}</text></svg>'

def load_data():
    file_path = os.path.join('data', 'data.csv')
    if not os.path.exists(file_path):
        print("⚠️ Data file not found!")
        return []
    try:
        # 强制读取所有字段为字符串，防止报错
        df = pd.read_csv(file_path, dtype=str).fillna("")
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ CSV Read Error: {e}")
        return []

def get_ga_script():
    # 这里的 ID 必须从 config.json 里读，绝不写死
    ga_id = CONFIG.get('google_analytics_id', '')
    if not ga_id or "G-XXXX" in ga_id:
        return ""
    
    return f"""<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{ga_id}');
    </script>"""

def generate_site():
    print(f"🚀 Starting pSEO Engine V4.5 for {CONFIG['site_name']}...")
    
    base_dir = 'public'
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)
    
    tools = load_data()
    if not tools: return

    # 生成组合
    combinations = list(itertools.combinations(tools, 2))
    print(f"🔥 Found {len(tools)} tools, generating {len(combinations)} comparison pages...")

    generated_links = []
    ga_code = get_ga_script() # 获取 GA 代码

    css = f"""<style>
        :root {{ --primary: {CONFIG['primary_color']}; --bg: #0f172a; --text: #f8fafc; --card: #1e293b; }}
        body {{ font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.6; }}
        .nav {{ background: rgba(15,23,42,0.9); padding: 15px; border-bottom: 1px solid #333; text-align:center; position:sticky; top:0; z-index:100; backdrop-filter:blur(10px); }}
        .nav a {{ color: #e2e8f0; text-decoration: none; margin: 0 10px; font-weight: 600; font-size: 0.95rem; }}
        .nav a:hover {{ color: var(--primary); }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
        .battle-card {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 40px 0; }}
        .fighter {{ background: var(--card); padding: 30px; border-radius: 12px; border: 1px solid #334155; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        .vs-badge {{ position: absolute; left: 50%; transform: translate(-50%, 150px); background: #ef4444; color: white; padding: 12px 20px; border-radius: 50%; font-weight: 900; font-size: 1.5rem; z-index: 10; box-shadow: 0 0 20px rgba(239, 68, 68, 0.5); }}
        h1 {{ text-align: center; font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(to right, #60a5fa, var(--primary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .price {{ font-size: 2rem; font-weight: 800; color: var(--primary); margin: 20px 0; }}
        .btn {{ display: inline-block; background: var(--primary); color: white; padding: 12px 30px; border-radius: 30px; text-decoration: none; font-weight: bold; margin-top: 20px; transition: all 0.2s; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 30px; background: var(--card); border-radius: 8px; overflow: hidden; }}
        td, th {{ padding: 15px; border-bottom: 1px solid #334155; text-align: left; }}
        th {{ background: #020617; text-transform: uppercase; font-size: 0.75rem; color: #94a3b8; }}
        footer {{ text-align: center; padding: 40px; color: #64748b; font-size: 0.9rem; border-top: 1px solid #334155; margin-top: 60px; }}
        @media (max-width: 768px) {{ .battle-card {{ grid-template-columns: 1fr; }} .vs-badge {{ display: none; }} }}
    </style>"""

    # 循环生成对比页
    for tool_a, tool_b in combinations:
        slug = f"{tool_a['Tool_Name'].lower()}-vs-{tool_b['Tool_Name'].lower()}".replace(" ", "-")
        filename = f"{slug}.html"
        
        # 简单的价格逻辑
        try:
            price_str_a = tool_a.get('Price', '0').replace('$','').replace('/mo','')
            price_str_b = tool_b.get('Price', '0').replace('$','').replace('/mo','')
            price_a = float(price_str_a) if price_str_a else 0
            price_b = float(price_str_b) if price_str_b else 0
            
            if price_a > 0 and price_b > 0:
                if price_a < price_b:
                    diff = price_b - price_a
                    verdict = f"🏆 <strong>{tool_a['Tool_Name']}</strong> is the value winner. You save approx <strong>${diff:.0f}/year</strong> compared to {tool_b['Tool_Name']}."
                else:
                    verdict = f"💎 <strong>{tool_b['Tool_Name']}</strong> is more affordable. {tool_a['Tool_Name']} is positioned as a premium option."
            else:
                verdict = "Compare features below to decide which tool fits your workflow."
        except:
            verdict = "Both tools offer unique advantages. Check the table below."

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tool_a['Tool_Name']} vs {tool_b['Tool_Name']} (2026 Comparison)</title>
    <meta name="description" content="Detailed comparison: {tool_a['Tool_Name']} vs {tool_b['Tool_Name']}. See pricing, features, pros & cons.">
    <link rel="canonical" href="{CONFIG['domain']}/{filename}">
    <link rel="icon" href="{FAVICON_SVG}">
    {ga_code}
    {css}
</head>
<body>
    <div class="nav">
        <a href="/">🏠 AI Tools</a>
        <a href="https://vpn.ii-x.com">🛡️ VPN</a>
        <a href="https://esim.ii-x.com">📲 eSIM</a>
    </div>

    <div class="container">
        <h1>{tool_a['Tool_Name']} <span style="color:#64748b">VS</span> {tool_b['Tool_Name']}</h1>
        <p style="text-align:center; color:#94a3b8">Last Updated: {datetime.datetime.now().strftime('%B %Y')}</p>

        <div style="position:relative">
            <div class="vs-badge">VS</div>
            <div class="battle-card">
                <div class="fighter">
                    <h2>{tool_a['Tool_Name']}</h2>
                    <div class="price">{tool_a['Price']}</div>
                    <p>{tool_a['Verdict']}</p>
                    <a href="{tool_a['Affiliate_Link']}" class="btn" rel="nofollow sponsored" target="_blank">👉 Check Price</a>
                </div>
                <div class="fighter">
                    <h2>{tool_b['Tool_Name']}</h2>
                    <div class="price">{tool_b['Price']}</div>
                    <p>{tool_b['Verdict']}</p>
                    <a href="{tool_b['Affiliate_Link']}" class="btn" rel="nofollow sponsored" target="_blank">👉 Check Price</a>
                </div>
            </div>
        </div>

        <div style="background:#1e293b; padding:20px; border-radius:8px; margin:20px 0; border-left:4px solid #2563eb;">
            <h3>💡 The Quick Verdict</h3>
            <p>{verdict}</p>
        </div>

        <table>
            <tr>
                <th style="width:20%">Feature</th>
                <th style="width:40%">{tool_a['Tool_Name']}</th>
                <th style="width:40%">{tool_b['Tool_Name']}</th>
            </tr>
            <tr>
                <td><strong>Pros</strong></td>
                <td>{tool_a['Pros']}</td>
                <td>{tool_b['Pros']}</td>
            </tr>
            <tr>
                <td><strong>Cons</strong></td>
                <td>{tool_a['Cons']}</td>
                <td>{tool_b['Cons']}</td>
            </tr>
            <tr>
                <td><strong>Description</strong></td>
                <td>{tool_a.get('Description', 'No description available.')}</td>
                <td>{tool_b.get('Description', 'No description available.')}</td>
            </tr>
        </table>
    </div>

    <footer>
        <p>&copy; {CONFIG['year']} {CONFIG['site_name']}. <a href="privacy.html" style="color:#64748b">Privacy</a> | <a href="terms.html" style="color:#64748b">Terms</a></p>
    </footer>
</body>
</html>"""
        
        with open(f"public/{filename}", "w", encoding="utf-8") as f:
            f.write(html)
        generated_links.append({"title": f"{tool_a['Tool_Name']} vs {tool_b['Tool_Name']}", "url": filename})

    # 生成首页
    index_links = "".join([f'<a href="{item["url"]}" style="display:block; padding:15px; background:#1e293b; margin:10px 0; color:#fff; text-decoration:none; border-radius:8px; border:1px solid #334155;">⚔️ <strong>{item["title"]}</strong></a>' for item in generated_links])
    
    index_html = f"""<!DOCTYPE html>
<html><head><title>{CONFIG['hero_title']}</title><link rel="icon" href="{FAVICON_SVG}">{ga_code}{css}</head><body>
<div class="nav"><a href="/">🏠 Home</a><a href="https://vpn.ii-x.com">🛡️ VPN</a></div>
<div class="container">
<h1>⚡ {CONFIG['hero_title']}</h1>
<p style="text-align:center; margin-bottom:40px;">Unbiased comparisons of {len(tools)} top SaaS tools. Generated {len(generated_links)} battle pages.</p>
{index_links}
</div>
<footer>&copy; {CONFIG['year']} {CONFIG['site_name']}</footer>
</body></html>"""
    
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # 生成 Sitemap (核心)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    # 首页
    sitemap += f'<url><loc>{CONFIG["domain"]}/</loc><lastmod>{datetime.datetime.now().strftime("%Y-%m-%d")}</lastmod></url>'
    # 所有对比页
    for item in generated_links:
        sitemap += f'<url><loc>{CONFIG["domain"]}/{item["url"]}</loc><lastmod>{datetime.datetime.now().strftime("%Y-%m-%d")}</lastmod></url>'
    sitemap += '</urlset>'
    
    with open("public/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)
    
    # 生成法律页
    with open("public/privacy.html", "w", encoding="utf-8") as f: f.write(f"<html><head><title>Privacy</title>{ga_code}</head><body><h1>Privacy Policy</h1><p>We respect your privacy.</p></body></html>")
    with open("public/terms.html", "w", encoding="utf-8") as f: f.write(f"<html><head><title>Terms</title>{ga_code}</head><body><h1>Terms of Use</h1><p>Standard terms apply.</p></body></html>")
    
    # 复制 CNAME
    if os.path.exists("CNAME"): shutil.copy("CNAME", "public/CNAME")

    print("✅ pSEO Engine V4.5 Upgrade Complete.")

if __name__ == "__main__":
    generate_site()
