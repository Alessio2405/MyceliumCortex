# Getting Started with MiniClaw

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Anthropic API key (or OpenAI key)

## Step-by-Step Setup

### Step 1: Get an API Key

**For Anthropic (Claude):**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to the API keys section
4. Create a new API key
5. Copy it (keep it secret!)

**For OpenAI (GPT):**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to the API keys section
4. Create a new API key
5. Copy it

### Step 2: Set Environment Variable

**On macOS/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxx"
```

Or add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

**On Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**On Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxx"
```

**On Windows (Permanent):**
1. Press `Win + R`
2. Type `sysdm.cpl`
3. Click "Environment Variables"
4. Click "New" (User variables)
5. Variable name: `ANTHROPIC_API_KEY`
6. Variable value: `sk-ant-xxxxxxxxxxxxx`
7. Click OK

### Step 3: Install Dependencies

```bash
# Navigate to project directory
cd miniclaw

# Install required packages
pip install -r requirements.txt
```

**Troubleshooting:**
- If you get permission errors, try: `pip install --user -r requirements.txt`
- If anthropic is not found, ensure it installed: `pip show anthropic`

### Step 4: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Check installed packages
pip list | grep anthropic
pip list | grep openai

# Check API key is set
python -c "import os; print('API Key set:', bool(os.environ.get('ANTHROPIC_API_KEY')))"
```

### Step 5: First Run

**Interactive Chat:**
```bash
python miniclaw.py chat
```

You should see:
```
🤖 MiniClaw Assistant (type 'exit' to quit)
==================================================

You: _
```

Type a message and press Enter!

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution:**
```bash
pip install anthropic
# or
pip install -r requirements.txt
```

### Issue: "ANTHROPIC_API_KEY not found" or "Unauthorized"

**Solution:**
1. Verify you set the API key: `echo $ANTHROPIC_API_KEY`
2. Check the key is correct in console.anthropic.com
3. Restart your terminal after setting the env variable
4. On Windows, restart your IDE/terminal completely

### Issue: "Invalid API key provided"

**Solution:**
1. Check your API key has no extra spaces: `echo "$ANTHROPIC_API_KEY"`
2. Verify it starts with `sk-ant-` (Anthropic) or `sk-` (OpenAI)
3. Check it's still active in the console
4. Try regenerating a new API key

### Issue: "Connection timeout" or "Network error"

**Solution:**
1. Check your internet connection
2. Verify Anthropic API is not down: https://status.anthropic.com/
3. Try a different network or VPN
4. Check firewall isn't blocking the connection

### Issue: Python version too old

**Solution:**
```bash
# Check your Python version
python --version

# If < 3.10, install Python 3.10+
# Visit: https://www.python.org/downloads/

# Or use a package manager:
# macOS: brew install python@3.10
# Ubuntu: sudo apt-get install python3.10
```

## Verification Checklist

- [ ] Python 3.10+ installed
- [ ] API key obtained
- [ ] API key set in environment
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Can run: `python miniclaw.py status` (shows "Ready")
- [ ] Can run: `python miniclaw.py message "test"` (gets response)
- [ ] Can run: `python miniclaw.py chat` (interactive mode works)

## Next Steps

Once verified, try:

1. **Explore examples:**
   ```bash
   python examples.py
   ```

2. **Read documentation:**
   - README.md - Overview
   - QUICKSTART.md - Quick reference
   - ARCHITECTURE.txt - System design
   - EXTENSIONS.md - How to extend

3. **Create a conversation:**
   ```bash
   python miniclaw.py chat --user "your_name"
   ```

4. **Try different models:**
   Edit `~/.miniclaw/config.json` and change the model to:
   - `claude-3-opus-20250219` (most capable)
   - `claude-3-5-sonnet-20241022` (best balanced)
   - `claude-3-haiku-20250307` (fastest)

5. **Use OpenAI instead:**
   Edit `~/.miniclaw/config.json`:
   ```json
   {
     "llm": {
       "provider": "openai",
       "model": "gpt-4-turbo",
       "api_key": "your-openai-key"
     }
   }
   ```

## Getting Help

1. Check **QUICKSTART.md** for quick commands
2. Read **IMPLEMENTATION.md** for technical details
3. See **EXTENSIONS.md** for customization
4. Review **examples.py** for code examples
5. Check **ARCHITECTURE.txt** for system design

## What to Do Next

- [ ] Follow steps 1-5 above
- [ ] Verify with the checklist
- [ ] Run `python miniclaw.py chat`
- [ ] Have a conversation with the AI
- [ ] Read the documentation
- [ ] Try the examples
- [ ] Create your first custom agent

Enjoy! 🚀
