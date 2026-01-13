from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="nl2cmd-ai",
    version="3.0.3",
    author="Cosy-y",
    author_email="your.email@example.com",
    description="Natural Language to Command Line Interface - Hybrid ML + Rule Engine with Git Support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Cosy-y/NL2CMD",
    packages=find_packages(),
    py_modules=[
        "main",
        "windows_cmd",
        "linux_cmd",
        "safety",
        "command_processor",
        "input_processor",
        "output_handler",
        "ml_predictor",
        "intelligence_engine",
        "fuzzy_matcher",
        "parameter_extractor",
        "train_model",
        "multi_command_processor"
    ],
    install_requires=[
        "pyperclip>=1.8.2",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "rapidfuzz>=3.0.0",
        "python-Levenshtein>=0.21.0",
        "fuzzywuzzy>=0.18.0",
        "nltk>=3.8.0",
        "sentence-transformers>=2.2.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "reportlab>=4.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "twine>=4.0.0",
            "wheel>=0.37.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "n2c=main:main",
            "nl2cmd=main:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    python_requires=">=3.8",
    keywords="cli, command-line, natural-language, ml, ai, automation, git, shell, terminal",
    include_package_data=True,
    package_data={
        "": ["*.json", "*.pkl", "*.txt", "*.md", "*.bat", "*.sh"]
    },
    project_urls={
        "Bug Reports": "https://github.com/Cosy-y/NL2CMD/issues",
        "Source": "https://github.com/Cosy-y/NL2CMD",
        "Documentation": "https://github.com/Cosy-y/NL2CMD/blob/main/COMPLETE_PROJECT_DOCUMENTATION.md"
    }
)
