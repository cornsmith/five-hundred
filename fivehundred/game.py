# -*- coding: utf-8 -*-
"""


"""

import argparse
import random

from ai import Policy


class Card(object):
    """Represents a standard playing card including Joker.

    Args:
        suit (int): int representation of card suit [0-3]
        rank (int): int representation of card rank [0-12]
        joker (bool): indicates joker

    Attributes:
        suit (int): directly passed from arg
        rank (int): directly passed from arg
        joker (bool): directly passed from arg
    """

    suit_names = ["S", "C", "D", "H"]
    suit_colours = ["B", "B", "R", "R"]
    rank_names = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    def __init__(self, suit=None, rank=None, joker=False):
        self.suit = suit
        self.rank = rank
        self.joker = joker

    def __str__(self):
        """Returns unicode (graphical) representation of card"""
        if self.joker:
            return u"\U0001F0CF"
        else:
            return chr(int('0001f0%s%s' % (
                'ADCB'[self.suit],
                '0123456789ABCDE'['BA23456789TJCQK'.index(Card.rank_names[self.rank])]
            ), base=16))

    def __lt__(self, other):
        """Compares this card to other, first by suit, then rank"""
        val1 = self.value(), self.suit, self.rank
        val2 = other.value(), other.suit, other.rank
        return val1 < val2

    def bower(self):
        """Returns bower type"""
        if trump_suit is not None:
            if self.rank == 9:
                if trump_suit == self.suit:
                    return 'Right'
                elif Card.suit_colours[trump_suit] == Card.suit_colours[self.suit]:
                    return 'Left'

    def value(self):
        """Value of card according to current trump suit

        Returns:
            400     - Joker
            300     - Right bower
            200     - Left bower
            100-199 - Trumps
            0       - Off-suit / No trumps
        """

        if self.joker:  # joker always highest
            return 400
        elif trump_suit is None: # no trumps
            return 0
        elif self.bower() == 'Right': # right bower
            return 300
        elif self.bower() == 'Left': # left bower
            return 200
        elif trump_suit == self.suit: # other trumps
            return self.rank + 100
        else:
            return 0


class Deck(object):
    """Represents a deck of cards.

    Notes:
        4-player 43-card deck including Joker

    Attributes:
      cards (list): list of Card objects
    """

    def __init__(self):
        self.cards = []
        for suit in range(4):
            for rank in range(2, 13):
                if rank > 2 or suit > 1: # 4-player deck
                    card = Card(suit, rank)
                    self.cards.append(card)
        # add joker
        joker = Card(joker=True)
        self.cards.append(joker)

    def __str__(self):
        res = [str(card) for card in self.cards]
        return ' '.join(res)

    def add_card(self, card):
        """Adds a card to the deck."""
        self.cards.append(card)

    def remove_card(self, card):
        """Removes a card from the deck."""
        self.cards.remove(card)

    def pop_card(self, i=-1):
        """Removes and returns a card from the deck.

        Args:
            i (int): card to pop
        """
        return self.cards.pop(i)

    def shuffle(self):
        """Shuffles the cards."""
        random.shuffle(self.cards)

    def sort(self):
        """Sorts the cards in ascending order."""
        self.cards.sort()

    def deal_cards(self, hand, num):
        """Moves the given number of cards from the deck into the Hand.

        Args:
            hand (Hand): destination hand
            num (int): number of cards to move
        """
        for i in range(num):
            hand.add_card(self.pop_card())

    def move_cards(self, hand, cards):
        """Moves the given cards from the deck into the Hand.

        Args:
            hand (Hand): destination hand
            cards (list): list of Card objects to move
        """
        for card in cards:
            self.remove_card(card)
            hand.add_card(card)


