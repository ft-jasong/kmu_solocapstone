import pang
import pygame

def event_handling(state):
	if state is pang.STAT_IN_GAME:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return pang.STAT_IN_GAME, False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT: # 캐릭터를 왼쪽으로
					game.player1.to_x -= game.player1.speed
					game.player1.walk_sprite = 0
					game.player1.walk_dir = 1
				elif event.key == pygame.K_RIGHT: # 캐릭터를 오른쪽으로
					game.player1.to_x += game.player1.speed
					game.player1.walk_sprite = 0
					game.player1.walk_dir = 2
				elif event.key == pygame.K_SPACE: # 무기 발사
					weapon_x_pos = game.player1.x_pos + (game.player1.width / 2) - (game.player1.weapon.width / 2)
					weapon_y_pos = game.player1.y_pos
					game.player1.weapon.bullets.append([weapon_x_pos, weapon_y_pos])
					game.gunshot.play()
		
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
					game.player1.to_x = 0
					game.player1.walk_dir = 0
			if game.player_num == 2:
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_a: # 캐릭터를 왼쪽으로
						game.player2.to_x -= game.player2.speed
						game.player2.walk_sprite = 0
						game.player2.walk_dir = 1
					elif event.key == pygame.K_d: # 캐릭터를 오른쪽으로
						game.player2.to_x += game.player2.speed
						game.player2.walk_sprite = 0
						game.player2.walk_dir = 2
					elif event.key == pygame.K_s: # 무기 발사
						weapon_x_pos = game.player2.x_pos + (game.player2.width / 2) - (game.player2.weapon.width / 2)
						weapon_y_pos = game.player2.y_pos
						game.player2.weapon.bullets.append([weapon_x_pos, weapon_y_pos])
						game.gunshot.play()

		
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_a or event.key == pygame.K_d:
						game.player2.to_x = 0
						game.player2.walk_dir = 1

	else:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return state, False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_1:
					game.set_player(game.stage.height, 1)
					state = pang.STAT_IN_GAME
					game.start_ticks = pygame.time.get_ticks()
				elif event.key == pygame.K_2:
					game.set_player(game.stage.height, 2)
					state = pang.STAT_IN_GAME
	return state, True

##############################################################
# 기본 초기화 (반드시 해야 하는 것들)

pygame.init()
game = pang.game()
game_result = "Game Exit"
running = True
while running:
	dt = game.clock.tick(30) # 30 FPS
	game.state, running = event_handling(game.state)
	if game.state is pang.STAT_SELECT:
		game.select_screen()
		continue
	game.player1.location(game.screen_width)
	game.player1.weapon.bullet_move()
	if game.player_num == 2:
		game.player2.location(game.screen_width)
		game.player2.weapon.bullet_move()
	# 공 위치 정의
	game.ball.ball_location(game.screen_width, game.screen_height, game.stage.height)
	# 4. 충돌 처리
	if running:
		game_result, running = game.colide_event()
	game.player1.walk_update(0.2)
	if game.player_num == 2:
		game.player2.walk_update(0.2)

	# 모든 공을 없앤 경우 게임 종료 (성공)
	if len(game.ball.balls) == 0:
		game_result = "Mission Complete"
		running = False
	# 5. 화면에 그리기
	game.draw_screen()
	# 시간 초과했다면
	if running:
		game_result, running = game.playtime()
	pygame.display.update()

# 게임 오버 메시지
msg = game.font.render(game_result, True, (255, 0, 20)) # 빨간색
msg_rect = msg.get_rect(center=(int(game.screen_width / 2), int(game.screen_height / 2)))
game.screen.blit(msg, msg_rect)
pygame.display.update()
pygame.time.delay(2000)
pygame.quit()