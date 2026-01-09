import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_charts(csv_file, output_dir, config):
    print("🎨 [Visualizer] Drawing charts...")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 如果没有丰富数据，尝试读取原始数据
    if not os.path.exists(csv_file):
        print("⚠️ No data file found for visualization.")
        return

    df = pd.read_csv(csv_file)
    plt.style.use('ggplot')
    hero = config['hero_product']
    
    # 尝试获取 Hero 价格，处理异常
    try:
        hero_price = float(df[df['Tool_Name'] == hero]['Price'].values[0])
    except:
        hero_price = 0

    for index, row in df.iterrows():
        comp = row['Tool_Name']
        if comp == hero: continue
        
        try:
            comp_price = float(row['Price'])
            
            names = [hero, comp]
            prices = [hero_price, comp_price]
            colors = ['#22c55e' if p <= comp_price else '#ef4444', '#ef4444' if p > comp_price else '#22c55e'] # 简单逻辑：便宜的绿色

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
            print(f"   ⚠️ Could not draw chart for {comp}: {e}")