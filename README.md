# NL2CMD - Natural Language to Command Line Interface

[![PyPI version](https://badge.fury.io/py/nl2cmd-ai.svg)](https://badge.fury.io/py/nl2cmd-ai)
[![Python Support](https://img.shields.io/pypi/pyversions/nl2cmd-ai.svg)](https://pypi.org/project/nl2cmd-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Transform natural language into command-line instructions instantly!**

NL2CMD v3.0 is an intelligent command-line interface that converts natural language queries into actual shell commands using a hybrid ML + Rule-based approach with Git support.

## ✨ Key Features

- 🧠 **5-Layer Hybrid Intelligence** (Template Engine + ML + Fuzzy Search + Problem Diagnosis + Rules)
- 🔗 **Multi-Command Chaining** ("create folder X and create file Y")
- 🔧 **Git Integration** (118 Git commands supported)
- 🎯 **Dynamic Parameter Extraction** (handles custom filenames, processes, URLs)
- 🛡️ **Safety Validation** (prevents dangerous commands)
- 🔍 **Typo Tolerance** (fuzzy matching with RapidFuzz)
- 🖥️ **Cross-Platform** (Windows, Linux, macOS)
- ⚡ **Offline Operation** (no API dependencies)

## 🚀 Quick Start

### Installation
```bash
pip install nl2cmd-ai
```

### Usage
```bash
# Single command mode
n2c "list all files"
n2c "create file config.json"
n2c "check git status"
n2c "kill process chrome"

# Interactive mode
n2c -i
n2c> show system info
n2c> create folder project and create file readme.txt
n2c> good  # Mark command as correct
n2c> exit

# Training
n2c --train     # Train ML model
n2c --retrain   # Retrain with feedback
```

## 💡 Examples

### Basic Commands
```bash
n2c "list all files"              → dir / ls
n2c "show system information"     → systeminfo / uname -a
n2c "check disk health"           → wmic diskdrive get status
n2c "find large files"            → forfiles /S /M * /C "cmd /c if @fsize GEQ 104857600 echo @path"
```

### Parameterized Commands
```bash
n2c "create file config.json"     → echo. > config.json
n2c "create folder Documents"     → mkdir Documents
n2c "kill process firefox"        → taskkill /IM firefox.exe /F
n2c "copy file src.txt to dst.txt" → copy src.txt dst.txt
```

### Git Commands
```bash
n2c "check git status"            → git status
n2c "push to github"              → git push
n2c "create new branch feature"   → git branch feature
n2c "commit changes with message" → git commit -m "Update"
```

### Multi-Command Chaining
```bash
n2c "create folder project and create file readme.txt"
→ mkdir project && echo. > readme.txt

n2c "list files then show system info"
→ dir && systeminfo
```

## 🏗️ Architecture

NL2CMD uses a **5-layer hybrid intelligence system**:

1. **Template Engine** (95% confidence) - Dynamic parameter extraction
2. **ML Predictor** (60-100% confidence) - Random Forest on 2,189 examples
3. **Problem Diagnosis** (90% confidence) - Error-to-solution mapping
4. **Fuzzy Search** (60-100% confidence) - Typo tolerance
5. **Rule Matcher** (100% confidence) - Hardcoded fallback

## 📊 Statistics

- **2,189 Commands** (601 Windows + 1,470 Linux + 118 Git)
- **278 Unique Intents**
- **73.98% ML Accuracy**
- **14 Command Categories**
- **5 Intelligence Methods**

## 🛠️ Development

### Local Setup
```bash
git clone https://github.com/Cosy-y/NL2CMD.git
cd NL2CMD
pip install -r requirements.txt
python train_model.py
n2c "test command"
```

### Building Package
```bash
pip install build twine
python -m build
twine upload dist/*
```

## 📚 Documentation

For complete documentation, architecture details, and development guide, see:
- [Complete Project Documentation](https://github.com/Cosy-y/NL2CMD/blob/main/COMPLETE_PROJECT_DOCUMENTATION.md)
- [Usage Guide](https://github.com/Cosy-y/NL2CMD/blob/main/N2C_USAGE_GUIDE.md)
- [Architecture Overview](https://github.com/Cosy-y/NL2CMD/blob/main/ARCHITECTURE.md)

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] Expand to 18,000 commands
- [ ] Add voice interface
- [ ] Web UI
- [ ] Plugin system
- [ ] Cloud sync

---

**Transform your command-line experience with natural language!** 🚀

