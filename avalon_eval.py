"""
To write an evaluation script for AvalonRL
"""

from start import (
    quick_start_mode
)
from avalon_ai_game import (
    AvalonGame,
    GameController,
)

def evaluation(num_runs = 10):
    """Function to run evaluation of the AvalonRL game."""
    
    player_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
    num_wins_per_player = {} # Track number of wins for each player
    for name in player_names:
        num_wins_per_player[name] = 0
    player_ais = quick_start_mode()

    for run in range(num_runs):
        print(f"\n=== Starting Game {run + 1} ===")
        # Run game with AI controller
        game = AvalonGame(player_names)
        controller = GameController(game, player_ais)
        results = controller.run_game()

        if results == "Good":
            for player_i in controller.game.players:
                if (player_i.is_evil == False): # good player
                    name = player_i.name
                    num_wins_per_player[name] += 1
        else:
            for player_i in controller.game.players:
                if (player_i.is_evil == True): # evil player
                    name = player_i.name
                    num_wins_per_player[name] += 1
        
    print("\n=== Evaluation Results ===")
    # print win rate for each player
    for name in player_names:
        wins = num_wins_per_player[name]
        win_rate = (wins / num_runs) * 100
        print(f"{name}: {wins} wins out of {num_runs} games ({win_rate:.2f}%)")
        