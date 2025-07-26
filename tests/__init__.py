"""
测试模块初始化文件
"""

import sys
import os

# 添加项目根目录到Python路径，以便测试文件能够导入app模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
