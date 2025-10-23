# AvalonRL

## Avalon 6-Player AI Game

A complete implementation of the Avalon board game (6-player version) where all players are controlled by AI using DeepSeek-R1 via Ollama.

## Features

- Full 6-player Avalon game implementation based on the PRD
- All game phases: role assignment, team proposals, voting, missions, and assassination
- Proper role visibility logic (Merlin, Percival, Evil team)
- AI players controlled by DeepSeek-R1 via Ollama
- Strict output parsing to ensure AI follows game rules

## Role Composition (6 Players)

- **Good Team (4 players):**
  - Merlin: Knows all Evil players
  - Percival: Sees Merlin and Morgana (cannot distinguish)
  - Loyal Servant (x2): No special abilities

- **Evil Team (2 players):**
  - Morgana: Appears as Merlin to Percival
  - Assassin: Can kill Merlin if Good wins

## Prerequisites

1. Install Ollama: https://ollama.ai
2. Pull the DeepSeek-R1 model:
   ```bash
   ollama pull deepseek-r1
   ```

## Installation

No additional Python dependencies required - uses only standard library.

## Usage

Run the game:
```bash
python avalon_ai_game.py
```

The game will:
1. Assign roles randomly to 6 AI players
2. Run through mission rounds with AI decision-making for:
   - Team proposals (leader)
   - Voting (all players)
   - Mission actions (team members)
3. Trigger assassination phase if Good wins 3 missions
4. Display final results

## How It Works

### AI Integration

Each decision point calls DeepSeek-R1 via Ollama with:
- Player's role information and visibility
- Current game state
- Strict output format requirements

Example prompt format:
```
You are playing Avalon. You are Merlin. You see the following Evil players: [Eve, Frank]

Mission Status: 1 Success, 0 Fail | Rejections this round: 0/5
Players: [Alice, Bob, Charlie, Diana, Eve, Frank]

You are the leader. You must select exactly 2 players for this mission.

IMPORTANT: Output ONLY a comma-separated list of player names, nothing else.
Example format: Alice,Bob

Your selection:
```

### Output Parsing

The system uses multiple strategies to extract valid choices:
1. Direct text matching
2. Regex pattern matching (brackets, quotes)
3. Fallback to random valid choice if parsing fails

### Game Flow

1. **Role Assignment**: Random distribution with proper 4 Good / 2 Evil split
2. **Mission Rounds**: 5 rounds with team sizes [2, 3, 4, 3, 4]
3. **Team Proposal**: Leader AI proposes team
4. **Voting**: All AI players vote to approve/reject
5. **Mission Execution**: Selected AI players choose Success/Fail
6. **Win Conditions**:
   - Good wins after 3 successful missions (then assassination phase)
   - Evil wins after 3 failed missions OR 5 consecutive rejections
   - Assassination: Evil wins if Assassin correctly identifies Merlin

## Example Output

```
========================================
AVALON - 6 PLAYER GAME
========================================

Role Assignment:
  Alice: Percival (Good)
  Bob: Loyal Servant (Good)
  Charlie: Assassin (Evil)
  Diana: Merlin (Good)
  Eve: Loyal Servant (Good)
  Frank: Morgana (Evil)

========================================
ROUND 1 - Mission requires 2 players
========================================

Leader: Alice
[AI] Alice is proposing a team...
Proposed team: ['Alice', 'Bob']

Voting phase:
  Alice: APPROVE
  Bob: APPROVE
  Charlie: REJECT
  Diana: APPROVE
  Eve: APPROVE
  Frank: REJECT

Result: 4 approve, 2 reject → APPROVED

Mission phase:
  Alice: SUCCESS
  Bob: SUCCESS

Mission Result: SUCCESS
...
```

## Game Rules

- Good players MUST always choose Success on missions
- Evil players MAY choose Success or Fail on missions
- Majority vote required to approve team
- 5 consecutive rejections = automatic Evil win
- First team to win 3 missions triggers endgame
- If Good wins, Assassin gets one chance to identify Merlin

## Notes

- Each AI call has a 60-second timeout
- Maximum 3 retry attempts per decision
- Fallback to random valid choices if AI fails to respond properly
- Good players are forced to choose Success even if AI outputs Fail