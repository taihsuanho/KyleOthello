import random

# Bitboard shit bits and masks for clear edges.
kBitBoardShiftRight = ((1, 0xfefefefefefefefe), (7, 0x7f7f7f7f7f7f7f00), (8, 0xffffffffffffff00), (9, 0xfefefefefefefe00))	# Shift bits and masks for moving E, SW, S, and SE respectively.
kBitBoardShiftLeft  = ((1, 0x7f7f7f7f7f7f7f7f), (7, 0x00fefefefefefefe), (8, 0x00ffffffffffffff), (9, 0x007f7f7f7f7f7f7f))	# Shift bits and masks for moving W, NE, N, and NW respectively.

# Use uniform scores trying to win as many pieces as possible at the final stage.
FINAL_STATE_ENTRIES = 10
FINAL_PIECE_SCORE  = [1] * 64
NORMAL_PIECE_SCORE = [ 999,-200,  50,  50,  50,  50,-200, 999,
					  -200,-200,  10,  10,  10,  10,-200,-200, 
						50,  10,  10,  10,  10,  10,  10,  50, 
						50,  10,  10,  10,  10,  10,  10,  50, 
						50,  10,  10,  10,  10,  10,  10,  50, 
						50,  10,  10,  10,  10,  10,  10,  50, 
					  -200,-200,  10,  10,  10,  10,-200,-200, 
					   999,-200,  50,  50,  50,  50,-200, 999]

gBoard = None
gBitBoard = None
gEntries = 0
gLastCompMove = None
gBoardHistory = None
gPieceScore = None  

def InitGameBoard(nAddPiece = 0):
	global gBoard, gBitBoard, gEntries, gBoardHistory, gLastCompMove, gPieceScore
	# Allocate and init the game board.
	gBoard = [0] * 64
	gBoard[3 * 8 + 3] =  1
	gBoard[4 * 8 + 4] =  1
	gBoard[3 * 8 + 4] = -1
	gBoard[4 * 8 + 3] = -1
	gEntries = 60
	gLastCompMove = -1
	gBoardHistory = []
	gPieceScore = NORMAL_PIECE_SCORE
	# Randomly put additional pieces on the board (for debug purpose)
	if nAddPiece > 64: 
		nAddPiece = 64
	tiles = [i for i in range(64)]	
	for i in range(nAddPiece):
		n = random.randint(0, len(tiles) - 1)
		t = tiles[n]
		gBoard[t] = 1 if (i % 2) == 1 else -1
		del tiles[n]
	gEntries = 64 - nAddPiece
	gBitBoard = BoardToBitBoard(gBoard)

def GetBoard():
	return gBoard

def BoardToBitBoard(board):
	bb0 = bb1 = 0
	for p in board:
		bb0 <<= 1
		bb1 <<= 1
		if p ==  1: bb0 |= 1
		if p == -1: bb1 |= 1
	return (bb0, bb1)

def BitBoardToBoard(bitboard):
	bb0, bb1 = bitboard
	board = []
	for i in range(64):
		if bb0 & 1: board.append(1)
		elif bb1 & 1: board.append(-1)
		else: board.append(0)
		bb0 >>= 1
		bb1 >>= 1
	return list(reversed(board))

def BitBoardToIndex(bb):
	# Return a list of on-bit indices in 0 ~ 63 from the given 64-bit bitboard bb.
	pos = []
	for i in range(64):
		if bb & 1:
			pos.append(63 - i)
		bb >>= 1
	return pos

def CountOnBits(n):
	n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
	n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
	n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
	n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
	n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
	n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
	return n	

def CheckGameOver():
	(na, nb) = GetPieceCount()
	(ma, mb) = (0, 0) if gEntries == 0 or na == 0 or nb == 0 else (LenMobility(1, gBitBoard), LenMobility(-1, gBitBoard))
	if ma == 0 and mb == 0:
		return 1 if na > nb else -1
	else:
		return 0

def GetPieceCount():
	return (CountOnBits(gBitBoard[0]), CountOnBits(gBitBoard[1]))

