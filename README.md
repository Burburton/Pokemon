# Pokemon
A game that is similar to Minesweeper was designed in the project. A new GUI and users interaction are the highlights of the project. It would give you unique gaming experience.
## Introduction
The rule of game is the same as Minesweeper but the GUI is a new design. The game provides 2 GUI modes (MODE ONE and MODE TWO). MODE ONE shows the game by pure color tiles and number to represent the valid area and mark. MODE TWO combines pokemon images as titles to show the game board. Users can toggle to another MODE during the gaming time. Also, the game has dynamical interaction module for users that the tile would feedback when the cursor falls on it. When all pokemons get caught, users win the game. 
## Operation Guide
| **Action** | **Game Behaviour** | **Display** | 
| :---         | :---        | :---        |
| left click on unexposed tile | expose the tile | text displays the number of surrounding pokemon. If there are no surrounding pokemon, it shows 0 or nothing |
| left click on unexposed tile with hidden pokemon | expose all hidden pokemon and show the user lost | tiles display all the pokemon |
| right click on unexposed tile | toggle status | toggle to attempted catch or original tile based on currrent status |
| left click on exposed tile or attempted catch tile | no behaviour | no change to game view | 
