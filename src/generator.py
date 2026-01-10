import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import datetime

# ===========================
# 1. 配置与翻译字典
# ===========================
TRANSLATIONS = {
    'en': {
        'folder': '',
        'title_suffix': 'The Honest Review',
        'verdict_title': 'The Verdict',
        'check_price': 'Check Pricing',
        'price_chart': 'Price Comparison',
        'pros_hero': 'Advantages',
        'pros_comp': 'Advantages',
        'rated': 'Rated',
        'footer_rights': 'All rights reserved.',
        'col_pros': 'Pros', 'col_cons': 'Cons', 'col_verdict': 'Verdict',
        'home_btn': 'Read Review', 'privacy': 'Privacy Policy', 'terms': 'Terms of Use'
    },
    'es': {
        'folder': 'es',
        'title_suffix': 'Opinión Honesta',
        'verdict_title': 'El Veredicto',
        'check_price': 'Ver Precios',
        'price_chart': 'Comparación de Precios',
        'pros_hero': 'Ventajas',
        'pros_comp': 'Ventajas',
        'rated': 'Calificado',
        'footer_rights': 'Todos los derechos reservados.',
        'col_pros': 'Pros_ES', 'col_cons': 'Cons_ES', 'col_verdict': 'Verdict_ES',
        'home_btn': 'Leer Opinión', 'privacy': 'Política de Privacidad', 'terms': 'Términos de Uso'
    },
    'pt': {
        'folder': 'pt',
        'title_suffix': 'Análise Honesta',
        'verdict_title': 'O Veredito',
        'check_price': 'Ver Preços',
        'price_chart': 'Comparação de Preços',
        'pros_hero': 'Vantagens',
        'pros_comp': 'Vantagens',
        'rated': 'Avaliado',
        'footer_rights': 'Todos os direitos reservados.',
        'col_pros': 'Pros_PT', 'col_cons': 'Cons_PT', 'col_verdict': 'Verdict_PT',
        'home_btn': 'Ler Análise', 'privacy': 'Política de Privacidade', 'terms': 'Termos de Uso'
    }
}

# 用于收集所有链接生成 Sitemap
ALL_URLS = []

