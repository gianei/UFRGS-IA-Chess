
import time
import sys
import random
import copy

from base_client import LiacBot

WHITE = 1
BLACK = -1
NONE = 0
MEU = 0
MAX = sys.maxint

# BOT =========================================================================

class RandomBot(LiacBot):
    name = 'Random Bot'

    def __init__(self):
        super(RandomBot, self).__init__()
        self.last_move = None

    def on_move(self, state):
        print "Generating a move...,"
        board = Board(state)
        if state['bad_move']:
            print(state['bad_move'])
            print "bad"
	    print "bad"
	    print "bad"
	    #raw_input()

        #moves = board.generate()

        nMoves = self.negamax(4, board, -MAX, MAX)
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
        sys.exit()


    def negamax(self, depth, board, alpha, beta):
	#print "profundidade[",depth
        if depth == 0:
            return ([],board.evaluate())

        moves = board.generate()
        if len(moves) == 0:
            return ([],board.evaluate())
	#max = -sys.maxint - 1
        myMove = []
        #j = 0
        for move in moves:
            #j = j+1
            #print "jogada", j
            board.moves = []
            #print move
	    posO, posNova, tipoMinha, tipoInimigo, idMinha, idInimigo = board.make_move(move)
            board.my_team = -board.my_team         
	    board.my_pieces, board.enemy_pieces = board.enemy_pieces, board.my_pieces
	
	    score = self.negamax(depth - 1, board, -beta, -alpha)
            score = (score[0],-score[1])
	    
            board.my_team = -board.my_team
            board.my_pieces, board.enemy_pieces = board.enemy_pieces, board.my_pieces
	    board.unmake_move(posO, posNova, tipoMinha, tipoInimigo, idMinha, idInimigo)
	   
	    if score[1] >= beta:
		n_move = [move]
                n_move.append(score[0])
                myMove = n_move		
		return (myMove,score[1])          
	    else:	
     		alpha = score[1]
                n_move = [move]
                n_move.append(score[0])
                myMove = n_move
        return (myMove,alpha)

    def negamax2(self, depth, board):
	#print "profundidade[",depth
        if depth == 0:
            return ([],board.evaluate())

        moves = board.generate()
        if len(moves) == 0:
            return ([],board.evaluate())
	max = -sys.maxint - 1
        myMove = []
        #j = 0
        for move in moves:
            #j = j+1
            #print "jogada", j
	    board.moves = []
	    posO, posNova, tipoMinha, tipoInimigo, idMinha, idInimigo = board.make_move(move)
            board.my_team = -board.my_team         
	    board.my_pieces, board.enemy_pieces = board.enemy_pieces, board.my_pieces
	
	    score = self.negamax(depth - 1, board)
            score = (score[0],-score[1])
	    
            board.my_team = -board.my_team
            board.my_pieces, board.enemy_pieces = board.enemy_pieces, board.my_pieces
	    board.unmake_move(posO, posNova, tipoMinha, tipoInimigo, idMinha, idInimigo)
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
	totalMeu = 0	
	totalOponente = 0	
	i = 0
        j = 0
	if self.my_team == BLACK:
	    for p in self.my_pieces['p']:
	    	totalMeu = totalMeu+7-p.position[0]
		i = i+1
	    for p in self.enemy_pieces['p']:
	    	totalOponente = totalOponente+p.position[0]
		j = j+10
	else:	    
	    for p in self.my_pieces['p']:
		i = i+1
	    	totalMeu = totalMeu+p.position[0]
	    for p in self.enemy_pieces['p']:
	    	totalOponente = totalOponente+7-p.position[0]	
	    	j = j+10
	

        #funcao de avaliacao. simples
        points = 9 * (len(self.my_pieces['q'])-len(self.enemy_pieces['q'])) + 3 * (len(self.my_pieces['n'])-len(self.enemy_pieces['n'])) + 5 * (len(self.my_pieces['r'])-len(self.enemy_pieces['r'])) + (len(self.my_pieces['p'])-len(self.enemy_pieces['p']))

        #print (points)
	#print self.my_team
        return (points)


    def __init__(self, state, board = None, move = None):
        if board == None:
            self.cells = [[None for j in xrange(8)] for i in xrange(8)]
            self.my_pieces = {
                'r': [],
                'p': [],
                'q': [],
                'n': [],
            }

            self.enemy_pieces = {
                'r': [],
                'p': [],
                'q': [],
                'n': [],
            }
            self.state = state
            self.moves = []

            self.my_team = state['who_moves']
	    MEU = state['who_moves']
            PIECES = {
                'r': Rook,
                'p': Pawn,
                'q': Queen,
                'n': Knight,
            }


            c = state['board']
            i = 0
	    #print "INICIAL"
            for row in xrange(7, -1, -1):
                for col in xrange(0, 8):
                    if c[i] != '.':
			identificacao = c[i].lower()
                        cls = PIECES[identificacao]
                        team = BLACK if identificacao == c[i] else WHITE
			
                        piece = cls(self, team, (row, col), row*8+col)
			self.cells[row][col] = piece

                        if team == self.my_team:
                            self.my_pieces[identificacao].append(piece)
			else:
			    self.enemy_pieces[identificacao].append(piece)
            

                    i += 1

    def make_move(self, move):
	#print "MAKE"
	p = self.cells[move[1][0]][move[1][1]]	
	myPiece = self.cells[move[0][0]] [move[0][1]]
	idMinha = myPiece.pk

	clsE= None
	idInimigo = None
	#print self.cells[7][0]
	#print self.cells[7][6]
	#print "POSICAO 00 self.cells[7][6]"
	pName =  type(p).__name__

	if(p is not None):
	    #print "minha pegou",type(myPiece), myPiece.position
	    #print pName	    
	    if(pName == "Pawn"):
		#print "removed ",pName," from ",p.position		
		clsE = Pawn
	        self.enemy_pieces['p'].remove(p)
	    elif(pName == "Rook"):
		#print "removed ",pName," from ",p.position
		self.enemy_pieces['r'].remove(p)
		clsE = Rook
	    elif(pName == "Queen"):	    
		#print "removed ",pName," from ",p.position
		self.enemy_pieces['q'].remove(p)
	    	clsE = Queen
            elif(pName == "Knight"):
		#print "removed ",pName," from ",p.position
		self.enemy_pieces['n'].remove(p)
		clsE = Knight
	    idInimigo = p.pk
	
	try:
	    #index = self.my_pieces['p'].index(myPiece)
    	    #pc = self.my_pieces['p'].pop(index)
	    #print "REMOVIDA ",pc.position,"-", pc.pk," ",type(pc)
	    #print "REMOVIDA ",myPiece.position,"-", myPiece.pk," ",type(myPiece)
	    self.my_pieces['p'].remove(myPiece)
	    #print "remove MYPIECE",type(myPiece).__name__,"FROM p ",myPiece.position
	    myPiece.position = move[1]
	    self.my_pieces['p'].append(myPiece)
	    #print "===and added to ", myPiece.position
	    clsM = Pawn
	except ValueError:		
    	    try:
    	        #index = self.my_pieces['q'].index(myPiece)
    	        #pc = self.my_pieces['q'].pop(index)
	        #print "REMOVIDA ",pc.position,"-", pc.pk," ",type(pc)
	        #print "REMOVIDA ",myPiece.position,"-", myPiece.pk," ",type(myPiece)
	        self.my_pieces['q'].remove(myPiece)
	    	#print "remove MYPIECE",type(myPiece).__name__,"FROM q ",myPiece.position
		myPiece.position = move[1]
		self.my_pieces['q'].append(myPiece)
		#print "===and added to ", myPiece.position
	        clsM = Queen
	    except ValueError:
    	        try:
    	            #index = self.my_pieces['n'].index(myPiece)
    	    	    #pc = self.my_pieces['n'].pop(index)
	    	    #print "REMOVIDA ",pc.position,"-", pc.pk," ",type(pc)
	    	    #print "REMOVIDA ",myPiece.position,"-", myPiece.pk," ",type(myPiece)
	            self.my_pieces['n'].remove(myPiece)
	            #print "remove MYPIECE",type(myPiece).__name__,"FROM n ",myPiece.position	
		    myPiece.position = move[1]
		    self.my_pieces['n'].append(myPiece)
		    #print "===and added to ", myPiece.position
		    clsM = Knight
		except ValueError:
    	       	    try:
    	                #index = self.my_pieces['r'].index(myPiece)
    	    		#pc = self.my_pieces['r'].pop(index)
	    		#print "REMOVIDA ",pc.position,"-", pc.pk," ",type(pc)
	    		#print "REMOVIDA ",myPiece.position,"-", myPiece.pk," ",type(myPiece)
	    		self.my_pieces['r'].remove(myPiece)
	    		#print "remove MYPIECE",type(myPiece).__name__,"FROM r ",myPiece.position
			myPiece.position = move[1]
			self.my_pieces['r'].append(myPiece)
			#print "===and added to ", myPiece.position
			clsM = Rook
		    except ValueError:
			print "ERRORERRORERRORERRORERRORERRORERRORERRORERRORERRORERRORERRORERRORERRORERRORERRORERROR"	
	
	self.cells[move[1][0]] [move[1][1]] = myPiece
	self.cells[move[0][0]] [move[0][1]] = None
	
	#adjust position variable inside
        self.cells[move[1][0]] [move[1][1]].position = move[1]
	
	#if not type(p).__name__==pName:
	#    print "MEGAERRRO"
	#    print type(p).__name__,"!=",pName
	#    print type(myPiece).__name__
	#    return
	#print clsM
	return move[0], move[1], clsM, clsE, idMinha, idInimigo

    def unmake_move(self, posO, posNova, clsM, clsE, idMinha, idInimigo):
	#print "UNMAKE"
	minha = clsM(self, self.my_team, posO, idMinha)	
	mineX = posNova[0]
	mineY = posNova[1]
	#print clsM
	try:
    	    self.my_pieces['p'].remove(minha)
	    #print "devolveu ",type(minha).__name__," da posicao ",self.cells[mineX][mineY].position
	    self.cells[posO[0]][posO[1]] = minha
	    #print "===para a posicao ",minha.position
	    self.my_pieces['p'].append(minha)		
        except ValueError:
    	    try:
    	        self.my_pieces['q'].remove(minha)
	    	#print "devolveu ",type(minha).__name__," da posicao ",self.cells[mineX][mineY].position
	    	self.cells[posO[0]][posO[1]] = minha
	        #print "===para a posicao ",minha.position
		self.my_pieces['q'].append(minha)
	    except ValueError:
    	        try:
    	            self.my_pieces['n'].remove(minha)
	    	    #print "devolveu ",type(minha).__name__," da posicao ",self.cells[mineX][mineY].position
	    	    self.cells[posO[0]][posO[1]] = minha
	            #print "===para a posicao ",minha.position
		    self.my_pieces['n'].append(minha)
		except ValueError:
    	       	    try:
    	                self.my_pieces['r'].remove(minha)
	    		#print "devolveu ",type(minha).__name__," da posicao ",self.cells[mineX][mineY].position
	    		self.cells[posO[0]][posO[1]] = minha
	                #print "===para a posicao ",minha.position
			self.my_pieces['r'].append(minha)
		    except ValueError:
			print "ERRORERRORERRORERRORERRORERROR"		
	    
	self.cells[posO[0]][posO[1]].position = posO            
	self.cells[mineX][mineY] = None
	
	if(idInimigo is not None):
	    inimigo = clsE(self, -self.my_team, posNova, idInimigo)
	    self.cells[mineX][mineY] = inimigo
	    self.cells[mineX][mineY].position = inimigo.position
	    

	    enemyName =  type(inimigo).__name__
	    
	    if(enemyName == "Pawn"):
	        self.enemy_pieces['p'].append(inimigo)
		#print "DEVOLVEU INIMIGO PARA ",inimigo.position  
	    elif(enemyName == "Rook"):
	        self.enemy_pieces['r'].append(inimigo)
		#print "DEVOLVEU INIMIGO PARA ",inimigo.position
	    elif(enemyName == "Queen"):	    
		self.enemy_pieces['q'].append(inimigo)
		#print "DEVOLVEU INIMIGO PARA ",inimigo.position
	    elif(enemyName == "Knight"):
		self.enemy_pieces['n'].append(inimigo)
		#print "DEVOLVEU INIMIGO PARA ",inimigo.position

    def __getitem__(self, pos):
        if not 0 <= pos[0] <= 7 or not 0 <= pos[1] <= 7:
            return None

        return self.cells[pos[0]][pos[1]]

    def __setitem__(self, pos, value):
        self._cells[pos[0]][pos[1]] = value

    def is_empty(self, pos):
        return self[pos] is None

    def generate(self):
        moves = []
        for piece in self.my_pieces['r']:
            ms = piece.generate()
            ms = [(piece.position, m) for m in ms]
            self.moves.extend(ms)
	for piece in self.my_pieces['n']:
            ms = piece.generate()
            ms = [(piece.position, m) for m in ms]
            self.moves.extend(ms)
        for piece in self.my_pieces['q']:
            ms = piece.generate()
            ms = [(piece.position, m) for m in ms]
            self.moves.extend(ms)
	for piece in self.my_pieces['p']:
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
	self.pk = None
        #self.type = None

    def __eq__(self, other):
	if other is None:
	    return False        
	
        if self.pk == other.pk:
            return True
        else:
            return False


    def generate(self):
        pass

    def is_opponent(self, piece):
        return piece is not None and piece.team != self.team

class Pawn(Piece):
    def __init__(self, board, team, position,pk):
        self.board = board
        self.team = team
        self.position = position
	self.pk = pk

    def generate(self):
        moves = []
        my_row, my_col = self.position

        d = self.team

        # Movement to 1 forward
        pos = (my_row + d*1, my_col)
	if 0<=pos[0]<=7:
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
    def __init__(self, board, team, position,pk):
        self.board = board
        self.team = team
        self.position = position
	self.pk = pk
        
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
    def __init__(self, board, team, position, pk):
        self.board = board
        self.team = team
        self.position = position
	self.pk = pk

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
    def __init__(self, board, team, position,pk):
        self.board = board
        self.team = team
        self.position = position
	self.pk = pk

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
    def __init__(self, board, team, position,pk):
        self.board = board
        self.team = team
        self.position = position
	self.pk = pk

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
            port = 50100

    bot = RandomBot()
    bot.port = port

    bot.start()



