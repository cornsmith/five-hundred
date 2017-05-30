# -*- coding: utf-8 -*-
"""


"""

import random


class Card(object):
    """
    Represents a standard playing card including Joker

    Attributes:
      suit: integer 0-4
      rank: integer 0-13
    """

    suit_names   = ["S", "C", "D", "H"]
    suit_colours = ["B", "B", "R", "R"]
    rank_names   = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    trump_values = [ 1 ,  2 ,  3 ,  4 ,  5 ,  6 ,  7 ,  8 ,  9 , 14 , 10 , 11 , 12 ]

    def __init__(self, suit=None, rank=None, joker=False):
        self.suit = suit
        self.rank = rank
        self.joker = joker

    def __str__(self):
        if self.joker:
            return u"\U0001F0CF"
        else:
            return chr(int('0001f0%s%s' % (
                'ADCB'[self.suit],
                '0123456789ABCDE'['BA23456789TJCQK'.index(Card.rank_names[self.rank])]
            ), base=16))

    def __lt__(self, other):
        """Compares this card to other, first by suit, then rank."""
        t1 = self.value(), self.suit, self.rank
        t2 = other.value(), other.suit, other.rank
        return t1 < t2

    def value(self):
        """
        Value of card according to current trump suit and current lead suit

        200 - Joker
        100-199 - Trumps
        1-99 - Non-trumps
        """
        if self.joker: # joker
            return 200
        else: # other cards
            base_value = (lead_suit == self.suit) * self.rank
            if trump_suit:
                # trump cards
                if trump_suit == self.suit:
                    return Card.trump_values[self.rank] + 100
                # left bower
                elif Card.suit_colours[trump_suit] == Card.suit_colours[self.suit] and self.rank == 9:
                    return 13 + 100
                else:
                    return base_value
            else:
                return base_value


