import time
import sys
import random
import copy
import timeit

from base_client import LiacBot

WHITE = 1
BLACK = -1
NONE = 0

MAX = sys.maxint
MIN = -sys.maxint - 1


# BOT =========================================================================



class RandomBot(LiacBot):
    name = 'Random Bot'

    def is_enough_time(self):
        if timeit.default_timer() - self.timer > 5:
            return  False
        return True

    def __init__(self):
        super(RandomBot, self).__init__()
        self.last_move = None

    def on_move(self, state):
        self.timer = timeit.default_timer()

        print('Generating a move...'),
        board = Board(state)

        if state['bad_move']:
            print(state['board'])
            raw_input()

        #moves = board.generate()

        nMoves = self.negamax(3, board, MIN, MAX)
        nMoves = nMoves[0][0]
        #nMoves = board.evaluate(moves)
        self.last_move = nMoves
        print(nMoves)
        self.send_move(nMoves[0], nMoves[1])

        #move = random.choice(moves)
        #self.last_move = move
        #print(move)
        #self.send_move(move[0], move[1])

    def on_game_over(self, state):
        print('Game Over.')
        # sys.exit()




    def negamax(self, depth, board, alpha, beta):
        #print "profundidade[",depth
        if depth == 0 or not self.is_enough_time():
            #print board.my_team
            return ([],board.evaluate())

        moves = board.generate()
        if len(moves) == 0:
            return ([],board.evaluate())

        max = -sys.maxint - 1
        myMove = []

        for move in moves:
            #board.moves = []

            removed_piece = board.make_move(move)
            board.my_team = -board.my_team

            score = self.negamax(depth - 1, board, -beta, -alpha)
            score = (score[0], -score[1])

            board.my_team = -board.my_team
            board.unmake_move(move, removed_piece)

            if score[1] > max:
                max = score[1]
                n_move = [move]
                n_move.append(score[0])
                myMove = n_move

            if max >= beta:
                return (myMove, score[1])

            if max > alpha:
                alpha = max;


        #     if score[1] >= beta:
        #         n_move = [move]
        #         n_move.append(score[0])
        #         myMove = n_move
        #         return (myMove, score[1])
        #     else:
        #         alpha = score[1]
        #         n_move = [move]
        #         n_move.append(score[0])
        #         myMove = n_move
        #
        # return (myMove,alpha)





        return (myMove,max)



# =============================================================================

# MODELS ======================================================================

