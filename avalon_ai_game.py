import random
import subprocess
import json
import re
import os
from typing import Optional
from pathlib import Path


class Player:
    """Represents a player in the Avalon game."""

    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.is_evil = role in ['Morgana', 'Assassin']

    def __repr__(self):
        return f"{self.name} ({self.role})"


class AvalonGame:
    """Main game engine for 6-player Avalon."""

    # Mission configuration for 6 players
    MISSION_SIZES = [2, 3, 4, 3, 4]

    def __init__(self, player_names):
        """Initialize game with 6 players."""
        self.players = self.assign_roles(player_names)
        self.leader_index = random.randint(0, 5)
        self.mission_results = []  # True = Success, False = Fail
        self.rejection_count = 0
        self.current_round = 0

        # Display initial game state
        print("\n" + "="*60)
        print("AVALON - 6 PLAYER GAME")
        print("="*60)
        print("\nRole Assignment:")
        for p in self.players:
            print(f"  {p.name}: {p.role} ({'Evil' if p.is_evil else 'Good'})")
        print("\n" + "="*60)

    def assign_roles(self, player_names):
        """Assign roles according to 6-player setup."""
        roles = ['Merlin', 'Percival', 'Loyal Servant', 'Loyal Servant', 'Morgana', 'Assassin']
        random.shuffle(roles)
        return [Player(name, role) for name, role in zip(player_names, roles)]

    def get_role_visibility(self, player):
        """Get what information a player can see based on their role."""
        info = []

        if player.role == 'Merlin':
            # Merlin sees all Evil players
            evil_players = [p.name for p in self.players if p.is_evil]
            info.append(f"You are Merlin. You see the following Evil players: {evil_players}")

        elif player.role == 'Percival':
            # Percival sees Merlin and Morgana (cannot distinguish)
            merlin_morgana = [p.name for p in self.players if p.role in ['Merlin', 'Morgana']]
            info.append(f"You are Percival. You see these as possible Merlins: {merlin_morgana}")

        elif player.role in ['Loyal Servant']:
            info.append(f"You are a Loyal Servant of Arthur. You have no special information.")

        elif player.is_evil:
            # Evil players see each other
            evil_team = [p.name for p in self.players if p.is_evil and p.name != player.name]
            info.append(f"You are {player.role} (Evil). Your evil teammates are: {evil_team}")

        return " ".join(info)

    def get_current_leader(self):
        """Get the current leader."""
        return self.players[self.leader_index]

    def rotate_leader(self):
        """Rotate leadership to next player."""
        self.leader_index = (self.leader_index + 1) % len(self.players)

    def get_game_state(self):
        """Get current game state summary."""
        good_wins = sum(1 for r in self.mission_results if r)
        evil_wins = sum(1 for r in self.mission_results if not r)
        return f"Mission Status: {good_wins} Success, {evil_wins} Fail | Rejections this round: {self.rejection_count}/5"


class BaseAI:
    """Base class for AI backends."""

    def call_model(self, prompt, max_retries=3):
        """Call the AI model. Must be implemented by subclasses."""
        raise NotImplementedError

    def extract_choice(self, response, valid_choices):
        """Extract a valid choice from AI response."""
        if not response:
            return None

        # Look for exact matches (case insensitive)
        response_lower = response.lower()
        for choice in valid_choices:
            if choice.lower() in response_lower:
                return choice

        # Try to find in brackets or quotes
        for pattern in [r'\[([^\]]+)\]', r'"([^"]+)"', r"'([^']+)'"]:
            matches = re.findall(pattern, response)
            for match in matches:
                if match in valid_choices:
                    return match

        return None


