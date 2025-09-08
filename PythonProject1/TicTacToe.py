board=[[1],[2],[3]],
[[4],["X"],[6]],
[[7],[8],[9]]

board1 = [
    "+-------+",
    "|       |",
    "|   1   |",
    "|       |",
    "+-------+"
]

board2 = [
    "+-------+",
    "|       |",
    "|   2   |",
    "|       |",
    "+-------+"
]

board3 = [
    "+-------+",
    "|       |",
    "|   3   |",
    "|       |",
    "+-------+"
]

board4 = [
    "+-------+",
    "|       |",
    "|   4   |",
    "|       |",
    "+-------+"
]

boardx = [
    "+-------+",
    "|       |",
    "|   X   |",
    "|       |",
    "+-------+"
]

board6 = [
    "+-------+",
    "|       |",
    "|   6   |",
    "|       |",
    "+-------+"
]

board7 = [
    "+-------+",
    "|       |",
    "|   7   |",
    "|       |",
    "+-------+"
]

board8 = [
    "+-------+",
    "|       |",
    "|   8   |",
    "|       |",
    "+-------+"
]

board9 = [
    "+-------+",
    "|       |",
    "|   9   |",
    "|       |",
    "+-------+"
]
board=[[[board1],[board2],[board3]],[[board4],[boardx],[board6]],[[board7],[board8],[board9]]]
print(board, sep="\n",end="\n")

def display_board(board):
     for row in board:
        for block in row:
            for line in block[0]:
                print(line)
            print()
        print("\n" + "-"*20)

display_board(board)


# def enter_move(board):
#     # The function accepts the board's current status, asks the user about their move,
#     # checks the input, and updates the board according to the user's decision.


# def make_list_of_free_fields(board):
#     # The function browses the board and builds a list of all the free squares;
#     # the list consists of tuples, while each tuple is a pair of row and column numbers.


# def victory_for(board, sign):
#     # The function analyzes the board's status in order to check if
#     # the player using 'O's or 'X's has won the game


# def draw_move(board):
#     # The function draws the computer's move and updates the board.
