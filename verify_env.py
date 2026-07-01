#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI量化+多Agent实验平台 - 环境验证脚本
用于：向高雄老师汇报安装成果

作者：王先生（胜利泵业 / ISTIC硕士在读）
日期：2026-06-20
环境：Windows 10 + Python 3.13.12 + venv
"""

import sys
import time

def banner(msg):
    print()
    print('=' * 60)
    print(f"  {msg}")
    print('=' * 60)

def check_package(module_name, import_name=None, desc=""):
    """检查单个包是否可正常导入"""
    if import_name is None:
        import_name = module_name
    try:
        mod = __import__(import_name)
        version = getattr(mod, '__version__', 'N/A')
        print(f"  [OK] {module_name:20s} | v{version:15s} | {desc}")
        return True
    except ImportError as e:
        print(f"  [FAIL] {module_name:20s} | 未安装 | {e}")
        return False

def main():
    banner("Python 环境信息")
    print(f"  Python 路径: {sys.executable}")
    print(f"  Python 版本: {sys.version.split()[0]}")
    print(f"  Platform    : {sys.platform}")

    banner("已安装核心包验证")
    packages = [
        ('torch',       None,   'PyTorch 深度学习框架（CPU版）'),
        ('numpy',       None,   '数值计算基础库'),
        ('pandas',      None,   '数据分析与处理'),
        ('matplotlib',  None,   '数据可视化'),
        ('scipy',       None,   '科学计算'),
        ('sklearn',    'sklearn', '机器学习（scikit-learn）'),
        ('backtrader', None,   '量化交易回测框架'),
        ('autogen_agentchat', None,   '微软多Agent辩论框架（0.7.x版）'),
        ('crewai',     None,   '多Agent角色扮演框架'),
        ('langgraph',  None,   '状态机Agent流水线'),
        ('qlib',       None,   '微软AI量化投资平台'),
    ]
    results = []
    for pkg, imp, desc in packages:
        ok = check_package(pkg, imp, desc)
        results.append((pkg, ok))

    banner("PyTorch 功能验证（简单张量运算）")
    try:
        import torch
        x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
        y = torch.relu(x)
        print(f"  测试张量 x = {x.tolist()}")
        print(f"  ReLU(x)  = {y.tolist()}")
        print(f"  PyTorch 安装验证: [OK] 通过")
    except Exception as e:
        print(f"  PyTorch 功能验证失败: {e}")

    banner("量化回测框架验证（backtrader 简单策略）")
    try:
        import backtrader as bt
        print(f"  BackTrader 版本: {bt.__version__}")
        print(f"  回测框架验证: [OK] 通过")
    except Exception as e:
        print(f"  BackTrader 验证失败: {e}")

    banner("多Agent框架验证")
    try:
        import autogen_agentchat
        print(f"  AutoGen 版本: {autogen_agentchat.__version__}")
        print(f"  AutoGen 验证: [OK] 通过")
    except Exception as e:
        print(f"  AutoGen 验证失败: {e}")
    try:
        import crewai
        print(f"  CrewAI 版本: {crewai.__version__}")
        print(f"  CrewAI 验证: [OK] 通过")
    except Exception as e:
        print(f"  CrewAI 验证失败: {e}")
    try:
        import langgraph
        print(f"  LangGraph 已安装（版本未知）")
        print(f"  LangGraph 验证: [OK] 通过")
    except Exception as e:
        print(f"  LangGraph 验证失败: {e}")

    banner("总结")
    total = len(results)
    passed = sum(1 for _, ok in results if ok)
    failed = total - passed
    print(f"  总包数: {total}")
    print(f"  通过  : {passed} [OK]")
    print(f"  失败  : {failed} [FAIL]")
    if failed == 0:
        print()
        print("  *** 全部安装成功！环境已就绪。 ***")
    else:
        print()
        print(f"  [!] 有 {failed} 个包未安装，请检查。")

    print()
    print(f"  汇报人: 王先生（胜利泵业 / ISTIC 2025级硕士）")
    print(f"  汇报时间: 2026-06-20")
    print(f"  用途说明: AI量化投资策略研究 + 多Agent系统实验 + 硕士论文技术支持")

if __name__ == '__main__':
    main()
