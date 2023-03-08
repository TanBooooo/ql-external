"""
cron: 50 59 1 * * ?
new Env('StarNetwork游戏-Sudoku')
"""
from utils.StarNetworkUtil import main
from StarNetwork.QL_StarNetworkGamePuzzle2048 import StarNetworkGame

if __name__ == '__main__':
    main('StarNetwork游戏-Sudoku', StarNetworkGame("sudoku"))
