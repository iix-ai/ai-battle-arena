import os
import pandas as pd
import json
from jinja2 import Environment, FileSystemLoader
from itertools import combinations
import datetime
import shutil

# Tiandao Project Generator v8.0 (Optimized & Monetized)
# Based on v7.1 Stable - Preserves Article Stitching Logic

class SiteGenerator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.base_dir, 'data', 'data.csv')
        self.config_path = os.path.join(self.base_dir, 'config.json') # 新增配置路径
        self.template_dir = os.path.join(self.base_dir, 'templates')
        self.output_dir = os.path.join(self.base_dir, 'output')
        self.static_dir = os.path.join(self.base_dir, 'static')
        self.generated_urls = []
        
        # 加载配置 (新增)
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}

    def load_data(self):
        print(f"📂 Loading data from {self.data_path}...")
        if not os.path.exists(self.data_path):
            print("❌ Data file missing!")
            return []
        
        try:
            df = pd.read_csv(self.data_path, header=0, on_bad_lines='skip', encoding='utf-8')
            df = df[df['Tool_Name'] != 'Tool_Name']
            df = df.fillna("Info pending")
            # 确保 Price 也是字符串，防止报错
            df['Price'] = df['Price'].astype(str).replace("nan", "Check Website").replace("", "Check Website")
            return df.to_dict('records')
        except Exception as e:
            print(f"❌ CSV Error: {e}")
            return []

    # 【核心新增】佣金拦截器
    def get_affiliate_link(self, tool_name, original_link):
        if not self.config or 'affiliate_map' not in self.config:
            return original_link
            
        clean_name = str(tool_name).strip()
        for key, link in self.config.get('affiliate_map', {}).items():
            if key.lower() in clean_name.lower():
                return link
        return original_link

    def generate_pages(self, tools):
        env = Environment(loader=FileSystemLoader(self.template_dir))
        try:
            template = env.get_template('page.html')
        except Exception as e:
            print(f"❌ Template Error: {e}")
            return

        pairs = list(combinations(tools, 2))
        print(f"⚔️  Generating {len(pairs)} battle pages...")

        for tool_a, tool_b in pairs:
            # 1. 在生成内容前，先把链接替换成高佣链接 (新增逻辑)
            tool_a['Affiliate_Link'] = self.get_affiliate_link(tool_a['Tool_Name'], tool_a.get('Affiliate_Link', '#'))
            tool_b['Affiliate_Link'] = self.get_affiliate_link(tool_b['Tool_Name'], tool_b.get('Affiliate_Link', '#'))

            # 2. 生成 Slug
            name_a = str(tool_a.get('Tool_Name', 'Unknown')).strip()
            name_b = str(tool_b.get('Tool_Name', 'Unknown')).strip()
            slug = f"{name_a.lower()}-vs-{name_b.lower()}".replace(" ", "-").replace(".", "")
            filename = f"{slug}.html"
            
            # 3. 生成长文内容 (完整保留您原有的拼接逻辑)
            article_body = f"""
            <div class="battle-section">
                <h2>The Ultimate Showdown: {name_a} vs {name_b}</h2>
                <p>In the competitive world of SEO tools, deciding between <strong>{name_a}</strong> and <strong>{name_b}</strong> is a common dilemma. Both platforms offer powerful features, but they cater to different needs.</p>
                
                <h3>1. Deep Dive: {name_a}</h3>
                <p>{tool_a.get('Long_Review', 'Review pending...')}</p>
                <div class="verdict-box"><strong>Verdict:</strong> {tool_a.get('Verdict', '')}</div>
                
                <h3>2. Deep Dive: {name_b}</h3>
                <p>{tool_b.get('Long_Review', 'Review pending...')}</p>
                <div class="verdict-box"><strong>Verdict:</strong> {tool_b.get('Verdict', '')}</div>
                
                <h3>3. Feature & Price Comparison</h3>
                <p>{name_a} enters the ring at {tool_a.get('Price', 'N/A')}, while {name_b} costs {tool_b.get('Price', 'N/A')}. 
                If budget is your primary concern, check the pricing details above carefully.</p>
                
                <h3>4. Final Recommendation</h3>
                <p>If you need <strong>{str(tool_a.get('Pros', '')).split(';')[0]}</strong>, then {name_a} is likely your best choice.</p>
                <p>However, for those prioritizing <strong>{str(tool_b.get('Pros', '')).split(';')[0]}</strong>, {name_b} stands out as the winner.</p>
            </div>
            """

            render_data = {
                'tool_a': tool_a,
                'tool_b': tool_b,
                'title': f"{name_a} vs {name_b}: Which is Better in 2026? (Honest Review)", # 优化了标题
                'meta_description': f"Unbiased comparison of {name_a} vs {name_b}. {str(tool_a.get('Description', ''))[:100]}...",
                'article_body': article_body,
                'date': datetime.datetime.now().strftime("%B %Y"),
                'config': self.config # 传入配置供模板使用
            }

            try:
                content = template.render(**render_data)
                with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
                self.generated_urls.append(filename)
            except Exception as e:
                print(f"⚠️ Error generating {filename}: {e}")

    def generate_index(self, tools):
        print("🏠 Generating Professional Index Page...")
        pairs = list(combinations(tools, 2))
        
        # 首页逻辑保持不变，确保首页也使用 favicon
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SaaS Battle Arena - Top 2026 Software Comparisons</title>
            <link rel="icon" href="/static/favicon.png" type="image/png">
            <meta name="description" content="Unbiased AI-driven comparisons of top B2B SaaS tools. Find the best software for your business.">
            <style>
                body {{ background: #0f172a; color: #f1f5f9; font-family: system-ui, sans-serif; padding: 40px 20px; margin: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                h1 {{ text-align: center; font-size: 2.5rem; margin-bottom: 10px; color: #3b82f6; }}
                .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 60px; font-size: 1.1rem; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
                .card {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; transition: 0.2s; text-align: center; text-decoration: none; display: block; }}
                .card:hover {{ transform: translateY(-5px); border-color: #3b82f6; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }}
                .card-title {{ color: #38bdf8; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; }}
                .vs-tag {{ color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }}
                footer {{ text-align: center; margin-top: 80px; color: #475569; border-top: 1px solid #1e293b; padding-top: 40px; }}
                footer a {{ color: #64748b; text-decoration: none; margin: 0 10px; transition: color 0.2s; }}
                footer a:hover {{ color: #38bdf8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚔️ SaaS Battle Arena</h1>
                <p class="subtitle">Unbiased, AI-driven comparisons of {len(tools)} top SEO tools. {len(pairs)} battles generated.</p>
                <div class="grid">
                    {''.join([f'''
                    <a href="{str(t[0].get("Tool_Name")).strip().lower().replace(" ", "-").replace(".", "")}-vs-{str(t[1].get("Tool_Name")).strip().lower().replace(" ", "-").replace(".", "")}.html" class="card">
                        <div class="vs-tag">Comparison</div>
                        <div class="card-title">
                            {t[0].get("Tool_Name")} <span style="color:#94a3b8">vs</span> {t[1].get("Tool_Name")}
                        </div>
                    </a>
                    ''' for t in pairs])}
                </div>
                <footer>
                    <p>&copy; 2026 SaaS Battle Arena.</p>
                    <div style="margin: 20px auto; max-width: 800px; font-size: 0.8rem; color: #64748b; line-height: 1.5; opacity: 0.8;">
                        {self.config.get('legal', {}).get('disclosure', 'Advertiser Disclosure: We may receive compensation if you click on links. This supports our research.')}
                    </div>
                    <p><a href="privacy.html">Privacy</a> | <a href="terms.html">Terms</a></p>
                </footer>
            </div>
        </body>
        </html>
        """
        with open(os.path.join(self.output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(html_content)

    def generate_sitemap(self):
        print("🗺️  Generating Sitemap...")
        base_url = "https://compare.ii-x.com"
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        xml += f'<url><loc>{base_url}/</loc><priority>1.0</priority></url>\n'
        for url in self.generated_urls:
            xml += f'<url><loc>{base_url}/{url}</loc><priority>0.8</priority></url>\n'
        xml += '</urlset>'
        with open(os.path.join(self.output_dir, "sitemap.xml"), 'w', encoding='utf-8') as f:
            f.write(xml)

    def generate_robots(self):
        with open(os.path.join(self.output_dir, "robots.txt"), 'w', encoding='utf-8') as f:
            f.write("User-agent: *\nAllow: /\nSitemap: https://compare.ii-x.com/sitemap.xml")

    def copy_assets(self):
        if os.path.exists(self.static_dir):
            try:
                output_static = os.path.join(self.output_dir, 'static')
                if os.path.exists(output_static):
                    shutil.rmtree(output_static)
                shutil.copytree(self.static_dir, output_static)
                print("🎨 Assets copied.")
            except Exception as e:
                print(f"⚠️ Asset copy failed: {e}")
                
        privacy_path = os.path.join(self.output_dir, "privacy.html")
        if not os.path.exists(privacy_path):
            with open(privacy_path, 'w', encoding='utf-8') as f:
                f.write("<h1>Privacy Policy</h1><p>We respect your privacy.</p>")
                
        terms_path = os.path.join(self.output_dir, "terms.html")
        if not os.path.exists(terms_path):
            with open(terms_path, 'w', encoding='utf-8') as f:
                f.write("<h1>Terms of Service</h1><p>Use at your own risk.</p>")

    def run(self):
        print("🚀 Starting Generator v8.0...")
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
            
        tools = self.load_data()
        if not tools:
            print("❌ No tools loaded. Aborting.")
            return

        self.generate_pages(tools)
        self.generate_index(tools)
        self.generate_sitemap()
        self.generate_robots()
        self.copy_assets()
        print("✅ Generation Complete.")

if __name__ == "__main__":
    generator = SiteGenerator()
    generator.run()


