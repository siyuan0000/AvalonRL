"""
Game logging functionality for Avalon games.
"""

import json
from datetime import datetime
from pathlib import Path


class GameLogger:
    """Handles logging of game events and saving game results."""

    def __init__(self, log_dir="logs"):
        """Initialize game logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.game_log = {
            'timestamp': datetime.now().isoformat(),
            'game_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'players': [],
            'rounds': [],
            'assassination': None,
            'final_result': None
        }

    def log_players(self, players, player_ais):
        """Log player information including roles and AI configurations."""
        from avalon_ai_game import OllamaAI, DeepSeekAPI, LocalModelAI

        for player, ai in zip(players, player_ais):
            ai_type = type(ai).__name__
            ai_config = ''

            if isinstance(ai, OllamaAI):
                ai_config = ai.model_name
            elif isinstance(ai, DeepSeekAPI):
                ai_config = ai.model
            elif isinstance(ai, LocalModelAI):
                ai_config = ai.model_path

            self.game_log['players'].append({
                'name': player.name,
                'role': player.role,
                'faction': 'Evil' if player.is_evil else 'Good',
                'ai_type': ai_type,
                'ai_config': ai_config
            })

    def start_round(self, round_num, team_size):
        """Start a new round log."""
        return {
            'round_number': round_num,
            'team_size': team_size,
            'proposals': []
        }

    def log_proposal(self, leader, initial_team, is_forced=False):
        """Log a team proposal."""
        return {
            'leader': leader,
            'initial_team': initial_team,
            'discussion': [],
            'final_team': [],
            'votes': {},
            'approved': False,
            'forced_mission': is_forced
        }

    def add_discussion_comment(self, proposal_log, player_name, comment):
        """Add a discussion comment to the proposal log."""
        proposal_log['discussion'].append({
            'player': player_name,
            'comment': comment
        })

    def log_final_team(self, proposal_log, final_team):
        """Log the final team after discussion."""
        proposal_log['final_team'] = final_team

    def log_votes(self, proposal_log, votes_dict):
        """Log voting results."""
        proposal_log['votes'] = votes_dict
        proposal_log['approved'] = sum(votes_dict.values()) > len(votes_dict) / 2

    def log_mission(self, round_log, team, actions, success):
        """Log mission execution and result."""
        round_log['mission'] = {
            'team': team,
            'actions': actions,
            'success': success
        }

    def log_assassination(self, assassin, target, success):
        """Log assassination attempt."""
        self.game_log['assassination'] = {
            'assassin': assassin,
            'target': target,
            'target_was_merlin': success,
            'result': 'EVIL WINS' if success else 'GOOD WINS'
        }

    def log_final_result(self, winner, mission_results):
        """Log final game result."""
        self.game_log['final_result'] = {
            'winner': winner,
            'mission_results': mission_results,
            'good_wins': sum(1 for r in mission_results if r == 'SUCCESS'),
            'evil_wins': sum(1 for r in mission_results if r == 'FAIL')
        }

    def save_json(self):
        """Save game log as JSON file."""
        game_id = self.game_log['game_id']
        json_path = self.log_dir / f"game_{game_id}.json"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.game_log, f, indent=2, ensure_ascii=False)

        print(f"\n[LOG] Game saved to: {json_path}")
        return json_path

    def save_text(self):
        """Save game log as human-readable text file."""
        game_id = self.game_log['game_id']
        text_path = self.log_dir / f"game_{game_id}.txt"

        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("AVALON GAME LOG\n")
            f.write("="*80 + "\n\n")

            f.write(f"Game ID: {game_id}\n")
            f.write(f"Timestamp: {self.game_log['timestamp']}\n\n")

            # Players
            f.write("-"*80 + "\n")
            f.write("PLAYERS\n")
            f.write("-"*80 + "\n")
            for p in self.game_log['players']:
                f.write(f"{p['name']}: {p['role']} ({p['faction']}) - AI: {p['ai_type']} ({p['ai_config']})\n")
            f.write("\n")

            # Rounds
            for round_data in self.game_log['rounds']:
                f.write("-"*80 + "\n")
                f.write(f"ROUND {round_data['round_number']} (Team size: {round_data['team_size']})\n")
                f.write("-"*80 + "\n")

                for proposal in round_data['proposals']:
                    f.write(f"\nProposal by {proposal['leader']}:\n")
                    f.write(f"  Initial team: {proposal['initial_team']}\n")

                    if proposal['discussion']:
                        f.write("  Discussion:\n")
                        for comment in proposal['discussion']:
                            f.write(f"    {comment['player']}: {comment['comment']}\n")

                    f.write(f"  Final team: {proposal['final_team']}\n")

                    if not proposal['forced_mission']:
                        f.write("  Votes:\n")
                        for player, vote in proposal['votes'].items():
                            f.write(f"    {player}: {'APPROVE' if vote else 'REJECT'}\n")

                    f.write(f"  Result: {'APPROVED' if proposal['approved'] else 'REJECTED'}")
                    if proposal['forced_mission']:
                        f.write(" (FORCED MISSION)")
                    f.write("\n")

                if 'mission' in round_data:
                    f.write(f"\nMission Execution:\n")
                    for player, action in round_data['mission']['actions'].items():
                        f.write(f"  {player}: {'SUCCESS' if action else 'FAIL'}\n")
                    f.write(f"  Result: {'SUCCESS' if round_data['mission']['success'] else 'FAIL'}\n")
                f.write("\n")

            # Assassination
            if self.game_log['assassination']:
                f.write("-"*80 + "\n")
                f.write("ASSASSINATION PHASE\n")
                f.write("-"*80 + "\n")
                ass = self.game_log['assassination']
                f.write(f"Assassin: {ass['assassin']}\n")
                f.write(f"Target: {ass['target']}\n")
                f.write(f"Target was Merlin: {ass['target_was_merlin']}\n")
                f.write(f"Result: {ass['result']}\n\n")

            # Final Result
            f.write("="*80 + "\n")
            f.write("FINAL RESULT\n")
            f.write("="*80 + "\n")
            result = self.game_log['final_result']
            f.write(f"Winner: {result['winner']}\n")
            f.write(f"Mission Results: {result['mission_results']}\n")
            f.write(f"Good Wins: {result['good_wins']} | Evil Wins: {result['evil_wins']}\n")

        print(f"[LOG] Game log saved to: {text_path}")
        return text_path

    def save(self):
        """Save both JSON and text logs."""
        self.save_json()
        self.save_text()

    def get_game_history_summary(self):
        """Generate a comprehensive game history summary for AI prompts."""
        if not self.game_log['rounds']:
            return "No previous rounds."

        summary_lines = []
        summary_lines.append("PREVIOUS ROUNDS:")

        for round_data in self.game_log['rounds']:
            round_num = round_data['round_number']
            summary_lines.append(f"\n--- Round {round_num} ---")

            # Show all proposals and their outcomes
            for idx, proposal in enumerate(round_data['proposals']):
                proposal_num = idx + 1
                leader = proposal['leader']
                final_team = proposal['final_team']
                approved = proposal['approved']

                summary_lines.append(f"Proposal {proposal_num} by {leader}: {final_team}")

                # Show votes if not forced
                if not proposal.get('forced_mission', False):
                    approves = [p for p, v in proposal['votes'].items() if v]
                    rejects = [p for p, v in proposal['votes'].items() if not v]
                    summary_lines.append(f"  Votes: APPROVE={approves}, REJECT={rejects}")

                summary_lines.append(f"  Result: {'APPROVED' if approved else 'REJECTED'}")

                # If approved, show mission result
                if approved and 'mission' in round_data:
                    mission = round_data['mission']
                    summary_lines.append(f"  Mission Team: {mission['team']}")
                    success_count = sum(1 for a in mission['actions'].values() if a)
                    fail_count = len(mission['actions']) - success_count
                    summary_lines.append(f"  Mission Actions: {success_count} SUCCESS, {fail_count} FAIL")
                    summary_lines.append(f"  Mission Result: {'SUCCESS' if mission['success'] else 'FAIL'}")

        return "\n".join(summary_lines)

    def get_player_behavioral_summary(self, player_name):
        """Generate a behavioral summary for a specific player."""
        if not self.game_log['rounds']:
            return f"No behavioral data for {player_name} yet."

        summary = {
            'missions_on': [],
            'missions_succeeded': [],
            'missions_failed': [],
            'proposals_made': [],
            'votes_approve': 0,
            'votes_reject': 0,
            'discussion_comments': []
        }

        for round_data in self.game_log['rounds']:
            round_num = round_data['round_number']

            for proposal in round_data['proposals']:
                # Track proposals
                if proposal['leader'] == player_name:
                    summary['proposals_made'].append({
                        'round': round_num,
                        'team': proposal['final_team'],
                        'approved': proposal['approved']
                    })

                # Track votes
                if player_name in proposal.get('votes', {}):
                    if proposal['votes'][player_name]:
                        summary['votes_approve'] += 1
                    else:
                        summary['votes_reject'] += 1

                # Track discussion comments
                for comment in proposal.get('discussion', []):
                    if comment['player'] == player_name:
                        summary['discussion_comments'].append({
                            'round': round_num,
                            'comment': comment['comment']
                        })

            # Track mission participation
            if 'mission' in round_data:
                mission = round_data['mission']
                if player_name in mission['team']:
                    summary['missions_on'].append(round_num)
                    if mission['success']:
                        summary['missions_succeeded'].append(round_num)
                    else:
                        summary['missions_failed'].append(round_num)

        return summary