def ModifyPieceScoreTable(board, scoreTable):
	# Do not modify score table at final stage, in which computer tries to win as many pieces as possible.
	if gPieceScore is FINAL_PIECE_SCORE:
		return
	# Modify the scores around the 4 corners when the corner is occupied
	scoreTable[1]  = scoreTable[8]  = scoreTable[9]  = 50 if board[0]  != 0 else -200
	scoreTable[6]  = scoreTable[14] = scoreTable[15] = 50 if board[7]  != 0 else -200
	scoreTable[48] = scoreTable[49] = scoreTable[57] = 50 if board[56] != 0 else -200
	scoreTable[55] = scoreTable[54] = scoreTable[62] = 50 if board[63] != 0 else -200

def EvalBoard(board, bitboard, scoreTable, piece, threshold = -10000000):
	score = 0
	for i in range(64):
		score += scoreTable[i] * board[i]
	# Calc the score in point of view of the input piece
	score *= piece 
	# Give penalty proportional to the mobility of the opponent while not in final stage.
	if score > threshold and gPieceScore is not FINAL_PIECE_SCORE:
		oppoMobility = LenMobility(-piece, bitboard)
		score -= oppoMobility * 50
	return score

def MovePiece(bitboard, piece, n):
	# Assign bitboard for owner and opponent.
	if piece == 1: 
		bbOwn, bbOpp = bitboard
	else:
		bbOpp, bbOwn = bitboard
	# Calc all flips after placing piece at tile n.
	flips = 0;
	bb = 1 << (63 - n);
	for (d, mask) in kBitBoardShiftRight:
		flip = 0
		cc = (bb & mask) >> d
		while cc & bbOpp:
			flip |= cc
			cc = (cc & mask) >> d
		if cc & bbOwn:
			flips |= flip
	for (d, mask) in kBitBoardShiftLeft:
		flip = 0
		cc = (bb & mask) << d
		while cc & bbOpp:
			flip |= cc
			cc = (cc & mask) << d
		if cc & bbOwn:
			flips |= flip
	# Flips the pieces and put the piece.
	bbOwn = bbOwn | flips | bb
	bbOpp = bbOpp & ~flips
	# Return the result bitboard.
	return (bbOwn, bbOpp) if piece == 1 else (bbOpp, bbOwn)

def DoMovePiece(piece, n, bitboard = None):
	# This function assume the piece can be put on bitboard[n].
	if not bitboard:
		bitboard = gBitBoard
	bb = MovePiece(bitboard, piece, n)
	board = BitBoardToBoard(bb)
	return (board, bb)

def Movable(piece, bitboard):
	# Assign bitboard for owner and opponent.
	if piece == 1: 
		bbOwn, bbOpp = bitboard
	else:
		bbOpp, bbOwn = bitboard
	# Get the bitboard for empty tiles.
	empty = ~(bbOwn | bbOpp)
	# Calc. allowable moves directing to E, SW, S, SE.
	moves = 0;
	for (d, mask) in kBitBoardShiftRight:
		candidates = bbOpp & ((bbOwn & mask) >> d)
		while candidates:
			moves |= empty & ((candidates & mask) >> d)
			candidates = bbOpp  & ((candidates & mask) >> d)
	# Calc. allowable moves directing to W, NE, N, NW.
	for (d, mask) in kBitBoardShiftLeft:
		candidates = bbOpp & ((bbOwn & mask) << d)
		while candidates:
			moves |= empty & ((candidates & mask) << d)
			candidates = bbOpp  & ((candidates & mask) << d)
	# Return the movable tiles in bitboard.
	return moves

def Mobility(piece, bitboard = None):
	# Find all movable tiles for the input piece, using fast bit-board algorithm implemented in C if the bit-board operation DLL exists.
	if not bitboard:
		bitboard = gBitBoard
	return BitBoardToIndex(Movable(piece, bitboard))

def LenMobility(piece, bitboard):
	bb = Movable(piece, bitboard)
	return CountOnBits(bb)

