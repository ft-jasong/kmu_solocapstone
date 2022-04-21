import pygame

STAT_SELECT = 1
STAT_IN_GAME = 2

class Stage:
	def __init__(self, filename):
		self.img = pygame.image.load(filename)
		self.size = self.img.get_rect().size
		self.height = self.size[1]

class Weapon:
	def __init__(self, filename):
		self.img = pygame.image.load(filename)
		self.size = self.img.get_rect().size
		self.width = self.size[0]
		self.height = self.size[1]
		self.bullet_speed = 10
		self.bullets = []
		self.bullet_to_remove = -1

	def bullet_move(self):
		self.bullets = [ [b[0], b[1] - self.bullet_speed] for b in self.bullets] # 총알 위로
		self.bullets = [ [b[0], b[1]] for b in self.bullets if b[1] > 0] # 천장 총알 삭제

	def delete_bullet(self):
		if self.bullet_to_remove > -1:
			del self.bullets[self.bullet_to_remove]
			self.bullet_to_remove = -1
			
class Character:
	def __init__(self, filename, screen_width, screen_height, stage_height):
		self.img = pygame.image.load(filename)
		self.rect = self.img.get_rect()
		self.size = self.rect.size
		self.width = self.size[0]
		self.height = self.size[1]
		self.x_pos = (screen_width / 2) - (self.width / 2)
		self.y_pos = screen_height - self.height - stage_height
		self.to_x = 0
		self.speed = 5

	def rect_update(self):
		self.rect.left = self.x_pos
		self.rect.top = self.y_pos

	def location(self, screen_width):
		self.x_pos += self.to_x
		if self.x_pos < 0:
			self.x_pos = 0
		elif self.x_pos > screen_width - self.width:
			self.x_pos = screen_width - self.width

class Ball:
	def __init__(self, filename, pos_x, pox_y):
		self.img = [
			pygame.image.load(filename + '1.png'),
			pygame.image.load(filename + '2.png'),
			pygame.image.load(filename + '3.png'),
			pygame.image.load(filename + '4.png'),
		]
		self.speed_y = [-18, -15, -12, -9]
		self.ball_to_remove = -1
		self.balls = []
		self.balls.append(
			{
				"pos_x" : pos_x,
				"pos_y" : pox_y,
				"img_idx" : 0,
				"to_x" : 3,
				"to_y" : -6,
				"init_spd_y" : self.speed_y[0]
			}
		)

	def ball_location(self, screen_width, screen_height, stage_height):
		for _, ball_val in enumerate(self.balls):
			ball_pos_x = ball_val["pos_x"]
			ball_pos_y = ball_val["pos_y"]
			ball_img_idx = ball_val["img_idx"]

			ball_size = self.img[ball_img_idx].get_rect().size
			ball_width = ball_size[0]
			ball_height = ball_size[1]

			# 가로벽에 닿았을 때 공 이동 위치 변경 (튕겨 나오는 효과)
			if ball_pos_x < 0 or ball_pos_x > screen_width - ball_width:
				ball_val["to_x"] = ball_val["to_x"] * -1

			# 세로 위치
			# 스테이지에 튕겨서 올라가는 처리
			if ball_pos_y >= screen_height - stage_height - ball_height:
				ball_val["to_y"] = ball_val["init_spd_y"]
			else: # 그 외의 모든 경우에는 속도를 증가
				ball_val["to_y"] += 0.5

			ball_val["pos_x"] += ball_val["to_x"]
			ball_val["pos_y"] += ball_val["to_y"]
		
	def delete_ball(self):
		if self.ball_to_remove > -1:
			del self.balls[self.ball_to_remove]
			self.ball_to_remove = -1

class game:
	def __init__(self):
		pygame.init()
		self.window_width = 640
		self.window_height = 480
		self.window = pygame.display.set_mode((self.window_width, self.window_height))
		pygame.display.set_caption("Copy Pang")

		# Set Clock
		self.clock = pygame.time.Clock()
		self.stage = Stage("./images/stage.png")
		self.font = pygame.font.Font(None, 40)
		self.total_time = 100
		# self.start_ticks = pygame.time.get_ticks() # 시작 시간 정의
		# self.game_result = "Game Over"

	def load_bg(self, bg_name):
		self.background = pygame.image.load("./images/" + str(bg_name))
	
	def set_player(self, stage_height, pl_num):
		if pl_num == 1:
			self.player1 = Character("./images/character.png", self.window_width, self.window_height, stage_height)
		if pl_num == 2:
			self.player1 = Character("./images/character.png", self.window_width, self.window_height, stage_height)

	def pang_exit(self):
		pygame.time.delay(2000)
		pygame.quit()