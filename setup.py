"""Setup script for MiniClaw."""

from setuptools import setup, find_packages

setup(
    name="miniclaw",
    version="0.1.0",
    description="Lightweight hierarchical multi-agent AI assistant",
    author="MiniClaw Team",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "anthropic>=0.7.0",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "miniclaw=miniclaw:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
