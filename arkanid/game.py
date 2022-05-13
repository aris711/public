import pgzrun
import random

TITLE = "Arkanoid v0.1"
WIDTH = 800
HEIGHT = 600

ball = Actor("ball-rose")
ball.pos = 400, 549
# board = Actor("board")
# board_size = 80 // 2
board = Actor("board-large")
board_size = 120 // 2
board.pos = 400, 569

start = False
fail = False
win = False
cost = 25
score = 0

block_list = []
block_name_list = ["block_red", "block_orange", "block_yellow", "block_green", "block_marine", "block_blue", "block_violet"]

board_speed = 5
ball_speed = 2
ball_inc_x = (-1) ** random.randint(0,1)
ball_inc_y = -1

def level_create(block_x, block_y, space):
    global block_list, block_name_list
    start_x = (WIDTH - (60 + space) * (block_x - 1)) // 2
    start_y = 100
    for _ in range(block_y):
        for n in range(block_x):
            block = Actor(block_name_list[random.randint(0,6)])
            block.pos = (start_x + n * (60 + space), start_y)
            block_list.append(block)
        start_y += 30 + space
    # for block_color in block_name_list[:block_y]:
    #     for n in range(block_x):
    #         block = Actor(block_color)
    #         block.pos = (start_x + n * (60 + space), start_y)
    #         block_list.append(block)
    #     start_y += 30 + space

def ball_update():
    global ball_speed, ball_inc_x, ball_inc_y, fail
    ball.x += ball_speed * ball_inc_x
    ball.y += ball_speed * ball_inc_y
    if (ball.x >= WIDTH - 11) or (ball.x <= 11):
        ball_inc_x *= -1
    if (ball.y <= 11):
        ball_inc_y *= -1
    if (ball.y > HEIGHT + 12):
        fail = True

def update():
    global board_speed, ball_speed, start, ball_inc_x, ball_inc_y, fail, win, block_list, board_size, score, cost
    start += keyboard.space
    if not start:
        ball.x = board.x
    if start and not fail:
        ball_update()
    if board.colliderect(ball):
        ball_inc_y *= -1
    for block in block_list:
        if ball.colliderect(block):
            block_list.remove(block)
            ball_inc_y *= -1
            score += int(cost * ball_speed)
            ball_speed += 0.01
    board.x += abs(board_speed) * (keyboard.right - keyboard.left)
    if board.x > WIDTH - board_size:
        board.x -= board_speed
    if board.x < board_size:
        board.x += board_speed

    ball_speed += 0.02 * (keyboard.up - keyboard.down)

def draw():
    global fail, win, block_list, score
    if not fail and not win:
        screen.clear()
        screen.blit("bg", (0, 0))
        board.draw()
        ball.draw()
        screen.draw.text(str(score), color="white", center=(WIDTH - 80, 30), fontname="alger", fontsize=48)
        for block in block_list:
            block.draw()
    elif fail and not win:
        screen.draw.text('THE END!', color="red", center=(WIDTH / 2, HEIGHT / 2), fontname="alger", fontsize=96)
    elif not fail and win:
        screen.draw.text('WIN!', color="green", center=(WIDTH / 2, HEIGHT / 2), fontname="alger", fontsize=96)
    if len(block_list) == 0:
        win = True

level_create(10, 4, 5)
pgzrun.go()

