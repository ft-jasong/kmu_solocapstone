import pygame

class stage:
	def __init__(self, filename):
		self.img = pygame.image.load(filename)
		self.size = self.img.get_rect().size
		self.height = self.size[1]

class weapon:
	def __init__(self, filename):
		self.img = pygame.image.load(filename)
		self.size = self.img.get_rect().size
		self.width = self.size[0]
		self.height = self.size[1]

class character:
	def __init__(self, filename, screen_width, screen_height, stage_height):
		self.img = pygame.image.load(filename)
		self.size = self.img.get_rect().size
		self.width = self.size[0]
		self.height = self.size[1]
		self.x_pos = (screen_width / 2) - (self.width / 2)
		self.y_pos = screen_height - self.height - stage_height
		self.to_x = 0
		self.speed = 5
		self.rect =  self.img.get_rect()
		self.weapon_speed = 10
		self.weapons = []
		self.weapon_to_remove = -1

	def rect_update(self):
		self.rect.left = self.x_pos
		self.rect.top = self.y_pos

class ball:
	def __init__(self, filename):
		self.img = [
			pygame.image.load(filename + '1.png'),
			pygame.image.load(filename + '2.png'),
			pygame.image.load(filename + '3.png'),
			pygame.image.load(filename + '4.png'),
		]
		self.speed_y = [-18, -15, -12, -9]

class round:
	def __init__(self, ball):
		self.balls = []
		self.balls.append(
			{
				"pos_x" : 50,
				"pos_y" : 50,
				"img_idx" : 0,
				"to_x" : 3,
				"to_y" : -6,
				"init_spd_y" : ball.speed_y # 테스트 해볼 에정
			}
		)