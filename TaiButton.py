import pygame
from pygame.locals import *

# Define a do-nothing lambda function
DO_NOTHING = lambda *args: None

# Define colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY 	= (192, 192, 192)
COLOR_LIGHTGRAY	= (234, 234, 234)

class TaiButton:
	def __init__(self, parent, pos, img, imgDn = None, imgDisable = None, event = DO_NOTHING, param = None):
		self.pressed = False
		self.enabled = True
		self.show = True
		self.z = 0
		self.textButton = False
		self.parentPos = (0, 0)
		self.parentSurface = parent
		self.SetPos(pos)
		self.SetImage(img, imgDn, imgDisable)
		self.SetCallback(event, param)

	def _in_region(self, pos):
		(x, y) = pos
		(w, h) = self.imgUp.get_size()
		(x0, y0) = self.absolutePos
		if x0 < x < x0 + w and y0 < y < y0 + h:
			return True

	def get_size(self):
		w, h = self.imgUp.get_size()
		return (w, h)

	def get_rect(self):
		rect = self.imgUp.get_rect()
		rect.topleft = self.pos
		return rect

	def Press(self):
		if self.show and self.enabled:
			self.pressed = True

	def Release(self):
		if self.show and self.enabled:
			self.pressed = False

	def Enable(self, enable = True):
		if enable == self.enabled:
			return
		self.pressed = False
		self.enabled = enable

	def Show(self, show = True):
		if show == self.show:
			return
		self.pressed = False
		self.show = show

	def SetPos(self, pos):
		# self.pos is the coord for drawing the button image to the self.parentSurface.
		# self.absolutePos is the actual coordinate on the screen and for checking if the mouse pos is within the button region.
		(x, y) = self.pos = pos
		self.absolutePos = (self.parentPos[0] + x, self.parentPos[1] + y)

	def SetParentPos(self, pos):
		self.parentPos = pos
		(x, y) = self.pos
		self.absolutePos = (self.parentPos[0] + x, self.parentPos[1] + y)

	def SetImage(self, img, imgDn = None, imgDisable = None):
		self.imgUp = img
		self.imgDn = imgDn if imgDn else self.imgUp
		self.imgDisable = imgDisable if imgDisable else self.imgUp

	def SetCallback(self, event, param = None):
		if type(event) is int:
			if param is None: param = {}
		if callable(event): 
			if param is None: param = ()
		self.callback = (event, param)

	def ProcessMouseMotion(self, event):
		# Check if the mouse has been moved out of the region of the pressed button.
		if self.pressed and not self._in_region(event.pos):
			self.Release()
			return self

	def ProcessMouseButtonDown(self, event):
		# Check if the mouse is pressed in the region of this button.
		if self.show and self.enabled and not self.pressed and self._in_region(event.pos):
			self.Press()
			return self

	def ProcessMouseButtonUp(self, event):
		# Check if pressed button is shown and enabled. If it is, post registered event or run callback function.
		if self.show and self.enabled and self.pressed:
			self.Release()
			(event, param) = self.callback
			if type(event) is int:
				pygame.event.post(pygame.event.Event(event, param))
			elif callable(event):
				event(*param)
			return self

	def ProcessMouseEvent(self, event):
		# Check and process mouse move, button up, and button down events.
		if event.type == MOUSEMOTION:
			return self.ProcessMouseMotion(event)
		elif event.type == MOUSEBUTTONDOWN:
			return self.ProcessMouseButtonDown(event)
		elif event.type == MOUSEBUTTONUP:
			return self.ProcessMouseButtonUp(event)

	def Draw(self):
		# Draw the button considering if it is shown/hidden, pressed/released, and enabled/disabled.
		if not self.show:
			return
		if not self.enabled:
			img = self.imgDisable
		else:
			img = self.imgDn if self.pressed else self.imgUp
		self.parentSurface.blit(img, self.pos)


class TaiSwitch(TaiButton):
	# Subclass TaiButton to impl. TaiSwitch.
	def __init__(self, parent, pos, imgON, imgOFF, eventON = DO_NOTHING, paramON = None, eventOFF = DO_NOTHING, paramOFF = None, initON = True):
		if initON:
			super().__init__(parent, pos, imgON, event = eventON, param = paramON)
		else:
			super().__init__(parent, pos, imgOFF, event = eventOFF, param = paramOFF)
		self.state = initON
		self.imgON = imgON
		self.imgOFF = imgOFF
		self.callbackON = (eventON, paramON)
		self.callbackOFF = (eventOFF, paramOFF)

	def _toggle_state(self):
		# Toggle the switch state, and change its image and callback function accordingly.
		self.state = not self.state
		if self.state:
			self.SetImage(self.imgON)
			self.SetCallback(*self.callbackON)
		else:
			self.SetImage(self.imgOFF)
			self.SetCallback(*self.callbackOFF)

	def Toggle(self):
		# If the button is enabled, toggle the state and run the callback function of the new state.
		if self.enabled:
			self._toggle_state()
			(event, param) = self.callback
			if type(event) is int:
				pygame.event.post(pygame.event.Event(event, param))
			elif callable(event):
				event(*param)
			return self.state

	def ProcessMouseButtonUp(self, event):
		# Subclass mouse button-up handling function by toggling the button after processing the event.
		if self.show and self.enabled and self.pressed:
			self._toggle_state()
			return super().ProcessMouseButtonUp(event)

