// FitPlay Games JavaScript
class FitPlayGames {
    constructor() {
        this.currentGame = null;
        this.gameTimer = null;
        this.gameStartTime = null;
        this.gameScore = 0;
        this.gameData = {};
        this.init();
    }

    init() {
        this.loadGameData();
        this.setupEventListeners();
    }

    async loadGameData() {
        try {
            const response = await fetch('/games/game_data');
            this.gameData = await response.json();
        } catch (error) {
            console.error('Error loading game data:', error);
        }
    }

    setupEventListeners() {
        // Add keyboard support for games
        document.addEventListener('keydown', (e) => {
            if (this.currentGame && e.code === 'Space') {
                e.preventDefault();
                this.gameAction();
            }
        });
    }

    async startGame(gameType) {
        try {
            const response = await fetch('/games/start_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ game_type: gameType })
            });

            if (response.ok) {
                this.currentGame = gameType;
                this.gameScore = 0;
                this.gameStartTime = Date.now();
                this.showGameInterface(gameType);
                this.startGameTimer();
            }
        } catch (error) {
            console.error('Error starting game:', error);
        }
    }

    showGameInterface(gameType) {
        const gameSelection = document.getElementById('game-selection');
        const gameInterface = document.getElementById('game-interface');
        const gameTitle = document.getElementById('game-title');
        const actionButton = document.getElementById('action-button');
        const instructions = document.getElementById('game-instructions');

        gameSelection.classList.add('d-none');
        gameInterface.classList.remove('d-none');

        const gameInfo = this.gameData[gameType];
        if (gameInfo) {
            gameTitle.innerHTML = `<i class="${gameInfo.icon} me-2"></i>${gameInfo.name}`;
            this.updateInstructions(gameType);
        }

        this.updateGameStats();
        this.updateActionButton(gameType);
    }

    updateInstructions(gameType) {
        const instructions = document.getElementById('game-instructions');
        const gameInfo = this.gameData[gameType];
        
        if (gameInfo) {
            instructions.innerHTML = `<p class="text-muted">${gameInfo.description}</p>`;
        }
    }

    updateActionButton(gameType) {
        const actionButton = document.getElementById('action-button');
        
        switch (gameType) {
            case 'squat_tap':
                actionButton.innerHTML = '<i class="fas fa-hand-pointer me-2"></i>TAP FOR SQUAT';
                actionButton.className = 'btn btn-primary btn-lg game-action-btn';
                break;
            case 'jump_counter':
                actionButton.innerHTML = '<i class="fas fa-arrow-up me-2"></i>TAP FOR JUMP';
                actionButton.className = 'btn btn-success btn-lg game-action-btn';
                break;
            case 'plank_timer':
                actionButton.innerHTML = '<i class="fas fa-clock me-2"></i>HOLD PLANK';
                actionButton.className = 'btn btn-info btn-lg game-action-btn';
                break;
            case 'burpee_challenge':
                actionButton.innerHTML = '<i class="fas fa-dumbbell me-2"></i>TAP FOR BURPEE';
                actionButton.className = 'btn btn-warning btn-lg game-action-btn';
                break;
        }
    }

    startGameTimer() {
        let seconds = 0;
        this.gameTimer = setInterval(() => {
            seconds++;
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            const timeDisplay = `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
            document.getElementById('game-timer').textContent = timeDisplay;

            // Update progress bar for plank timer
            if (this.currentGame === 'plank_timer') {
                const targetTime = this.gameData[this.currentGame]?.target_score || 60;
                const progress = Math.min((seconds / targetTime) * 100, 100);
                document.getElementById('game-progress').style.width = `${progress}%`;
            }
        }, 1000);
    }

    gameAction() {
        if (!this.currentGame) return;

        // Add visual feedback
        const actionButton = document.getElementById('action-button');
        actionButton.classList.add('active');
        setTimeout(() => actionButton.classList.remove('active'), 200);

        // Handle different game types
        switch (this.currentGame) {
            case 'squat_tap':
            case 'jump_counter':
            case 'burpee_challenge':
                this.gameScore++;
                this.updateGameStats();
                this.updateScore();
                break;
            case 'plank_timer':
                // For plank timer, score is time in seconds
                this.gameScore = Math.floor((Date.now() - this.gameStartTime) / 1000);
                this.updateGameStats();
                this.updateScore();
                break;
        }

        // Check if target reached
        this.checkGameCompletion();
    }

    async updateScore() {
        try {
            await fetch('/games/update_score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ score: this.gameScore })
            });
        } catch (error) {
            console.error('Error updating score:', error);
        }
    }

    updateGameStats() {
        document.getElementById('game-score').textContent = this.gameScore;
        
        // Calculate estimated points and calories
        let estimatedPoints = 0;
        let estimatedCalories = 0;

        switch (this.currentGame) {
            case 'squat_tap':
                estimatedPoints = this.gameScore * 2;
                estimatedCalories = this.gameScore * 0.5;
                break;
            case 'jump_counter':
                estimatedPoints = this.gameScore * 3;
                estimatedCalories = this.gameScore * 0.8;
                break;
            case 'plank_timer':
                estimatedPoints = this.gameScore * 5;
                estimatedCalories = this.gameScore * 0.1;
                break;
            case 'burpee_challenge':
                estimatedPoints = this.gameScore * 10;
                estimatedCalories = this.gameScore * 1.5;
                break;
        }

        document.getElementById('game-points').textContent = Math.floor(estimatedPoints);
        document.getElementById('game-calories').textContent = Math.floor(estimatedCalories);

        // Update progress bar (except for plank timer)
        if (this.currentGame !== 'plank_timer') {
            const targetScore = this.gameData[this.currentGame]?.target_score || 50;
            const progress = Math.min((this.gameScore / targetScore) * 100, 100);
            document.getElementById('game-progress').style.width = `${progress}%`;
        }
    }

    checkGameCompletion() {
        const gameInfo = this.gameData[this.currentGame];
        if (!gameInfo) return;

        const targetScore = gameInfo.target_score;
        const timeLimit = gameInfo.time_limit;
        const currentTime = Math.floor((Date.now() - this.gameStartTime) / 1000);

        // Check if game should end
        if (this.gameScore >= targetScore || currentTime >= timeLimit) {
            this.endGame();
        }
    }

    async endGame() {
        if (!this.currentGame) return;

        // Stop timer
        if (this.gameTimer) {
            clearInterval(this.gameTimer);
            this.gameTimer = null;
        }

        try {
            const response = await fetch('/games/end_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });

            if (response.ok) {
                const result = await response.json();
                this.showGameResults(result);
            }
        } catch (error) {
            console.error('Error ending game:', error);
        }
    }

    showGameResults(result) {
        // Update result modal
        document.getElementById('result-points').textContent = result.points_earned;
        document.getElementById('result-calories').textContent = Math.floor(result.calories_burned);

        // Show new badges if any
        const newBadgesContainer = document.getElementById('new-badges');
        if (result.new_badges && result.new_badges.length > 0) {
            newBadgesContainer.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-trophy me-2"></i>
                    <strong>New Badge${result.new_badges.length > 1 ? 's' : ''} Earned!</strong>
                    <ul class="mb-0 mt-2">
                        ${result.new_badges.map(badge => `<li>${badge.replace('_', ' ').toUpperCase()}</li>`).join('')}
                    </ul>
                </div>
            `;
        } else {
            newBadgesContainer.innerHTML = '';
        }

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('gameResultsModal'));
        modal.show();

        // Reset game state
        this.currentGame = null;
        this.gameScore = 0;
        this.gameStartTime = null;
    }

    playAgain() {
        // Hide modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('gameResultsModal'));
        modal.hide();

        // Reset interface
        this.resetGameInterface();
    }

    resetGameInterface() {
        const gameSelection = document.getElementById('game-selection');
        const gameInterface = document.getElementById('game-interface');

        gameInterface.classList.add('d-none');
        gameSelection.classList.remove('d-none');

        // Reset displays
        document.getElementById('game-timer').textContent = '0:00';
        document.getElementById('game-score').textContent = '0';
        document.getElementById('game-points').textContent = '0';
        document.getElementById('game-calories').textContent = '0';
        document.getElementById('game-progress').style.width = '0%';
    }
}

// Initialize games when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.fitPlayGames = new FitPlayGames();
});

// Global functions for button clicks
function startGame(gameType) {
    window.fitPlayGames.startGame(gameType);
}

function gameAction() {
    window.fitPlayGames.gameAction();
}

function endGame() {
    window.fitPlayGames.endGame();
}

function playAgain() {
    window.fitPlayGames.playAgain();
}

// Add touch support for mobile devices
document.addEventListener('DOMContentLoaded', () => {
    let touchStartTime = 0;
    
    document.addEventListener('touchstart', (e) => {
        touchStartTime = Date.now();
    });
    
    document.addEventListener('touchend', (e) => {
        const touchDuration = Date.now() - touchStartTime;
        if (touchDuration < 500 && window.fitPlayGames.currentGame) {
            // Quick tap gesture
            window.fitPlayGames.gameAction();
        }
    });
});
