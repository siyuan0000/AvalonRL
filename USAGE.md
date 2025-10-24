# Usage Guide

## Quick Start

### 1. Start the Game

```bash
python start.py
```

### 2. Choose Launch Mode

```
Launch Mode:
  1. Quick Start (All players use same AI)
  2. Custom Mode (Configure each player individually)

Select mode (1-2, default 1):
```

## Configuration Examples

### Example 1: All Using Ollama DeepSeek-R1

1. Select mode `1` (Quick Start)
2. Select AI backend `1` (Ollama)
3. Enter model name: `deepseek-r1`

The game will run with 6 DeepSeek-R1 instances.

### Example 2: All Using DeepSeek API

1. First, configure API key (choose one method):

   **Method 1: .env.local file (Recommended)**
   ```bash
   # Create .env.local file
   echo "DEEPSEEK_API_KEY=your_api_key_here" > .env.local
   ```

   **Method 2: Environment variable**
   ```bash
   export DEEPSEEK_API_KEY=your_api_key_here
   ```

   **Method 3: Manual input**
   (Enter key when prompted)

2. Select mode `1` (Quick Start)
3. Select AI backend `2` (DeepSeek API)
4. Press Enter for API key (auto-loads from .env.local or environment)
5. Press Enter for model name (use default deepseek-chat)

### Example 3: Mixed Configuration (Different Models per Player)

1. Select mode `2` (Custom Mode)
2. Configure each player:
   - Alice: Ollama - deepseek-r1
   - Bob: Ollama - qwen2.5
   - Charlie: DeepSeek API - deepseek-chat
   - Diana: Ollama - llama3.1
   - Eve: DeepSeek API - deepseek-reasoner
   - Frank: Ollama - mistral

This allows you to compare different models' performance in Avalon!

### Example 4: Using Local Transformers Models

First, install dependencies:
```bash
pip install transformers torch accelerate
```

1. Select mode `1` (Quick Start)
2. Select AI backend `3` (Local Model)
3. Enter model path: `Qwen/Qwen2.5-7B-Instruct`
4. Press Enter for backend type (use default transformers)

Note: Local models will be downloaded to cache on first run, which may take some time.

## Game Flow

After starting, the game runs automatically:

1. **Role Assignment**: System randomly assigns 6 roles
2. **Mission Rounds**: Execute up to 5 mission rounds
   - Leader proposes initial team
   - **Discussion Phase**: Each player (except leader) comments on the proposal
   - Leader makes final decision (can modify team based on discussion)
   - All players vote on final team
   - Team executes mission
3. **Assassination Phase**: If Good wins 3 missions
4. **Result Announcement**: Display final winner and all roles

### What's New: Discussion Phase

Each round now includes strategic discussion:
- Players can express support or concerns about the team
- Evil players can sow doubt or misdirect
- Good players can try to identify suspicious behavior
- Leader considers feedback before finalizing the team
- Makes the game more realistic and strategic!

**Exception**: On the 5th vote attempt (after 4 rejections), discussion is skipped and the team is forced to proceed without voting.

## Environment Variables

### DeepSeek API Key Configuration

The system will try to load your API key in this priority order:
1. **Manual input** during configuration
2. **`.env.local` file** in the project directory (recommended)
3. **Environment variable** `DEEPSEEK_API_KEY`

#### Method 1: .env.local File (Recommended)

Create a `.env.local` file in the project root:

```bash
# Using command line
echo "DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx" > .env.local

# Or manually create the file with this content:
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

**Benefits:**
- Persistent across sessions
- Project-specific
- Already in .gitignore (won't be committed)
- No need to set environment variables

#### Method 2: Environment Variable

```bash
# Linux/Mac
export DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# Windows CMD
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxx"
```

#### Method 3: Manual Input

Simply enter the key when prompted during configuration.

## Troubleshooting

### Ollama Not Found

```
ERROR: Ollama not found
```

**Solution**:
1. Install Ollama: https://ollama.ai
2. Pull model: `ollama pull deepseek-r1`
3. Verify: `ollama list`

### DeepSeek API Error

```
[Error] DeepSeek API key not found
```

**Solution**: Set environment variable `DEEPSEEK_API_KEY`

### Local Model Loading Failed

```
[Error] transformers not installed
```

**Solution**:
```bash
pip install transformers torch accelerate
```

### AI Response Timeout

If you see multiple retries:
```
[Attempt 1] Timeout, retrying...
[Attempt 2] Timeout, retrying...
```

**Solutions**:
- Ollama: Ensure model is loaded correctly `ollama list`
- API: Check network connection
- Local: Check GPU/CPU resources

## Advanced Usage

### Direct Run (Skip Launcher)

Modify the `main()` function in `avalon_ai_game.py` to manually configure AI:

```python
# Example: All using qwen2.5
player_ais = [OllamaAI(model_name='qwen2.5') for _ in range(6)]

game = AvalonGame(player_names)
controller = GameController(game, player_ais)
controller.run_game()
```

### Mix API and Local Models

```python
player_ais = [
    OllamaAI('deepseek-r1'),      # Alice
    OllamaAI('qwen2.5'),          # Bob
    DeepSeekAPI(),                # Charlie
    DeepSeekAPI(),                # Diana
    OllamaAI('llama3.1'),         # Eve
    OllamaAI('mistral'),          # Frank
]
```

## Performance Tips

1. **Ollama**: Fastest, recommended for daily use
2. **DeepSeek API**: Requires network but no local resources
3. **Local Model**: Good for offline use, but needs GPU acceleration

Recommended configurations:
- Testing/Development: Ollama (fast iteration)
- Research/Comparison: Mixed configuration (compare different models)
- Production/Demo: DeepSeek API (stable and reliable)

## Logging and Debugging

The game outputs detailed decision-making process:
- `[AI] {player} is proposing a team...` - AI is thinking
- `[Attempt X]` - Retry information
- `[Fallback]` - Using fallback strategy

For debugging, you can view the AI's raw output (add print statements in the code).