class Board(object):

    def evaluate(self):

        count_pieces = {
            Rook: 0,
            Pawn: 0,
            Bishop: 0,
            Queen: 0,
            Knight: 0
        }

        my_pawns = 0
        enemy_pawns = 0


        forward_points = 0


        #conta pecas no mapa atual
        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                if self.cells[row][col] is not None:
                    piece = self.cells[row][col];
                    if piece.team == self.my_team:
                        count_pieces[type(piece)] += 1
                        my_pawns +=1
                    else:
                        count_pieces[type(piece)] -= 1
                        enemy_pawns +=1

                    #gives points for forwarding Pawns and huge points when last move
                    if type(piece) == Pawn:
                        position = 0.0
                        if piece.team == BLACK:
                            position = pow((6 -row), 1.1)
                            #if in final row
                            if row == 0:
                                if piece.team == self.my_team:
                                    forward_points +=400
                                else:
                                    forward_points -=400
                        else:
                            position = pow((row - 1), 1.1)
                            #if in final row
                            if row == 7:
                                if piece.team == self.my_team:
                                    forward_points +=400
                                else:
                                    forward_points -=400


                        if piece.team == self.my_team:
                            my_pawns +=1
                        else:
                            enemy_pawns +=1

                        #middle = (4 - abs(col - 4)) * 0.1
                        #forward_points += middle


                        if piece.team == self.my_team:
                            forward_points += position
                        else:
                            forward_points -= position

        if my_pawns == 0:
            forward_points -= 400
        if enemy_pawns == 0:
            forward_points += 400
        # points if last



        #funcao de avaliacao. simples
        points = 9 * count_pieces[Queen] + 5 * count_pieces[Rook] + 3 * count_pieces[Bishop] + 3 * count_pieces[Knight] + count_pieces[Pawn]

        points += forward_points


        return points


    def __init__(self, state):
        self.cells = [[None for j in xrange(8)] for i in xrange(8)]
        #self.my_pieces = []
        self.state = state
        #self.moves = []

        self.my_team = state['who_moves']

        PIECES = {
            'r': Rook,
            'p': Pawn,
            'b': Bishop,
            'q': Queen,
            'n': Knight,
        }


        c = state['board']
        i = 0

        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                if c[i] != '.':
                    cls = PIECES[c[i].lower()]
                    team = BLACK if c[i].lower() == c[i] else WHITE

                    piece = cls(self, team, (row, col))
                    self.cells[row][col] = piece

                    #if team == self.my_team:
                    #    self.my_pieces.append(piece)

                i += 1


    def make_move(self, move):
        removed_piece = None

        #saves the removed piece
        if self.cells[move[1][0]] [move[1][1]] is not None:
            removed_piece = self.cells[move[1][0]] [move[1][1]];

        #self.moves = [] doent clean up board moves

        self.cells[move[1][0]] [move[1][1]] = self.cells[move[0][0]] [move[0][1]]
        self.cells[move[0][0]] [move[0][1]] = None
        #adjust position variable inside
        self.cells[move[1][0]] [move[1][1]].position = move[1]

        return removed_piece

    def unmake_move(self, move, removed_piece):
        #self.moves = []

        self.cells[move[0][0]] [move[0][1]] = self.cells[move[1][0]] [move[1][1]]
        self.cells[move[1][0]] [move[1][1]] = None
        #adjust position variable inside
        self.cells[move[0][0]] [move[0][1]].position = move[0]

        #retrieves the removed piece
        if removed_piece is not None:
            self.cells[move[1][0]] [move[1][1]] = removed_piece



    def __getitem__(self, pos):
        if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7:
            return None

        return self.cells[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self._cells[pos[0]][pos[1]] = value

    def is_empty(self, pos):
        if 0 <= pos[0] <= 7:
            return self[pos] is None
        else:
            return False

    def generate(self):
        moves = []

        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                if self.cells[row][col] is not None:
                    if self.cells[row][col].team == self.my_team:
                        piece = self.cells[row][col]
                        ms = piece.generate()
                        ms = [(piece.position, m) for m in ms]
                        moves.extend(ms)

        return moves

class Piece(object):
    myType = None
    def __init__(self):
        self.board = None
        self.team = None
        self.position = None
        #self.type = None

    def generate(self):
        pass

    def is_opponent(self, piece):
        return piece is not None and piece.team != self.team

class Pawn(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def generate(self):
        moves = []
        my_row, my_col = self.position

        d = self.team

        # Movement to 1 forward
        pos = (my_row + d*1, my_col)
        if self.board.is_empty(pos):
            moves.append(pos)

        # Normal capture to right
        pos = (my_row + d*1, my_col+1)
        piece = self.board[pos]
        if self.is_opponent(piece):
            moves.append(pos)

        # Normal capture to left
        pos = (my_row + d*1, my_col-1)
        piece = self.board[pos]
        if self.is_opponent(piece):
            moves.append(pos)

        return moves

class Rook(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position
        
    def _col(self, dir_):
        my_row, my_col = self.position
        d = -1 if dir_ < 0 else 1
        for col in xrange(1, abs(dir_)):
            yield (my_row, my_col + d*col)

    def _row(self, dir_):
        my_row, my_col = self.position

        d = -1 if dir_ < 0 else 1
        for row in xrange(1, abs(dir_)):
            yield (my_row + d*row, my_col)

    def _gen(self, moves, gen, idx):
        for pos in gen(idx):
            piece = self.board[pos]
            
            if piece is None: 
                moves.append(pos)
                continue
            
            elif piece.team != self.team:
                moves.append(pos)

            break

    def generate(self):
        moves = []

        my_row, my_col = self.position
        self._gen(moves, self._col, 8-my_col) # RIGHT
        self._gen(moves, self._col, -my_col-1) # LEFT
        self._gen(moves, self._row, 8-my_row) # TOP
        self._gen(moves, self._row, -my_row-1) # BOTTOM

        return moves

class Bishop(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _gen(self, moves, row_dir, col_dir):
        my_row, my_col = self.position

        for i in xrange(1, 8):
            row = row_dir*i
            col = col_dir*i
            q_row, q_col = my_row+row, my_col+col

            if not 0 <= q_row <= 7 or not 0 <= q_col <= 7:
                break

            piece = self.board[q_row, q_col]
            if piece is not None:
                if piece.team != self.team:
                    moves.append((q_row, q_col))
                break

            moves.append((q_row, q_col))

    def generate(self):
        moves = []

        self._gen(moves, row_dir=1, col_dir=1) # TOPRIGHT
        self._gen(moves, row_dir=1, col_dir=-1) # TOPLEFT
        self._gen(moves, row_dir=-1, col_dir=-1) # BOTTOMLEFT
        self._gen(moves, row_dir=-1, col_dir=1) # BOTTOMRIGHT

        return moves

class Queen(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _col(self, dir_):
        my_row, my_col = self.position
        
        d = -1 if dir_ < 0 else 1
        for col in xrange(1, abs(dir_)):
            yield (my_row, my_col + d*col)

    def _row(self, dir_):
        my_row, my_col = self.position

        d = -1 if dir_ < 0 else 1
        for row in xrange(1, abs(dir_)):
            yield (my_row + d*row, my_col)

    def _gen_rook(self, moves, gen, idx):
        for pos in gen(idx):
            piece = self.board[pos]
            
            if piece is None: 
                moves.append(pos)
                continue
            
            elif piece.team != self.team:
                moves.append(pos)

            break

    def _gen_bishop(self, moves, row_dir, col_dir):
        my_row, my_col = self.position

        for i in xrange(1, 8):
            row = row_dir*i
            col = col_dir*i
            q_row, q_col = my_row+row, my_col+col

            if not 0 <= q_row <= 7 or not 0 <= q_col <= 7:
                break

            piece = self.board[q_row, q_col]
            if piece is not None:
                if piece.team != self.team:
                    moves.append((q_row, q_col))
                break

            moves.append((q_row, q_col))

    def generate(self):
        moves = []

        my_row, my_col = self.position
        self._gen_rook(moves, self._col, 8-my_col) # RIGHT
        self._gen_rook(moves, self._col, -my_col-1) # LEFT
        self._gen_rook(moves, self._row, 8-my_row) # TOP
        self._gen_rook(moves, self._row, -my_row-1) # BOTTOM
        self._gen_bishop(moves, row_dir=1, col_dir=1) # TOPRIGHT
        self._gen_bishop(moves, row_dir=1, col_dir=-1) # TOPLEFT
        self._gen_bishop(moves, row_dir=-1, col_dir=-1) # BOTTOMLEFT
        self._gen_bishop(moves, row_dir=-1, col_dir=1) # BOTTOMRIGHT

        return moves

class Knight(Piece):
    def __init__(self, board, team, position):
        self.board = board
        self.team = team
        self.position = position

    def _gen(self, moves, row, col):
        if not 0 <= row <= 7 or not 0 <= col <= 7:
            return

        piece = self.board[(row, col)]
        if piece is None or self.is_opponent(piece):
            moves.append((row, col))

    def generate(self):
        moves = []
        my_row, my_col = self.position

        self._gen(moves, my_row+1, my_col+2)
        self._gen(moves, my_row+1, my_col-2)
        self._gen(moves, my_row-1, my_col+2)
        self._gen(moves, my_row-1, my_col-2)
        self._gen(moves, my_row+2, my_col+1)
        self._gen(moves, my_row+2, my_col-1)
        self._gen(moves, my_row-2, my_col+1)
        self._gen(moves, my_row-2, my_col-1)

        return moves
# =============================================================================

if __name__ == '__main__':
    color = WHITE
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = BLACK
            port = 50200

    bot = RandomBot()
    bot.port = port

    bot.start()






