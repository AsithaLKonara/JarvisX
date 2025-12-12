"""
Setup script for desktop application
"""
from setuptools import setup, find_packages

setup(
    name="jarvisx-v2-desktop",
    version="2.0.0",
    description="JarvisX V2 Desktop Application",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.0",
        "requests>=2.31.0",
        "websocket-client>=1.6.0",
        "PyJWT>=2.8.0",
        "cryptography>=41.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "jarvisx-desktop=src.main:main",
        ],
    },
)

