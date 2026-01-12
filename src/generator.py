import os
import pandas as pd
import json
from jinja2 import Environment, FileSystemLoader
from itertools import combinations
import shutil
from datetime import datetime

# Tiandao Project Generator v8.0 (Optimized & Monetized)
class SiteGenerator:
    def __init__(self):
        # 1. 路径初始化 (保持原逻辑)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.base_dir, 'data', 'data.csv')
        self.config_path = os.path.join(self.base_dir, 'config.json')
        self.template_dir = os.path.join(self.base_dir, 'templates')
        self.output_dir = os.path.join(self.base_dir, 'output')
        self.static_dir = os.path.join(self.base_dir, 'static')
        
        # 2. 加载配置文件 (新增功能：用于控制佣金链接)
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {} #以此防止配置缺失报错
        
        self.generated_urls = []

    def load_data(self):
        # 3. 数据加载与清洗 (增强稳定性)
        if not os.path.exists(self.data_path): 
            print("Error: Data file not found!")
            return []
        try:
            # 增加 on_bad_lines='skip' 防止 DeepSeek 生成的坏数据导致崩溃
            df = pd.read_csv(self.data_path, header=0, on_bad_lines='skip', encoding='utf-8')
            df = df.fillna("Info pending")
            return df.to_dict('records')
        except Exception as e:
            print(f"Data Load Error: {e}")
            return []

    def get_affiliate_link(self, tool_name, original_link):
        # 4. 【核心新增】佣金拦截器
        # 逻辑：如果在 config.json 里配置了高佣链接，就替换掉 CSV 里的官网链接
        if not self.config or 'affiliate_map' not in self.config:
            return original_link
            
        clean_name = str(tool_name).strip()
        for key, link in self.config.get('affiliate_map', {}).items():
            if key.lower() in clean_name.lower():
                # 命中高佣名单！替换链接！
                return link
        return original_link

    def generate_pages(self, tools):
        # 5. 页面生成引擎
        env = Environment(loader=FileSystemLoader(self.template_dir))
        env.globals['now'] = datetime.utcnow
        template = env.get_template('comparison.html') 
        
        # 核心裂变：C(N, 2) 排列组合
        pairs = list(combinations(tools, 2))
        print(f"Generating {len(pairs)} comparison pages...")

        for tool_a, tool_b in pairs:
            # 执行链接替换
            tool_a['Affiliate_Link'] = self.get_affiliate_link(tool_a['Tool_Name'], tool_a.get('Affiliate_Link', '#'))
            tool_b['Affiliate_Link'] = self.get_affiliate_link(tool_b['Tool_Name'], tool_b.get('Affiliate_Link', '#'))
            
            # 生成 SEO 友好的 URL (slug)
            slug = f"{str(tool_a['Tool_Name']).lower()}-vs-{str(tool_b['Tool_Name']).lower()}".replace(" ", "-").replace(".", "")
            filename = f"{slug}.html"
            
            # 渲染 (HTML 结构全部在 comparison.html 中)
            html = template.render(
                tool_a=tool_a,
                tool_b=tool_b,
                config=self.config,
                current_year=datetime.now().year,
                page_slug=slug
            )
            
            with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                f.write(html)
            
            self.generated_urls.append(filename)

    def generate_index(self, tools):
        # 6. 首页生成
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template('index.html')
        
        # 为了首页加载速度，只取前 20 对热门组合展示
        top_pairs = list(combinations(tools[:10], 2)) 
        
        html = template.render(
            tools=tools,
            top_pairs=top_pairs,
            config=self.config,
            current_year=datetime.now().year
        )
        with open(os.path.join(self.output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)

    def generate_sitemap(self):
        # 7. 【核心新增】Sitemap 生成器
        # 旧代码可能缺失了这里，导致内页不被收录
        base_url = self.config.get('site_domain', 'https://compare.ii-x.com')
        sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        # 写入首页
        sitemap_content += f'  <url><loc>{base_url}/</loc><priority>1.0</priority></url>\n'
        
        # 循环写入所有对比页
        for filename in self.generated_urls:
            sitemap_content += f'  <url><loc>{base_url}/{filename}</loc><priority>0.8</priority></url>\n'
            
        sitemap_content += '</urlset>'
        
        with open(os.path.join(self.output_dir, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write(sitemap_content)

    def copy_assets(self):
        # 8. 资源复制 (保持不变)
        if os.path.exists(self.static_dir):
            target_static = os.path.join(self.output_dir, 'static')
            if os.path.exists(target_static):
                shutil.rmtree(target_static)
            shutil.copytree(self.static_dir, target_static)
        
        robots_path = os.path.join(self.base_dir, 'robots.txt')
        if os.path.exists(robots_path):
            shutil.copy(robots_path, os.path.join(self.output_dir, 'robots.txt'))

    def run(self):
        # 主执行流
        if os.path.exists(self.output_dir): shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
        
        tools = self.load_data()
        if not tools: return
            
        self.generate_pages(tools)
        self.generate_index(tools)
        self.generate_sitemap()
        self.copy_assets()
        print("Build Complete.")

if __name__ == "__main__":
    generator = SiteGenerator()
    generator.run()
