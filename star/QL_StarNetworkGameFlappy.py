"""
cron: 55 59 7 * * ?
new Env('StarNetwork游戏-Flappy')
"""
from utils.StarNetworkUtil import main
from star.QL_StarNetworkGamePuzzle2048 import StarNetworkGame

if __name__ == '__main__':
    main('StarNetwork游戏-Flappy', StarNetworkGame("flappy"))