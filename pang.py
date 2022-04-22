from pydoc import plain
import pygame

STAT_SELECT = 1
STAT_IN_GAME = 2

def image_at(img, rectangle, colorkey = None):
	"Loads image from x, y, x+offset, y+offset"
	rect = pygame.Rect(rectangle)
	image = pygame.Surface(rect.size).convert()
	image.blit(img, (0, 0), rect)
	if colorkey != None:
		if colorkey == -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, pygame.RLEACCEL)
	return image

class Spritesheet(object):
	def __init__(self, filename):
		try:
			self.sheet = pygame.image.load(filename).convert()
		except pygame.error as message:
			print('Unable to load spritesheet image:', filename)
			raise SystemExit(message)
	# Load a specific image from a specific rectangle
	def image_at(self, rectangle, colorkey = None):
		"Loads image from x, y, x+offset, y+offset"
		rect = pygame.Rect(rectangle)
		image = pygame.Surface(rect.size).convert()
		image.blit(self.sheet, (0, 0), rect)
		if colorkey != None:
			if colorkey == -1:
				colorkey = image.get_at((0,0))
			image.set_colorkey(colorkey, pygame.RLEACCEL)
		return image
	# Load a whole bunch of images and return them as a list
	def images_at(self, rects, colorkey = None):
		"Loads multiple images, supply a list of coordinates"
		return [self.image_at(rect, colorkey) for rect in rects]
	# Load a whole strip of images
	def load_strip(self, rect, image_count, colorkey = None):
		"Loads a strip of images and returns them as a list"
		tups = [(rect[0]+(2+rect[2])*x, rect[1], rect[2], rect[3])
				for x in range(image_count)]
		return self.images_at(tups, colorkey)

class Stage:
	def __init__(self, filename, screen_width):
		self.img = pygame.image.load(filename).convert()
		self.img = pygame.transform.scale(self.img, (screen_width, 18))
		self.size = self.img.get_rect().size
		self.height = self.size[1]

class Weapon:
	def __init__(self, filename):
		self.img = pygame.image.load(filename).convert()
		colorkey = self.img.get_at((0,0))
		self.img.set_colorkey(colorkey, pygame.RLEACCEL)
		self.size = self.img.get_rect().size
		self.width = self.size[0]
		self.height = self.size[1]
		self.bullet_speed = 10
		self.bullets = []
		self.bullet_to_remove = -1

	def image_at(self, rectangle, colorkey = None):
		"Loads image from x, y, x+offset, y+offset"
		rect = pygame.Rect(rectangle)
		image = pygame.Surface(rect.size).convert()
		image.blit(self.img, (0, 0), rect)
		if colorkey != None:
			if colorkey == -1:
				colorkey = image.get_at((0,0))
			image.set_colorkey(colorkey, pygame.RLEACCEL)
		return image

	def bullet_move(self):
		self.bullets = [ [b[0], b[1] - self.bullet_speed] for b in self.bullets] # 총알 위로
		self.bullets = [ [b[0], b[1]] for b in self.bullets if b[1] > 0] # 천장 총알 삭제

	def delete_bullet(self):
		if self.bullet_to_remove > -1:
			del self.bullets[self.bullet_to_remove]
			self.bullet_to_remove = -1

class Character:
	def __init__(self, filename, screen_width, screen_height, stage_height):
		self.ss = Spritesheet(filename)
		self.imgs_right = self.ss.load_strip((0, 0, 32, 32), 5, colorkey=-1)
		self.imgs_left = [pygame.transform.flip(img,True,False) for img in self.imgs_right]
		self.img = self.imgs_right[0]
		self.rect = self.img.get_rect()
		self.size = self.rect.size
		self.width = self.size[0]
		self.height = self.size[1]
		self.x_pos = (screen_width / 2) - (self.width / 2)
		self.y_pos = screen_height - self.height - stage_height
		self.to_x = 0
		self.speed = 5
		self.walk_sprite = 0
		self.walk_dir = 0
		self.shoot = 0
		self.weapon = 0

	def rect_update(self):
		self.rect.left = self.x_pos
		self.rect.top = self.y_pos

	def location(self, screen_width):
		self.x_pos += self.to_x
		if self.x_pos < 0:
			self.x_pos = 0
		elif self.x_pos > screen_width - self.width:
			self.x_pos = screen_width - self.width
	
	def walk_update(self, speed):
		self.walk_sprite += speed
		if self.walk_sprite >= len(self.imgs_left):
			self.walk_sprite = 0
		if self.walk_dir == 1:
			self.img = self.imgs_left[int(self.walk_sprite)]
		elif self.walk_dir == 2:
			self.img = self.imgs_right[int(self.walk_sprite)]
		else:
			self.img = self.shoot

