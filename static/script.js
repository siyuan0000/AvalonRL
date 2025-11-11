// Avalon AI Game Web UI - JavaScript

// Global state
let statusInterval = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadRecentGames();
    checkOllama();
    updateBackendOptions();  // Initialize with default backend
});

// Toggle configuration mode
function toggleConfigMode() {
    const mode = document.querySelector('input[name="configMode"]:checked').value;
    const allSameConfig = document.getElementById('allSameConfig');
    const customConfig = document.getElementById('customConfig');

    if (mode === 'all_same') {
        allSameConfig.style.display = 'block';
        customConfig.style.display = 'none';
    } else {
        allSameConfig.style.display = 'none';
        customConfig.style.display = 'block';
    }
}

// Update backend options display
function updateBackendOptions() {
    const backend = document.getElementById('backendSelect').value;
    const ollamaOptions = document.getElementById('ollamaOptions');
    const deepseekOptions = document.getElementById('deepseekOptions');
    const localOptions = document.getElementById('localOptions');

    // Hide all options
    ollamaOptions.style.display = 'none';
    deepseekOptions.style.display = 'none';
    localOptions.style.display = 'none';

    // Show selected backend options
    if (backend === 'ollama') {
        ollamaOptions.style.display = 'block';
    } else if (backend === 'deepseek') {
        deepseekOptions.style.display = 'block';
    } else if (backend === 'local') {
        localOptions.style.display = 'block';
    }
}

// Check Ollama availability
async function checkOllama() {
    try {
        const response = await fetch('/api/check_ollama');
        const data = await response.json();

        if (data.available && data.models.length > 0) {
            const select = document.getElementById('ollamaModel');
            select.innerHTML = '';

            // Add detected models
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to check Ollama:', error);
    }
}

// Start a new game
async function startGame() {
    const startButton = document.getElementById('startButton');
    const mode = document.querySelector('input[name="configMode"]:checked').value;

    if (mode === 'custom') {
        alert('Custom mode is not yet implemented in the web interface. Please use start.py for custom configurations.');
        return;
    }

    // Disable start button
    startButton.disabled = true;
    startButton.textContent = 'Starting...';

    // Get configuration
    const backend = document.getElementById('backendSelect').value;
    const config = {
        mode: 'all_same',
        ai_config: {
            backend: backend
        }
    };

    if (backend === 'ollama') {
        config.ai_config.model = document.getElementById('ollamaModel').value;
    } else if (backend === 'deepseek') {
        config.ai_config.model = document.getElementById('deepseekModel').value;
        const apiKey = document.getElementById('apiKey').value.trim();
        if (apiKey) {
            config.ai_config.api_key = apiKey;
        }
    } else if (backend === 'local') {
        const modelPath = document.getElementById('localModelPath').value.trim();
        if (!modelPath) {
            alert('Please enter a model path');
            startButton.disabled = false;
            startButton.textContent = 'Start Game';
            return;
        }
        config.ai_config.model = modelPath;
    }

    try {
        const response = await fetch('/api/start_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to start game');
        }

        // Start polling for status
        startStatusPolling();

    } catch (error) {
        alert('Error starting game: ' + error.message);
        startButton.disabled = false;
        startButton.textContent = 'Start Game';
    }
}

// Start polling for game status
function startStatusPolling() {
    if (statusInterval) {
        clearInterval(statusInterval);
    }

    statusInterval = setInterval(updateGameStatus, 1000);
    updateGameStatus(); // Initial update
}

// Update game status display
async function updateGameStatus() {
    try {
        const response = await fetch('/api/game_status');
        const status = await response.json();

        const statusDisplay = document.getElementById('gameStatus');
        const statusBadge = statusDisplay.querySelector('.status-badge');
        const statusMessage = document.getElementById('statusMessage');
        const startButton = document.getElementById('startButton');

        // Update badge
        statusBadge.className = 'status-badge ' + status.status;
        statusBadge.textContent = status.status.replace('_', ' ');

        // Update message
        if (status.status === 'idle') {
            statusMessage.textContent = 'Ready to start a new game';
            startButton.disabled = false;
            startButton.textContent = 'Start Game';
            if (statusInterval) {
                clearInterval(statusInterval);
                statusInterval = null;
            }
        } else if (status.status === 'starting' || status.status === 'initializing') {
            statusMessage.textContent = 'Game is starting...';
        } else if (status.status === 'running') {
            statusMessage.textContent = 'Game is running... (this may take several minutes)';
        } else if (status.status === 'completed') {
            statusMessage.innerHTML = `Game completed! <a href="/viewer?game=${status.game_id}">View results</a>`;
            startButton.disabled = false;
            startButton.textContent = 'Start Another Game';
            if (statusInterval) {
                clearInterval(statusInterval);
                statusInterval = null;
            }
            loadRecentGames(); // Refresh game list
        } else if (status.status === 'error') {
            statusMessage.textContent = 'Error: ' + (status.error || 'Unknown error');
            startButton.disabled = false;
            startButton.textContent = 'Try Again';
            if (statusInterval) {
                clearInterval(statusInterval);
                statusInterval = null;
            }
        }

    } catch (error) {
        console.error('Failed to update status:', error);
    }
}

// Load recent games list
async function loadRecentGames() {
    const gamesContainer = document.getElementById('recentGames');

    try {
        const response = await fetch('/api/logs');
        const data = await response.json();

        if (data.logs.length === 0) {
            gamesContainer.innerHTML = '<p class="info-text">No games played yet. Start a game to see results here!</p>';
            return;
        }

        // Display recent games (limit to 10)
        const recentGames = data.logs.slice(0, 10);
        gamesContainer.innerHTML = recentGames.map(game => `
            <div class="game-item" onclick="viewGame('${game.game_id}')">
                <div class="game-item-header">
                    <span class="game-id">${game.game_id}</span>
                    <span class="winner-badge ${game.winner.toLowerCase()}">${game.winner}</span>
                </div>
                <div class="game-timestamp">${formatTimestamp(game.timestamp)}</div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Failed to load games:', error);
        gamesContainer.innerHTML = '<p class="loading">Failed to load games</p>';
    }
}

// View a specific game
function viewGame(gameId) {
    window.location.href = `/viewer?game=${gameId}`;
}

// Format timestamp for display
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
