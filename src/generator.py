import pandas as pd
import os
import shutil
import datetime
import itertools # 引入排列组合库

# ===========================
# 天道 pSEO 核动力引擎 V4.0
# 逻辑：读取 CSV -> 自动两两组合 -> 生成海量对比页
# ===========================

CONFIG = {
    "site_name": "SaaS Battle Arena",
    "domain": "https://compare.ii-x.com",
    "hero_title": "Software Comparisons 2026",
    "description": "Unbiased side-by-side comparisons of top SaaS tools.",
    "primary_color": "#2563eb",
    "year": "2026"
}

def load_data():
    # 优先读取 data.csv
    file_path = os.path.join('data', 'data.csv')
    if not os.path.exists(file_path):
        print("⚠️ Data file not found!")
        return []
    
    try:
        df = pd.read_csv(file_path).fillna("")
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ CSV Read Error: {e}")
        return []

def generate_site():
    print(f"🚀 Starting pSEO Engine for {CONFIG['site_name']}...")
    
    # 1. 清理旧文件
    base_dir = 'public'
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)
    
    # 2. 读取弹药
    tools = load_data()
    if not tools: return

    print(f"🔫 Loaded {len(tools)} tools. Generating combinations...")
    
    # 3. 生成组合 (Combinations)
    # 这就是 pSEO 的核心：C(N, 2)
    combinations = list(itertools.combinations(tools, 2))
    print(f"🔥 Generating {len(combinations)} comparison pages...")

    generated_links = []

    # 4. 准备 CSS (极简风，加载快)
    css = f"""<style>
        :root {{ --primary: {CONFIG['primary_color']}; --bg: #0f172a; --text: #f8fafc; --card: #1e293b; }}
        body {{ font-family: system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; line-height: 1.6; }}
        .nav {{ background: rgba(15,23,42,0.9); padding: 15px; border-bottom: 1px solid #333; text-align:center; }}
        .nav a {{ color: #fff; text-decoration: none; margin: 0 10px; font-weight: bold; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
        .battle-card {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 40px 0; }}
        .fighter {{ background: var(--card); padding: 30px; border-radius: 12px; border: 1px solid #334155; text-align: center; }}
        .vs-badge {{ position: absolute; left: 50%; transform: translate(-50%, 130px); background: #ef4444; color: white; padding: 10px 20px; border-radius: 50%; font-weight: 900; font-size: 1.2rem; z-index: 10; }}
        h1 {{ text-align: center; font-size: 2.5rem; margin-bottom: 10px; }}
        .price {{ font-size: 2rem; font-weight: 800; color: var(--primary); margin: 20px 0; }}
        .btn {{ display: inline-block; background: var(--primary); color: white; padding: 12px 30px; border-radius: 30px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
        .btn:hover {{ filter: brightness(110%); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 30px; background: var(--card); }}
        td, th {{ padding: 15px; border-bottom: 1px solid #333; text-align: left; }}
        th {{ background: #020617; }}
        .tag {{ background: #334155; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; margin: 2px; display:inline-block; }}
        footer {{ text-align: center; padding: 40px; color: #64748b; font-size: 0.9rem; }}
    </style>"""

    # 5. 循环生成每一个对比页
    for tool_a, tool_b in combinations:
        slug = f"{tool_a['Tool_Name'].lower()}-vs-{tool_b['Tool_Name'].lower()}".replace(" ", "-")
        filename = f"{slug}.html"
        
        # 动态文案逻辑
        try:
            price_a = float(tool_a['Price'].replace('$',''))
            price_b = float(tool_b['Price'].replace('$',''))
            if price_a < price_b:
                verdict = f"🏆 <strong>{tool_a['Tool_Name']}</strong> is cheaper. You save ${price_b - price_a:.2f}/mo."
                winner = tool_a
            else:
                verdict = f"💎 <strong>{tool_b['Tool_Name']}</strong> is the budget pick. <strong>{tool_a['Tool_Name']}</strong> is for power users."
                winner = tool_b
        except:
            verdict = "Both are excellent choices depending on your needs."

        # HTML 模板
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tool_a['Tool_Name']} vs {tool_b['Tool_Name']}: Which is Better in 2026?</title>
    <meta name="description" content="Detailed comparison of {tool_a['Tool_Name']} vs {tool_b['Tool_Name']}. Pricing, features, and pros/cons analyzed.">
    <link rel="canonical" href="{CONFIG['domain']}/{filename}">
    {css}
    </head>
