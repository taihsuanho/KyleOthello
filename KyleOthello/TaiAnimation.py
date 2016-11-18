import pygame
from pygame.locals import *
import TaiTimer

DO_NOTHING = lambda *args: None

class ImageAnimator:
	def __init__(self, img, dura, repeat = False, dimension = None):
		# Argument "img" can be a list of images or an image containing a series of images of equal size changing graduately.
		if type(img) is list:
			self.img_list = img
			self.sprite_number = len(self.img_list)
			self.sprite_size = self.img_list[0].get_size()
		else:
			self.sprite_number = dimension[0] * dimension[1]
			width, height = img.get_size()
			self.sprite_size = w, h = (width // dimension[0], height // dimension[1])
			self.img_list = []
			for i in range(self.sprite_number):
				col, row = i % dimension[0], i // dimension[0]
				self.img_list.append(img.subsurface((col * w, row * h, w, h)))
		self.dura = dura // self.sprite_number
		self.repeat = repeat
		self.index = 0
		self.timer_id = -1
		self.bHideWhenStop = False
		self.lastDrawIndex = self.index

	def get_size(self):
		return self.sprite_size

	def _anim_timer_proc(self):
		if not self.repeat and self.index == self.sprite_number - 1:
			self.Stop()
			(event, param) = self.callback
			if type(event) is int:
				pygame.event.post(pygame.event.Event(event, param))
			elif callable(event):
				event(*param)
		else:
			self.index = (self.index + 1) % self.sprite_number

	def Play(self, event = DO_NOTHING, param = None):
		self.Stop()
		if type(event) is int and param is None: param = {}
		if callable(event) and param is None: param = ()
		self.callback = (event, param)
		self.timer_id = TaiTimer.CreateTimer(self.dura, self._anim_timer_proc, repeat = True)

	def Stop(self):
		if self.IsPlaying():
			TaiTimer.KillTimer(self.timer_id)
			self.timer_id = -1
			self.index = 0
			self.lastDrawIndex = self.index

	def Pause(self):
		if self.IsPlaying():
			TaiTimer.KillTimer(self.timer_id)
			self.timer_id = -1

	def IsPlaying(self):
		return self.timer_id >= 0

	def GetCurrentImage(self):
		return self.img_list[self.index]

	def SetHideWhenStop(self, bHide):
		self.bHideWhenStop = bHide

	def Draw(self, surface, pos):
		if self.bHideWhenStop and not self.IsPlaying():
			return
		surface.blit(self.img_list[self.index], pos)
		self.lastDrawIndex = self.index

	def NeedRedraw(self):
		return self.lastDrawIndex != self.index

