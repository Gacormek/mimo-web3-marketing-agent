"""MiMo Web3 Marketing Agent - Package Setup."""

from setuptools import setup, find_packages

setup(
    name="mimo-web3-marketing-agent",
    version="1.0.0",
    description="AI-powered multi-agent system for Web3 marketing automation",
    author="MiMo Team",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "httpx>=0.25.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "web3>=6.11.0",
        "chromadb>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)
