import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import shutil

def generate_pages(csv_file, config):
    print("🏭 [Generator] Building HTML...")
    
    output_dir = 'public' # GitHub Pages 常用发布目录名
    
    # 清理旧构建并重建
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    os.makedirs(f"{output_dir}/images")
    
    # 复制静态资源 (CSS)
    if os.path.exists('static'):
        shutil.copytree('static', f"{output_dir}/static")

    # 复制生成的图片过来
    source_img_dir = "data/images" # 假设 visualizer 输出到这里
    if os.path.exists(source_img_dir):
        for img in os.listdir(source_img_dir):
            shutil.copy(f"{source_img_dir}/{img}", f"{output_dir}/images/{img}")

    if not os.path.exists(csv_file):
        print("❌ Data file missing.")
        return

    df = pd.read_csv(csv_file)
    df.fillna("", inplace=True) # 填充空值防止报错
    
    env = Environment(loader=FileSystemLoader('templates'))
    tpl_compare = env.get_template('comparison.html')
    tpl_index = env.get_template('index.html')
    
    pages = []
    hero = config['hero_product']
    
    try:
        hero_data = df[df['Tool_Name'] == hero].iloc[0]
    except:
        print("❌ Hero product not found in CSV.")
        return

    for index, row in df.iterrows():
        comp = row['Tool_Name']
        if comp == hero: continue
        
        slug = f"{hero.lower()}-vs-{comp.lower().replace(' ', '-')}"
        
        # 简单判决逻辑
        price_diff = float(row['Price']) - float(hero_data['Price'])
        winner = hero if price_diff > 0 else comp
        
        html = tpl_compare.render(
            config=config,
            hero=hero_data,
            comp=row,
            winner=winner,
            slug=slug
        )
        
        with open(f"{output_dir}/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        pages.append({'title': f"{hero} vs {comp}", 'link': f"{slug}.html"})

    # 生成首页
    with open(f"{output_dir}/index.html", "w", encoding="utf-8") as f:
        f.write(tpl_index.render(config=config, pages=pages))
    
    # 生成 CNAME (这是 GitHub Pages 的关键)
    if os.path.exists("CNAME"):
        shutil.copy("CNAME", f"{output_dir}/CNAME")
        
    print(f"🎉 Build complete! {len(pages)} pages generated in '/public'.")