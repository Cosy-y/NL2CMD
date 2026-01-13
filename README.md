NL2CMD - Natural Language to Command Line Interface

[![PyPI version](https://badge.fury.io/py/nl2cmd-ai.svg)](https://badge.fury.io/py/nl2cmd-ai)
[![Python Support](https://img.shields.io/pypi/pyversions/nl2cmd-ai.svg)](https://pypi.org/project/nl2cmd-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform natural language into command-line instructions instantly

NL2CMD  is an intelligent command-line interface that converts natural language queries into actual shell commands using a hybrid ML + Rule-based approach and works on multiple platform windows and linux



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

##  Examples

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


Sem 5 project

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

