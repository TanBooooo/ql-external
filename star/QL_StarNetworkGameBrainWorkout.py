"""
cron: 50 59 13 * * ?
new Env('StarNetwork游戏-BrainWorkout')
"""
from utils.QLTask import main
from QL_StarNetworkGamePuzzle2048 import StarNetworkGame

if __name__ == '__main__':
    main('StarNetwork游戏-BrainWorkout', StarNetworkGame("brain_workout"), 'StarNetworkGameToken')