def generate_pages(csv_file, config):
    print("🏭 [Generator V9.6] Building Multi-language Site with Sitemap...")
    
    base_output_dir = 'public'
    if os.path.exists(base_output_dir):
        shutil.rmtree(base_output_dir)
    os.makedirs(base_output_dir)
    
    # --- 资源复制 ---
    os.makedirs(f"{base_output_dir}/images", exist_ok=True)
    os.makedirs(f"{base_output_dir}/static", exist_ok=True)
    
    if os.path.exists('static'):
        for item in os.listdir('static'):
            s = os.path.join('static', item)
            d = os.path.join(f"{base_output_dir}/static", item)
            if os.path.isfile(s): shutil.copy2(s, d)

    if os.path.exists('data/images'):
        for img in os.listdir('data/images'):
            shutil.copy(f"data/images/{img}", f"{base_output_dir}/images/{img}")

    if not os.path.exists(csv_file): 
        print("❌ CSV Not Found!")
        return

    df = pd.read_csv(csv_file).fillna("")
    env = Environment(loader=FileSystemLoader('templates'))
    tpl_compare = env.get_template('comparison.html')
    
    # 如果有 index.html 模板就用，没有就忽略（这里假设你有）
    try:
        tpl_index = env.get_template('index.html')
    except:
        tpl_index = None

    hero = config['hero_product']
    try:
        hero_data = df[df['Tool_Name'] == hero].iloc[0]
    except:
        print("❌ Hero product not found in CSV")
        return

    # --- 核心循环：遍历三种语言 ---
    for lang, trans in TRANSLATIONS.items():
        print(f"   🌍 Generating {lang.upper()} pages...")
        
        # 确定路径
        if trans['folder']:
            current_output_dir = f"{base_output_dir}/{trans['folder']}"
            url_prefix = f"{config['domain']}/{trans['folder']}"
        else:
            current_output_dir = base_output_dir
            url_prefix = f"{config['domain']}"
            
        os.makedirs(current_output_dir, exist_ok=True)

        # 收集当前语言的所有页面，用于生成该语言的首页
        lang_pages_list = []

        # 1. 生成对比页
        for index, row in df.iterrows():
            comp = row['Tool_Name']
            if comp == hero: continue
            
            slug = f"{hero.lower()}-vs-{comp.lower().replace(' ', '-')}"
            filename = f"{slug}.html"
            
            # 数据逻辑
            hero_pros = str(hero_data.get(trans['col_pros'], hero_data['Pros']))
            comp_pros = str(row.get(trans['col_pros'], row['Pros']))
            verdict_text = str(row.get(trans['col_verdict'], row['Verdict']))
            price_diff = float(row['Price']) - float(hero_data['Price'])
            reason = verdict_text if verdict_text else (f"Save ${int(price_diff)}/mo" if price_diff > 0 else "Great alternative")

            html = tpl_compare.render(
                config=config,
                hero=hero_data,
                comp=row,
                slug=slug,
                reason=reason,
                hero_pros=hero_pros,
                comp_pros=comp_pros,
                trans=trans,
                lang_code=lang
            )
            
            with open(f"{current_output_dir}/{filename}", "w", encoding="utf-8") as f:
                f.write(html)
            
            # 记录 URL 到 Sitemap 和 首页列表
            full_url = f"{url_prefix}/{filename}"
            ALL_URLS.append(full_url)
            lang_pages_list.append({'title': f"{hero} vs {comp}", 'link': filename})

        # 2. 生成当前语言的 Index 首页
        if tpl_index:
            index_html = tpl_index.render(config=config, pages=lang_pages_list, trans=trans, lang_code=lang)
            with open(f"{current_output_dir}/index.html", "w", encoding="utf-8") as f:
                f.write(index_html)
            ALL_URLS.append(f"{url_prefix}/") # 记录首页 URL

        # 3. 生成简单的 Privacy 和 Terms (防止死链)
        # 这里直接生成简单的静态 HTML，不需要模板，保证功能可用
        privacy_content = f"""<html><head><title>{trans['privacy']}</title></head><body style="padding:20px; font-family:sans-serif;"><h1>{trans['privacy']}</h1><p>We use cookies to improve experience.</p><p><a href="index.html">Back to Home</a></p></body></html>"""
        with open(f"{current_output_dir}/privacy.html", "w", encoding="utf-8") as f:
            f.write(privacy_content)
        ALL_URLS.append(f"{url_prefix}/privacy.html")

        terms_content = f"""<html><head><title>{trans['terms']}</title></head><body style="padding:20px; font-family:sans-serif;"><h1>{trans['terms']}</h1><p>Standard terms apply.</p><p><a href="index.html">Back to Home</a></p></body></html>"""
        with open(f"{current_output_dir}/terms.html", "w", encoding="utf-8") as f:
            f.write(terms_content)
        ALL_URLS.append(f"{url_prefix}/terms.html")

    # --- 4. 生成 CNAME ---
    if os.path.exists("CNAME"): shutil.copy("CNAME", f"{base_output_dir}/CNAME")

    # --- 5. 生成 Robots.txt ---
    robots_txt = f"""User-agent: *
Allow: /
Sitemap: {config['domain']}/sitemap.xml
"""
    with open(f"{base_output_dir}/robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_txt)
    print("✅ Robots.txt generated.")

    # --- 6. 生成 Sitemap.xml (核心) ---
    print(f"🗺️ Generating Sitemap with {len(ALL_URLS)} URLs...")
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in ALL_URLS:
        # 清理可能产生的双斜杠 (除 https:// 外)
        clean_url = url.replace('//', '/').replace('https:/', 'https://')
        sitemap_content += '  <url>\n'
        sitemap_content += f'    <loc>{clean_url}</loc>\n'
        sitemap_content += f'    <lastmod>{datetime.datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_content += '  </url>\n'
    
    sitemap_content += '</urlset>'
    
    with open(f"{base_output_dir}/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    
    print("✅ Sitemap.xml generated successfully.")
    print("✅ Full Site Build Complete.")

if __name__ == "__main__":
    # 模拟 Config 运行 (Cloudflare 会调用 generate_pages)
    import json
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
            generate_pages(f"data/{config['data_file']}", config)
    else:
        # 本地测试 fallback
        print("⚠️ No config.json found, checking local mode...")
