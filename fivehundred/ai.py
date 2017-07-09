import random


class Policy(object):
    """Policy class.

    Functions:
        bid: policy for bidding round
        discard: policy for discard round
        card: policy for card playing round
    """

    def __init__(self):
        pass

    def bid(self, env, type_):
        """Bidding round policy"""
        player, bids, possible, Bid = env
        bid_text = ''

        if type_ == 'random':
            if random.random() < 0.2:
                bid_text = random.choice(possible)

        elif type_ == 'score':
            # initialise scores
            suit_scores = [0, 0, 0, 0, 0]
            misere = 0

            # score each card
            for card in player.cards:
                if card.joker:
                    suit_scores = [ss + 15 for ss in suit_scores]
                    misere += 2
                else:
                    misere += (card.rank > 7)
                    suit_scores[card.suit] += card.rank
                    if card.rank > 10:
                        suit_scores[4] += card.rank
                    if card.rank == 9:
                        suit_scores[card.suit] += 5
                        suit_scores[(card.suit + 2) % 4] += 4

            # turn scores to maximum tricks
            suit_scores = [(ss // 15) + 5 for ss in suit_scores]

            # get lowest possible bid that meets score thresholds
            for bid in possible:
                if bid[-1] == 'M':
                    if bid == 'CM' and misere < 4:
                        bid_text = bid
                        break
                    if bid == 'OM' and misere < 2:
                        bid_text = bid
                        break
                else:
                    if Bid(bid).tricks <= suit_scores[Bid(bid).suit_rank]:
                        bid_text = bid
                        break
        else:
            raise ValueError

        return bid_text

    def discard(self, env, type_):
        """Discard round policy"""
        cards, bid = env

        # never throw trump cards away
        keep_list = [card for card in cards if card.suit == bid.suit or card.joker or card.bower() is not None]
        discard_list = list(set(cards) - set(keep_list))

        if type_ == 'random':
            discard_cards = random.sample(discard_list, 3)

        elif type_ == 'lowest':
            reverse = bid.misere is not None
            discard_cards = sorted(discard_list, key=lambda x: x.rank, reverse=reverse)[:3]
            discard_cards += sorted(keep_list, reverse=reverse)[:3 - len(discard_cards)]

        #TODO: by suit
        else:
            raise ValueError

        return discard_cards

    def card(self, env, type_):
        """Card playing policy"""
        player, trick, tricks = env
        psv = {i: (player.cards[i].value(), player.cards[i].rank) for i in player.possible_index}
        lowest_index = min(psv, key=lambda k: psv[k])
        highest_index = max(psv, key=lambda k: psv[k])

        if type_ == 'random':
            card_index = random.choice(player.possible_index)

        elif type_ == 'highest':
            if trick.misere is not None:
                card_index = lowest_index
            else:
                card_index = highest_index

        elif type_ == 'basic':
            # misere policy
            if trick.misere is not None:
                if trick.cards:
                    #TODO: of all possible, play highest card that can't win
                    card_index = lowest_index
                else:
                    # lead lowest
                    card_index = lowest_index

            # non-misere policy
            else:
                if len(trick.cards) == 0:
                    # lead the highest
                    card_index = highest_index

                elif len(trick.cards) == 1:
                    #TODO: if highest can't win then lowest possible
                    card_index = highest_index

                elif len(trick.cards) == 2:
                    # partner winning but 1 player left after this turn
                    if trick.get_winner() == 0:
                        #TODO: work out if last player is out of suit
                        card_index = lowest_index
                    else:
                        card_index = highest_index

                elif len(trick.cards) == 3:
                    # partner has already won
                    if trick.get_winner() == 1:
                        card_index = lowest_index
                    else:
                        #TODO: lowest winning card
                        card_index = highest_index

                else:
                    raise RuntimeError
        else:
            raise ValueError

        return card_index
