"""
AvalonRL evaluation script
Runs multiple games and computes win statistics.
"""

from start import quick_start_mode
from avalon_ai_game import AvalonGame, GameController
from avalon_ai_game import OllamaAI

def evaluation(num_runs=10):
    """Run evaluation of the AvalonRL game with logging support."""
    
    player_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
    num_wins_per_player = {name: 0 for name in player_names}

    for run in range(num_runs):
        print(f"\n=== Starting Game {run + 1} ===")

        # Create new AI config and game each run (to reset state)
        player_ais = player_ais = [OllamaAI(model_name="Llama-3.2-1B-Instruct-Q6_K") for _ in range(6)]
        game = AvalonGame(player_names)
        controller = GameController(game, player_ais)

        # Run game
        controller.run_game()

        # Extract winner from logger
        result = controller.logger.game_log['final_result']['winner']  # "GOOD" or "EVIL"

        # Update per-player stats
        for player in controller.game.players:
            if result == "GOOD" and not player.is_evil:
                num_wins_per_player[player.name] += 1
            elif result == "EVIL" and player.is_evil:
                num_wins_per_player[player.name] += 1

    # --- Results summary ---
    print("\n=== Evaluation Summary ===")
    for name, wins in num_wins_per_player.items():
        rate = (wins / num_runs) * 100
        print(f"{name}: {wins}/{num_runs} wins ({rate:.2f}%)")

    good_wins = sum(1 for _ in range(num_runs) if controller.logger.game_log['final_result']['winner'] == "GOOD")
    evil_wins = num_runs - good_wins
    print(f"\nGood team win rate: {good_wins/num_runs:.2%}")
    print(f"Evil team win rate: {evil_wins/num_runs:.2%}")