class TaiButtonGroup:
	def __init__(self):
		self.buttons = []
		self.pressedButton = None
		self.needRedraw = False

	def CreateButton(self, parent, pos, imgUp, imgDn, imgDisable, event = DO_NOTHING, param = None):
		# Create a button and put it in the button list.
		if not (type(event) is int or callable(event)):
			return None
		btn = TaiButton(parent, pos, imgUp, imgDn, imgDisable, event, param)
		self.buttons.append(btn)
		self.needRedraw = True
		return btn

	def CreateTextButton(self, parent, pos, text, font, bd_color = COLOR_WHITE, bk_color = COLOR_BLACK, text_color = COLOR_LIGHTGRAY, shadow = True, event = DO_NOTHING, param = None):
		# Create a text button by rendering the text image and encloing it with a rectangle. Set textButton flag of TaiButton to indicating 
		# it is a text button. Note that all the button states use the same rendered text image.
		if not (type(event) is int or callable(event)):
			return None
		imgText = font.render(text, True, text_color)
		(w, h) = imgText.get_size()
		n = 1 if shadow else 0
		imgBtnUp = pygame.Surface((w + n, h + n))
		imgBtnDn = pygame.Surface((w + n, h + n))
		imgBtnUp.fill(bk_color)
		imgBtnDn.fill(bk_color)
		if shadow:
			pygame.draw.rect(imgBtnUp, COLOR_BLACK, imgBtnUp.get_rect(), 1)
		pygame.draw.rect(imgBtnUp, bd_color, imgText.get_rect(), 1)
		if shadow: 
			pygame.draw.rect(imgBtnDn, COLOR_BLACK, imgBtnDn.get_rect(), 1)
		pygame.draw.rect(imgBtnDn, bd_color, imgText.get_rect(topleft = (n, n)), 1)
		imgBtnUp.blit(imgText, (0, 0))
		imgBtnDn.blit(imgText, (n, n))
		btn = self.CreateButton(parent, pos, imgBtnUp, imgBtnDn, imgBtnUp, event, param)
		btn.textButton = True	
		self.needRedraw = True
		return btn

	def CreateSwitch(self, parent, pos, imgON, imgOFF, eventON = DO_NOTHING, paramON = None, eventOFF = DO_NOTHING, paramOFF = None, initON = True):
		# Create a switch (also a type of button) and add it to the button list.
		if not (type(eventON) is int or callable(eventON)):
			return None
		if not (type(eventOFF) is int or callable(eventOFF)):
			return None
		btn = TaiSwitch(parent, pos, imgON, imgOFF, eventON, paramON, eventOFF, paramOFF, initON)
		self.buttons.append(btn)
		self.needRedraw = True
		return btn

	def DrawAll(self):
		# Draw the buttons in the list in reverse order, since they are sorted by z in decending order.
		# After drawing, reset needRedraw flag.
		for btn in reversed(self.buttons):
			btn.Draw()
		self.needRedraw = False

	def ShowAll(self, show = True):
		# Show or hide all the buttones.
		for btn in self.buttons:
			btn.Show(show)

	def ProcessMouseEvent(self, event):
		# This function can process mouse motion and button up event faster, since there is only one button can be pressed at the same time.
		# If any button is pressed, or the pressed button is released, set needRedraw flag True.
		if event.type == MOUSEMOTION and self.pressedButton:
			if self.pressedButton.ProcessMouseMotion(event):
				self.pressedButton = None
				self.needRedraw = True
		elif event.type == MOUSEBUTTONUP and self.pressedButton:
			if self.pressedButton.ProcessMouseButtonUp(event):
				self.pressedButton = None
				self.needRedraw = True
		# All buttons need to be examined only for mouse button down event.
		elif event.type == MOUSEBUTTONDOWN and not self.pressedButton:
			for btn in self.buttons:
				if btn.ProcessMouseButtonDown(event):
					self.pressedButton = btn
					self.needRedraw = True
					break

	def SetZ(self, btn, z):
		# Modify z order of btn. Buttons of higher z are on top of those of lower z.
		btn.z = z
		self.buttons.sort(key = lambda btn: btn.z, reverse = True)
		self.needRedraw = True

	def NeedRedraw(self):
		return self.needRedraw


