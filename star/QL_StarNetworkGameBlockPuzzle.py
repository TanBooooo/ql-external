"""
cron: 50 59 19 * * ?
new Env('StarNetwork游戏-BlockPuzzle')
"""
from utils.CommonUtil import main
from star.QL_StarNetworkGamePuzzle2048 import StarNetworkGame

if __name__ == '__main__':
    main('StarNetwork游戏-BlockPuzzle', StarNetworkGame("block_puzzle"), 'StarNetworkGameToken')
