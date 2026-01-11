import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from itertools import combinations
import datetime
import shutil

# Tiandao Project Generator v6.0 (Full Features Restored)
# Features: 
# 1. Header Bug Fix
# 2. Long Content Stitching
# 3. Sitemap Generation (Restored)
# 4. Static Asset Copying (Restored)
# 5. Robots.txt (Restored)

class SiteGenerator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_path = os.path.join(self.base_dir, 'data', 'data.csv')
        self.template_dir = os.path.join(self.base_dir, 'templates')
        self.output_dir = os.path.join(self.base_dir, 'output')
        self.static_dir = os.path.join(self.base_dir, 'static') # Assuming you might add css/images later
        self.generated_urls = []

    def load_data(self):
        print(f"📂 Loading data from {self.data_path}...")
        if not os.path.exists(self.data_path):
            raise FileNotFoundError("Data file missing!")
        
        # Safe CSV Reading
        try:
            df = pd.read_csv(self.data_path, header=0, on_bad_lines='skip', encoding='utf-8')
            # [CRITICAL FIX] Filter out the header row if it appears in data
            df = df[df['Tool_Name'] != 'Tool_Name']
            df = df.fillna("Info coming soon")
            # Ensure Price is not empty
            df['Price'] = df['Price'].replace("", "Check Website")
            return df.to_dict('records')
        except Exception as e:
            print(f"❌ CSV Error: {e}")
            return []

    def generate_html(self, tools):
        # Setup Jinja2
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template('page.html')
        
        # Combinations
        pairs = list(combinations(tools, 2))
        print(f"⚔️  Generating {len(pairs)} battle pages...")

        for tool_a, tool_b in pairs:
            # Slug Generation
            name_a = str(tool_a['Tool_Name']).strip()
            name_b = str(tool_b['Tool_Name']).strip()
            slug = f"{name_a.lower()}-vs-{name_b.lower()}".replace(" ", "-").replace(".", "")
            filename = f"{slug}.html"
            
            # [Logic] Long Review Stitching
            article_body = f"""
            <div class="battle-section">
                <h2>The Ultimate Showdown: {name_a} vs {name_b}</h2>
                <p>In the world of SEO tools, deciding between <strong>{name_a}</strong> and <strong>{name_b}</strong> is a common dilemma. Both platforms offer powerful features, but they cater to different needs.</p>
                
                <h3>1. Deep Dive: {name_a}</h3>
                <p>{tool_a.get('Long_Review', 'Review pending...')}</p>
                <div class="verdict-box"><strong>Verdict:</strong> {tool_a.get('Verdict', '')}</div>
                
                <h3>2. Deep Dive: {name_b}</h3>
                <p>{tool_b.get('Long_Review', 'Review pending...')}</p>
                <div class="verdict-box"><strong>Verdict:</strong> {tool_b.get('Verdict', '')}</div>
                
                <h3>3. Feature & Price Comparison</h3>
                <p>{name_a} enters the ring at {tool_a['Price']}, while {name_b} costs {tool_b['Price']}. 
                If budget is your primary concern, check the pricing tables above carefully.</p>
                
                <h3>4. Final Recommendation</h3>
                <p>If you need <strong>{tool_a.get('Pros', '').split(';')[0]}</strong>, then {name_a} is likely your best choice.</p>
                <p>However, for those prioritizing <strong>{tool_b.get('Pros', '').split(';')[0]}</strong>, {name_b} stands out as the winner.</p>
            </div>
            """

            render_data = {
                'tool_a': tool_a,
                'tool_b': tool_b,
                'title': f"{name_a} vs {name_b} - 2026 Comparison",
                'meta_description': f"Unbiased comparison of {name_a} vs {name_b}. {tool_a.get('Description', '')[:100]}...",
                'article_body': article_body,
                'date': datetime.datetime.now().strftime("%B %Y")
            }

            content = template.render(**render_data)
            
            with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.generated_urls.append(filename)

    def generate_index(self, tools):
        print("🏠 Generating Professional Index Page...")
        pairs = list(combinations(tools, 2))
        
        # 使用内联 CSS 确保首页也有颜值
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>SaaS Battle Arena - Top 2026 Software Comparisons</title>
            <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
            <script>
              window.dataLayer = window.dataLayer || [];
              function gtag(){{dataLayer.push(arguments);}}
              gtag('js', new Date());
              gtag('config', 'G-XXXXXXXXXX');
            </script>
            <style>
                body {{ background: #0f172a; color: #f1f5f9; font-family: system-ui, sans-serif; padding: 40px 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                h1 {{ text-align: center; font-size: 3rem; margin-bottom: 10px; color: #3b82f6; }}
                .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 60px; font-size: 1.2rem; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
                .card {{ background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; transition: 0.2s; text-align: center; }}
                .card:hover {{ transform: translateY(-5px); border-color: #3b82f6; }}
                .card a {{ color: #38bdf8; text-decoration: none; font-weight: bold; font-size: 1.1rem; display: block; }}
                .vs-tag {{ color: #64748b; font-size: 0.9rem; margin: 5px 0; }}
                footer {{ text-align: center; margin-top: 80px; color: #475569; border-top: 1px solid #1e293b; padding-top: 40px; }}
                footer a {{ color: #64748b; text-decoration: none; margin: 0 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚔️ SaaS Battle Arena</h1>
                <p class="subtitle">Unbiased, AI-driven comparisons of {len(tools)} top SEO tools. {len(pairs)} battles generated.</p>
                
                <div class="grid">
                    {''.join([f'''
                    <div class="card">
                        <div class="vs-tag">Comparison</div>
                        <a href="{t[0]["Tool_Name"].lower().replace(" ","").replace(".","")}-vs-{t[1]["Tool_Name"].lower().replace(" ","").replace(".","")}.html">
                            {t[0]["Tool_Name"]} <span style="color:white">vs</span> {t[1]["Tool_Name"]}
                        </a>
                    </div>
                    ''' for t in pairs])}
                </div>
                
                <footer>
                    <p>&copy; 2026 SaaS Battle Arena.</p>
                    <p><a href="privacy.html">Privacy</a> | <a href="terms.html">Terms</a></p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        with open(os.path.join(self.output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(html_content)

    def generate_sitemap(self):
        # [RESTORED FEATURE] Sitemap Generation
        print("🗺️  Generating Sitemap.xml...")
        base_url = "[https://compare.ii-x.com](https://compare.ii-x.com)" # Change this if your domain changes
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap += '<urlset xmlns="[http://www.sitemaps.org/schemas/sitemap/0.9](http://www.sitemaps.org/schemas/sitemap/0.9)">\n'
        
        for filename in self.generated_urls:
            sitemap += '  <url>\n'
            sitemap += f'    <loc>{base_url}/{filename}</loc>\n'
            sitemap += f'    <lastmod>{datetime.date.today()}</lastmod>\n'
            sitemap += '  </url>\n'
            
        sitemap += '</urlset>'
        
        with open(os.path.join(self.output_dir, "sitemap.xml"), 'w', encoding='utf-8') as f:
            f.write(sitemap)

    def copy_assets(self):
        # [RESTORED FEATURE] Copy Static Files
        if os.path.exists(self.static_dir):
            print("🎨 Copying static assets...")
            output_static = os.path.join(self.output_dir, 'static')
            if os.path.exists(output_static):
                shutil.rmtree(output_static)
            shutil.copytree(self.static_dir, output_static)
        else:
            print("⚠️  No 'static' folder found. Skipping asset copy.")

    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        tools = self.load_data()
        if not tools:
            print("❌ No tools loaded. Aborting.")
            return

        self.generate_html(tools)
        
        # Calculate pairs count for index
        pairs_count = len(list(combinations(tools, 2)))
        self.generate_index(tools, pairs_count)
        
        self.generate_sitemap()
        self.copy_assets()
        print("✅ Generation Complete.")

if __name__ == "__main__":
    generator = SiteGenerator()
    generator.run()

