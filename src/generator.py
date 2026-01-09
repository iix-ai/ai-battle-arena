import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import datetime

# 翻译字典：让界面文字也变成本地语言
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
        'col_pros': 'Pros', 'col_cons': 'Cons', 'col_verdict': 'Verdict' # 对应CSV列名后缀
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
        'col_pros': 'Pros_ES', 'col_cons': 'Cons_ES', 'col_verdict': 'Verdict_ES'
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
        'col_pros': 'Pros_PT', 'col_cons': 'Cons_PT', 'col_verdict': 'Verdict_PT'
    }
}

def generate_pages(csv_file, config):
    print("🏭 [Generator] Building Multi-language Site...")
    
    base_output_dir = 'public'
    if os.path.exists(base_output_dir):
        shutil.rmtree(base_output_dir)
    os.makedirs(base_output_dir)
    
    # 复制静态资源
    os.makedirs(f"{base_output_dir}/images", exist_ok=True)
    os.makedirs(f"{base_output_dir}/static", exist_ok=True)
    
    if os.path.exists('static'):
        # 复制 favicon 等
        for item in os.listdir('static'):
            s = os.path.join('static', item)
            d = os.path.join(f"{base_output_dir}/static", item)
            if os.path.isfile(s): shutil.copy2(s, d)

    if os.path.exists('data/images'):
        for img in os.listdir('data/images'):
            shutil.copy(f"data/images/{img}", f"{base_output_dir}/images/{img}")

    if not os.path.exists(csv_file): return

    df = pd.read_csv(csv_file).fillna("")
    env = Environment(loader=FileSystemLoader('templates'))
    tpl_compare = env.get_template('comparison.html')
    
    hero = config['hero_product']
    try:
        hero_data = df[df['Tool_Name'] == hero].iloc[0]
    except:
        return

    # --- 核心循环：遍历三种语言 ---
    for lang, trans in TRANSLATIONS.items():
        print(f"   🌍 Generating {lang.upper()} pages...")
        
        # 确定输出子目录
        if trans['folder']:
            current_output_dir = f"{base_output_dir}/{trans['folder']}"
            os.makedirs(current_output_dir, exist_ok=True)
            # 这里的 images 路径需要处理，为了简单，我们在 HTML 里用绝对路径 config.domain
        else:
            current_output_dir = base_output_dir

        pages_meta = []
        
        for index, row in df.iterrows():
            comp = row['Tool_Name']
            if comp == hero: continue
            
            slug = f"{hero.lower()}-vs-{comp.lower().replace(' ', '-')}"
            
            # 获取对应语言的数据
            # 如果是 ES/PT，读取 Pros_ES/Pros_PT；如果是 EN，读取 Pros
            # 注意：CSV列名可能为空，要做容错
            hero_pros = str(hero_data.get(trans['col_pros'], hero_data['Pros']))
            comp_pros = str(row.get(trans['col_pros'], row['Pros']))
            verdict_text = str(row.get(trans['col_verdict'], row['Verdict']))

            # 价格逻辑
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
                trans=trans, # 传入翻译字典
                lang_code=lang
            )
            
            with open(f"{current_output_dir}/{slug}.html", "w", encoding="utf-8") as f:
                f.write(html)

    # 复制 CNAME (只在根目录)
    if os.path.exists("CNAME"): shutil.copy("CNAME", f"{base_output_dir}/CNAME")
    
    # 简单生成英文首页 (为了不报错，首页暂时只做英文，或者你可以复制逻辑做多语言首页)
    # 这里为了稳妥，我们生成一个英文首页
    tpl_index = env.get_template('index.html')
    # 首页数据我们只拿英文的
    en_pages = []
    for index, row in df.iterrows():
        if row['Tool_Name'] == hero: continue
        slug = f"{hero.lower()}-vs-{row['Tool_Name'].lower().replace(' ', '-')}"
        en_pages.append({'title': f"{hero} vs {row['Tool_Name']}", 'link': f"{slug}.html"})
        
    with open(f"{base_output_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(tpl_index.render(config=config, pages=en_pages, trans=TRANSLATIONS['en']))

    print("✅ Full Site Build Complete.")