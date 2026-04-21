"""
Basic Strategy for 6-deck, dealer stands on soft 17 (S17).
Actions: H=Hit, S=Stand, D=Double(else Hit), Ds=Double(else Stand), P=Split, R=Surrender(else Hit)
"""

# Hard totals: player_total -> {dealer_upcard: action}
HARD = {
    # total : 2    3    4    5    6    7    8    9   10    A
    8:  {2:'H', 3:'H', 4:'H', 5:'H', 6:'H', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    9:  {2:'H', 3:'D', 4:'D', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    10: {2:'D', 3:'D', 4:'D', 5:'D', 6:'D', 7:'D', 8:'D', 9:'D', 10:'H', 'A':'H'},
    11: {2:'D', 3:'D', 4:'D', 5:'D', 6:'D', 7:'D', 8:'D', 9:'D', 10:'D', 'A':'D'},
    12: {2:'H', 3:'H', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    13: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    14: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    15: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'H', 10:'R', 'A':'H'},
    16: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'H', 8:'H', 9:'R', 10:'R', 'A':'R'},
    17: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S', 10:'S', 'A':'S'},
}

# Soft totals (one Ace counted as 11): player_total -> {dealer_upcard: action}
SOFT = {
    # Soft 13 = A+2, Soft 14 = A+3, ...
    13: {2:'H', 3:'H', 4:'H', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    14: {2:'H', 3:'H', 4:'H', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    15: {2:'H', 3:'H', 4:'D', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    16: {2:'H', 3:'H', 4:'D', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    17: {2:'H', 3:'D', 4:'D', 5:'D', 6:'D', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    18: {2:'Ds',3:'Ds',4:'Ds',5:'Ds',6:'Ds',7:'S', 8:'S', 9:'H', 10:'H', 'A':'H'},
    19: {2:'S', 3:'S', 4:'S', 5:'S', 6:'Ds',7:'S', 8:'S', 9:'S', 10:'S', 'A':'S'},
    20: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S', 10:'S', 'A':'S'},
}

# Pairs: card_value -> {dealer_upcard: action}  P=Split, else follow hard/soft
PAIRS = {
    2:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'H', 9:'H', 10:'H', 'A':'H'},
    3:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'H', 9:'H', 10:'H', 'A':'H'},
    4:  {2:'H', 3:'H', 4:'H', 5:'P', 6:'P', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    5:  {2:'D', 3:'D', 4:'D', 5:'D', 6:'D', 7:'D', 8:'D', 9:'D', 10:'H', 'A':'H'},
    6:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'H', 8:'H', 9:'H', 10:'H', 'A':'H'},
    7:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'H', 9:'H', 10:'H', 'A':'H'},
    8:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'P', 9:'P', 10:'P', 'A':'P'},
    9:  {2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'S', 8:'P', 9:'P', 10:'S', 'A':'S'},
    10: {2:'S', 3:'S', 4:'S', 5:'S', 6:'S', 7:'S', 8:'S', 9:'S', 10:'S', 'A':'S'},
    'A':{2:'P', 3:'P', 4:'P', 5:'P', 6:'P', 7:'P', 8:'P', 9:'P', 10:'P', 'A':'P'},
}

ACTION_LABELS = {
    'H':  'Hit（要牌）',
    'S':  'Stand（停牌）',
    'D':  'Double Down（加倍，否則要牌）',
    'Ds': 'Double Down（加倍，否則停牌）',
    'P':  'Split（分牌）',
    'R':  'Surrender（投降，否則要牌）',
}

CARD_VALUES = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
               '10':10,'J':10,'Q':10,'K':10,'A':11}


def card_val(c: str) -> int:
    return CARD_VALUES.get(c.upper(), 0)


def dealer_key(dealer_up: str) -> int | str:
    v = card_val(dealer_up)
    return 'A' if dealer_up.upper() == 'A' else v


def recommend(player_cards: list[str], dealer_up: str) -> dict:
    """
    player_cards: list of card strings e.g. ['A', '7']
    dealer_up: dealer's visible card e.g. '9'
    Returns dict with action code, label, and hand description.
    """
    d = dealer_key(dealer_up)
    vals = [card_val(c) for c in player_cards]

    # Check pair
    if len(player_cards) == 2:
        c0 = player_cards[0].upper()
        c1 = player_cards[1].upper()
        p_key = None
        if c0 == c1:
            p_key = 'A' if c0 == 'A' else card_val(c0)
        elif card_val(c0) == card_val(c1):
            p_key = card_val(c0)

        if p_key is not None and p_key in PAIRS:
            action = PAIRS[p_key].get(d, 'H')
            return {
                'action': action,
                'label': ACTION_LABELS.get(action, action),
                'hand_type': f'對子 {c0}+{c1}',
            }

    # Check soft hand (has Ace counted as 11 without busting)
    has_ace = any(c.upper() == 'A' for c in player_cards)
    total_hard = sum(min(v, 10) for v in vals)  # treat all aces as 1
    total_soft = total_hard + 10 if has_ace else total_hard  # one ace as 11

    if has_ace and total_soft <= 21 and total_soft in SOFT:
        action = SOFT[total_soft].get(d, 'S')
        return {
            'action': action,
            'label': ACTION_LABELS.get(action, action),
            'hand_type': f'軟牌 Soft {total_soft}',
        }

    # Hard hand
    total = total_soft if has_ace and total_soft <= 21 else total_hard
    if total >= 17:
        action = HARD.get(17, {}).get(d, 'S')
        action = 'S'
    elif total <= 8:
        action = 'H'
    else:
        action = HARD.get(total, {}).get(d, 'H')

    return {
        'action': action,
        'label': ACTION_LABELS.get(action, action),
        'hand_type': f'硬牌 Hard {total}',
    }
