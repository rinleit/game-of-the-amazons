
import imp
import time
#======================================================================


def board_print(board, move=[], num=0):

    print("====== The current board(", num, ")is (after move): ======")
    if move:
        print("move = ", move)
    for i in [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]:
        print(i, ":", end=" ")
        for j in range(10):
            print(board[i][j], end=" ")
        print()
    print("   ", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    print("")


def board_copy(board):
    new_board = [[]]*10
    for i in range(10):
        new_board[i] = [] + board[i]
    return new_board

#======================================================================

def doit(move, state):
    new_state = board_copy(state)
    # example: [(0,3),(5,3),(8,6)]
    if state[move[0][0]][move[0][1]] == 'w':
        new_state[move[1][0]][move[1][1]] = 'w'
    elif state[move[0][0]][move[0][1]] == 'b':
        new_state[move[1][0]][move[1][1]] = 'b'
    new_state[move[0][0]][move[0][1]] = '.'
    new_state[move[2][0]][move[2][1]] = 'X'

    return new_state

#======================================================================
Initial_Board = [
                  ['.', '.', '.', 'w', '.', '.', 'w', '.', '.', '.'], \
                  ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], \
                  ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], \
                  ['w', '.', '.', '.', '.', '.', '.', '.', '.', 'w'], \
                  ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], \
                  ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], \
                  ['b', '.', '.', '.', '.', '.', '.', '.', '.', 'b'], \
                  ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], \
                  ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'], \
                  ['.', '.', '.', 'b', '.', '.', 'b', '.', '.', '.'], \
                ]

# 9 : . . . b . . b . . .
# 8 : . . . . . . . . . .
# 7 : . . . . . . . . . .
# 6 : b . . . . . . . . b
# 5 : . . . . . . . . . .
# 4 : . . . . . . . . . .
# 3 : w . . . . . . . . w
# 2 : . . . . . . . . . .
# 1 : . . . . . . . . . .
# 0 : . . . w . . w . . .
#     0 1 2 3 4 5 6 7 8 9
#======================================================================


def play(student_a, student_b, start_state=Initial_Board):
    player_a = imp.load_source(student_a, student_a + ".py")
    player_b = imp.load_source(student_b, student_b + ".py")

    a = player_a.Player('w')
    b = player_b.Player('b')
    
    curr_player = a
    state = start_state    

    board_num = 0
        
    board_print(state)
    
    while True:
        print("It is ", curr_player, "'s turn")

        start = time.time()
        move = curr_player.nextMove(state)
        elapse = time.time() - start

        # print(move)

        if not move:
            break

        print("The move is : ", move, end=" ")
        print(" (in %.2f ms)" % (elapse*1000), end=" ")
        if elapse > 3.0:
            print(" ** took more than three second!!", end=" ")
            break
        print()
        # check_move
        state = doit(move, state)

        board_num += 1
        board_print(state, num=board_num)

        if curr_player == a:
            curr_player = b
        else:
            curr_player = a

    print("Game Over")
    if curr_player == a:
        print("The Winner is:", student_b, 'black')
    else:
        print("The Winner is:", student_a, 'white')

play("amazons", "amazons")
