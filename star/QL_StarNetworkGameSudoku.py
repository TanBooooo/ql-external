"""
cron: 50 59 1 * * ?
new Env('StarNetwork游戏-Sudoku')
"""
from utils.QLTask import main
from QL_StarNetworkGamePuzzle2048 import StarNetworkGame

if __name__ == '__main__':
    main('StarNetwork游戏-Sudoku', StarNetworkGame("sudoku"), 'StarNetworkGameToken')
