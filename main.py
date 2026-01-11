import sys
import os
import runpy
import glob

# 设置路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
data_path = os.path.join(current_dir, 'data', 'data.csv')
output_dir = os.path.join(current_dir, 'output') # 假设默认输出目录是 output

if src_dir not in sys.path:
    sys.path.append(src_dir)

print("="*40)
print("🚀 Tiandao Project Diagnostics Mode")
print(f"📂 Working Directory: {current_dir}")
print(f"🔎 Looking for data at: {data_path}")

# 1. 检查数据是否存在
if os.path.exists(data_path):
    print("✅ Data file FOUND.")
    with open(data_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"📊 Data line count: {len(lines)}")
else:
    print("❌ CRITICAL: Data file NOT found! Generator will likely do nothing.")
    # 尝试列出当前目录有什么，帮我们找文件
    print("Files in current dir:", os.listdir(current_dir))
    if os.path.exists(os.path.join(current_dir, 'data')):
         print("Files in data dir:", os.listdir(os.path.join(current_dir, 'data')))

print("="*40)
print("▶️  Running Generator...")

try:
    # 运行生成器
    runpy.run_module('src.generator', run_name='__main__')
    print("✅ Generator execution finished.")

    print("="*40)
    print("🕵️ Post-Run Check:")
    # 检查输出了什么
    if os.path.exists(output_dir):
        files = glob.glob(os.path.join(output_dir, '*.html'))
        print(f"📁 Output Directory exists: {output_dir}")
        print(f"📄 Generated HTML files: {len(files)}")
        if len(files) > 0:
            print(f"   Example: {files[0]}")
        else:
            print("⚠️  Warning: Output directory is empty!")
    else:
        print(f"❌ Output directory not found at: {output_dir}")
        print("   Did the generator save to a different folder? (e.g., 'dist', 'site')")
        print("   Current dirs:", [d for d in os.listdir(current_dir) if os.path.isdir(d)])

except Exception as e:
    print(f"❌ Error during execution: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
