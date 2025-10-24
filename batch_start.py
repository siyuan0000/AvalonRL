#!/usr/bin/env python3
"""
Batch Game Launcher for Avalon
Runs multiple games automatically with default configuration.
Default: 10 games, all 6 players using DeepSeek API
"""

import sys
from avalon_ai_game import AvalonGame, GameController, DeepSeekAPI


def run_batch_games(num_games=10, player_names=None):
    """
    Run multiple Avalon games in batch.

    Args:
        num_games: Number of games to run (default: 10)
        player_names: List of player names (default: Alice, Bob, Charlie, Diana, Eve, Frank)
    """
    if player_names is None:
        player_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']

    print("="*80)
    print(" "*25 + "AVALON BATCH GAME RUNNER")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Number of games: {num_games}")
    print(f"  AI Backend: DeepSeek API (all 6 players)")
    print(f"  API Key: Loaded from .env.local or environment variable")
    print(f"  Players: {', '.join(player_names)}")
    print("\n" + "="*80)

    # Track results
    results = {
        'total_games': num_games,
        'good_wins': 0,
        'evil_wins': 0,
        'games': []
    }

    for game_num in range(1, num_games + 1):
        print(f"\n{'='*80}")
        print(f" "*30 + f"GAME {game_num}/{num_games}")
        print(f"{'='*80}\n")

        try:
            # Create game
            game = AvalonGame(player_names)

            # Create AI configurations - all using DeepSeek API
            # API key will be loaded from .env.local automatically
            player_ais = [DeepSeekAPI(model='deepseek-chat') for _ in range(6)]

            # Run game
            controller = GameController(game, player_ais)
            controller.run_game()

            # Extract result from logger
            final_result = controller.logger.game_log.get('final_result', {})
            winner = final_result.get('winner', 'UNKNOWN')

            # Track results
            game_result = {
                'game_number': game_num,
                'winner': winner,
                'game_id': controller.logger.game_log.get('game_id', 'unknown')
            }
            results['games'].append(game_result)

            if winner == 'GOOD':
                results['good_wins'] += 1
            elif winner == 'EVIL':
                results['evil_wins'] += 1

            print(f"\n[BATCH] Game {game_num} completed. Winner: {winner}")

        except KeyboardInterrupt:
            print(f"\n\n[BATCH] Interrupted by user at game {game_num}")
            break
        except Exception as e:
            print(f"\n[BATCH ERROR] Game {game_num} failed: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Print summary
    print("\n" + "="*80)
    print(" "*30 + "BATCH SUMMARY")
    print("="*80)
    print(f"\nTotal games completed: {len(results['games'])}/{num_games}")
    print(f"Good wins: {results['good_wins']} ({results['good_wins']/len(results['games'])*100:.1f}%)")
    print(f"Evil wins: {results['evil_wins']} ({results['evil_wins']/len(results['games'])*100:.1f}%)")

    print("\nGame-by-game results:")
    for game_result in results['games']:
        print(f"  Game {game_result['game_number']}: {game_result['winner']} (ID: {game_result['game_id']})")

    print("\n" + "="*80)
    print("All game logs saved to ./logs/ directory")
    print("="*80 + "\n")

    return results


def main():
    """Main entry point for batch runner."""
    # Parse command line arguments
    num_games = 10  # Default

    if len(sys.argv) > 1:
        try:
            num_games = int(sys.argv[1])
            if num_games <= 0:
                print("Error: Number of games must be positive")
                sys.exit(1)
        except ValueError:
            print(f"Error: Invalid number of games: {sys.argv[1]}")
            print("Usage: python batch_start.py [num_games]")
            print("Example: python batch_start.py 20")
            sys.exit(1)

    # Check if .env.local exists or DEEPSEEK_API_KEY is set
    import os
    from pathlib import Path

    env_file = Path(__file__).parent / '.env.local'
    api_key_env = os.getenv('DEEPSEEK_API_KEY')

    if not env_file.exists() and not api_key_env:
        print("\n" + "="*80)
        print("WARNING: DeepSeek API Key Not Found!")
        print("="*80)
        print("\nPlease set up your API key using one of these methods:")
        print("  1. Create .env.local file with: DEEPSEEK_API_KEY=your_key")
        print("  2. Set environment variable: export DEEPSEEK_API_KEY=your_key")
        print("\nGet your API key from: https://platform.deepseek.com")
        print("="*80 + "\n")

        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Exiting...")
            sys.exit(0)

    # Run batch games
    try:
        run_batch_games(num_games)
    except KeyboardInterrupt:
        print("\n\nBatch run interrupted by user")
    except Exception as e:
        print(f"\nBatch run failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