class OllamaAI(BaseAI):
    """Interface to call models via Ollama."""

    def __init__(self, model_name='deepseek-r1'):
        self.model_name = model_name

    def call_model(self, prompt, max_retries=3):
        """Call Ollama model."""
        for attempt in range(max_retries):
            try:
                result = subprocess.run(
                    ['ollama', 'run', self.model_name, prompt],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                response = result.stdout.strip()

                if not response:
                    print(f"  [Attempt {attempt + 1}] Empty response, retrying...")
                    continue

                return response

            except subprocess.TimeoutExpired:
                print(f"  [Attempt {attempt + 1}] Timeout, retrying...")
                continue
            except Exception as e:
                print(f"  [Attempt {attempt + 1}] Error: {e}")
                continue

        return None


class DeepSeekAPI(BaseAI):
    """Interface to call DeepSeek via API."""

    def __init__(self, api_key=None, model='deepseek-chat'):
        # Try to load API key from: 1) parameter, 2) .env.local file, 3) environment variable
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = self._load_api_key_from_env_file() or os.getenv('DEEPSEEK_API_KEY')

        self.model = model
        self.base_url = 'https://api.deepseek.com/v1/chat/completions'

    def _load_api_key_from_env_file(self):
        """Load API key from .env.local file."""
        env_file = Path(__file__).parent / '.env.local'
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('DEEPSEEK_API_KEY='):
                            # Remove DEEPSEEK_API_KEY= prefix and any quotes
                            key = line.split('=', 1)[1].strip()
                            # Remove surrounding quotes if present
                            if (key.startswith('"') and key.endswith('"')) or \
                               (key.startswith("'") and key.endswith("'")):
                                key = key[1:-1]
                            return key
            except Exception as e:
                print(f"  [Warning] Could not read .env.local: {e}")
        return None

    def call_model(self, prompt, max_retries=3):
        """Call DeepSeek API."""
        if not self.api_key:
            print("  [Error] DeepSeek API key not found")
            return None

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        data = {
            'model': self.model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7
        }

        for attempt in range(max_retries):
            try:
                import urllib.request
                req = urllib.request.Request(
                    self.base_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers
                )

                with urllib.request.urlopen(req, timeout=30) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return result['choices'][0]['message']['content'].strip()

            except Exception as e:
                print(f"  [Attempt {attempt + 1}] API Error: {e}")
                continue

        return None


class LocalModelAI(BaseAI):
    """Interface for local models (placeholder for transformers/vllm)."""

    def __init__(self, model_path, backend='transformers'):
        self.model_path = model_path
        self.backend = backend
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        """Load the local model."""
        if self.backend == 'transformers':
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                print(f"Loading model from {self.model_path}...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    device_map='auto',
                    trust_remote_code=True
                )
                print("Model loaded successfully!")
            except ImportError:
                print("  [Error] transformers not installed. Install with: pip install transformers torch")
            except Exception as e:
                print(f"  [Error] Failed to load model: {e}")
        else:
            print(f"  [Error] Backend '{self.backend}' not supported")

    def call_model(self, prompt, max_retries=3):
        """Call local model."""
        if not self.model or not self.tokenizer:
            return None

        try:
            inputs = self.tokenizer(prompt, return_tensors='pt').to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            return response.strip()
        except Exception as e:
            print(f"  [Error] Generation failed: {e}")
            return None


class GameController:
    """Controls the game flow with AI players."""

    def __init__(self, game, player_ai_configs):
        """
        Initialize game controller with per-player AI configurations.

        Args:
            game: AvalonGame instance
            player_ai_configs: List of 6 AI instances, one for each player
        """
        self.game = game
        self.player_ais = player_ai_configs

    def get_player_ai(self, player):
        """Get the AI instance for a specific player."""
        player_index = self.game.players.index(player)
        return self.player_ais[player_index]

    def ai_discuss_proposal(self, player, leader, proposed_team, discussion_history):
        """AI player discusses the proposed team."""
        role_info = self.game.get_role_visibility(player)
        game_state = self.game.get_game_state()
        team_names = [p.name for p in proposed_team]

        # Format discussion history
        history_text = "\n".join([f"  {name}: {comment}" for name, comment in discussion_history]) if discussion_history else "  (No previous comments)"

        prompt = f"""You are playing Avalon. {role_info}

{game_state}
Leader {leader.name} has proposed this team: {team_names}

Previous discussion:
{history_text}

You now have the opportunity to discuss this proposal. You can:
- Express support or concerns about the team composition
- Share your thoughts (without revealing your role)
- Question the leader's choices
- Make strategic comments

IMPORTANT: Output a brief comment (1-2 sentences) about this team proposal. Be concise and strategic.

Your comment:"""

        ai = self.get_player_ai(player)
        response = ai.call_model(prompt)

        if not response:
            return "I'll go with the majority decision."

        # Clean up response - take first 2 sentences max
        sentences = response.strip().split('.')[:2]
        comment = '.'.join(sentences).strip()
        if comment and not comment.endswith('.'):
            comment += '.'

        return comment if comment else "I'll trust the leader's judgment."

    def ai_leader_final_proposal(self, leader, initial_team, team_size, discussion_history):
        """AI leader makes final proposal after hearing discussion."""
        player_names = [p.name for p in self.game.players]
        role_info = self.game.get_role_visibility(leader)
        game_state = self.game.get_game_state()
        initial_team_names = [p.name for p in initial_team]

        # Format discussion history
        history_text = "\n".join([f"  {name}: {comment}" for name, comment in discussion_history])

        prompt = f"""You are playing Avalon. {role_info}

{game_state}
Players: {player_names}

You initially proposed: {initial_team_names}

Discussion from other players:
{history_text}

Based on the discussion, you can now:
1. Keep your original proposal
2. Modify your team selection

You must select exactly {team_size} players for this mission.

IMPORTANT: Output ONLY a comma-separated list of player names for your FINAL team proposal, nothing else.
Example format: Alice,Bob,Charlie

Your final team:"""

        ai = self.get_player_ai(leader)
        response = ai.call_model(prompt)

        if not response:
            # Fallback: keep initial team
            return initial_team

        # Parse the response
        selected_names = [name.strip() for name in response.replace('\n', ',').split(',')]
        selected_names = [name for name in selected_names if name in player_names]

        # Ensure we have exactly team_size players
        if len(selected_names) != team_size:
            # Fallback: keep initial team
            return initial_team

        team = [p for p in self.game.players if p.name in selected_names]
        return team

    def ai_propose_team(self, leader, team_size):
        """AI leader proposes a team."""
        player_names = [p.name for p in self.game.players]
        role_info = self.game.get_role_visibility(leader)
        game_state = self.game.get_game_state()

        prompt = f"""You are playing Avalon. {role_info}

{game_state}
Players: {player_names}

You are the leader. You must select exactly {team_size} players for this mission.

IMPORTANT: Output ONLY a comma-separated list of player names, nothing else.
Example format: Alice,Bob,Charlie

Your selection:"""

        print(f"\n[AI] {leader.name} is proposing a team...")
        ai = self.get_player_ai(leader)
        response = ai.call_model(prompt)

        if not response:
            # Fallback: random selection
            print(f"  [Fallback] No valid response, selecting randomly")
            return random.sample(self.game.players, team_size)

        # Parse the response
        selected_names = [name.strip() for name in response.replace('\n', ',').split(',')]
        selected_names = [name for name in selected_names if name in player_names]

        # Ensure we have exactly team_size players
        if len(selected_names) != team_size:
            print(f"  [Fallback] Invalid count ({len(selected_names)} != {team_size}), selecting randomly")
            return random.sample(self.game.players, team_size)

        team = [p for p in self.game.players if p.name in selected_names]
        return team

    def ai_vote(self, player, proposed_team):
        """AI player votes on proposed team."""
        role_info = self.game.get_role_visibility(player)
        game_state = self.game.get_game_state()
        team_names = [p.name for p in proposed_team]

        prompt = f"""You are playing Avalon. {role_info}

{game_state}
Proposed team: {team_names}

You must vote to APPROVE or REJECT this team.

IMPORTANT: Output ONLY one word: either "APPROVE" or "REJECT", nothing else.

Your vote:"""

        ai = self.get_player_ai(player)
        response = ai.call_model(prompt)
        vote = ai.extract_choice(response, ['APPROVE', 'REJECT'])

        if not vote:
            # Fallback: random vote
            vote = random.choice(['APPROVE', 'REJECT'])

        return vote == 'APPROVE'

    def ai_mission_action(self, player):
        """AI player chooses mission action (Success or Fail)."""
        role_info = self.game.get_role_visibility(player)
        game_state = self.game.get_game_state()

        prompt = f"""You are playing Avalon. {role_info}

{game_state}

You are on the mission. Choose your action:
- Good players MUST choose "SUCCESS"
- Evil players MAY choose "SUCCESS" or "FAIL"

IMPORTANT: Output ONLY one word: either "SUCCESS" or "FAIL", nothing else.

Your action:"""

        ai = self.get_player_ai(player)
        response = ai.call_model(prompt)
        action = ai.extract_choice(response, ['SUCCESS', 'FAIL'])

        if not action:
            # Fallback based on role
            if player.is_evil:
                action = random.choice(['SUCCESS', 'FAIL'])
            else:
                action = 'SUCCESS'

        # Good players MUST choose success
        if not player.is_evil and action == 'FAIL':
            action = 'SUCCESS'

        return action == 'SUCCESS'

    def ai_assassinate(self, assassin):
        """AI assassin chooses target to kill."""
        player_names = [p.name for p in self.game.players if not p.is_evil]
        role_info = self.game.get_role_visibility(assassin)

        prompt = f"""You are playing Avalon. {role_info}

The Good team has won 3 missions! As the Assassin, you have ONE chance to kill Merlin and win the game for Evil.

Good players: {player_names}

IMPORTANT: Output ONLY the name of one player, nothing else.

Your assassination target:"""

        ai = self.get_player_ai(assassin)
        response = ai.call_model(prompt)

        # Extract target name
        target_name = None
        for name in player_names:
            if name in response:
                target_name = name
                break

        if not target_name:
            # Fallback: random good player
            target_name = random.choice(player_names)

        return next(p for p in self.game.players if p.name == target_name)

    def run_mission_round(self, round_num):
        """Run a complete mission round with discussion phase."""
        team_size = AvalonGame.MISSION_SIZES[round_num]

        print(f"\n{'='*60}")
        print(f"ROUND {round_num + 1} - Mission requires {team_size} players")
        print(f"{'='*60}")

        self.game.rejection_count = 0

        while self.game.rejection_count < 5:
            leader = self.game.get_current_leader()
            print(f"\nLeader: {leader.name}")
            print(f"Vote attempt: {self.game.rejection_count + 1}/5")

            # Check if this is the 5th vote (forced mission)
            is_forced_mission = (self.game.rejection_count == 4)

            # Leader proposes initial team
            initial_team = self.ai_propose_team(leader, team_size)
            print(f"Initial proposal: {[p.name for p in initial_team]}")

            # Skip discussion phase on 5th vote
            if is_forced_mission:
                print(f"\n{'─'*60}")
                print("⚠️  5TH VOTE - FORCED MISSION (No discussion)")
                print(f"{'─'*60}")
                print("\nAfter 4 rejections, this team must proceed without voting!")
                final_team = initial_team
            else:
                # Discussion phase - each player comments in order
                print(f"\n{'─'*60}")
                print("DISCUSSION PHASE")
                print(f"{'─'*60}")

                discussion_history = []
                for player in self.game.players:
                    if player.name != leader.name:  # Skip leader for now
                        comment = self.ai_discuss_proposal(player, leader, initial_team, discussion_history)
                        discussion_history.append((player.name, comment))
                        print(f"\n{player.name}: {comment}")

                # Leader's final summary and decision
                print(f"\n{'─'*60}")
                print(f"Leader {leader.name} makes final decision after hearing discussion...")
                print(f"{'─'*60}")

                final_team = self.ai_leader_final_proposal(leader, initial_team, team_size, discussion_history)

                # Check if team changed
                initial_names = set(p.name for p in initial_team)
                final_names = set(p.name for p in final_team)

                if initial_names != final_names:
                    print(f"\n{leader.name}: After considering your input, I'm changing my proposal.")
                    print(f"Final team: {[p.name for p in final_team]}")
                else:
                    print(f"\n{leader.name}: I'm keeping my original proposal.")
                    print(f"Final team: {[p.name for p in final_team]}")

            # Voting phase (skip on 5th vote)
            if is_forced_mission:
                print(f"\n{'─'*60}")
                print("FORCED MISSION - NO VOTE")
                print(f"{'─'*60}")
                print("\nThe team automatically proceeds to mission!")
                approved = True
            else:
                print(f"\n{'─'*60}")
                print("VOTING PHASE")
                print(f"{'─'*60}")

                votes = []
                for player in self.game.players:
                    vote = self.ai_vote(player, final_team)
                    votes.append(vote)
                    print(f"  {player.name}: {'APPROVE' if vote else 'REJECT'}")

                approve_count = sum(votes)
                approved = approve_count > len(votes) / 2

                print(f"\nResult: {approve_count} approve, {len(votes) - approve_count} reject → {'APPROVED' if approved else 'REJECTED'}")

            if approved:
                # Run mission
                print(f"\n{'─'*60}")
                print("MISSION PHASE")
                print(f"{'─'*60}")

                mission_actions = []
                for player in final_team:
                    action = self.ai_mission_action(player)
                    mission_actions.append(action)
                    print(f"  {player.name}: {'SUCCESS' if action else 'FAIL'}")

                success_count = sum(mission_actions)
                mission_success = success_count == len(final_team)

                print(f"\nMission Result: {'SUCCESS' if mission_success else 'FAIL'}")
                self.game.mission_results.append(mission_success)
                return mission_success
            else:
                # Team rejected, rotate to next leader
                self.game.rejection_count += 1
                self.game.rotate_leader()
                print(f"\nLeadership passes to next player...")

        # Should never reach here (5th vote is forced)
        return False

    def run_assassination_phase(self):
        """Run assassination phase after Good wins 3 missions."""
        print(f"\n{'='*60}")
        print("ASSASSINATION PHASE")
        print(f"{'='*60}")

        assassin = next(p for p in self.game.players if p.role == 'Assassin')
        print(f"\n{assassin.name} (Assassin) must identify and kill Merlin...")

        target = self.ai_assassinate(assassin)
        print(f"\nAssassin targets: {target.name}")

        if target.role == 'Merlin':
            print(f"\n{target.name} was Merlin! EVIL WINS!")
            return False
        else:
            print(f"\n{target.name} was {target.role}, not Merlin! GOOD WINS!")
            return True

    def run_game(self):
        """Run the complete game."""
        # Run 5 rounds or until win condition
        for round_num in range(5):
            self.run_mission_round(round_num)

            good_wins = sum(1 for r in self.game.mission_results if r)
            evil_wins = sum(1 for r in self.game.mission_results if not r)

            # Check win conditions
            if good_wins >= 3:
                # Good wins 3 missions, assassin phase
                good_victory = self.run_assassination_phase()
                return self.print_final_result(good_victory)
                
            elif evil_wins >= 3:
                # Evil wins 3 missions
                print(f"\n{'='*60}")
                print("EVIL WINS 3 MISSIONS!")
                print(f"{'='*60}")
                return self.print_final_result(False)
                

        # Should not reach here
        self.print_final_result(False)

    def print_final_result(self, good_victory):
        """Print final game result."""
        print(f"\n{'='*60}")
        print("GAME OVER")
        print(f"{'='*60}")
        print(f"\nWinner: {'GOOD' if good_victory else 'EVIL'}")
        print(f"\nMission Results: {['SUCCESS' if r else 'FAIL' for r in self.game.mission_results]}")
        print(f"\nFinal Roles:")
        for p in self.game.players:
            print(f"  {p.name}: {p.role} ({'Evil' if p.is_evil else 'Good'})")
        print(f"\n{'='*60}")

        return "Good" if good_victory else "Evil"


def main():
    """Main entry point."""
    print("Starting Avalon 6-Player AI Game...")
    print("Using DeepSeek-R1 via Ollama for all players\n")

    # Check if ollama is available
    try:
        subprocess.run(['ollama', 'list'], capture_output=True, check=True)
    except Exception as e:
        print(f"ERROR: Ollama not found. Please install Ollama and run 'ollama pull deepseek-r1'")
        return

    # Create game with 6 players
    player_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
    game = AvalonGame(player_names)

    # Run game with AI controller
    controller = GameController(game)
    controller.run_game()


if __name__ == "__main__":
    main()
