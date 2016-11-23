import _thread
import random
import time
import glob
import pygame
from pygame.locals import *
import TaiTimer
import TaiButton
import TaiAnimation
import TaiImageSlider
import TaiMsgBox
import TaiTalkBox
import KyleSayings
from OthelloLogic import *
from BackImage import *
from ShowLoading import *


# Set up global constants
COLOR_BLACK		= (  0,   0,   0)
COLOR_WHITE		= (255, 255, 255)
COLOR_GRAY 		= (192, 192, 192)
COLOR_LIGHTGRAY = (234, 234, 234)
COLOR_BLUE    	= (  0,   0, 255)
COLOR_DARKBLUE  = (  0,   0, 100)
COLOR_ORANGE  	= (222,  24,   5)
COLOR_WHITE_A 	= (200, 200, 200, 96)

FRAME_PER_SECOND = 60

# User defined events in the pygame loop 
USEREVENT_COMPUTERMOVE = USEREVENT + 1
USEREVENT_USERMOVE = USEREVENT + 2
USEREVENT_NEWGAME = USEREVENT + 3
USEREVENT_RESOURCELOAD = USEREVENT + 4
USEREVENT_MUSIC_END = USEREVENT + 5

# Global list for all mp3 files
gAllMP3 = None

# Global controls: buttons, images, sounds, and labels
gAllBtns = None
gSwitchMusic = None
gBtnLeft, gBtnRight = None, None
gBtnActor, gBtnReset = None, None
gImgActor, gImgActorWin, gImgActorLose = None, None, None
gImgPass, gImgOhYeah, gImgOhNo, gAnimThinks = None, None, None, None
gImgPieceWhite, gImgPieceBlack, gImgPieceWhiteSmall, gImgPieceBlackSmall, gPieceSlider = None, None, None, None, None
gImgArrowDown, gImgWoodFrame = None, None
gSndActorChess, gSndUserChess = None, None
gSndActorWin, gSndActorLose = None, None
gSndActorPass, gSndPlayerPass = None, None
gLabelKyle, gLabelPlayer, gLabelKyleScore, gLabelPlayerScore  = None, None, None, None
gCoverView = None	

# Game level items
gLevelItems = None
gGameTreeSearchLevel = [0, 1, 2, 3]
gLevelIndex = 1      

# Flag to hide the chess board and show the background image
gShowBkImg = False 

