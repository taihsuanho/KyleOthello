import pygame
from pygame.locals import *

COLOR_WHITE 	= (255, 255, 255)
COLOR_BLACK		= (  0,   0,   0)
COLOR_LIGHTGRAY	= (234, 234, 234)

TEXT_MARGIN = 16

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

def _blink_image(image, pos, duration):
	# Keep blinking an image until KEYUP or MOUSEBUTTONUP is received.
	# Argument pos is topleft coord for the blinking image, relative to the game display surface.
	displaySurface = pygame.display.get_surface()
	imgBack = pygame.Surface(image.get_size())
	rect = image.get_rect(topleft = pos)
	imgBack.blit(displaySurface, (0, 0), rect)
	bShow = True
	fps = 1000 / duration
	myClock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.event.post(pygame.event.Event(QUIT, {}))
				return
			if event.type in (MOUSEBUTTONUP, KEYUP):
				if event.type == KEYUP and event.key == K_ESCAPE:
					pygame.event.post(pygame.event.Event(KEYUP, {'key': K_ESCAPE}))
				displaySurface.blit(imgBack, pos)
				pygame.display.update(rect)
				return
		img = image if bShow else imgBack
		displaySurface.blit(img, pos)
		bShow = not bShow
		pygame.display.update(rect)
		myClock.tick(fps)

def _draw_next_indicator(font, pos, duration, color):
	# Keep animating from '.' to '....' until KEYUP or MOUSEBUTTONUP is received.
	# Argument pos is topleft coord for showing animation, relative to the game display surface.
	imgNext = [font.render(text, True, color) for text in ('  ', '.', '. .', '. . .', '. . . .')]
	imgBack = pygame.Surface(imgNext[-1].get_size())
	rect = imgNext[-1].get_rect(topleft = pos)
	displaySurface = pygame.display.get_surface()
	imgBack.blit(displaySurface, (0, 0), rect)
	index = 0
	fps = 1000 / duration
	myClock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.event.post(pygame.event.Event(QUIT, {}))
				return
			if event.type in (MOUSEBUTTONUP, KEYUP):
				if event.type == KEYUP and event.key == K_ESCAPE:
					pygame.event.post(pygame.event.Event(KEYUP, {'key': K_ESCAPE}))
				displaySurface.blit(imgBack, pos)
				pygame.display.update(rect)
				return
		displaySurface.blit(imgBack, pos)
		displaySurface.blit(imgNext[index], pos)
		index = (index + 1) % len(imgNext)
		pygame.display.update(rect)
		myClock.tick(fps)

def _draw_box(surface, bk_image, bk_color, bd_color, left_image, right_image):
	# Draw background image or fill color to the base surface, and draw the border, and left and right images.
	(width, height) = surface.get_size()
	if bk_image:
		surface.blit(bk_image, (0, 0))
	else:
		surface.fill(bk_color)
	if bd_color:
		pygame.draw.rect(surface, bd_color, surface.get_rect(), 1)
	if left_image:
		surface.blit(left_image, (TEXT_MARGIN, (height - left_image.get_height()) // 2))
	if right_image:
		surface.blit(right_image, (width - right_image.get_width() - TEXT_MARGIN, (height - right_image.get_height()) // 2))

def TalkBox(message, rect, **args):
	# Draw a box showing the input message char-by-char. All text is drawn when MOUSEBUTTONUP or KEYUP event is received.
	try: 	font = args['font'] 
	except: font = pygame.font.SysFont("microsoftjhenghei, comicsansms", 20, bold = False)
	try: 	bk_image = args['bk_image']
	except: bk_image = None
	try: 	left_image = args['left_image']
	except: left_image = None
	try: 	right_image = args['right_image']
	except: right_image = None
	try: 	next_image = args['next_image']
	except: next_image = None
	try:	bd_color = args['bd_color']
	except:	bd_color = None
	try:	bk_color = args['bk_color']
	except:	bk_color = COLOR_BLACK
	try:	text_color = args['text_color']
	except:	text_color = COLOR_LIGHTGRAY
	try:	duration = args['duration']
	except:	duration = 25
	# Get the width and height of the left and right images.
	(wl, hl) = (left_image.get_width() + TEXT_MARGIN, left_image.get_height() + 2 * TEXT_MARGIN) if left_image else (0, 0)
	(wr, hr) = (right_image.get_width() + TEXT_MARGIN, right_image.get_height() + 2 * TEXT_MARGIN) if right_image else (0, 0)
	# Determine the text width.
	ht = rect.height - 2 * TEXT_MARGIN
	wt = rect.width - wl - wr - 2 * TEXT_MARGIN
	min_size = font.size("W")
	if wt < min_size[0] or ht < min_size[1]:
		return
	text_rect = pygame.Rect(wl + TEXT_MARGIN, TEXT_MARGIN, wt, ht)
	# Create talk box surface and draw the box.
	surface = pygame.Surface(rect.size)
	_draw_box(surface, bk_image, bk_color, bd_color, left_image, right_image)
	# Start to draw text char-by-char.
	x, y, line_height, row_text, bOneShot = 0, 0, 0, '', False
	fps = 1000 / duration
	myClock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.event.post(pygame.event.Event(QUIT, {}))
				return
			elif event.type == KEYUP and event.key == K_ESCAPE:
				return
			elif event.type in (MOUSEBUTTONUP, KEYUP):
				if not message and not row_text:
					return
				else:
					bOneShot = True
		if message or row_text:
			# If drawing of current row has finished, prepare to draw next row.
			if not row_text:
				row_text, message = _determine_row(message, font, text_rect.width)
				x = 0
				y += line_height
				line_height = font.size(row_text)[1]
				# Check if drawing of the text has reached the bottom.
				if y + line_height > text_rect.height:
					# Show animation to indicate that next page is available.
					if next_image:
						xNext = rect.left + text_rect.left + text_rect.width // 2 - next_image.get_width() // 2
						yNext =  rect.top + rect.height - next_image.get_height() - 2
						_blink_image(next_image, (xNext, yNext), 400)
					else:
						size = font.size('. . . .')
						xNext = rect.left + text_rect.left + text_rect.width // 2 - size[0]
						yNext = rect.top + rect.height - max(TEXT_MARGIN, size[1])
						_draw_next_indicator(font, (xNext, yNext), 200, text_color)
					# Clear the text region and prepare to draw next page.
					_draw_box(surface, bk_image, bk_color, bd_color, left_image, right_image)
					y, bOneShot = 0, False
					continue
			# If there are chars available in the current row, draw them one-by-one or in one shot.
			if row_text:
				if bOneShot:
					img = font.render(row_text, True, text_color)
					row_text = ''
				else:
					img = font.render(row_text[:1], True, text_color)
					row_text = row_text[1:]
				surface.blit(img, (text_rect.left + x, text_rect.top + y))
				x += img.get_width()
				pygame.display.get_surface().blit(surface, rect)
				pygame.display.update(rect)

		myClock.tick(fps)

