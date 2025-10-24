#!/usr/bin/env python3
"""
Avalon 6-Player Game Launcher
Configure AI backend for each player and start the game.
"""

from avalon_ai_game import (
    AvalonGame,
    GameController,
    OllamaAI,
    DeepSeekAPI,
    LocalModelAI
)


def print_header():
    """Print welcome header."""
    print("\n" + "="*70)
    print(" "*20 + "AVALON 6-PLAYER GAME LAUNCHER")
    print("="*70)


def select_ai_backend():
    """Let user select AI backend type."""
    print("\nSelect AI Backend Type:")
    print("  1. Ollama (Local Ollama models)")
    print("  2. DeepSeek API (Online API)")
    print("  3. Local Model (Local Transformers models)")

    while True:
        choice = input("\nEnter option (1-3): ").strip()
        if choice in ['1', '2', '3']:
            return choice
        print("Invalid option, please try again")


def configure_ollama():
    """Configure Ollama backend."""
    print("\nAvailable Ollama models:")
    print("  - deepseek-r1")
    print("  - qwen2.5")
    print("  - llama3.1")
    print("  - mistral")

    model_name = input("\nEnter model name (default: deepseek-r1): ").strip()
    if not model_name:
        model_name = 'deepseek-r1'

    return OllamaAI(model_name=model_name)


def configure_deepseek_api():
    """Configure DeepSeek API backend."""
    print("\nConfigure DeepSeek API:")
    print("API key will be loaded from (in priority order):")
    print("  1. Manual input")
    print("  2. .env.local file (DEEPSEEK_API_KEY=your_key)")
    print("  3. Environment variable DEEPSEEK_API_KEY")

    api_key = input("\nEnter DeepSeek API key (or press Enter to auto-load): ").strip()

    print("\nAvailable models:")
    print("  - deepseek-chat (recommended)")
    print("  - deepseek-reasoner")

    model = input("\nEnter model name (default: deepseek-chat): ").strip()
    if not model:
        model = 'deepseek-chat'

    if api_key:
        return DeepSeekAPI(api_key=api_key, model=model)
    else:
        # Will auto-load from .env.local or environment variable
        return DeepSeekAPI(model=model)


def configure_local_model():
    """Configure local model backend."""
    print("\nConfigure Local Model:")
    print("Required: pip install transformers torch accelerate")

    model_path = input("\nEnter model path or HuggingFace model ID: ").strip()

    if not model_path:
        print("Error: Model path is required")
        return None

    print("\nBackend type:")
    print("  - transformers (default)")

    backend = input("\nEnter backend type (default: transformers): ").strip()
    if not backend:
        backend = 'transformers'

    return LocalModelAI(model_path=model_path, backend=backend)


def configure_player_ai(player_num, player_name):
    """Configure AI for a single player."""
    print(f"\n{'='*70}")
    print(f"Configure Player {player_num}: {player_name}")
    print(f"{'='*70}")

    backend_choice = select_ai_backend()

    if backend_choice == '1':
        return configure_ollama()
    elif backend_choice == '2':
        return configure_deepseek_api()
    elif backend_choice == '3':
        return configure_local_model()

    return None


def quick_start_mode():
    """Quick start with all players using the same configuration."""
    print("\nQuick Start Mode: All players use the same AI configuration")

    backend_choice = select_ai_backend()

    if backend_choice == '1':
        ai_instance = configure_ollama()
    elif backend_choice == '2':
        ai_instance = configure_deepseek_api()
    elif backend_choice == '3':
        ai_instance = configure_local_model()

    if not ai_instance:
        print("Configuration failed")
        return None

    # Create 6 instances with same config
    player_ais = []
    for i in range(6):
        if backend_choice == '1':
            player_ais.append(OllamaAI(model_name=ai_instance.model_name))
        elif backend_choice == '2':
            player_ais.append(DeepSeekAPI(api_key=ai_instance.api_key, model=ai_instance.model))
        elif backend_choice == '3':
            # Share the same model instance for local models to save memory
            player_ais.append(ai_instance)

    return player_ais


def custom_mode():
    """Custom mode: configure each player individually."""
    print("\nCustom Mode: Configure AI for each player individually")

    player_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
    player_ais = []

    for i, name in enumerate(player_names):
        ai = configure_player_ai(i + 1, name)
        if not ai:
            print(f"Failed to configure player {name}")
            return None
        player_ais.append(ai)

    return player_ais


def run_the_game():
    """Main launcher function."""
    print_header()

    print("\nLaunch Mode:")
    print("  1. Quick Start (All players use same AI)")
    print("  2. Custom Mode (Configure each player individually)")

    mode = input("\nSelect mode (1-2, default 1): ").strip()
    if not mode:
        mode = '1'

    if mode == '1':
        player_ais = quick_start_mode()
    elif mode == '2':
        player_ais = custom_mode()
    else:
        print("Invalid option")
        return

    if not player_ais:
        print("\nConfiguration failed, exiting")
        return

    # Verify we have 6 AI instances
    if len(player_ais) != 6:
        print(f"\nError: Need 6 AI configurations, but only have {len(player_ais)}")
        return

    # Create and start game
    print("\n" + "="*70)
    print("Starting game...")
    print("="*70)

    player_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
    game = AvalonGame(player_names)

    # Display player AI configurations
    print("\nPlayer AI Configuration:")
    for i, (name, ai) in enumerate(zip(player_names, player_ais)):
        ai_type = type(ai).__name__
        if isinstance(ai, OllamaAI):
            config = f"{ai_type} (model: {ai.model_name})"
        elif isinstance(ai, DeepSeekAPI):
            config = f"{ai_type} (model: {ai.model})"
        elif isinstance(ai, LocalModelAI):
            config = f"{ai_type} (path: {ai.model_path})"
        else:
            config = ai_type
        print(f"  {name}: {config}")

    print("\nGame starting!\n")

    controller = GameController(game, player_ais)
    controller.run_game()

def main():
    run_the_game()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
