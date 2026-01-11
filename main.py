import sys
import os
import runpy

# 设置路径，确保能找到 src
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)

print("🚀 Starting Tiandao Project v4.5 Generator...")

try:
    # 【核心修复】
    # 不再去 import 具体的函数名（如 generate_pages），而是直接运行 generator 模块本身。
    # 这样无论 v4.5 内部是 main() 还是 class，都会自动执行其 if __name__ == "__main__": 下的逻辑。
    runpy.run_module('src.generator', run_name='__main__')
    
    print("✅ Generator execution completed.")

except Exception as e:
    print(f"❌ Critical Error executing src.generator: {e}")
    # 打印错误详情以便调试
    import traceback
    traceback.print_exc()
    sys.exit(1)
