I need the app with easily extendable functionality, that allows to play basic card games (cards (fool, 101, black jack, etc.), Uno, monopoly cards, etc), 
and card games authors / right holders will buy/sell/gift permission to add their game. 
Users will also either pay the subscription or buy digital games. 
Like a steam but for tabletop games. Both PC and phone versions will be needed.

App must have the menu with basic buttons: "Play", "Settings", "Exit". 
Buttons however must be in the form of hand of three playing cards. Hovering mouse above them will trigger them reordering, putting the active card (under the cursor) on top of other two.
Tapping "Play" button will trigger card "reshuffling", which then form a hand of several cards, each representing an available game. By stock, classical card games (fool, 101, black jack - 3 games total) and Uno are available. Additional card "Back to menu" is put as the first card in the hand.
Tapping on any of Game named cards triggers reshuffling again to form a game menu. There player can start a game against AI (algorithmic artificial players), "online" game (can be introduced later or made as local game on same wifi), find their game-related achievements, statistics, read the rules (same as in-game, see below) or go back to games menu (first card in the deck for convenience).
Clicking on "Settings" triggers a normal setting menu (with screen size, volume level and some other viable settings).
Exit shuts down the app, saving what was not saved.

Gameplay must be with comfortable graphics, much more realistic (cards must not be ideally white, they must be like shadowed a bit and be seen like they are a bit 3D) than in Windows' solitaire.
Cards should be drawn with animation.
Game description and rules must be shown if the player opens the game for the first time. Instructions should have mini card icons when needed (to show interactions or which card is meant).
Description and rules must be accessible in the in-game menu since then.

Game rules must be coded properly, deck must have the exact number and content of cards as in original game. It should be done algorithmically.
When the losing condition of current game is satisfied, the player who lost gets pretty message about their loss and then can either spectate or click the Exit button to be transferred to that game menu.
When the winning condition is triggered (it can be the condition when all other players lost, or any other game-related condition), winner sees the pretty message that he/she is winner, gets experience report (change in statistics), game report is shown to all the players who spectate or still participated, and then the button "Main menu" appears. 

Please create the code for all the four games (fool, 101, black jack, Uno), algorithmic AI for them, and whole application of what is described above. 

Code practices:
Allowed: Flutter, Python, HTML, CSS, JS, any other which are needed. 
Any type of convenient database: vector database or MongoDB, or SQL-based, etc.

Code in python must be structured according to OOP best practices.
Docstring is must have for all the code parts. Inline comments are prohibited.

Flutter part should have the documentation and comments.

Design must be realistic.