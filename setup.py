from setuptools import setup, find_packages

setup(
    name="cc-switch",
    version="0.1.0",
    description="国产化 AI 编程工具切换器 - 桌面 GUI",
    author="fast118 / wudijia2026",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "cc-switch=cc_switch.__main__:main",
        ],
    },
)