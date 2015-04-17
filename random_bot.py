import time
import sys
import random
import copy

from base_client import LiacBot

WHITE = 1
BLACK = -1
NONE = 0

# BOT =========================================================================

class RandomBot(LiacBot):
    name = 'Random Bot'

    def __init__(self):
        super(RandomBot, self).__init__()
        self.last_move = None

    def on_move(self, state):
        print('Generating a move...'),
        board = Board(state)

        if state['bad_move']:
            print(state['board'])
            raw_input()

        #moves = board.generate()

        nMoves = self.negamax(1, board)
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


    def negamax(self, depth, board):
        if depth == 0:
            return ([],board.evaluate())

        moves = board.generate()
        if len(moves) == 0:
            return ([],board.evaluate())

        max = -sys.maxint - 1
        myMove = []

        for move in moves:
            score = self.negamax(depth - 1, Board(None, board, move))
            score = (score[0],-score[1])

            if score[1] > max:
                max = score[1]
                n_move = [move]
                n_move.append(score[0])
                myMove = n_move
        return (myMove,max)


# =============================================================================

# MODELS ======================================================================

class Board(object):


    # pega todos movimentos possiveis, copia o mapa do tabuleiro. Para cada movimento possivel, faz evaluation simples
    # retorna o movimento com o melhor evaluation
    def evaluate(self):

        count_pieces = {
            Rook: 0,
            Pawn: 0,
            Bishop: 0,
            Queen: 0,
            Knight: 0
        }

        #conta pecas no mapa copiado
        for row in xrange(7, -1, -1):
            for col in xrange(0, 8):
                if self.cells[row][col] is not None:
                    if self.cells[row][col].team == self.my_team:
                        count_pieces[type(self.cells[row][col])] += 1
                    else:
                        count_pieces[type(self.cells[row][col])] -= 1

        #funcao de avaliacao. simples
        points = 9 * count_pieces[Queen] + 5 * count_pieces[Rook] + 3 * count_pieces[Bishop] + 3 * count_pieces[Knight] + count_pieces[Pawn]

        #print (points)

        return (points)


    def __init__(self, state, board = None, move = None):
        if board == None:
            self.cells = [[None for j in xrange(8)] for i in xrange(8)]
            self.my_pieces = []
            self.state = state
            self.moves = []

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

                        if team == self.my_team:
                            self.my_pieces.append(piece)

                    i += 1

        else:
            self.cells = copy.deepcopy(board.cells)
            self.my_pieces = []
            self.state = None
            self.moves = []
            self.my_team = -board.my_team


            #make the move in this board

            self.make_move(move)

            #update my cells for later use
            for row in xrange(7, -1, -1):
                for col in xrange(0, 8):
                    if self.cells[row][col] is not None:
                        if self.cells[row][col].team == self.my_team:
                            self.my_pieces.append(self.cells[row][col])

    def make_move(self, move):
        self.moves = []
        self.cells[move[1][0]] [move[1][1]] = self.cells[move[0][0]] [move[0][1]]
        self.cells[move[0][0]] [move[0][1]] = None
        #adjust position variable inside
        self.cells[move[1][0]] [move[1][1]].position = move[1]


    def __getitem__(self, pos):
        if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7:
            return None

        return self.cells[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self._cells[pos[0]][pos[1]] = value

    def is_empty(self, pos):
        return self[pos] is None

    def generate(self):
        #moves = []
        for piece in self.my_pieces:
            ms = piece.generate()
            ms = [(piece.position, m) for m in ms]
            self.moves.extend(ms)

        return self.moves

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
    color = 0
    port = 50200

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = 1
            port = 50200

    bot = RandomBot()
    bot.port = port

    bot.start()






