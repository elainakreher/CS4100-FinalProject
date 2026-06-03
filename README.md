# MinesweeperAPI
Minesweeper game with controls exposed through an HTTP API for research purposes. It is written with simplicity and portability in mind and has no external dependencies, it only uses Python 3 and its standard library. A full usage example can be found in my [Minesweeper CSP solver](https://github.com/jgesc/Minesweeper_CSP) repository.

```
python minesweeper --help
usage: minesweeper [-h] [--no-threading] [-p PORT] [-i IP]

Minesweeper HTTP API

optional arguments:
  -h, --help            show this help message and exit
  --no-threading        do not enable multithreading
  -p PORT, --port PORT  port to listen on
  -i IP, --ip IP        host IP to listen on
  ```

# Features
 * Interact through a simple HTTP API
 * No external dependencies
 * First opened cell will never contain a mine and lose the game

# API Documentation
## Create Game
 * **Description:** creates a new game
 * **Method:** PUT
 * **Body JSON Arguments (*optional*):**
   * **width**: width of the generated board *(Default: 10)*
   * **height**: height of the generated board *(Default: 10)*
   * **mine_count**: number of mines, must be greater than total cell count *(Default: 10)*
 * **Returns JSON:**
   * **id**: ID of the created game
 * **Status Codes:**
   * **200**: Success
   * **400**: Request path is not empty
   * **500**: Internal error

## Delete Game
 * **Description:** deletes an existing game
 * **Method:** DELETE
 * **Path arguments:** /*<GAME_ID>*
   * **GAME_ID**: ID of the game to remove
 * **Status Codes:**
   * **200**: Success
   * **404**: Game not found
   * **500**: Internal error

## Play Game
 * **Description:** opens a cell of an existing game. Can only be used on games whose state is neither 'Win' nor 'Lose'
 * **Method:** POST
 * **Path arguments:** /*<GAME_ID>*
   * **GAME_ID**: ID of the game to interact with
 * **Body JSON Arguments:**
   * **x**: X coordinate of the board (width, starting from 0)
   * **y**: Y coordinate of the board (height, starting from 0)
 * **Returns JSON:**
   * **new_state**: New game state. Can be one of the following
     * **First Move**: Player has yet to make their first move
     * **Playing**: The game has already started
     * **Win**: Game has finished, the player has won
     * **Lose**: Game has finished, the player has lost
 * **Status Codes:**
   * **200**: Success
   * **400**: Body JSON is mandatory
   * **404**: Game ID not found
   * **500**: Internal error

## Get Game State
 * **Description:** gets the visible game state, showing only the uncovered cells.
 * **Method:** GET
 * **Path arguments:** /*<GAME_ID>*
   * **GAME_ID**: ID of the game to get the game state of
 * **Returns JSON:**
   * **state**: Current game state. Can be one of the following
     * **First Move**: Player has yet to make their first move
     * **Playing**: The game has already started
     * **Win**: Game has finished, the player has won
     * **Lose**: Game has finished, the player has lost
   * **width**: Width of the board
   * **height**: Height of the board
   * **mine_count**: Number of total mines
   * **board**: 2D list of size (width, height). Each cell can have one of the following values:
     * **-1**: Unknown, the cell has not yet been opened
     * **9**: There was a mine in this cell
     * ***Any other number in [0, 8]***: Number of mines in surrounding cells
 * **Status Codes:**
   * **200**: Success
   * **404**: Game ID not found
   * **500**: Internal error

# Examples
## Intended game workflow
 1. Create game through PUT request, modifying the game settings if desired, obtain the game **ID**
 2. Get game state through GET request. Make a decision and open an unknown cell through POST request on path /**ID**, sending the **x** and **y** coordinates as a JSON formatted body.
 3. Read **new_state** field. If the value is neither **Win** nor **Lose**, repeat step 2.
 4. If **new_state** is either **Win** or **Lose**, delete the game with DELETE request on path /**ID**.

## Examples with `curl`
### Create game
**Command**
```
curl -XPUT -d "{\"mine_count\": 12}" http://localhost:8000/
```
**Response**
```
{"id": "FPHPSDCL"}
```
### Interact with game
**Command**
```
curl -XPOST -d "{\"x\": 9, \"y\": 8}" http://localhost:8080/FPHPSDCL
```
**Response**
```
{"new_state": "Playing"}
```
### Get game state
**Command**
```
curl http://localhost:8080/FPHPSDCL
```
**Response**
```
{"state": "Playing", "width": 10, "height": 10, "mine_count": 12, "board": [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1], [-1, -1, 2, 1, 1, 2, -1, -1, -1, -1], [-1, -1, 1, 0, 0, 1, -1, -1, -1, -1], [-1, 2, 1, 0, 1, 1, -1, -1, -1, -1], [-1, 2, 0, 0, 1, -1, 2, 1, 2, -1], [-1, 2, 0, 0, 1, 1, 1, 0, 1, -1], [1, 2, 1, 1, 0, 0, 0, 0, 1, -1], [0, 1, -1, 1, 0, 0, 0, 0, 1, -1], [0, 1, 1, 1, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]}
```
### Delete game
**Command**
```
curl -XDELETE http://localhost:8080/FPHPSDCL/
```
**Response**
```

```
