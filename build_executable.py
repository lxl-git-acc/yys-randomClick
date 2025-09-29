#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
随机鼠标点击器打包脚本
用于将Python程序打包成独立的可执行文件
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# 确保中文显示正常
os.environ['PYTHONIOENCODING'] = 'utf-8'

# ========== 用户可配置部分 ==========
# 版本号（用户可以自行修改）
VERSION = '1.0.5'

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 主程序文件
MAIN_SCRIPT = PROJECT_ROOT / 'random_clicker.py'

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / 'dist'

# 临时目录
BUILD_DIR = PROJECT_ROOT / 'build'

# 图标文件（如果有）
ICON_FILE = None  # 可以设置为.ico文件路径


def check_dependencies():
    """检查必要的依赖是否已安装"""
    try:
        # 检查PyInstaller是否已安装
        subprocess.run(['pip', 'show', 'pyinstaller'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("PyInstaller 已安装")
    except subprocess.CalledProcessError:
        print("正在安装 PyInstaller...")
        subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
    
    try:
        # 检查主程序依赖是否已安装
        subprocess.run(['pip', 'install', '-r', str(PROJECT_ROOT / 'requirements.txt')], check=True)
        print("主程序依赖已安装")
    except subprocess.CalledProcessError:
        print("安装依赖时出错，尝试单独安装pyautogui...")
        subprocess.run(['pip', 'install', 'pyautogui'], check=True)


def clean_build_files():
    """清理之前的构建文件"""
    if OUTPUT_DIR.exists():
        print(f"清理输出目录: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    
    if BUILD_DIR.exists():
        print(f"清理构建目录: {BUILD_DIR}")
        shutil.rmtree(BUILD_DIR)


def build_executable():
    """使用PyInstaller构建可执行文件"""
    # 构建PyInstaller命令
    cmd = [
        'pyinstaller',
        '--onefile',  # 创建单个可执行文件
        '--windowed',  # 不显示控制台窗口
        f'--name=随机鼠标点击器_v{VERSION}',  # 可执行文件名称（含版本号）
        f'--distpath={OUTPUT_DIR}',
        f'--workpath={BUILD_DIR}',
    ]
    
    # 添加图标（如果有）
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.append(f'--icon={ICON_FILE}')
    
    # 添加主脚本
    cmd.append(str(MAIN_SCRIPT))
    
    # 执行构建命令
    print(f"开始构建可执行文件，命令: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"构建完成！可执行文件位于: {OUTPUT_DIR}")
        
        # 复制README文件到输出目录
        readme_src = PROJECT_ROOT / 'README.md'
        if readme_src.exists():
            readme_dst = OUTPUT_DIR / 'README.md'
            shutil.copy2(readme_src, readme_dst)
            print(f"已复制README.md到输出目录")
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        sys.exit(1)


def create_portable_version():
    """创建便携版本的压缩包"""
    if not OUTPUT_DIR.exists():
        print("输出目录不存在，无法创建便携版本")
        return
    
    # 创建ZIP压缩包
    if platform.system() == 'Windows':
        zip_name = f'点击器_v{VERSION}.zip'
        zip_path = PROJECT_ROOT / zip_name
        
        try:
            import zipfile
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(OUTPUT_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, OUTPUT_DIR)
                        zipf.write(file_path, arcname)
            print(f"便携版本压缩包已创建: {zip_path}")
        except Exception as e:
            print(f"创建压缩包失败: {e}")


def main():
    """主函数"""
    print(f"==== 随机鼠标点击器打包工具 v{VERSION} ====")
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"当前版本: v{VERSION}")
    print("提示: 如需修改版本号，请编辑脚本顶部的VERSION变量")
    
    # 检查依赖
    check_dependencies()
    
    # 清理之前的构建文件
    clean_build_files()
    
    # 构建可执行文件
    build_executable()
    
    # 创建便携版本
    create_portable_version()
    
    print("\n打包完成！")
    print(f"可执行文件位置: {OUTPUT_DIR}\随机鼠标点击器_v{VERSION}.exe")
    if platform.system() == 'Windows':
        print(f"便携版本: 随机鼠标点击器_v{VERSION}_便携版.zip")
    print("\n注意事项:")
    print("1. 生成的可执行文件可以在没有安装Python的电脑上运行")
    print("2. 如需在其他操作系统上运行，请在对应系统上重新打包")
    print("3. 便携版本可以直接解压使用，无需安装")


if __name__ == '__main__':
    main()