def LoadResources(gameDisplay):
	global gAllMP3
	gAllMP3 = glob.glob("BGM/*.mp3")
	random.seed(time.time())
	random.shuffle(gAllMP3)

	global gAllBtns 
	gAllBtns = TaiButton.TaiButtonGroup()

	global gBtnReset
	imgBtnUp  = pygame.image.load("resources/ResetBtnUp.png").convert_alpha()
	imgBtnDn  = pygame.image.load("resources/ResetBtnDn.png").convert_alpha()
	imgBtnDb  = pygame.image.load("resources/ResetBtnDb.png").convert_alpha()
	gBtnReset = gAllBtns.CreateButton(gameDisplay, (660, 20), imgBtnUp, imgBtnDn, imgBtnDb, event = USEREVENT_NEWGAME)

	global gSwitchMusic
	imgMusicON  = pygame.image.load("resources/MusicNote.png").convert_alpha()
	imgMusicOFF  = pygame.image.load("resources/StopMusicNote.png").convert_alpha()
	btnMusicNote = gAllBtns.CreateButton(gameDisplay, (605, 115), imgMusicON, imgMusicON, imgMusicOFF)
	imgSwitchON = pygame.image.load("resources/MusicON.png").convert_alpha()
	imgSwitchOFF = pygame.image.load("resources/MusicOFF.png").convert_alpha()
	gSwitchMusic = gAllBtns.CreateSwitch(gameDisplay, (665, 128), imgSwitchON, imgSwitchOFF, eventON = TurnOnOffMusic, paramON = (True, btnMusicNote), eventOFF = TurnOnOffMusic, paramOFF = (False, btnMusicNote))

	global gBtnLeft, gBtnRight
	imgLeftUp  = pygame.image.load("resources/LeftUp.png").convert_alpha()
	imgLeftDn  = pygame.image.load("resources/LeftDn.png").convert_alpha()
	imgLeftDb  = pygame.image.load("resources/LeftDb.png").convert_alpha()
	imgRightUp = pygame.image.load("resources/RightUp.png").convert_alpha()
	imgRightDn = pygame.image.load("resources/RightDn.png").convert_alpha()
	imgRightDb = pygame.image.load("resources/RightDb.png").convert_alpha()
	gBtnLeft   = gAllBtns.CreateButton(gameDisplay, (605, 200), imgLeftUp, imgLeftDn, imgLeftDb)
	gBtnRight  = gAllBtns.CreateButton(gameDisplay, (735, 200), imgRightUp, imgRightDn, imgRightDb)
	gBtnLeft.SetCallback(ChangeDifficulty, (-1, ))
	gBtnRight.SetCallback(ChangeDifficulty, (1, ))
	
	global gBtnActor, gImgActor, gImgActorWin, gImgActorLose, gImgArrowDown, gImgWoodFrame
	gImgActor = pygame.image.load("resources/KyleThink.png").convert_alpha()
	gBtnActor = gAllBtns.CreateButton(gameDisplay, (610, 380), gImgActor, None, None, OnBtnActorPressed)
	gImgActorWin = pygame.image.load("resources/KyleWin.png").convert_alpha()
	gImgActorLose = pygame.image.load("resources/KyleLose.png").convert_alpha()
	gImgArrowDown = pygame.image.load("resources/ArrowDown.png").convert_alpha()
	gImgWoodFrame = pygame.image.load("resources/WoodFrame.jpg").convert()

	global gImgPass, gImgOhYeah, gImgOhNo
	gImgPass   = pygame.image.load("resources/Pass.png").convert_alpha()
	gImgOhYeah = pygame.image.load("resources/Oh-Yeah.png").convert_alpha()
	gImgOhNo   = pygame.image.load("resources/Oh-No.png").convert_alpha()

	global gAnimThinks
	imgThinks = []
	for file in ('resources/Hmm0.png', 'resources/Hmm1.png', 'resources/Hmm2.png', 'resources/Hmm3.png'):
		imgThinks.append(pygame.image.load(file).convert_alpha())
	gAnimThinks = TaiAnimation.ImageAnimator(imgThinks, 2000, repeat = True)

	global gImgPieceWhite, gImgPieceBlack, gImgPieceWhiteSmall, gImgPieceBlackSmall, gPieceSlider
	gImgPieceWhite = pygame.image.load("resources/PieceWhite.png").convert_alpha()
	gImgPieceBlack = pygame.image.load("resources/PieceBlack.png").convert_alpha()
	gImgPieceWhiteSmall = pygame.transform.scale(gImgPieceWhite, (25, 25))
	gImgPieceBlackSmall = pygame.transform.scale(gImgPieceBlack, (25, 25))
	gPieceSlider = TaiImageSlider.ImageSlider(gImgPieceWhite, gImgPieceBlack, fps = FRAME_PER_SECOND // 2, animationType = TaiImageSlider.ANIMATION_SLIDING)

	global gSndActorChess, gSndUserChess, gSndActorWin, gSndActorLose, gSndActorPass, gSndPlayerPass
	gSndActorChess = pygame.mixer.Sound("resources/ChessSoundKyle.wav")
	gSndUserChess  = pygame.mixer.Sound("resources/ChessSoundUser.wav")
	gSndActorWin   = pygame.mixer.Sound("resources/Oh-Yeah.wav")
	gSndActorLose  = pygame.mixer.Sound("resources/Oh-No.wav")
	gSndActorPass  = pygame.mixer.Sound("resources/KylePass.wav")
	gSndPlayerPass = pygame.mixer.Sound("resources/PlayerPass.wav")

	global gLevelItems
	myfont = pygame.font.SysFont("comicsansms", 25, bold = True)
	gLevelItems = []
	for text in ('Easy', 'Normal', 'Hard', 'Harder'):
		gLevelItems.append(myfont.render(text, True, COLOR_ORANGE))

	global gLabelKyle, gLabelPlayer, gLabelKyleScore, gLabelPlayerScore
	gLabelKyle   = myfont.render("Kyle", True, COLOR_ORANGE)
	gLabelPlayer = myfont.render("Player", True, COLOR_ORANGE)
	gLabelKyleScore   = None
	gLabelPlayerScore = None

	global gCoverView
	gCoverView = pygame.Surface(gameDisplay.get_size(), pygame.SRCALPHA, 32)
	gCoverView.fill(COLOR_WHITE_A)

	InitBackImageSlider(fps = FRAME_PER_SECOND // 2)

	# Post event to game loop to inform that the time-consuming resource loading process has been completed.
	pygame.event.post(pygame.event.Event(USEREVENT_RESOURCELOAD))

def PlayBackgroundMusic():
	while gAllMP3:
		try:
			# Load and play the first mp3 in the list, and then move it to the list tail.
			pygame.mixer.music.load(gAllMP3[0])
			pygame.mixer.music.play()
			gAllMP3.append(gAllMP3[0])
			del gAllMP3[0]
			return True
		except:
			del gAllMP3[0]
	return False

def GetUserInput(pos):
	(x, y) = pos
	if x < 600:
		col, row = x // 75, y // 75
		return row * 8 + col
	else:
		return -1

def DrawCoverView(gameDisplay, coverView):
	if not gShowBkImg:
		gameDisplay.blit(coverView, (0, 0))

def DrawGameBoard(gameDisplay, board, movable_list, flip_list, lastMove, highlightColor):
	# Draw game board border and grid lines with shadow.
	for i in range(0, 8):
		pygame.draw.line(gameDisplay, COLOR_LIGHTGRAY, (i * 75 + 2, 0), (i * 75 + 2, 600), 1)
		pygame.draw.line(gameDisplay, COLOR_LIGHTGRAY, (0, i * 75 + 2), (600, i * 75 + 2), 1)
	for i in range(1, 8):
		pygame.draw.line(gameDisplay, COLOR_BLACK, (i * 75, 0), (i * 75, 600), 2)
		pygame.draw.line(gameDisplay, COLOR_BLACK, (0, i * 75), (600, i * 75), 2)
	pygame.draw.rect(gameDisplay, COLOR_BLACK, (0,0, 600,600), 4)
	# Draw pieces.
	for i in range(64):
		if board[i] != 0:
			col, row = i % 8, i // 8
			x, y = col * 75 + 7, row * 75 + 7
			if i in flip_list:
				gPieceSlider.Draw(gameDisplay, (x, y))
			elif board[i] == 1:
				gameDisplay.blit(gImgPieceBlack, (x, y))
			else:
				gameDisplay.blit(gImgPieceWhite, (x, y))
	# Draw indications of the movable places with small red circle.
	if movable_list:
		for i in movable_list:
			col, row = i % 8, i // 8
			x, y = col * 75 + 37, row * 75 + 38
			pygame.draw.circle(gameDisplay, COLOR_ORANGE, (x, y), 7, 0)
	# Higlight the move that was made by computer or user previously.
	if lastMove or highlightColor:
		col, row = lastMove % 8, lastMove // 8
		if 0 <= col <=7 and 0 <= row <= 7:
			x, y = col * 75 + 4, row * 75 + 4
			pygame.draw.rect(gameDisplay, highlightColor, (x, y, 68, 68), 4)

def DrawScore(gameDisplay, piece_comp, piece_user):
	(p1, p2) = (gImgPieceBlackSmall, gImgPieceWhiteSmall) 
	if piece_comp == -1: (p1, p2) = (p2, p1)
	gameDisplay.blit(p1, (620, 288))
	gameDisplay.blit(p2, (620, 328))
	gameDisplay.blit(gLabelKyle, (660, 280))
	gameDisplay.blit(gLabelPlayer, (660, 320))
	gameDisplay.blit(gLabelKyleScore, (750, 280))
	gameDisplay.blit(gLabelPlayerScore, (750, 320))

def DrawLevelInCenter(gameDisplay, label, rect):
	rect = label.get_rect()
	rect.center = (700, 230)
	gameDisplay.blit(label, rect)

def DrawActorBalloon(gameDisplay, balloon):
	if isinstance(balloon, TaiAnimation.ImageAnimator):
		balloon.Draw(gameDisplay, (720, 360))
	elif balloon:
		gameDisplay.blit(balloon, (720, 360))

def ChangeDifficulty(n):
	# n is either 1 or -1. This function is called when left and right image buttons 
	# are pressed to adjust the game search level.
	global gLevelIndex
	gLevelIndex += n
	if gLevelIndex < 0: 
		gLevelIndex = 0
	if gLevelIndex >= len(gGameTreeSearchLevel): 
		gLevelIndex = len(gGameTreeSearchLevel) - 1
	gBtnLeft.Enable(gLevelIndex > 0)
	gBtnRight.Enable(gLevelIndex < len(gGameTreeSearchLevel) - 1)

def OnEscapeKeyPressed():
	# Toggle to show/hide the chess board.
	global gShowBkImg
	gShowBkImg = not gShowBkImg
	gAllBtns.ShowAll(not gShowBkImg)
	gBtnActor.Show(True)

def OnBtnActorPressed():
	saying = KyleSayings.GetSaying()
	rect = pygame.Rect(150, 450, 500, 100)
	if all(ord(c) < 128 for c in saying):
		font = pygame.font.SysFont('comicsansms', 16, bold = False)
		TaiTalkBox.TalkBox(saying, rect, font = font, bk_image = gImgWoodFrame, next_image = gImgArrowDown, bd_color = COLOR_WHITE, text_color = COLOR_WHITE, duration = 20)
	else:
		TaiTalkBox.TalkBox(saying, rect, bk_image = gImgWoodFrame, next_image = gImgArrowDown, bd_color = COLOR_WHITE, text_color = COLOR_WHITE, duration = 50)

def TurnOnOffMusic(turnON, btnMusicNote):
	if turnON:
		pygame.mixer.music.unpause()
		btnMusicNote.Enable(True)
	else:
		pygame.mixer.music.pause()
		btnMusicNote.Enable(False)

def UpdateScoreLabel(piece_comp, piece_user):
	global gLabelKyleScore, gLabelPlayerScore
	(nC, nU) = GetPieceCount()
	if piece_comp == -1: (nC, nU) = (nU, nC)
	myfont = pygame.font.SysFont("comicsansms", 25, bold = True)
	gLabelKyleScore = myfont.render(str(nC), True, COLOR_ORANGE)
	gLabelPlayerScore = myfont.render(str(nU), True, COLOR_ORANGE)

def _computer_move(piece, nNotifyDelay):
	# Computer thinks for the best move. After that, delay some time before notifying main thread, 
	# so that it doesn't response too fast at lower game search level.
	n = CompCalcMove(piece, gGameTreeSearchLevel[gLevelIndex])
	TaiTimer.CreateTimer(nNotifyDelay, USEREVENT_COMPUTERMOVE, {'bestMove':n})
	TaiTimer.CreateTimer(nNotifyDelay, gBtnReset.Enable, (True,))

def ThreadComputerMove(piece, nNotifyDelay):
	# Do not allow to reset the game until computer-thinking thread is termindated.
	gBtnReset.Enable(False)
	# Use thread for computer thinking, so that the UI will not be blocked at higher game search level.
	_thread.start_new_thread(_computer_move, (piece, nNotifyDelay))

def StartPlayChess():
	# Randomly decide who moves first and initialize the game data.
	piece_comp = 0
	while piece_comp == 0:
		piece_comp = random.randint(-1, 1)
	piece_user = -piece_comp
	InitGameBoard() 
	
	# Set up global vars: the actor btn image and flag for locking user input
	UpdateScoreLabel(piece_comp, piece_user)
	gBtnActor.SetImage(gImgActor)
	
	# Init variables for game states for drawing
	bActorSoundPlayed = False
	piece_winner, movable_list, flip_list = 0, [], []
	actorBalloon, lastMove, highlightColor = None, None, None
	
	# If computer moves first, lock user input and make computer move first.
	if 1 == piece_comp:
		bLockUserInput = True
		ThreadComputerMove(piece_comp, 500)
	else:
		bLockUserInput = False
		movable_list = Mobility(piece_user)
		lastMove, highlightColor = movable_list[0], COLOR_DARKBLUE

	# Initialie bNeedUpdateScreen flag to True, making the screen paint for the first time.
	bNeedUpdateScreen = True
	# The game loop
	gameDisplay = pygame.display.get_surface()
	myClock = pygame.time.Clock()
	while True:
		# Process events: mouse clicking on reset button or the board, making the computer move, or restart a new game
		for event in pygame.event.get():
			if event.type == QUIT:
				return -1
			if event.type == USEREVENT_MUSIC_END:
				PlayBackgroundMusic()
			if event.type == USEREVENT_NEWGAME:
				bNeedUpdateScreen = True
				if piece_winner != 0:
					return
				text = 'This chess tournament is still ongoing. Do you really want to abandon this round?'
				img = pygame.image.load('resources/Othello.png').convert_alpha()
				font = pygame.font.SysFont('comicsansms', 20, bold = False)
				if TaiMsgBox.MessageBox(text, font = font, width = 500, bk_image = gImgWoodFrame, left_image = img, text_ok = '   Yes   ', text_cancel = '   No   ', bd_color = COLOR_LIGHTGRAY, text_color = COLOR_WHITE):
					return
			# Processing mouse events.
			if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
				gAllBtns.ProcessMouseEvent(event)
			# In the play-chess mode, perform one-step back for backspace and swap pieces for key R.
			if event.type == KEYUP and not gShowBkImg and not bLockUserInput:
				if event.key == K_BACKSPACE :
					bNeedUpdateScreen = True
					lastMove = UndoMove(piece_user)
					movable_list = Mobility(piece_user)
					if lastMove < 0:
						lastMove, highlightColor = movable_list[0], COLOR_DARKBLUE
					else:	
						highlightColor = COLOR_ORANGE
					UpdateScoreLabel(piece_comp, piece_user)
					flip_list, actorBalloon, piece_winner, bActorSoundPlayed = [], None, 0, False
					gBtnActor.imgUp = gBtnActor.imgDn = gImgActor
				if event.key == K_r:
					(piece_comp, piece_user) = (piece_user, piece_comp)
					UpdateScoreLabel(piece_comp, piece_user)
					movable_list, actorBalloon = [], None
					bLockUserInput = True
					ThreadComputerMove(piece_comp, 1000)
					gAnimThinks.Play()
					actorBalloon = gAnimThinks				
			# Processing arrow keys and space/enter events in play-chess mode.
			if event.type == KEYDOWN and not gShowBkImg and not bLockUserInput:
				bNeedUpdateScreen = True
				if event.key == K_LEFT and lastMove % 8 != 0:
					lastMove, highlightColor = lastMove - 1, COLOR_DARKBLUE
				if event.key == K_RIGHT and lastMove % 8 != 7:
					lastMove, highlightColor = lastMove + 1, COLOR_DARKBLUE
				if event.key == K_UP and lastMove >= 8:
					lastMove, highlightColor = lastMove - 8, COLOR_DARKBLUE
				if event.key == K_DOWN and lastMove < 56:
					lastMove, highlightColor = lastMove + 8, COLOR_DARKBLUE
				if event.key in (K_SPACE, K_RETURN) and lastMove in movable_list:
					pygame.event.post(pygame.event.Event(USEREVENT_USERMOVE, {'pos': lastMove}))
			# Processing ESC key: send mouse button down and up event to simulate clicking at the actor's button.
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				bNeedUpdateScreen = True
				OnEscapeKeyPressed()
			# Processing left and right key events in show-background-image mode.
			if event.type == KEYDOWN and gShowBkImg:
				if event.key == K_LEFT:
					bNeedUpdateScreen = True
					BackwardBackImageSliding()
				elif event.key == K_RIGHT:
					bNeedUpdateScreen = True
					ForwardBackImageSliding()
			# Processing mouse click on the chess tile if it is user's turn currently.
			if event.type == MOUSEBUTTONDOWN and not bLockUserInput:
				n = GetUserInput(event.pos)
				if n in movable_list:
					pygame.event.post(pygame.event.Event(USEREVENT_USERMOVE, {'pos': n}))
			# Processing for user selected an allowable tile and made a move.
			if event.type == USEREVENT_USERMOVE:
				bNeedUpdateScreen = True
				flip_list = UserMakeMove(piece_user, event.pos)
				gPieceSlider.Slide(200, direction = piece_user)
				gSndUserChess.play()
				UpdateScoreLabel(piece_comp, piece_user)
				movable_list, actorBalloon, lastMove, highlightColor = [], None, event.pos, COLOR_BLUE
				piece_winner = CheckGameOver()
				if piece_winner == 0:
					if len(Mobility(piece_comp)) == 0:
						movable_list = Mobility(piece_user)
						actorBalloon = gImgPass
						TaiTimer.CreateTimer(200, gSndActorPass.play)
					else:
						bLockUserInput = True
						ThreadComputerMove(piece_comp, 1000)
						gAnimThinks.Play()
						actorBalloon = gAnimThinks				
			# Processing after computer figured out the best move.
			if event.type == USEREVENT_COMPUTERMOVE:
				bNeedUpdateScreen = True
				bLockUserInput = False
				lastMove, highlightColor = event.bestMove, COLOR_ORANGE
				flip_list = CompMakeMove(piece_comp, event.bestMove)
				gPieceSlider.Slide(200, direction = piece_comp)
				gSndActorChess.play()
				UpdateScoreLabel(piece_comp, piece_user)
				gAnimThinks.Stop()
				actorBalloon = None
				movable_list = Mobility(piece_user)
				piece_winner = CheckGameOver()
				if piece_winner == 0 and len(movable_list) == 0:
					TaiTimer.CreateTimer(200, gSndPlayerPass.play)
					bLockUserInput = True
					ThreadComputerMove(piece_comp, 2000)
					gAnimThinks.Play()
					actorBalloon = gAnimThinks
		# Processing end of game when piece_winner != 0 and it has not been processed (bActorSoundPlayed not True)
		if piece_winner != 0 and not bActorSoundPlayed:
			bActorSoundPlayed = True
			if piece_winner == piece_comp:
				gSndActorWin.play()
				gBtnActor.SetImage(gImgActorWin)
				actorBalloon = gImgOhYeah
			else:
				gSndActorLose.play()
				gBtnActor.SetImage(gImgActorLose)
				actorBalloon = gImgOhNo
		# Call Tai's timer check iteration function before drawing the display.
		TaiTimer.CheckTimerIteration()
		# Redraw everything and update to the display screen
		bNeedUpdateScreen = bNeedUpdateScreen or BackImageNeedRedraw() or gPieceSlider.NeedRedraw() or gAnimThinks.NeedRedraw() or gAllBtns.NeedRedraw()
		if bNeedUpdateScreen:
			bNeedUpdateScreen = False
			DrawBackImageSlider(gameDisplay, (0, 0))
			if not gShowBkImg:
				DrawCoverView(gameDisplay, gCoverView)
				DrawGameBoard(gameDisplay, GetBoard(), movable_list, flip_list, lastMove, highlightColor)
				DrawLevelInCenter(gameDisplay, gLevelItems[gLevelIndex], Rect(665, 200, 70, 60))
				DrawScore(gameDisplay, piece_comp, piece_user)
			if actorBalloon:
				DrawActorBalloon(gameDisplay, actorBalloon)
			gAllBtns.DrawAll()
			# Update everything to the screen.
			pygame.display.update()
		# Controlling the running speed of this game.
		myClock.tick(FRAME_PER_SECOND)
	# Finish the current round

def main():
	pygame.init()
	icon = pygame.image.load('resources/KyleOthello.ico_32x32.png')
	pygame.display.set_icon(icon)
	gameDisplay = pygame.display.set_mode((800,600))
	pygame.display.set_caption("Play Reversi with Kyle")

	# Use a thread to load the resources, and show loading animation.
	_thread.start_new_thread(LoadResources, (gameDisplay, ))
	ShowLoading(USEREVENT_RESOURCELOAD, min_duration = 1000)

	# If no valid mp3 file is available, toggle the switch and turn off playback.
	pygame.mixer.init()
	pygame.mixer.music.set_endevent(USEREVENT_MUSIC_END)
	if not PlayBackgroundMusic():
		gSwitchMusic.Toggle()
		gSwitchMusic.Enable(False)

	# Start playing the chess.
	while True:
		if StartPlayChess() == -1:
			break
	
	# End playing game after user click QUIT.
	pygame.mixer.stop()
	pygame.mixer.quit()
	pygame.quit()

if __name__ == "__main__":
	main()