class Hand(Deck):
    """Represents a hand of playing cards.

    Attributes:
      cards (list): list of Card objects
      label (str): name of the hand
      possible (list): list of Card objects that are valid for the trick
      possible_index (list): hand index of possible
    """

    def __init__(self, label=''):
        self.label = label
        self.cards = []
        self.possible = []
        self.possible_index = []

    def set_possible(self, trick):
        """Sets the possible attribute.

        Args:
            trick (Trick): the current trick being played
        """
        self.possible = []
        self.possible_index = []

        # append cards in hand of lead suit
        if trick.lead_suit is not None:
            for card in self.cards:
                # joker and bowers should be trump suit
                test_suit = card.suit
                if card.joker or card.bower() is not None:
                    test_suit = trump_suit
                if test_suit == trick.lead_suit:
                    self.possible.append(card)
                    self.possible_index.append(self.cards.index(card))

        # all cards if cannot follow suit
        if not self.possible:
            self.possible = self.cards
            self.possible_index = range(len(self.cards))


class Bid(object):
    """Represents a bid.

    Attributes:
      bid (str): bid string - ([6-10][SCDHN]|[OM|CM])
      pass_ (bool): indicates a pass bid
      tricks (int): number of tricks to be won
      suit_rank (int): suit of bid including no trumps - [0-4]
      suit (int): suit of bid - [0-3], NoneType for no trumps
      valid (bool): indicates a valid bid
      misere (bool): indicates a misere bid
    """

    possible = []
    for trick in range(6, 11):
        for suit in range(5):
            possible.append('%s%s' % (trick, 'SCDHN'[suit]))
    possible.insert(possible.index('8C'), 'CM')
    possible.insert(possible.index('10N'), 'OM')

    def __init__(self, bid=None):
        self.bid = None
        self.pass_ = False
        self.tricks = None
        self.suit_rank = None
        self.suit = None
        self.valid = True
        self.misere = None

        if bid:
            # clean up bid
            bid = bid.upper()

            if bid in Bid.possible:
                self.bid = bid
                if bid in ("OM", "CM"):
                    self.misere = bid

                # tricks, rank, suit
                if self.misere is None:
                    self.tricks = int(bid[0:-1])
                    self.suit_rank = 'SCDHN'.index(bid[-1])
                    if self.suit_rank < 4:
                        self.suit = self.suit_rank
            else:
                self.valid = False
        else:
            self.pass_ = True

    def points(self):
        """Returns the number of points for bid."""
        if self.pass_:
            return 0

        if self.bid == "OM":
            return 500
        elif self.bid == "CM":
            return 250
        else:
            return ((self.tricks - 6) * 100) + (self.suit_rank * 20) + (40)

    def __str__(self):
        if self.bid:
            return self.bid
        else:
            return 'Ps'

    def __lt__(self, other):
        """Compares this bid to other by points.

        Notes:
            Open misere beats 10H
        """
        if self.bid == "OM":
            return self.points() + 1 < other.points()
        if other.bid == "OM":
            return self.points() - 1 < other.points()
        else:
            return self.points() < other.points()