<body>
    <div class="nav">
        <a href="/">🏠 Home</a>
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
                    <a href="{tool_a['Affiliate_Link']}" class="btn" rel="nofollow sponsored">👉 Check Price</a>
                </div>
                <div class="fighter">
                    <h2>{tool_b['Tool_Name']}</h2>
                    <div class="price">{tool_b['Price']}</div>
                    <p>{tool_b['Verdict']}</p>
                    <a href="{tool_b['Affiliate_Link']}" class="btn" rel="nofollow sponsored">👉 Check Price</a>
                </div>
            </div>
        </div>

        <div style="background:#1e293b; padding:20px; border-radius:8px; margin:20px 0; border-left:4px solid #2563eb;">
            <h3>💡 The Quick Verdict</h3>
            <p>{verdict}</p>
        </div>

        <table>
            <tr>
                <th>Feature</th>
                <th>{tool_a['Tool_Name']}</th>
                <th>{tool_b['Tool_Name']}</th>
            </tr>
            <tr>
                <td><strong>Best For</strong></td>
                <td>{tool_a['Verdict']}</td>
                <td>{tool_b['Verdict']}</td>
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
                <td><strong>Features</strong></td>
                <td>{tool_a['Features'].replace(';', '<br>')}</td>
                <td>{tool_b['Features'].replace(';', '<br>')}</td>
            </tr>
        </table>

    </div>

    <footer>
        <p>&copy; 2026 {CONFIG['site_name']}. <a href="privacy.html">Privacy</a> | <a href="terms.html">Terms</a></p>
    </footer>
</body>
</html>"""
        
        with open(f"public/{filename}", "w", encoding="utf-8") as f:
            f.write(html)
        
        generated_links.append({"title": f"{tool_a['Tool_Name']} vs {tool_b['Tool_Name']}", "url": filename})

    # 6. 生成首页 (包含所有对比的索引)
    index_links = "".join([f'<a href="{item["url"]}" style="display:block; padding:10px; background:#1e293b; margin:5px 0; color:#fff; text-decoration:none; border-radius:4px;">{item["title"]}</a>' for item in generated_links])
    
    index_html = f"""<!DOCTYPE html>
<html><head><title>{CONFIG['hero_title']}</title>{css}</head><body>
<div class="nav"><a href="/">Home</a></div>
<div class="container">
<h1>⚡ {CONFIG['hero_title']}</h1>
<p style="text-align:center">Comparing {len(tools)} tools, generated {len(generated_links)} battle pages.</p>
<div style="margin-top:40px;">{index_links}</div>
</div>
</body></html>"""
    
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # 7. 生成 Sitemap (这就是海量流量的入口)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for item in generated_links:
        sitemap += f'<url><loc>{CONFIG["domain"]}/{item["url"]}</loc><lastmod>{datetime.datetime.now().strftime("%Y-%m-%d")}</lastmod></url>'
    sitemap += '</urlset>'
    
    with open("public/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)
    
    # 8. 补全法律页 (防止死链)
    with open("public/privacy.html", "w") as f: f.write("<h1>Privacy Policy</h1><p>We respect your privacy.</p>")
    with open("public/terms.html", "w") as f: f.write("<h1>Terms of Use</h1><p>Standard terms apply.</p>")

    print("✅ pSEO Mission Accomplished.")

if __name__ == "__main__":
    generate_site()
