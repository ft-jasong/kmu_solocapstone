import pang
import pygame

def event_handling(state):
	if state is pang.STAT_IN_GAME:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return pang.STAT_IN_GAME, False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT: # 캐릭터를 왼쪽으로
					player1.to_x -= player1.speed
				elif event.key == pygame.K_RIGHT: # 캐릭터를 오른쪽으로
					player1.to_x += player1.speed
				elif event.key == pygame.K_SPACE: # 무기 발사
					weapon_x_pos = player1.x_pos + (player1.width / 2) - (player1.weapon.width / 2)
					weapon_y_pos = player1.y_pos
					player1.weapon.bullets.append([weapon_x_pos, weapon_y_pos])
		
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
					player1.to_x = 0
	else:
		global player_num
		global start_ticks
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return state, False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_1:
					player_num = 1
					state = pang.STAT_IN_GAME
					start_ticks = pygame.time.get_ticks()
				elif event.key == pygame.K_2:
					player_num = 2
					start_ticks = pygame.time.get_ticks()
					state = pang.STAT_IN_GAME
	return state, True

##############################################################
# 기본 초기화 (반드시 해야 하는 것들)
pygame.init()

# 화면 크기 설정
screen_width = 640 # 가로 크기
screen_height = 480 # 세로 크기
screen = pygame.display.set_mode((screen_width, screen_height))

# 화면 타이틀 설정
pygame.display.set_caption("Copy Pang")

# FPS
clock = pygame.time.Clock()
game_state = pang.STAT_SELECT
player_num = 1

# 배경 만들기
background = pygame.image.load("./images/background.png")
# 스테이지 만들기
stage = pang.Stage("./images/stage.png")

# 캐릭터 만들기
player1 = pang.Character("./images/character.png", screen_width, screen_height, stage.height)
player1.weapon = pang.Weapon("./images/weapon.png")

ball = pang.Ball("./images/balloon", 50, 50)

# Font 정의
game_font = pygame.font.Font(None, 40)
total_time = 100

# 게임 종료 메시지 
# Time Over(시간 초과 실패)
# Mission Complete(성공)
# Game Over (캐릭터 공에 맞음, 실패)
game_result = ""

running = True
while running:
	dt = clock.tick(30) # 30 FPS
	game_state, running = event_handling(game_state)
	if game_state is pang.STAT_SELECT:
		select_msg = "Press player numbers to play[1]: Player 1[2]: Player 2[3]Two Player"
		announce = game_font.render(select_msg, True, (255, 255, 0)) # 노란색
		announce_rect = announce.get_rect(center=(int(screen_width / 2), int(screen_height / 2)))
		screen.blit(announce, announce_rect)
		pygame.display.update()
		continue

	player1.location(screen_width)
	player1.weapon.bullet_move()
	
	# 공 위치 정의
	ball.ball_location(screen_width, screen_height, stage.height)
	# 4. 충돌 처리

	# 캐릭터 rect 정보 업데이트
	player1.rect_update()
	for ball_idx, ball_val in enumerate(ball.balls):
		ball_pos_x = ball_val["pos_x"]
		ball_pos_y = ball_val["pos_y"]
		ball_img_idx = ball_val["img_idx"]

		# 공 rect 정보 업데이트
		ball_rect = ball.img[ball_img_idx].get_rect()
		ball_rect.left = ball_pos_x
		ball_rect.top = ball_pos_y

		# 공과 캐릭터 충돌 체크
		if player1.rect.colliderect(ball_rect):
			running = False
			game_result = "Game Over"
			break

		# 공과 무기들 충돌 처리
		for weapon_idx, weapon_val in enumerate(player1.weapon.bullets):
			weapon_pos_x = weapon_val[0]
			weapon_pos_y = weapon_val[1]

			# 무기 rect 정보 업데이트
			weapon_rect =player1.weapon.img.get_rect()
			weapon_rect.left = weapon_pos_x
			weapon_rect.top = weapon_pos_y

			# 충돌 체크
			if weapon_rect.colliderect(ball_rect):
				player1.weapon.bullet_to_remove = weapon_idx # 해당 무기 없애기 위한 값 설정
				ball.ball_to_remove = ball_idx # 해당 공 없애기 위한 값 설정

				# 가장 작은 크기의 공이 아니라면 다음 단계의 공으로 나눠주기
				if ball_img_idx < 3:
					# 현재 공 크기 정보를 가지고 옴
					ball_width = ball_rect.size[0]
					ball_height = ball_rect.size[1]

					# 나눠진 공 정보
					small_ball_rect = ball.img[ball_img_idx + 1].get_rect()
					small_ball_width = small_ball_rect.size[0]
					small_ball_height = small_ball_rect.size[1]

					# 왼쪽으로 튕겨나가는 작은 공
					ball.balls.append({
						"pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2), # 공의 x 좌표
						"pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2), # 공의 y 좌표
						"img_idx" : ball_img_idx + 1, # 공의 이미지 인덱스
						"to_x": -3, # x축 이동방향, -3 이면 왼쪽으로, 3 이면 오른쪽으로
						"to_y": -6, # y축 이동방향,
						"init_spd_y": ball.speed_y[ball_img_idx + 1]})# y 최초 속도

					# 오른쪽으로 튕겨나가는 작은 공
					ball.balls.append({
						"pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2), # 공의 x 좌표
						"pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2), # 공의 y 좌표
						"img_idx" : ball_img_idx + 1, # 공의 이미지 인덱스
						"to_x": 3, # x축 이동방향, -3 이면 왼쪽으로, 3 이면 오른쪽으로
						"to_y": -6, # y축 이동방향,
						"init_spd_y": ball.speed_y[ball_img_idx + 1]})# y 최초 속도

				break
		else: # 계속 게임을 진행
			continue # 안쪽 for 문 조건이 맞지 않으면 continue. 바깥 for 문 계속 수행
		break # 안쪽 for 문에서 break 를 만나면 여기로 진입 가능. 2중 for 문을 한번에 탈출
	# 충돌된 공 or 무기 없애기
	ball.delete_ball()
	player1.weapon.delete_bullet()

	# 모든 공을 없앤 경우 게임 종료 (성공)
	if len(ball.balls) == 0:
		game_result = "Mission Complete"
		running = False

	# 5. 화면에 그리기
	screen.blit(background, (0, 0))
	
	for weapon_x_pos, weapon_y_pos in player1.weapon.bullets:
		screen.blit(player1.weapon.img, (weapon_x_pos, weapon_y_pos))

	for idx, val in enumerate(ball.balls):
		ball_pos_x = val["pos_x"]
		ball_pos_y = val["pos_y"]
		ball_img_idx = val["img_idx"]
		screen.blit(ball.img[ball_img_idx], (ball_pos_x, ball_pos_y))

	screen.blit(stage.img, (0, screen_height - stage.height))
	screen.blit(player1.img, (player1.x_pos, player1.y_pos))
	
	# 경과 시간 계산
	elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000 # ms -> s
	timer = game_font.render("Time : {}".format(int(total_time - elapsed_time)), True, (255, 255, 255))
	screen.blit(timer, (10, 10))

	# 시간 초과했다면
	if total_time - elapsed_time <= 0:
		game_result = "Time Over"
		running = False

	pygame.display.update()

# 게임 오버 메시지
msg = game_font.render(game_result, True, (255, 255, 0)) # 노란색
msg_rect = msg.get_rect(center=(int(screen_width / 2), int(screen_height / 2)))
screen.blit(msg, msg_rect)
pygame.display.update()

# 2초 대기
pygame.time.delay(2000)

pygame.quit()