class Round(object):
    """Represents a round.

    Attributes:
        number (int): round number
        dealer (int): index of current dealer for round
        turn (int): index of current turn within round - [0-3]
        status (str): status of round
        starting_hands(list): list of lists of Card objects
        bids (list): list of bids made
        passes (list): list of passed bids made
        highest_bid (Bid): winning bid for round
        possible_bids (Bid.possible)
        tricks (list): list of Trick objects played
        tricks_won (list): team tricks tally for round
        scores (list) : team scores for round
    """

    def __init__(self, number, dealer):
        # general
        self.number = number
        self.dealer = dealer
        self.turn = None
        self.status = "Bidding in progress"
        self.starting_hands = []

        # bids
        self.bids = []
        self.passes = [None, None, None, None]
        self.highest_bid = Bid()
        self.trump_suit = None
        self.highest_bidder = None
        self.possible_bids = Bid.possible

        # tricks
        self.tricks = []
        self.tricks_won = [0, 0]
        self.scores = [0, 0]

    def __str__(self):
        pass

    def increment_turn(self):
        """Updates turn by one. Cycles through players."""
        self.turn = (self.turn + 1) % 4

        # skip misere partner
        if self.status == "Card play in progress":
            if self.highest_bid.misere and self.turn == (self.highest_bidder + 2) % 4:
                self.turn = (self.turn + 1) % 4

    def update_status(self):
        """Updates the status for round."""
        if self.status == "Bidding in progress":
            if len(self.bids) >= 4:
                if self.passes.count(True) == 4:
                    self.status = "Bidding all passed"
                elif self.passes.count(True) == 3:
                    self.status = "Bidding complete"
            else:
                self.status = "Bidding in progress"

    def make_bid(self, bid):
        """Attempts to make a bid in round.

        Args:
            bid (Bid): Bid object
        """
        if not bid.valid:
            print("Not a valid bid")
        else:
            if bid.pass_:
                self.bids.append(bid)
                self.passes[self.turn] = True
                self.increment_turn()
            else:
                if bid > self.highest_bid:
                    self.bids.append(bid)
                    self.highest_bid = bid
                    self.highest_bidder = self.turn
                    self.increment_turn()
                    self.possible_bids = Bid.possible[Bid.possible.index(str(bid))+1:]
                else:
                    print(bid.points(), self.highest_bid.points())
                    print("Current bid must be higher than", self.highest_bid)

    def play_card(self, player, hand_index, trick):
        """Attempts to play a card in trick.

        Args:
            player (Hand): Hand object of player hand to be played
            hand_index (int): index of player hand to be played
            trick (Trick): trick to play card in
        """
        try:
            card = player.cards[hand_index]
            if trick.cards:
                if card in player.possible:
                    player.move_cards(trick, [card])
                    self.increment_turn()
                else:
                    print("Need to follow suit")
            else:
                if card.joker or card.bower() is not None:
                    trick.lead_suit = trump_suit
                else:
                    trick.lead_suit = card.suit
                player.move_cards(trick, [card])
                self.increment_turn()

        except:
            print("Card not present")

    def set_scores(self):
        """Sets the scores at the end of round."""
        bid_team = self.highest_bidder % 2
        off_team = (self.highest_bidder + 1) % 2

        if self.highest_bid.misere: # misere
            bid_made = self.tricks_won[bid_team] == 0
        else: # non-misere
            bid_made = self.tricks_won[bid_team] >= self.highest_bid.tricks
            self.scores[off_team] += self.tricks_won[off_team] * 10

        # increment major scores
        if bid_made:
            self.scores[bid_team] += self.highest_bid.points()
        else:
            self.scores[bid_team] -= self.highest_bid.points()

class Trick(Deck):
    """Represents a trick.

    Args:
        lead (int): player index of lead player
        misere: indicates a misere player

    Attributes:
        lead (int): player index of lead player
        misere (int): player index of misere player
        lead_suit (int): suit index of suit led
        winner (int): player index of trick winner
        cards (list): list of Card objects played in trick
    """

    def __init__(self, lead, number, misere=None):
        self.lead = lead
        self.number = number
        self.misere = misere
        self.lead_suit = None
        self.winner = None
        self.cards = []

    def __str__(self):
        res = [str(card) for card in self.cards]
        return ' '.join(res)

    def get_winner(self):
        """Gets the current winning card index"""
        card_values = dict(zip(range(4), [-1] * 4))
        player_index = self.lead

        if len(self.cards) > 0:
            for card in self.cards:
                try:
                    lead_value = (card.suit == self.lead_suit) * card.rank
                except TypeError:
                    lead_value = 0

                if self.misere is not None:
                    if (self.misere + 2) % 4 == player_index:
                        player_index = (player_index + 1) % 4

                card_values[player_index] = max(lead_value, card.value())
                player_index = (player_index + 1) % 4

            return max(card_values, key=card_values.get)
        else:
            return None

    def set_winner(self):
        """Sets the winner of the trick"""
        if self.is_complete():
            self.winner = self.get_winner()

    def is_complete(self):
        """Returns whether all players have played their cards in trick"""
        return len(self.cards) + (self.misere is not None) == 4