class Deck(object):
    """
    Represents a deck of cards.

    Attributes:
      cards: list of Card objects.
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
        res = []
        for card in self.cards:
            res.append(str(card))
        return ' '.join(res)

    def add_card(self, card):
        """Adds a card to the deck."""
        self.cards.append(card)

    def remove_card(self, card):
        """Removes a card from the deck."""
        self.cards.remove(card)

    def pop_card(self, i=-1):
        """
        Removes and returns a card from the deck.
        
        i: card to pop        
        """
        return self.cards.pop(i)

    def shuffle(self):
        """Shuffles the cards."""
        random.shuffle(self.cards)

    def sort(self):
        """Sorts the cards in ascending order."""
        self.cards.sort()

    def deal_cards(self, hand, num):
        """
        Moves the given number of cards from the deck into the Hand.

        hand: destination Hand object
        num: integer number of cards to move
        """
        for i in range(num):
            hand.add_card(self.pop_card())

    def move_cards(self, hand, cards):
        """
        Moves the given cards from the deck into the Hand.

        hand: destination Hand object
        cards: list of Card objects to move
        """
        for card in cards:
            self.remove_card(card)
            hand.add_card(card)


class Hand(Deck):
    """Represents a hand of playing cards."""

    def __init__(self, label=''):
        self.cards = []
        self.label = label


class Bid(object):
    """
    Represents a 500 bid

    Attributes:
      bid: string [6-10][SCDHN]
      misere: string [OM|CM]
    """

    def __init__(self, bid=None):
        self.bid = bid.upper()
        self.misere = None
        self.suit = None
        self.tricks = None
        if self.bid in ("OM", "CM"):
            self.misere = self.bid
        elif bid:
            self.tricks = int(self.bid[0:-1])
            self.rank = ["S", "C", "D", "H", "N"].index(self.bid[-1])
            if self.rank < 4:
                self.suit = self.rank

    def points(self):
        """Returns the number of points for bid."""
        if self.misere is None:
            return ((self.tricks - 6) * 100) + (self.rank * 20) + (40)
        elif self.misere == "OM":
            return 500
        elif self.misere == "CM":
            return 250

    def __str__(self):
        return self.bid

    def __lt__(self, other):
        """
        Compares this bid to other by points.

        Open misere beats 10H
        """
        if self.misere == "Open":
            return self.points() + 1 < other.points()
        if other.misere == "Open":
            return self.points() - 1 < other.points()
        else:
            return self.points() < other.points()


class Round(object):
    """Represents a round"""

    def __init__(self, number, dealer):
        # general
        self.number = number
        self.dealer = dealer
        self.turn = None
        self.status = "Bidding in progress"
        
        # bids
        self.bids = []        
        self.passes = [None, None, None, None]
        self.highest_bid = None        
        self.trump_suit = None
        self.highest_bidder = None                
        self.possible_bids = []
        for trick in range(6, 11):
            for suit in range(5):
                self.possible_bids.append('%s%s' % (trick, 'SCDHN'[suit]))
                if trick == 7 and suit == 3:
                    self.possible_bids.append('CM')
                if trick == 10 and suit == 3:
                    self.possible_bids.append('OM')
        
        # tricks
        self.tricks = []
        self.scores = [0, 0, 0, 0]        
        
    def __str__(self):
        pass
        
    def increment_turn(self):
        """Updates turn by one. Cycles through players."""
        self.turn = (self.turn + 1) % 4

    def update_status(self):
        """Updates the status for round."""
        if self.status == "Bidding in progress":
            if len(self.bids) >= 4:
                if self.bids[-4:].count(None) == 4:
                    self.status = "Bidding all passed"            
                elif self.bids[-3:].count(None) == 3:
                    self.status = "Bidding complete"            
            else:
                self.status = "Bidding in progress"
    
    def make_bid(self, bid):
        """Attempts to make a bid in round"""
        if self.highest_bid:
            if bid > self.highest_bid:
                self.bids.append(bid)
                self.highest_bid = bid
                self.highest_bidder = self.turn
                self.increment_turn()
                self.possible_bids = self.possible_bids[self.possible_bids.index(str(bid))+1:]
            else:
                print("Current bid must be higher than", self.highest_bid)
        else:
            self.bids.append(bid)
            self.highest_bid = bid
            self.highest_bidder = self.turn
            self.increment_turn()
            self.possible_bids = self.possible_bids[self.possible_bids.index(str(bid))+1:]
            
        self.update_status()

    def make_pass(self):
        """Makes a passing bid for current player"""
        self.bids.append(None)
        self.passes[self.turn] = True
        self.increment_turn()
        self.update_status()
    

class Trick(object):
    """Represents a trick."""
    
    def __init__(self, lead):
        self.lead = lead
        self.winner = None
        self.cards = []
        

class Game(object):
    """Represents a game."""

    def __init__(self):
        self.rounds = []        
        self.round_number = 0
        self.dealer = -1        
        self.scores = [0, 0]
        self.status = "In progress"
        
        # initialise players
        self.players = [Hand("Player 1"), Hand("Player 2"), Hand("Player 3"), Hand("Player 4")]
        self.kitty = Hand("Kitty")

    def Deal(self):
        """Deal the cards."""    
        deck = Deck()
        deck.shuffle()
        
        # deal to players
        for player in self.players:
            player.cards = []
            deck.deal_cards(player, 10)
            player.sort()
        
        # deal to kitty
        self.kitty.cards = []
        deck.deal_cards(self.kitty, 3)

    def Start_Round(self):
        """Starts a new round"""
        self.round_number += 1
        self.dealer = (self.dealer + 1) % 4
        self.round = Round(self.round_number, self.dealer)
        self.Deal()
        print('--------------------------')
        print('Round %s' % (self.round_number))
        print('--------------------------')

    def Bid_Round(self):
        """Starts a round of bidding"""
        br = self.round
        br.turn = self.dealer + 1
        while br.status == "Bidding in progress":
            if br.passes[br.turn]:
                br.make_pass()
            else:
                bid_text = input('%s - enter bid (blank for pass):' % self.players[br.turn].label)
                if bid_text:
                    br.make_bid(Bid(bid_text))
                else:
                    br.make_pass()
            print('--------------------------')
            print('Status        :', br.status)
            print('Bid History   :', '|'.join([str(bid) for bid in br.bids]))
            print('Highest Bid   :', br.highest_bid)
            print('Highest Bidder:', self.players[br.highest_bidder].label)
            print('\n')

        # bidding finished
        if br.status == "Bidding complete":
            br.trump_suit = br.highest_bid.suit
            self.kitty.deal_cards(players[br.highest_bidder], 3) # winning bidder gets kitty
        elif br.status == "Bidding all passed":
            pass
        
    def Discard_Kitty(self, policy=None):
        """Discards extra 3 cards from hand back to kitty"""
        player = players[self.round.highest_bidder]
        if policy:
            pass
        else:
            cards = random.sample(player.cards, 3)
        player.move_cards(kitty, cards)
    
    def Card_Round(self):
        """Starts a round of card playing"""
        pass
               
    def End_Round(self):
        """Ends a round"""
        self.rounds.append(self.round)
        if max(abs(i) for i in self.scores) >= 500:
            self.status = "Complete"
    
    

def Print_Hands():
    # print hands
    for player in players:
        player.sort()
        print(player.label, player)
    print(kitty.label, kitty)


if __name__ == '__main__':
    trump_suit = None
    lead_suit = None

    game = Game()
    players = game.players
    kitty = game.kitty

    while game.status == "In progress":
        # deal cards
        game.Start_Round()
        Print_Hands()
    
        # bidding
        game.Bid_Round()        
        if game.round.status == "Bidding complete":
            trump_suit = game.round.trump_suit
            
            Print_Hands()
            game.Discard_Kitty()
            Print_Hands()
        
            # card play

        # end round
        game.End_Round()