def CompMoveMax(board, bitboard, scoreTable, piece, nEntries, nLevel, threshold):
	maxScore, sn = -10000000, -1
	moves = Mobility(piece, bitboard)
	for n in moves:
		table_try = list(scoreTable)
		board_try, bitboard_try = DoMovePiece(piece, n, bitboard)
		ModifyPieceScoreTable(board_try, table_try)
		if nEntries == 1 or nLevel == 0:  
			score = EvalBoard(board_try, bitboard_try, table_try, piece, maxScore)
		else:
			score, _ = OppoMoveMin(board_try, bitboard_try, table_try, -piece, nEntries - 1, nLevel, maxScore)
		if maxScore < score:
			maxScore, sn = score, n
		# alpha-beta pruning
		if maxScore > threshold:
			return (maxScore, sn)
	# Computer pass, evaluate the current board or pass it directly to opponent.
	if sn == -1:
		if nEntries == 0 or nLevel == 0:  
			maxScore = EvalBoard(board, bitboard, scoreTable, piece)
		else:
			maxScore, _ = OppoMoveMin(board, bitboard, scoreTable, -piece, nEntries, nLevel, maxScore)

	return (maxScore, sn)

def OppoMoveMin(board, bitboard, scoreTable, piece, nEntries, nLevel, threshold):
	minScore, sn = 10000000, -1
	moves = Mobility(piece, bitboard)
	for n in moves:
		table_try = list(scoreTable)
		board_try, bitboard_try = DoMovePiece(piece, n, bitboard)
		ModifyPieceScoreTable(board_try, table_try)
		score, _ = CompMoveMax(board_try, bitboard_try, table_try, -piece, nEntries - 1, nLevel - 1, minScore)
		if minScore > score:
			minScore, sn = score, n
		# alpha-beta pruning
		if minScore < threshold:
			return (minScore, sn)
	# Opponent pass, evaluate the current board or pass it directly to computer.
	if sn == -1:
		minScore, _ = CompMoveMax(board, bitboard, scoreTable, -piece, nEntries, nLevel - 1, minScore)
	return (minScore, sn)

def PieceChangeInBoard(piece, board1, board2):
	change_list = []
	for i in range(64):
		if board1[i] == -piece and board2[i] == piece:
			change_list.append(i)
	return change_list

def CompCalcMove(piece, nSteps):
	# Calculate and find the best move for computer. At final stage with few empty tiles, search the game tree to end of the game,
	# and maximize the number of pieces won with all piece scores uniformly set to one.
	if gEntries <= FINAL_STATE_ENTRIES:
		global gPieceScore
		gPieceScore = FINAL_PIECE_SCORE
		nSteps = gEntries
	_, n = CompMoveMax(gBoard, gBitBoard, gPieceScore, piece, gEntries, nSteps, 10000000)
	return n

def CompMakeMove(piece, n):
	# Computer actually make the move and update the board.
	global gBoard, gBitBoard, gEntries, gLastCompMove
	if gEntries > 0 and 0 <= n <= 63:
		gBoardHistory.append((gBoard, gBitBoard, piece, gLastCompMove))
		gBoard, gBitBoard = DoMovePiece(piece, n)
		gEntries -= 1
		ModifyPieceScoreTable(gBoard, gPieceScore)
		gLastCompMove = n
		return PieceChangeInBoard(piece, gBoardHistory[-1][0], gBoard)
	else:
		return []

def UserMakeMove(piece, n):
	global gBoard, gBitBoard, gEntries, gBoardHistory
	if gEntries > 0 and 0 <= n <= 63:
		gBoardHistory.append((gBoard, gBitBoard, piece, gLastCompMove))
		gBoard, gBitBoard = DoMovePiece(piece, n)
		gEntries -= 1
		ModifyPieceScoreTable(gBoard, gPieceScore)
		return PieceChangeInBoard(piece, gBoardHistory[-1][0], gBoard)
	else:
		return []

def UndoMove(piece):
	# Restore chess board state to last time before the specified piece was moved.
	global gBoard, gBitBoard, gEntries, gLastCompMove
	n = 0
	for (board, bitboard, p, lastCompMove) in reversed(gBoardHistory):
		n += 1
		if p == piece:
			del gBoardHistory[len(gBoardHistory) - n:]
			gBoard, gBitBoard, gLastCompMove = board, bitboard, lastCompMove
			(na, nb) = GetPieceCount()
			gEntries = 64 - na - nb
			ModifyPieceScoreTable(gBoard, gPieceScore)
			return gLastCompMove
	else:
		return -1

