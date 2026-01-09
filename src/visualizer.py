import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_charts(csv_file, output_dir, config):
    print("🎨 [Visualizer] Drawing charts...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if not os.path.exists(csv_file):
        print("⚠️ No data file found for visualization.")
        return

    df = pd.read_csv(csv_file)
    plt.style.use('ggplot')
    hero = config['hero_product']
    
    # 获取 Hero 价格
    try:
        hero_row = df[df['Tool_Name'] == hero]
        if not hero_row.empty:
            hero_price = float(hero_row['Price'].values[0])
        else:
            hero_price = 0.0
    except:
        hero_price = 0.0

    for index, row in df.iterrows():
        comp = row['Tool_Name']
        if comp == hero: continue
        
        try:
            comp_price = float(row['Price'])
            
            names = [hero, comp]
            prices = [hero_price, comp_price]
            
            # 修复点：正确的颜色判断逻辑
            # 价格低的显示绿色(#22c55e)，价格高的显示红色(#ef4444)
            colors = []
            for p in prices:
                if p == min(prices):
                    colors.append('#22c55e')
                else:
                    colors.append('#ef4444')

            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(names, prices, color=colors, width=0.5)
            ax.set_title('Monthly Price Comparison', fontsize=10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'${int(height)}', ha='center', va='bottom')

            slug = f"{hero.lower()}-vs-{comp.lower().replace(' ', '-')}"
            plt.savefig(f"{output_dir}/{slug}.png", dpi=100)
            plt.close()
        except Exception as e:
            # 打印错误但不中断整个流程
            print(f"   ⚠️ Could not draw chart for {comp}: {e}")