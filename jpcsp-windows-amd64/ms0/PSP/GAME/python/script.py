import psp2d# from './psp2d.py'
font = psp2d.Font("font.png")
image = psp2d.Image(480, 272)
screen = psp2d.Screen()
CLEAR_COLOR = psp2d.Color(0,0,0)
image.clear(CLEAR_COLOR)
font.drawText(image, 0, 0, "Hello World")
screen.blit(image)
screen.swap()
