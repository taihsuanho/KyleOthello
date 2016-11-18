import pygame
from pygame.locals import *
import TaiButton

USEREVENT_OK = USEREVENT + 1
USEREVENT_CANCEL = USEREVENT + 2

COLOR_WHITE 	= (255, 255, 255)
COLOR_BLACK		= (  0,   0,   0)
COLOR_LIGHTGRAY	= (234, 234, 234)

TEXT_MARGIN = 16
FRAME_PER_SECOND = 40

def _determine_row(text, font, width):
	# Extract the row of text with max allowed width.
	i, w = 0, 0
	while w < width and i < len(text):
		w += font.size(text[i:i+1])[0]
		i += 1
	# If there is a new line char, return the text before new line as a row.
	j = text.find("\n", 0, i)
	if j >= 0:
		return (text[:j], text[j+1:])
	# If width of text is smaller than the specified width, return the whole text as a row.
	if i >= len(text):
		return (text, '')
	# O/w, try to find the last space char as teh word delimiter.
	j = text.rfind(" ", 0, i)
	if j >= 0:
		return (text[:j], text[j+1:])
	else:
		return (text[:i-1], text[i-1:])

def _draw_text(surface, text, color, font, width):
	# Draw text to the specified surface, automatically wraping words for the given width, 
	# and return the necessary size of the surface.
	x = y = 0
	while text:
		(row, text) = _determine_row(text, font, width)
		if surface:
			image = font.render(row, True, color)
			surface.blit(image, (0, y))
		(w, h) = font.size(row)
		(x, y) = (max(x, w), y + h)
	return (x, y)

def _create_text_image(text, color, font, width):
	# Create and return a text image for the given text and the desired width.
	(w, h) = _draw_text(None, text, color, font, width)
	surface = pygame.Surface((w, h), flags = SRCALPHA)
	_draw_text(surface, text, color, font, width)
	return surface

def _draw_text_image(surface, text_image, bd_color, bk_color, left_image):
	# Draw the text image to the surface, considering the existence of the left image.
	surface.fill(bk_color)
	pygame.draw.rect(surface, bd_color, surface.get_rect(), 1)
	x = y = TEXT_MARGIN
	if left_image:
		x += left_image.get_width() + TEXT_MARGIN
	surface.blit(text_image, (x, y))
	