class Ball:
	def __init__(self, filename, pos_x, pox_y):
		self.img = [
			pygame.image.load(filename + '1.png').convert(),
			pygame.image.load(filename + '2.png').convert(),
			pygame.image.load(filename + '3.png').convert(),
			pygame.image.load(filename + '4.png').convert(),
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
		self.rectangle = [
			(0, 0, 50, 42),
			(0, 0, 34, 28),
			(0, 0, 18, 16),
			(0, 0, 11, 11),
		]

	def ball_location(self, screen_width, screen_height, stage_height):
		for _, ball_val in enumerate(self.balls):
			ball_pos_x = ball_val["pos_x"]
			ball_pos_y = ball_val["pos_y"]
			ball_img_idx = ball_val["img_idx"]

			ball_size = self.img[ball_img_idx].get_rect().size
			ball_width = ball_size[0]
			ball_height = ball_size[1]

			# 가로벽에 닿았을 때 공 이동 위치 변경 (튕겨 나오는 효과)
			if ball_pos_x < 18 or ball_pos_x > (screen_width - 18) - ball_width:
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
		pygame.mixer.init()
		self.screen_width = 640
		self.screen_height = 480
		self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
		pygame.display.set_caption("Copy Pang")
		self.background = pygame.image.load("./images/background.png")
		self.background = pygame.transform.scale(self.background, (self.screen_width, self. screen_height))
		# Set Clock
		self.clock = pygame.time.Clock()
		self.state = STAT_SELECT
		self.stage = Stage("./images/stage.png", self.screen_width)
		self.font = pygame.font.Font(None, 40)
		self.total_time = 100
		self.player_num = 1
		self.ball = Ball("./images/balloon", 50, 50)
		for i in range(len(self.ball.img)):
			self.ball.img[i] = image_at(self.ball.img[i], self.ball.rectangle[i], -1)
		self.start_ticks = pygame.time.get_ticks() # 시작 시간 정의
		# self.game_result = "Game Over"
		self.gunshot = pygame.mixer.Sound("./sounds/gunshot.wav")
		self.balloonpop = pygame.mixer.Sound("./sounds/balloonpop.wav")


	def set_player(self, stage_height, pl_num=1):
		self.player1 = Character("./images/player1_walk.png", self.screen_width, self.screen_height, stage_height)
		self.player1.shoot = pygame.image.load("./images/player1.png").convert()
		self.player1.shoot = image_at(self.player1.shoot, (0, 0, 32, 32), -1)
		self.player1.weapon = Weapon("./images/weapon.png")
		self.player1.weapon.img = image_at(self.player1.weapon.img, (0, 0, 9, 193), colorkey=-1)
		if pl_num == 2:
			self.player2 = Character("./images/player2_walk.png", self.screen_width, self.screen_height, stage_height)
			self.player2.shoot = pygame.image.load("./images/player2.png").convert()
			self.player2.shoot = image_at(self.player2.shoot, (0, 0, 32, 32), -1)
			self.player2.weapon = Weapon("./images/weapon.png")
			self.player2.weapon.img = image_at(self.player2.weapon.img, (0, 0, 9, 193), colorkey=-1)
			self.player_num = 2

	def select_screen(self):
		if self.state is STAT_SELECT:
			select_msg = "Press player numbers to play"
			announce = self.font.render(select_msg, True, (255, 255, 0)) # 노란색
			announce_rect = announce.get_rect(center=(int(self.screen_width / 2), int((self.screen_height / 4) * 1)))
			self.screen.blit(announce, announce_rect)
			select_msg = "[1] : One Player"
			announce = self.font.render(select_msg, True, (255, 255, 0)) # 노란색
			announce_rect = announce.get_rect(center=(int(self.screen_width / 2), int((self.screen_height / 8) * 4)))
			self.screen.blit(announce, announce_rect)
			select_msg = "[2] : Two Player"
			announce = self.font.render(select_msg, True, (255, 255, 0)) # 노란색
			announce_rect = announce.get_rect(center=(int(self.screen_width / 2), int((self.screen_height / 8) * 5)))
			self.screen.blit(announce, announce_rect)
			pygame.display.update()

	def colide_event(self):
		self.player1.rect_update()
		for ball_idx, ball_val in enumerate(self.ball.balls):
			ball_pos_x = ball_val["pos_x"]
			ball_pos_y = ball_val["pos_y"]
			ball_img_idx = ball_val["img_idx"]

			# 공 rect 정보 업데이트
			ball_rect = self.ball.img[ball_img_idx].get_rect()
			ball_rect.left = ball_pos_x
			ball_rect.top = ball_pos_y

			# 공과 캐릭터 충돌 체크
			if self.player1.rect.colliderect(ball_rect):
				return "Game Over", False

			# 공과 무기들 충돌 처리
			for weapon_idx, weapon_val in enumerate(self.player1.weapon.bullets):
				weapon_pos_x = weapon_val[0]
				weapon_pos_y = weapon_val[1]

				# 무기 rect 정보 업데이트
				weapon_rect =self.player1.weapon.img.get_rect()
				weapon_rect.left = weapon_pos_x
				weapon_rect.top = weapon_pos_y

				# 충돌 체크
				if weapon_rect.colliderect(ball_rect):
					self.balloonpop.play()
					self.player1.weapon.bullet_to_remove = weapon_idx # 해당 무기 없애기 위한 값 설정
					self.ball.ball_to_remove = ball_idx # 해당 공 없애기 위한 값 설정
					self.ball.delete_ball()
					self.player1.weapon.delete_bullet()

					# 가장 작은 크기의 공이 아니라면 다음 단계의 공으로 나눠주기
					if ball_img_idx < 3:
						# 현재 공 크기 정보를 가지고 옴
						ball_width = ball_rect.size[0]
						ball_height = ball_rect.size[1]

						# 나눠진 공 정보
						small_ball_rect = self.ball.img[ball_img_idx + 1].get_rect()
						small_ball_width = small_ball_rect.size[0]
						small_ball_height = small_ball_rect.size[1]

						# 왼쪽으로 튕겨나가는 작은 공
						self.ball.balls.append({
							"pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2), # 공의 x 좌표
							"pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2), # 공의 y 좌표
							"img_idx" : ball_img_idx + 1, # 공의 이미지 인덱스
							"to_x": -3, # x축 이동방향, -3 이면 왼쪽으로, 3 이면 오른쪽으로
							"to_y": -6, # y축 이동방향,
							"init_spd_y": self.ball.speed_y[ball_img_idx + 1]})# y 최초 속도

						# 오른쪽으로 튕겨나가는 작은 공
						self.ball.balls.append({
							"pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2), # 공의 x 좌표
							"pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2), # 공의 y 좌표
							"img_idx" : ball_img_idx + 1, # 공의 이미지 인덱스
							"to_x": 3, # x축 이동방향, -3 이면 왼쪽으로, 3 이면 오른쪽으로
							"to_y": -6, # y축 이동방향,
							"init_spd_y": self.ball.speed_y[ball_img_idx + 1]})# y 최초 속도

					break
			else: # 계속 게임을 진행
				continue # 안쪽 for 문 조건이 맞지 않으면 continue. 바깥 for 문 계속 수행

		if self.player_num == 2:
			self.player2.rect_update()
			for ball_idx, ball_val in enumerate(self.ball.balls):
				ball_pos_x = ball_val["pos_x"]
				ball_pos_y = ball_val["pos_y"]
				ball_img_idx = ball_val["img_idx"]

				# 공 rect 정보 업데이트
				ball_rect = self.ball.img[ball_img_idx].get_rect()
				ball_rect.left = ball_pos_x
				ball_rect.top = ball_pos_y

				# 공과 캐릭터 충돌 체크
				if self.player2.rect.colliderect(ball_rect):
					return "Game Over", False

				# 공과 무기들 충돌 처리
				for weapon_idx, weapon_val in enumerate(self.player2.weapon.bullets):
					weapon_pos_x = weapon_val[0]
					weapon_pos_y = weapon_val[1]

					# 무기 rect 정보 업데이트
					weapon_rect =self.player2.weapon.img.get_rect()
					weapon_rect.left = weapon_pos_x
					weapon_rect.top = weapon_pos_y

					# 충돌 체크
					if weapon_rect.colliderect(ball_rect):
						self.balloonpop.play()
						self.player2.weapon.bullet_to_remove = weapon_idx # 해당 무기 없애기 위한 값 설정
						self.ball.ball_to_remove = ball_idx # 해당 공 없애기 위한 값 설정
						self.ball.delete_ball()
						self.player2.weapon.delete_bullet()

						# 가장 작은 크기의 공이 아니라면 다음 단계의 공으로 나눠주기
						if ball_img_idx < 3:
							# 현재 공 크기 정보를 가지고 옴
							ball_width = ball_rect.size[0]
							ball_height = ball_rect.size[1]

							# 나눠진 공 정보
							small_ball_rect = self.ball.img[ball_img_idx + 1].get_rect()
							small_ball_width = small_ball_rect.size[0]
							small_ball_height = small_ball_rect.size[1]

							# 왼쪽으로 튕겨나가는 작은 공
							self.ball.balls.append({
								"pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2), # 공의 x 좌표
								"pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2), # 공의 y 좌표
								"img_idx" : ball_img_idx + 1, # 공의 이미지 인덱스
								"to_x": -3, # x축 이동방향, -3 이면 왼쪽으로, 3 이면 오른쪽으로
								"to_y": -6, # y축 이동방향,
								"init_spd_y": self.ball.speed_y[ball_img_idx + 1]})# y 최초 속도

							# 오른쪽으로 튕겨나가는 작은 공
							self.ball.balls.append({
								"pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2), # 공의 x 좌표
								"pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2), # 공의 y 좌표
								"img_idx" : ball_img_idx + 1, # 공의 이미지 인덱스
								"to_x": 3, # x축 이동방향, -3 이면 왼쪽으로, 3 이면 오른쪽으로
								"to_y": -6, # y축 이동방향,
								"init_spd_y": self.ball.speed_y[ball_img_idx + 1]})# y 최초 속도

						break
				else: # 계속 게임을 진행
					continue # 안쪽 for 문 조건이 맞지 않으면 continue. 바깥 for 문 계속 수행
		# 충돌된 공 or 무기 없애기
		return "Game Exit", True

	def draw_screen(self):
		self.screen.blit(self.background, (0, 0))
		for weapon_x_pos, weapon_y_pos in self.player1.weapon.bullets:
			self.screen.blit(self.player1.weapon.img, (weapon_x_pos, weapon_y_pos))
		if self.player_num == 2:
			for weapon_x_pos, weapon_y_pos in self.player2.weapon.bullets:
				self.screen.blit(self.player1.weapon.img, (weapon_x_pos, weapon_y_pos))
		for _, val in enumerate(self.ball.balls):
			ball_pos_x = val["pos_x"]
			ball_pos_y = val["pos_y"] 
			ball_img_idx = val["img_idx"]
			self.screen.blit(self.ball.img[ball_img_idx], (ball_pos_x, ball_pos_y))

		self.screen.blit(self.stage.img, (0, self.screen_height - self.stage.height))
		self.screen.blit(self.player1.img, (self.player1.x_pos, self.player1.y_pos))
		if self.player_num == 2:
			self.screen.blit(self.player2.img, (self.player2.x_pos, self.player2.y_pos))
			
	def playtime(self):
		elapsed_time = (pygame.time.get_ticks() - self.start_ticks) / 1000 # ms -
		timer = self.font.render("Time : {}".format(int(self.total_time - elapsed_time)), True, (255, 255, 255))
		self.screen.blit(timer, (18, 18))
		if self.total_time - elapsed_time <= 0:
			return "Time Over", False
		return "", True