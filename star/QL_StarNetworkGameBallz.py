"""
cron: 50 59 21 * * ?
new Env('StarNetwork游戏-Ballz')
"""
from utils.CommonUtil import main
from star.QL_StarNetworkGamePuzzle2048 import StarNetworkGame

if __name__ == '__main__':
    main('StarNetwork游戏-Ballz', StarNetworkGame("puzzle_ballz"), 'StarNetworkGameToken')

# tournament_id = ''
# resp = requests.get("https://api.starnetwork.io/v3/game/" + game + "?lang=zh-CN", headers=headers,
#                     proxies={"https": proxy}, timeout=15)
# if resp.text.count('tournament') > 0:
#     ids = resp.json()['tournament']['_id']['id']['data']
#     for id in ids:
#         val = str(hex(id)[2:])
#         if len(val) == 1:
#             val = '0' + str(hex(id)[2:])
#         tournament_id = tournament_id + val
# score = ''
# if tournament_id != '':
#     resp = requests.get("https://api.starnetwork.io/v3/game/leaderboard/" + tournament_id, headers=headers,
#                         proxies={"https": proxy}, timeout=15)
#     if resp.text.count('top') > 0:
#         score = resp.json()['data']['top'][0]['score']
#
# if score != '':
#     score = str(int(score) + rm)
#     log.info("随机增加分数:{} 提交分数:{}".format(rm, score))
# else:
#     score = str(rm)
