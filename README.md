# Five Hundred Card Game
Five hundred card game engine with basic rule-based AI. Play the game from the command line.  

Engine built for experimentation with Re-inforcement Learning. _No RL implemented yet_

#### AI Components
3 main components of gameplay:  
-__Bid__: bidding round  
-__Discard__: bid winner's kitty discard  
-__Card__: card playing round  


## Usage
The engine plays a whole game by itself and output the results to a file
```
python fivehundred/game.py --savedir savegames
```

Play as Player 1 against 3 computer players
```
python fivehundred/game.py --play 1
```

Show options include AI options
```
python fivehundred/game.py --help
```
