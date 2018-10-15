## Pokemon 20 questions

## Table of Contents

- [About](#about)
- [Running the game](#running-the-game)
- [Todo](#todo)

## About

This is a simple implementation of the classic 20 questions game.
For those that aren't familiar, the game has two players A and B.
Player A thinks of something--let's call this the target--and 
and Player B gets to ask up to 20 questions to determine the
target. Player A cannot change the target after the first question
is asked and must also answer each question truthfully, usually in
the form of yes or no.

While the classic 20 questions game is played using people, places,
and things, this version just asks about pokemon. You think of the
pokemon and the computer will guess.

## Running the game

Fork a branch and run it using the following commands:

`git checkout -b game`

`git remote add laukevinh https://github.com/laukevinh/poke20q.git`

`git fetch --all`

Make sure you're running Python 3, then

`python main.py`

To try playing from an example, type `saved_game.csv` when prompted
after starting the game. The `saved_game.csv` file contains over 950 
pokemon names but only a handful of questions. This dataset will  
need more game time to improve.

(e.g. bulbasaur is marked Yes as a grass type. However, the saved game
hasn't learend that there are other grass types like ivysaur and 
venesaur. For the game to learn about other grass types, a player will
need to play the game with ivysaur in mind, and when it gives up, 
the player should reveal the answer and add a truthful description
of ivysaur.)

## Todo

- When a player adds a new question or a new answer, suggest 
similar, existing question or answer before adding.
- Add database of existing questions and answers.
- Implement the game online.
- Improve the speed of the guessing algorithm.
