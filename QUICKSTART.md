# Quick Start Guide

## 5-Minute Setup

### 1. Get an API Key

Get Claude API key from: https://console.anthropic.com/

### 2. Set Environment Variable

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or on Windows (CMD):
```cmd
set ANTHROPIC_API_KEY=sk-ant-...
```

Or on Windows (PowerShell):
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Interactive Chat

```bash
python miniclaw.py chat
```

## Usage Examples

### Interactive Chat

```bash
$ python miniclaw.py chat

🤖 MiniClaw Assistant (type 'exit' to quit)
==================================================

You: What is machine learning?