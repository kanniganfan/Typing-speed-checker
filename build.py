#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打字速度检测器 - 打包脚本
使用PyInstaller将程序打包为可执行文件
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("📦 正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['customtkinter', 'zhipuai', 'requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='打字速度检测器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('typing_speed_test.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ 配置文件已创建: typing_speed_test.spec")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    try:
        # 使用spec文件构建
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "typing_speed_test.spec"
        ])
        print("✅ 构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_portable_package():
    """创建便携版包"""
    print("📦 创建便携版包...")
    
    # 创建发布目录
    release_dir = "打字速度检测器_便携版"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # 复制可执行文件
    exe_path = os.path.join("dist", "打字速度检测器.exe")
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, release_dir)
        print(f"✅ 可执行文件已复制到 {release_dir}")
    else:
        print("❌ 找不到可执行文件")
        return False
    
    # 创建说明文件
    readme_content = """# 🚀 打字速度检测器 - 便携版

## 📖 使用说明

1. **直接运行**: 双击 `打字速度检测器.exe` 即可启动程序
2. **无需安装**: 这是便携版，无需安装Python环境
3. **功能完整**: 包含所有功能（中英文切换、AI文本生成、历史记录等）

## ✨ 主要功能

- 🎯 实时WPM计算和准确率统计
- 🌍 中英文切换支持
- 🤖 AI文本生成（需配置API Key）
- 📊 专业测试报告
- 💾 历史记录保存
- ⚙️ 个性化设置

## 🔧 AI功能配置

1. 点击程序中的"⚙️ 设置"按钮
2. 输入智谱AI的API Key
3. 获取地址: https://bigmodel.cn/dev/activities/free/glm-4-flash

## 📁 文件说明

- `打字速度检测器.exe` - 主程序
- `typing_history.json` - 历史记录文件（自动生成）
- `config.json` - 配置文件（自动生成）

## 🎮 快速开始

1. 运行程序
2. 选择语言模式（中文/英文）
3. 开始打字练习
4. 查看详细的测试报告

---

**享受打字练习的乐趣！** 🎯
"""
    
    with open(os.path.join(release_dir, "使用说明.txt"), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 便携版包已创建: {release_dir}")
    return True

def clean_build_files():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    
    # 清理目录
    dirs_to_clean = ["build", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 已清理: {dir_name}")
    
    # 清理文件
    files_to_clean = ["typing_speed_test.spec"]
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"✅ 已清理: {file_name}")

def main():
    """主打包流程"""
    print("🚀 打字速度检测器 - 自动打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，请手动安装:")
            print("   pip install pyinstaller")
            return
    
    # 检查主程序文件
    if not os.path.exists("main.py"):
        print("❌ 找不到主程序文件 main.py")
        return
    
    print("\n📋 开始打包流程...")
    
    # 创建配置文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        return
    
    # 创建便携版包
    if not create_portable_package():
        return
    
    # 清理构建文件
    clean_build_files()
    
    print("\n🎉 打包完成!")
    print("=" * 50)
    print("📁 输出文件:")
    print("   - 便携版: 打字速度检测器_便携版/")
    print("   - 可执行文件: 打字速度检测器_便携版/打字速度检测器.exe")
    print("\n💡 使用提示:")
    print("   1. 直接运行可执行文件即可使用")
    print("   2. 可以将整个文件夹复制到任何地方使用")
    print("   3. 查看'使用说明.txt'了解详细功能")

if __name__ == "__main__":
    main()
