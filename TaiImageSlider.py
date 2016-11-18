import pygame
from pygame.locals import *
import TaiTimer

ANIMATION_SLIDING = 0
ANIMATION_FADING = 1
DO_NOTHING = lambda *args: None

class ImageSlider:
	def __init__(self, img0, img1, fps = 60, animationType = ANIMATION_SLIDING):
		self.imgs = (img0, img1)
		self.fps = fps
		self.tick = fps
		self.totTick = fps
		self.timer_id = -1
		self.direction = 1
		self.animationType = animationType
		self.lastDrawTick = self.tick

	def _slider_timer_proc(self):
		if self.tick == self.totTick:
			TaiTimer.KillTimer(self.timer_id)
			self.timer_id = -1
			(event, param) = self.callback
			if type(event) is int:
				pygame.event.post(pygame.event.Event(event, param))
			elif callable(event):
				event(*param)
		else:
			self.tick += 1

	def Slide(self, dura, direction = 1, event = DO_NOTHING, param = None):
		if self.IsSliding():
			self.Stop()
		self.tick = 0
		self.totTick = dura * self.fps // 1000
		self.direction = 1 if direction > 0 else -1
		if type(event) is int and param is None: param = {}
		if callable(event) and param is None: param = ()
		self.callback = (event, param)
		self.timer_id = TaiTimer.CreateTimer(1000//self.fps, self._slider_timer_proc, repeat = True)

	def Stop(self):
		if self.IsSliding():
			TaiTimer.KillTimer(self.timer_id)
			self.timer_id = -1

	def SetImages(self, img0, img1):
		if not self.IsSliding():
			self.imgs = (img0, img1)

	def SetDirection(self, direction):
		# Change direction while sliding. 
		direction = 1 if direction > 0 else -1
		if self.IsSliding() and self.direction != direction:
			self.direction = direction
			self.tick = self.totTick - self.tick
			return True
		else:
			return False

	def IsSliding(self): 
		return self.timer_id >= 0

	def Draw(self, surface, pos):
		if self.animationType == ANIMATION_SLIDING:
			(width, height) = self.imgs[0].get_size()
			w = width * self.tick // self.totTick
			if self.direction == -1: w = width - w
			surface.blit(self.imgs[0], pos, (w, 0, width - w, height))
			surface.blit(self.imgs[1], (pos[0] + width - w, pos[1]), (0, 0, w, height))
			self.lastDrawTick = self.tick
		elif self.animationType == ANIMATION_FADING:
			a = 255 * self.tick // self.totTick
			if self.direction == -1: a = 255 - a
			self.imgs[0].set_alpha(255 - a)
			self.imgs[1].set_alpha(a)
			surface.blit(self.imgs[0], pos)
			surface.blit(self.imgs[1], pos)
			self.lastDrawTick = self.tick

	def NeedRedraw(self):
		return self.lastDrawTick != self.tick
