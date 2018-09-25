## Pokemon 20 questions

## Table of Contents

- [About](#about)
- [Implementation](#implementation)

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

## Todo

- When a player adds a new question or a new answer, suggest 
similar, existing question or answer before adding.
- Add database of existing questions and answers.
- Implement the game online.
- Improve the guessing algorithm.
