import random
import time
import pygame
from pygame.locals import *
import TaiTimer
import TaiMsgBox

# Seed the random number generator with current time.
random.seed(time.time())

FONT_SIZE = 20

COLOR_BLACK		= (  0,   0,   0)
COLOR_WHITE		= (255, 255, 255)
COLOR_LIGHTGRAY = (234, 234, 234)
COLOR_DARKGRAY 	= ( 96,  96,  96)

TIP0 = 'Press ESC key to hide the chess board and get clearer view of background images. Press again to restore the chess board.'
TIP1 = 'Click Kyle to get some wise sayings from him.'
TIP2 = 'While showing the background images, pressing RIGHT and LEFT arrow keys can slide the images forward and backward.'
TIP3 = 'Press BACKSPACE to retract a false move, and \'R\' to swap chess pieces.'
TIP4 = 'Copy your JPG files to folder \"BKIMG\" to show the images behind the chess board.'
TIP5 = 'Copy your MP3 files to folder \"BGM\" to enable playback of background music.'

TIPS = (TIP0, TIP1, TIP2, TIP3, TIP4, TIP5)
IMGS = ('resources/ESC_Land.png', 'resources/KyleThink.png', 'resources/ArrowKeys.png', 'resources/R_BackSpace.png', 'resources/Folder.png', 'resources/Folder.png')

LOADINGS = ('LOADING', 'LOADING.', 'LOADING..', 'LOADING...', 'LOADING....')

def ShowLoading(check_event, color = COLOR_WHITE, min_duration = 0):
	# Show the loading animation in center of the window, until receiving the specified event type.
	font = pygame.font.SysFont("comicsansms", 50, bold = True)
	loading = [font.render(text, True, color) for text in LOADINGS]
	index = 0
	gameDisplay = pygame.display.get_surface()
	rect = loading[-1].get_rect(center = gameDisplay.get_rect().center)
	TaiTimer.CreateTimer(min_duration, USEREVENT)
	timertFired = chkEventOK = False
	myClock = pygame.time.Clock()
	while not timertFired or not chkEventOK:
		for event in pygame.event.get():
			if event.type == QUIT:
				return -1
			if event.type == check_event:
				chkEventOK = True
			if event.type == USEREVENT:
				timertFired = True
		TaiTimer.CheckTimerIteration()
		gameDisplay.fill(COLOR_BLACK, rect)
		gameDisplay.blit(loading[index], rect)
		index = (index + 1) % len(loading)
		pygame.display.update(rect)
		myClock.tick(5)
	# Show the tips on top of the "LOADING..." text.
	n = random.randint(0, len(TIPS) - 1)
	text = 'Tips:\n' + TIPS[n]
	try:
		img = pygame.image.load(IMGS[n]).convert_alpha()
		img = pygame.transform.smoothscale(img, (140, (140 * img.get_height() // img.get_width())))
	except: 
		img = None
	font = pygame.font.SysFont('comicsansms', 20, bold = False)
	TaiMsgBox.MessageBox(text, font = font, width = 600, right_image = img, text_ok = '   OK   ', bk_color = COLOR_DARKGRAY, text_color = COLOR_WHITE)

