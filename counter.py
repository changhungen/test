"""
Hi-Lo Card Counting Engine
- Running count, True count, bet sizing recommendation
"""

# Hi-Lo values: small cards (+1) benefit player when gone, big cards (-1) benefit player when present
HILO = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
    '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1,
}

CARD_ALIASES = {
    'T': '10', 't': '10', 'j': 'J', 'q': 'Q', 'k': 'K', 'a': 'A',
    '1': 'A',  # allow '1' as Ace shorthand
}


class CardCounter:
    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self.running_count = 0
        self.cards_seen = 0
        self.total_cards = num_decks * 52

    def reset(self):
        self.running_count = 0
        self.cards_seen = 0

    def normalize(self, card: str) -> str | None:
        card = card.strip().upper()
        card = CARD_ALIASES.get(card, card)
        if card in HILO:
            return card
        return None

    def add_card(self, card: str) -> bool:
        normalized = self.normalize(card)
        if normalized is None:
            return False
        self.running_count += HILO[normalized]
        self.cards_seen += 1
        return True

    @property
    def decks_remaining(self) -> float:
        cards_left = self.total_cards - self.cards_seen
        return max(cards_left / 52, 0.5)  # floor at 0.5 to avoid division issues

    @property
    def true_count(self) -> float:
        return self.running_count / self.decks_remaining

    @property
    def penetration(self) -> float:
        return self.cards_seen / self.total_cards

    def bet_advice(self, unit: int = 100) -> dict:
        tc = self.true_count
        if tc <= 1:
            multiplier = 1
            label = "最小注 (Min bet)"
        elif tc <= 2:
            multiplier = 2
            label = "小注 (2 units)"
        elif tc <= 3:
            multiplier = 4
            label = "中注 (4 units)"
        elif tc <= 4:
            multiplier = 8
            label = "大注 (8 units)"
        else:
            multiplier = 12
            label = "最大注 (12 units) ★"
        return {
            'multiplier': multiplier,
            'amount': unit * multiplier,
            'label': label,
            'true_count': round(tc, 2),
            'running_count': self.running_count,
        }

    def status(self) -> dict:
        return {
            'running_count': self.running_count,
            'true_count': round(self.true_count, 2),
            'decks_remaining': round(self.decks_remaining, 1),
            'cards_seen': self.cards_seen,
            'penetration_pct': round(self.penetration * 100, 1),
        }
