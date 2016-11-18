# Tai 2016/10/19: 
# pygame.time.set_timer() cannot pass parameters to the event posted. I therefore implement this timer mechanism 
# to have timer event posted or callback function executed with parameters. CheckTimerIteration() has to be called  
# repeatedly in the game loop before pygame.display.update() is called.

import pygame
from pygame.locals import *

gTimers = {}
gSerialNumber = 256

def CreateTimer(dura, event, param = None, repeat = False):
	# Set a timer to post a message or call a function after the sepecified delay in milliseconds.
	# This function returns the timer ID.
	global gSerialNumber
	if dura < 0:
		return -1
	if not (type(event) is int or callable(event)):
		return -1
	if type(event) is int and param is None: param = {}
	if callable(event) and param is None: param = ()
	timer_id = gSerialNumber
	gSerialNumber += 1
	fire_time = pygame.time.get_ticks() + dura
	gTimers[timer_id] = [fire_time, dura, event, param, repeat]
	return timer_id

def SetTimerParam(timer_id, param):
	if timer_id in gTimers:
		timer = gTimers[timer_id]
		timer[3] = param

def KillTimer(timer_id):
	if timer_id in gTimers:
		del gTimers[timer_id]

def CheckTimerIteration():
	# Call this function  repeatedly in the game loop before pygame.display.update() is called.
	curr_time = pygame.time.get_ticks()
	callbacks = []
	remove_list = []
	# Enumerate the timers and fire those that has been expired.
	for timer_id, timer in gTimers.items():
		[fire_time, dura, event, param, repeat] = timer
		if curr_time >= fire_time:
			if type(event) is int:
				pygame.event.post(pygame.event.Event(event, param))
			elif callable(event):
				callbacks.append((event, param, fire_time))
			if repeat:
				timer[0] = timer[0] + timer[1]
			else:
				remove_list.append(timer_id)
	# Remvoe all the fired one-shot timers from tbhe timer list
	for timer_id in remove_list:
		del gTimers[timer_id]
	# Execute all the collected callback functions in order of fire times that have been expired.
	callbacks.sort(key = lambda callback: callback[2])
	for (event, param, _) in callbacks:
		event(*param)


