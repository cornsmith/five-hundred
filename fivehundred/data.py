# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 16:24:27 2017

@author: ubuntu
"""


import pickle
for rnd in game.rounds:
    print(rnd)
    
rnd = game.rounds[1]
print([str(b) for b in rnd.bids])
rnd.get_dict()
rnd.starting_hands
def get_dict(self):
        round_ = {
            'round': self.number,
            'dealer': self.dealer,
            'bid': str(self.highest_bid),
            'bidder': self.highest_bidder,
            'trump': self.trump_suit,
            't0_tricks': self.tricks_won[0],
            't1_tricks': self.tricks_won[1],
            't0_score': self.scores[0],
            't1_score': self.scores[1],
        }
        
        bids = dict(zip(['bid_' + str(n) for n in range(len(self.bids))], [str(_) for _ in self.bids]))
            #'hands'
            #'tricks'
        return {**bids, **round_}
    
    
    
    with open('data.pickle', 'wb') as f:
    pickle.dump(game, f, pickle.HIGHEST_PROTOCOL)

with open('data.pickle', 'rb') as f:
    game = pickle.load(f)
    