class Game(object):
    """Represents a game.

    Attributes:
        rounds (list): list of Round objects in game
        round (Round): current Round object
        round_number (int): current round number
        dealer (int): player index of current dealer
        scores (list): list of team scores for the game
        status (str): current status of the game {'In progress', 'Complete'}
        players (list): list of players (Hand objects) in the game
        kitty (Hand): the kitty container
    """

    def __init__(self):
        self.rounds = []
        self.round = None
        self.round_number = 0
        self.dealer = -1
        self.scores = [0, 0]
        self.status = "In progress"

        # initialise players
        self.players = [Hand("P1"), Hand("P2"), Hand("P3"), Hand("P4")]
        self.kitty = Hand()

    def deal(self):
        """Deal the cards."""
        # initialise new deck
        deck = Deck()
        deck.shuffle()

        # deal to players
        for player in self.players:
            player.cards = []
            deck.deal_cards(player, 10)
            player.sort()

        # deal to kitty
        self.kitty.cards = []
        self.kitty.label = "Kitty"
        deck.deal_cards(self.kitty, 3)

    def start_round(self):
        """Starts a new round."""
        self.round_number += 1
        self.dealer = (self.dealer + 1) % 4
        self.round = Round(self.round_number, self.dealer)
        trump_suit = None
        self.deal()
        self.round.starting_hands = [player.cards[:] for player in self.players] + [self.kitty.cards[:]]

        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Round %s' % (self.round_number))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    def bid_round(self, policy):
        """Starts a round of bidding."""
        # setup
        br = self.round
        br.turn = (self.dealer + 1) % 4

        print('\n========================================')
        print('Begin bidding')
        print('========================================')

        # bidding in progress
        while br.status == "Bidding in progress":
            # passed players cannot make any more bids in round
            if br.passes[br.turn]:
                br.make_bid(Bid(None))
                continue

            if br.turn == HUMAN_PLAYER or policy == 'human':
                print('\n--------------------------')
                print('Status        :', br.status)
                print('Bid History   :', '|'.join([str(bid) for bid in br.bids]))
                if br.highest_bidder is not None:
                    print('Highest Bidder:', self.players[br.highest_bidder].label)
                print('--------------------------')
                print('{0} - {1}'.format(self.players[br.turn].label, self.players[br.turn]))
                print('Possible -', ' '.join(br.possible_bids))
                bid_text = input('Bid (blank for pass):')
            else:
                pol = Policy()
                try:
                    bid_text = pol.bid((self.players[br.turn], br.bids, br.possible_bids, Bid), policy)
                except IndexError:
                    bid_text = ''
            br.make_bid(Bid(bid_text))
            br.update_status()

        # bidding finished
        if br.status == "Bidding complete":
            print('\n--------------------------')
            print('Bidding complete')
            print(self.players[br.highest_bidder].label, '-', br.highest_bid)
            print('|'.join([str(bid) for bid in br.bids]))
            print('--------------------------')
            br.trump_suit = br.highest_bid.suit
            self.kitty.deal_cards(self.players[br.highest_bidder], 3) # winning bidder gets kitty

        elif br.status == "Bidding all passed":
            print('\n--------------------------')
            print('Bidding complete - all passed')
            print('--------------------------')

    def discard_round(self, policy):
        """Discards extra 3 cards from hand back to kitty.

        Args:
            policy (?): AI policy for discard strategy
        """
        # setup
        dr = self.round
        player = self.players[dr.highest_bidder]

        if dr.highest_bidder == HUMAN_PLAYER or policy == 'human':
            discard_text = input('Discard indices [0-12] (Enter 3 indices separated by commas, e.g. x,y,z):')
            cards = [player.cards[int(x)] for x in discard_text.split(',')]
        elif policy is not None:
            pol = Policy()
            cards = pol.discard((player.cards, dr.highest_bid), policy)
        else:
            raise ValueError

        # make discard
        player.move_cards(self.kitty, cards)
        self.kitty.label = 'Discard'

    def card_round(self, policy):
        """Starts a round of card playing."""
        # setup
        cr = self.round
        cr.status = "Card play in progress"
        misere = None
        if cr.highest_bid.misere is not None:
            misere = cr.highest_bidder
        cr.turn = cr.highest_bidder

        print('\n========================================')
        print('Begin card play')
        print('========================================')

        # card play in progress
        for trick_num in range(10):
            trick = Trick(cr.turn, trick_num, misere)

            while not trick.is_complete():
                self.players[cr.turn].set_possible(trick)
                if cr.turn == HUMAN_PLAYER or policy == 'human':
                    print('\n--------------------------')
                    print('Status        :', cr.status)
                    print('Bid           :', cr.highest_bid)
                    print('Trick {0} - {1}'.format(trick_num + 1, trick))
                    print('--------------------------')
                    print('{0} - {1} | {2}'.format(
                        self.players[cr.turn].label,
                        self.players[cr.turn],
                        ' '.join([str(card) for card in self.players[cr.turn].possible]),
                    ))
                    input_text = 'Card index ({0}):'.format(' '.join([str(_) for _ in self.players[cr.turn].possible_index]))
                    hand_index = input(input_text)
                    if hand_index:
                        hand_index = int(hand_index)
                elif policy is not None:
                    pol = Policy()
                    hand_index = pol.card((self.players[cr.turn], trick, cr.tricks), policy)
                else:
                    raise ValueError

                cr.play_card(self.players[cr.turn], hand_index, trick)

            trick.set_winner()
            cr.turn = trick.winner
            cr.tricks_won[trick.winner % 2] += 1
            cr.tricks.append(trick)

            print('\n--------------------------')
            print('Trick         :', trick_num + 1)
            print('Cards Played  :', trick)
            print('Lead          :', self.players[trick.lead].label)
            print('Winner        :', self.players[trick.winner].label)
            print('Trick Count   :', cr.tricks_won)
            print('--------------------------')

        # card play complete
        cr.status = "Card play complete"
        cr.set_scores()

    def end_round(self):
        """Ends a round."""
        self.rounds.append(self.round)
        self.scores = [a + b for a, b in zip(self.scores, self.round.scores)]
        if max(abs(i) for i in self.scores) >= 500:
            self.status = "Complete"

        print('\n--------------------------')
        print('Round {0} complete'.format(self.round_number))
        print('Round Score: ', self.round.scores)
        print('Game Scores: ', self.scores)
        print('Game Status: ', self.status)
        print('--------------------------')

    def print_hands(self):
        """Sorts and prints hands including kitty."""
        for player in self.players:
            player.sort()
            if HUMAN_PLAYER == self.players.index(player) or HUMAN_PLAYER is None:
                print(player.label, player)
        if HUMAN_PLAYER is None:
            print(self.kitty.label, self.kitty)


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--play',
        type=int,
        choices=range(1, 5),
        default=None,
        help="Human player",
    )
    parser.add_argument(
        '--bidai',
        type=str,
        choices=["human", "random", "score",],
        default="score",
        help="Bid Round AI",
    )
    parser.add_argument(
        '--discardai',
        type=str,
        choices=["human", "random", "lowest",],
        default="lowest",
        help="Discard Round AI",
    )
    parser.add_argument(
        '--cardai',
        type=str,
        choices=["human", "random", "highest", "basic",],
        default="basic",
        help="Card Round AI",
    )
    parser.add_argument(
        '--savedir',
        type=str,
        help="Directory to save finished game",
        default=None,
    )
    args = parser.parse_args()

    # setup arguments
    BID_POLICY = args.bidai
    DISCARD_POLICY = args.discardai
    CARD_POLICY = args.cardai

    if args.play:
        HUMAN_PLAYER = args.play - 1
    else:
        HUMAN_PLAYER = None

    # setup game
    trump_suit = None
    game = Game()

    # main game loop
    while game.status == "In progress":
        # deal cards
        game.start_round()
        game.print_hands()

        # bidding
        game.bid_round(policy=BID_POLICY)
        if game.round.status == "Bidding complete":
            trump_suit = game.round.trump_suit

            game.print_hands()
            game.discard_round(policy=DISCARD_POLICY)
            game.print_hands()

            # card play
            game.card_round(policy=CARD_POLICY)

        # end round
        game.end_round()

    if args.savedir:
        import pickle
        import time
        filename = args.savedir + '/' + str(time.time()) + '.500'
        with open(filename, 'wb') as f:
            pickle.dump(game, f, pickle.HIGHEST_PROTOCOL)
