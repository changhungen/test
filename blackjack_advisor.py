#!/usr/bin/env python3
"""
Blackjack Card Counting Advisor
Hi-Lo system + Basic Strategy (6-deck, dealer S17)

Usage:
  python blackjack_advisor.py [--decks N] [--unit N]

Commands during play:
  new          - start a new round (reset player/dealer hand)
  reset        - reset the ENTIRE shoe (new shoe)
  p <cards>    - set your hand, e.g.  p A 7
  d <card>     - set dealer upcard, e.g.  d 9
  seen <cards> - record cards seen this round (all visible cards)
  advice       - get bet + strategy advice
  status       - show count status
  q / quit     - exit
  help         - show commands
"""

import argparse
import sys
from counter import CardCounter
from strategy import recommend


def color(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"

def green(t):  return color(t, "92")
def yellow(t): return color(t, "93")
def red(t):    return color(t, "91")
def cyan(t):   return color(t, "96")
def bold(t):   return color(t, "1")


def print_banner():
    print(bold(cyan("""
╔══════════════════════════════════════════╗
║   Blackjack Hi-Lo Counting Advisor       ║
║   6-deck · Dealer stands on Soft 17      ║
╚══════════════════════════════════════════╝
""")))


def print_help():
    print(cyan("""
Commands:
  new              開始新一局（清空手牌）
  reset            重新洗牌（清空計數）
  p <牌> <牌> ...  設定你的手牌  e.g. p A 7
  d <牌>           設定莊家明牌  e.g. d 9
  seen <牌> ...    記錄本局看到的牌（含公開牌）
  advice           顯示下注建議 + 策略建議
  status           顯示計數狀態
  q / quit         退出

牌面輸入方式：
  數字牌: 2 3 4 5 6 7 8 9 10
  花牌:   J Q K  (或小寫 j q k)
  A牌:    A      (或小寫 a)
"""))


def format_count_bar(tc: float) -> str:
    level = int(tc)
    if tc < 0:
        bar = red(f"{'◄' * min(abs(level), 10)}  TC={tc:+.1f}  不利")
    elif tc == 0:
        bar = yellow(f"  TC={tc:+.1f}  中性")
    elif tc <= 2:
        bar = yellow(f"  TC={tc:+.1f}  略有優勢")
    elif tc <= 4:
        bar = green(f"{'►' * level}  TC={tc:+.1f}  有利 ▲")
    else:
        bar = bold(green(f"{'►' * min(level, 10)}  TC={tc:+.1f}  非常有利 ★★"))
    return bar


def print_status(counter: CardCounter, unit: int):
    s = counter.status()
    bet = counter.bet_advice(unit)
    print()
    print(bold("═══ 計數狀態 ═══════════════════════"))
    print(f"  Running Count : {yellow(str(s['running_count']))}")
    print(f"  True Count    : {format_count_bar(s['true_count'])}")
    print(f"  剩餘牌組      : {s['decks_remaining']} 副")
    print(f"  已見牌數      : {s['cards_seen']}  ({s['penetration_pct']}% 滲透率)")
    print(bold("═══ 下注建議 ═══════════════════════"))
    print(f"  {green(bet['label'])}")
    print(f"  建議下注      : {bold(green(str(bet['amount'])))} (單位 {unit})")
    print()


def print_strategy(player_cards: list[str], dealer_up: str):
    if not player_cards or not dealer_up:
        print(yellow("  請先輸入手牌 (p ...) 和莊家牌 (d ...)"))
        return
    result = recommend(player_cards, dealer_up)
    print()
    print(bold("═══ 策略建議 ═══════════════════════"))
    print(f"  你的手牌  : {' '.join(player_cards)}  ({result['hand_type']})")
    print(f"  莊家明牌  : {dealer_up}")
    print(f"  建議動作  : {bold(green(result['label']))}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Blackjack Hi-Lo Advisor')
    parser.add_argument('--decks', type=int, default=6, help='牌組數量 (預設 6)')
    parser.add_argument('--unit', type=int, default=100, help='基本下注單位 (預設 100)')
    args = parser.parse_args()

    counter = CardCounter(num_decks=args.decks)
    player_cards: list[str] = []
    dealer_up: str = ''

    print_banner()
    print(f"  牌組: {args.decks} 副  |  下注單位: {args.unit}")
    print(f"  輸入 {cyan('help')} 查看指令\n")

    while True:
        try:
            line = input(bold(cyan("BJ> "))).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再見！")
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd in ('q', 'quit', 'exit'):
            print("再見！")
            break

        elif cmd == 'help':
            print_help()

        elif cmd == 'new':
            player_cards = []
            dealer_up = ''
            print(green("  ✓ 新一局開始，手牌已清空"))

        elif cmd == 'reset':
            counter.reset()
            player_cards = []
            dealer_up = ''
            print(green(f"  ✓ 重新洗牌，{args.decks} 副牌組已重置"))

        elif cmd == 'p':
            if len(parts) < 2:
                print(yellow("  用法: p <牌1> <牌2> ...  e.g. p A 7"))
                continue
            cards = [counter.normalize(c) for c in parts[1:]]
            invalid = [p for p, n in zip(parts[1:], cards) if n is None]
            if invalid:
                print(red(f"  無效牌面: {' '.join(invalid)}"))
                continue
            player_cards = cards
            print(green(f"  ✓ 你的手牌: {' '.join(player_cards)}"))

        elif cmd == 'd':
            if len(parts) < 2:
                print(yellow("  用法: d <牌>  e.g. d 9"))
                continue
            n = counter.normalize(parts[1])
            if n is None:
                print(red(f"  無效牌面: {parts[1]}"))
                continue
            dealer_up = n
            print(green(f"  ✓ 莊家明牌: {dealer_up}"))

        elif cmd == 'seen':
            if len(parts) < 2:
                print(yellow("  用法: seen <牌1> <牌2> ..."))
                continue
            ok, fail = [], []
            for c in parts[1:]:
                if counter.add_card(c):
                    ok.append(counter.normalize(c))
                else:
                    fail.append(c)
            if ok:
                print(green(f"  ✓ 已記錄: {' '.join(ok)}"))
            if fail:
                print(red(f"  無效牌面（跳過）: {' '.join(fail)}"))

        elif cmd == 'advice':
            print_status(counter, args.unit)
            print_strategy(player_cards, dealer_up)

        elif cmd == 'status':
            print_status(counter, args.unit)

        elif cmd == 'strategy':
            print_strategy(player_cards, dealer_up)

        else:
            print(yellow(f"  未知指令: {cmd}，輸入 help 查看指令列表"))


if __name__ == '__main__':
    main()