def _create_buttons(surface, posMsgBox, btns, text_ok, text_cancel, font, bd_color, bk_color, text_color, left_image, right_image):
	# Create buttons and place it in the center bottom of the text part, considering the existence of left and right images.
	if not text_ok:
		return None, None
	wMsg, hMsg = surface.get_size()
	btnOK = btns.CreateTextButton(surface, (0, 0), text_ok, font, bd_color = bd_color, bk_color = bk_color, text_color = text_color, event = USEREVENT_OK)
	btnOK.SetParentPos(posMsgBox)
	wOK, hOK = btnOK.get_size() 
	# Calc. the x-coord of text center cx and y-coord to pleace buttons.
	wl = left_image.get_width() + TEXT_MARGIN if left_image else 0
	wr = right_image.get_width() + TEXT_MARGIN if right_image else 0
	cx = (wMsg - wl - wr) // 2 + wl
	x = cx - wOK // 2
	y = hMsg - hOK - TEXT_MARGIN
	btnOK.SetPos((x, y))
	if not text_cancel:
		btnCancel = None
	else:
		btnCancel = btns.CreateTextButton(surface, (0, 0), text_cancel, font, bd_color = bd_color, bk_color = bk_color, text_color = text_color, event = USEREVENT_CANCEL)
		btnCancel.SetParentPos(posMsgBox)
		btnCancel.SetPos((cx + TEXT_MARGIN // 2, y))
		btnOK.SetPos((cx - wOK - TEXT_MARGIN // 2, y))
	return btnOK, btnCancel

def MessageBox(message, **args):
	# Draw a message box with optional OK and Cancel buttons.
	try: 	font = args['font'] 
	except: font = pygame.font.SysFont("microsoftjhenghei, comicsansms", 20, bold = False)
	try: 	width = args['width']
	except: width = 0
	try: 	left_image = args['left_image']
	except: left_image = None
	try: 	right_image = args['right_image']
	except: right_image = None
	try: 	text_ok = args['text_ok']
	except: text_ok = None
	try: 	text_cancel = args['text_cancel']
	except: text_cancel = None
	try:	bd_color = args['bd_color']
	except:	bd_color = COLOR_WHITE
	try:	bk_color = args['bk_color']
	except:	bk_color = COLOR_BLACK
	try:	text_color = args['text_color']
	except:	text_color = COLOR_LIGHTGRAY
	# Cancel button is ignored if OK button text is not given.
	if not text_ok: text_cancel = None
	# Determine the sizes of the buttons.
	(wOK, hOK) = font.size(text_ok) if text_ok else (0, 0)
	(wCancel, hCancel) = font.size(text_cancel) if text_cancel else (0, 0)
	# Get the width and height, including the added margin, of the left and right images.
	(wl, hl) = (left_image.get_width() + TEXT_MARGIN, left_image.get_height() + 2 * TEXT_MARGIN) if left_image else (0, 0)
	(wr, hr) = (right_image.get_width() + TEXT_MARGIN, right_image.get_height() + 2 * TEXT_MARGIN) if right_image else (0, 0)
	# Determine the width of the text image, a quarter of the screen width if it is not specified.
	displaySurface = pygame.display.get_surface()
	if width <= 0:
		width = displaySurface.get_width() // 4 + wl + wr
	width -= wl + wr + 2 * TEXT_MARGIN
	if width < font.size("W")[0]:
		return
	# Create the text image, and determine the size of the text part, regardless the left and right images.
	imgText = _create_text_image(message, text_color, font, width)
	wMsg, hMsg = imgText.get_size()
	if  wMsg < max(wOK, wCancel) * 2 + TEXT_MARGIN:
		wMsg = max(wOK, wCancel) * 2 + TEXT_MARGIN
	wMsg += 2 * TEXT_MARGIN
	hMsg += 2 * TEXT_MARGIN + max(hOK, hCancel) + (TEXT_MARGIN if text_ok else 0)
	# Create the surface for the message box, considering the optional left and right images.
	wMsg += wl + wr
	hMsg = max(hMsg, hl, hr)
	surface = pygame.Surface((wMsg, hMsg))
	# Draw text image and the left and right images.
	_draw_text_image(surface, imgText, bd_color, bk_color, left_image)	
	if left_image:
		surface.blit(left_image, (TEXT_MARGIN, (hMsg - hl) // 2 + TEXT_MARGIN))
	if right_image:
		surface.blit(right_image, (wMsg - wr, (hMsg - hr) // 2 + TEXT_MARGIN))
	# Calc. the left top position of the message box, putting the message box in center of the display.
	(w0, h0) = displaySurface.get_size()
	posMsg = ((w0 - wMsg) // 2, (h0 - hMsg) // 2)
	rectMsg = pygame.Rect(posMsg, (wMsg, hMsg))
	# Create OK and Cancel buttons, and then get their rect for update display.
	btns = TaiButton.TaiButtonGroup()
	btnOK, btnCancel = _create_buttons(surface, posMsg, btns, text_ok, text_cancel, font, bd_color, bk_color, text_color, left_image, right_image)
	# Game loop for the message box.
	bNeedRedraw = True
	myClock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.event.post(pygame.event.Event(QUIT, {}))
				return
			if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
				btns.ProcessMouseEvent(event)
			if event.type == KEYUP and event.key == K_ESCAPE:
				return
			if event.type in (MOUSEBUTTONUP, KEYUP) and not text_ok and not text_cancel:
				return
			if event.type == USEREVENT_OK:
				return True
			if event.type == USEREVENT_CANCEL:
				return
		# Draw the message box on the screen.
		bNeedRedraw = bNeedRedraw or btns.NeedRedraw()
		if bNeedRedraw:
			bNeedRedraw = False
			if btnOK:
				surface.fill(bk_color, btnOK.get_rect())
			if btnCancel:
				surface.fill(bk_color, btnCancel.get_rect())
			btns.DrawAll()
			displaySurface.blit(surface, posMsg)
			pygame.display.update(rectMsg)
		myClock.tick(FRAME_PER_SECOND)

