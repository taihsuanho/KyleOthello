import pygame
from pygame.locals import *
import os
import glob
import TaiTimer
import TaiImageSlider

COLOR_BLACK = (0, 0, 0)

gBkImgDuration = 4000
gBkImgTimerID = -1
gBkImgSlider = None
gBkImgPrev, gBkImgCurr = None, None	
gBkImgPool = []

def InitBackImageSlider(duration = 4000, fps = 60, animationType = TaiImageSlider.ANIMATION_SLIDING):
	global gBkImgPool
	gBkImgPool = sorted(glob.glob('BKIMG/*.jpg'), key = os.path.getmtime)
	if not gBkImgPool:
		return
	global gBkImgPrev, gBkImgCurr
	gBkImgPrev = pygame.image.load(gBkImgPool[-1]).convert();
	if gBkImgPrev.get_size() != (800, 600):
		gBkImgPrev = pygame.transform.smoothscale(gBkImgPrev, (800, 600))
	gBkImgCurr = pygame.image.load(gBkImgPool[0]).convert(); 
	if gBkImgCurr.get_size() != (800, 600):
		gBkImgCurr = pygame.transform.smoothscale(gBkImgCurr, (800, 600))
	global gBkImgSlider
	gBkImgSlider = TaiImageSlider.ImageSlider(gBkImgPrev, gBkImgCurr, fps = fps, animationType = animationType)
	global gBkImgTimerID, gBkImgDuration
	gBkImgDuration = duration
	# Setup timer for sliding. No need to slide if there are less than two back images.
	if len(gBkImgPool) >= 2:
		gBkImgTimerID = TaiTimer.CreateTimer(gBkImgDuration, _change_backimage, param = (1,))

def DrawBackImageSlider(gameDisplay, pos):
	if gBkImgSlider:
		gBkImgSlider.Draw(gameDisplay, pos)
	else:
		gameDisplay.fill(COLOR_BLACK)

def _prepare_sliding(direction):
	global gBkImgPrev, gBkImgCurr
	if direction > 0:
		gBkImgPool.append(gBkImgPool[0])
		del gBkImgPool[0]
		gBkImgPrev = gBkImgCurr
		gBkImgCurr = pygame.image.load(gBkImgPool[0]).convert(); 
		if gBkImgCurr.get_size() != (800, 600):
			gBkImgCurr = pygame.transform.smoothscale(gBkImgCurr, (800, 600))
	else:
		gBkImgPool.insert(0, gBkImgPool[-1])
		del gBkImgPool[-1]
		gBkImgCurr = gBkImgPrev
		gBkImgPrev = pygame.image.load(gBkImgPool[-1]).convert();
		if gBkImgPrev.get_size() != (800, 600):
			gBkImgPrev = pygame.transform.smoothscale(gBkImgPrev, (800, 600))

def _on_finish_sliding(direction):
	# Setup new timer for sliding in the next time. No need to setup timer if there are less than two back images.
	if len(gBkImgPool) >= 2:
		global gBkImgTimerID
		gBkImgTimerID = TaiTimer.CreateTimer(gBkImgDuration, _change_backimage, param = (direction,))

def _change_backimage(direction):
	if direction > 0:
		_prepare_sliding(direction)
		gBkImgSlider.SetImages(gBkImgPrev, gBkImgCurr)
		gBkImgSlider.Slide(1000, direction = direction, event = _on_finish_sliding, param = (direction,))
	else:
		gBkImgSlider.SetImages(gBkImgPrev, gBkImgCurr)
		gBkImgSlider.Slide(1000, direction = direction, event = _on_finish_sliding, param = (direction,))
		_prepare_sliding(direction)

def BackwardBackImageSliding():
	if not gBkImgSlider:
		return
	TaiTimer.KillTimer(gBkImgTimerID)
	if gBkImgSlider.IsSliding(): 
		if gBkImgSlider.SetDirection(-1):
			_prepare_sliding(-1)
	else: 
		gBkImgSlider.SetImages(gBkImgPrev, gBkImgCurr)
		gBkImgSlider.Slide(1000, direction = -1, event = _on_finish_sliding, param = (1,))
		_prepare_sliding(-1)

def ForwardBackImageSliding():
	if not gBkImgSlider:
		return
	TaiTimer.KillTimer(gBkImgTimerID)
	if gBkImgSlider.IsSliding(): 
		if gBkImgSlider.SetDirection(1):
			_prepare_sliding(1)
	else: 
		_prepare_sliding(1)
		gBkImgSlider.SetImages(gBkImgPrev, gBkImgCurr)
		gBkImgSlider.Slide(1000, direction = 1, event = _on_finish_sliding, param = (1,))

def BackImageNeedRedraw():
	if gBkImgSlider:
		return gBkImgSlider.NeedRedraw()

