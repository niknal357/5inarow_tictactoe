import subprocess
import time
import random
import math
import sys
import os
if not os.path.exists('replays/'):
    os.makedirs('replays/')

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--trusted-host", "pypi.org",
                          "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", package])

BOT_THINKING_TIME_ALLOWED = 1/10
DEBUG_RENDERING = False

subprocess.run(["curl", "--insecure", "https://raw.githubusercontent.com/niknal357/5inarow_tictactoe/main/tictactoe_lib.py", "-o", "tictactoe_lib.py"])

if True:
    from tictactoe_lib import *

try:
    import pygame
except:
    print('pygame missing; attempting install...')
    try:
        install("pygame")
    except:
        print('pygame install failed; aborting...')
        sys.exit()
    import pygame

try:
    import ujson as json
except:
    try:
        print('ujson missing; attempting install...')
        install('ujson')
        import ujson
    except:
        print('ujson install failed; using json...')
        import json

replay_name_x = ''
replay_name_o = ''

if len(sys.argv) == 2:
    replay_file = sys.argv[1]
    with open(replay_file, 'r') as f:
        repl = f.read().strip()
    replay_playback = repl.split('\n')[2].split(',')
    print(replay_playback)
    replay_name_x = json.loads(repl.split('\n')[0])
    replay_name_o = json.loads(repl.split('\n')[1])
    save_replay = False
else:
    save_replay = True
    replay = ''

if save_replay:
    replay_file = 'replays/'+str(int(time.time()))+str(random.randint(0, 999999))+'.replay'

win = '_'
win_x_1 = None
win_y_2 = None
win_x_2 = None
win_y_2 = None

turn_times = []


X_BOT = None
O_BOT = bot_attempt_2

bots = [{'name': 'Human', 'func': None}, {'name': 'Kabir', 'func': Kabir}, {'name': 'Bot 2',
                                                                            'func': bot_attempt_2}, {'name': 'Bot 3', 'func': bot_3}, {'name': 'Bot 3.1', 'func': bot_quasi_3}, {'name': 'Bot 4', 'func': bot_4}, {'name': 'Bot 5', 'func': bot_5}, {'name': 'Bot 6 (Prototype -> not good)', 'func': bot_proto_6}, {'name': 'Over-dedicated', 'func': over_dedicated_bot}, {'name': 'Easy Bot', 'func': easy_bot}, {'name': 'Manzoh Bot', 'func': manzoh_bot}, {'name': 'Meh Bot', 'func': meh_bot}, {'name': 'Bot 7 (prototype)', 'func': testing_bot}]  # {'name': 'Stress Depth', 'func': stress_depth_search}, {'name': 'Bot 5', 'func': bot_5}]


def replay_bot(grid, playing_as):
    global win
    global replay_counter
    replay_counter += 1
    a = replay_playback[replay_counter].split(':')
    if replay_counter+1 >= len(replay_playback):
        win = '-'
    yield (int(a[0]), int(a[1]))


def setup():
    global bot_generator
    global grid
    global replay_file
    global x_memory
    global o_memory
    global replay
    global hint_position_x
    global hint_position_y
    global win, win_x_1, win_x_2, win_y_1, win_y_2
    global x_mem
    global o_mem
    bot_generator = None
    x_mem = None
    o_mem = None
    win = '_'
    hint_position_x = None
    hint_position_y = None
    win_x_1 = None
    win_y_2 = None
    win_x_2 = None
    win_y_2 = None
    x_memory = None
    o_memory = None
    replay_file = 'replays/'+str(int(time.time()))+str(random.randint(0, 999999))+'.replay'
    grid = []
    for x in range(GRID_SIZE_X):
        grid.append([])
        for y in range(GRID_SIZE_Y):
            grid[x].append('_')
    if save_replay:
        replay = ''


if save_replay:
    next_robot_turn_allowed = time.time()+BOT_PLAY_DELAY
else:
    next_robot_turn_allowed = time.time()+REPLAY_PLAY_DELAY

hint_position_x = None
hint_position_y = None


def scan_for_win(grid):
    global win
    global win_x_1
    global win_y_1
    global win_x_2
    global win_y_2
    fail = False
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            if grid[x][y] == '_':
                fail = True
                continue
            if x < GRID_SIZE_X-4:
                horizonal_check = True
                if y < GRID_SIZE_Y-4:
                    diagonal_check_upwards = True
                else:
                    diagonal_check_upwards = False
                if y > 3:
                    diagonal_check_downwards = True
                else:
                    diagonal_check_downwards = False
            else:
                horizonal_check = False
                diagonal_check_upwards = False
                diagonal_check_downwards = False
            if y < GRID_SIZE_Y-4:
                vertical_check = True
            else:
                vertical_check = False
            if horizonal_check:
                if grid[x][y] == grid[x+1][y] and grid[x][y] == grid[x+2][y] and grid[x][y] == grid[x+3][y] and grid[x][y] == grid[x+4][y]:
                    win = grid[x][y]
                    win_x_1 = grid_coords[x][y][0]-square_size*SQUARE_PADDING
                    win_y_1 = grid_coords[x][y][1]/2+grid_coords[x][y][3]/2
                    win_x_2 = grid_coords[x+4][y][2]+square_size*SQUARE_PADDING
                    win_y_2 = grid_coords[x+4][y][1]/2+grid_coords[x+4][y][3]/2
                    break
            if vertical_check:
                if grid[x][y] == grid[x][y+1] and grid[x][y] == grid[x][y+2] and grid[x][y] == grid[x][y+3] and grid[x][y] == grid[x][y+4]:
                    win = grid[x][y]
                    win_x_1 = grid_coords[x][y][0]/2+grid_coords[x][y][2]/2
                    win_y_1 = grid_coords[x][y][1]-square_size*SQUARE_PADDING
                    win_x_2 = grid_coords[x][y+4][0]/2+grid_coords[x][y+4][2]/2
                    win_y_2 = grid_coords[x][y+4][3]+square_size*SQUARE_PADDING
                    break
            if diagonal_check_upwards:
                if grid[x][y] == grid[x+1][y+1] and grid[x][y] == grid[x+2][y+2] and grid[x][y] == grid[x+3][y+3] and grid[x][y] == grid[x+4][y+4]:
                    win = grid[x][y]
                    win_x_1 = grid_coords[x][y][0]-square_size*SQUARE_PADDING
                    win_y_1 = grid_coords[x][y][1]-square_size*SQUARE_PADDING
                    win_x_2 = grid_coords[x+4][y+4][2] + \
                        square_size*SQUARE_PADDING
                    win_y_2 = grid_coords[x+4][y+4][3] + \
                        square_size*SQUARE_PADDING
                    break
            if diagonal_check_downwards:
                if grid[x][y] == grid[x+1][y-1] and grid[x][y] == grid[x+2][y-2] and grid[x][y] == grid[x+3][y-3] and grid[x][y] == grid[x+4][y-4]:
                    win = grid[x][y]
                    win_x_1 = grid_coords[x][y][0]-square_size*SQUARE_PADDING
                    win_y_1 = grid_coords[x][y][3]+square_size*SQUARE_PADDING
                    win_x_2 = grid_coords[x+4][y-4][2] + \
                        square_size*SQUARE_PADDING
                    win_y_2 = grid_coords[x+4][y-4][1] - \
                        square_size*SQUARE_PADDING
                    break
    if win == '_' and fail == False:
        win = '-'


last_x = None
last_y = None

if not save_replay:
    X_BOT = replay_bot
    O_BOT = replay_bot

game_running = True
x_player = 0
o_player = -7

x_memory = None
o_memory = None

bot_generator = None

def menu():
    global X_BOT
    global O_BOT
    global x_player
    global o_player
    global game_running
    global replay
    running = True
    prev_mouse_x = 0
    prev_mouse_y = 0
    framerate = 15
    no_move = 0
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if prev_mouse_x != mouse_x:
            framerate = 60
            no_move = 0
        elif prev_mouse_y != mouse_y:
            framerate = 60
            no_move = 0
        else:
            no_move += 1
            if no_move >= 200:
                framerate = 3
            elif no_move >= 100:
                framerate = 25*0.1+framerate*0.9
        prev_mouse_x = mouse_x
        prev_mouse_y = mouse_y
        frame_end = time.time()+1/framerate
        keys_down = pygame.key.get_pressed()
        mouse_down = pygame.mouse.get_pressed(num_buttons=3)[0]
        if mousewasdown != mouse_down:
            framerate = 60
            no_move = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    game_running = False
        button_size = (300, 170)
        button_spacing = 10
        button_1_pos = (x_size//2, y_size//2 -
                        button_size[1]//2-button_spacing//2)
        button_2_pos = (x_size//2, y_size//2 +
                        button_size[1]//2+button_spacing//2)
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BACKGROUND)
        play_rect = pygame.Rect(
            button_1_pos[0]-button_size[0]//2, button_1_pos[1]-button_size[1]//2, button_size[0], button_size[1])
        color = BACKGROUND_DARK
        if play_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            color = BLACK
            if mouse_down and mouse_was_down:
                running = False
                X_BOT = bots[x_player]['func']
                O_BOT = bots[o_player]['func']
                replay += json.dumps(bots[x_player]['name'])+'\n'
                replay += json.dumps(bots[o_player]['name'])+'\n'
        pygame.draw.rect(screen, color, play_rect, width=0, border_radius=10)
        # pygame.draw.rect(screen, WHITE, play_rect,
        #                 width=2, border_radius=10)
        txt = 'play'
        text = big_font.render(txt, True, WHITE)
        screen.blit(text, (button_1_pos[0]-big_font.size(txt)
                    [0]//2, button_1_pos[1]-big_font.size(txt)[1]//2))
        quit_rect = pygame.Rect(
            button_2_pos[0]-button_size[0]//2, button_2_pos[1]-button_size[1]//2, button_size[0], button_size[1])
        color = BACKGROUND_DARK
        if quit_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            color = BLACK
            if mouse_down and mouse_was_down:
                game_running = False
                running = False
        pygame.draw.rect(screen, color, quit_rect, width=0, border_radius=10)
        # pygame.draw.rect(screen, WHITE, quit_rect,
        #                 width=2, border_radius=10)
        txt = 'quit'
        text = big_font.render(txt, True, WHITE)
        screen.blit(text, (button_2_pos[0]-big_font.size(txt)
                    [0]//2, button_2_pos[1]-big_font.size(txt)[1]//2))

        x_toggle_button = pygame.Rect(25, 25, 75, 75)
        color = BACKGROUND_DARK
        if x_toggle_button.collidepoint(mouse_pos[0], mouse_pos[1]):
            color = BLACK
            if mouse_down and not mouse_was_down:
                if keys_down[pygame.K_LSHIFT] or keys_down[pygame.K_RSHIFT] or keys_down[pygame.K_LCTRL] or keys_down[pygame.K_RCTRL]:
                    x_player -= 1
                else:
                    x_player += 1
        x_player %= len(bots)
        pygame.draw.rect(screen, color, x_toggle_button,
                         width=0, border_radius=10)
        # pygame.draw.rect(screen, WHITE,
        #                 x_toggle_button, width=2, border_radius=10)
        pygame.draw.line(screen, RED, (30, 30), (95, 95), width=2)
        pygame.draw.line(screen, RED, (30, 95), (95, 30), width=2)
        txt = bots[x_player]['name']
        text = big_font.render(txt, True, WHITE)
        screen.blit(text, (125, 25+75/2-big_font.size(txt)[1]/2))

        o_toggle_button = pygame.Rect(25, 125, 75, 75)
        color = BACKGROUND_DARK
        if o_toggle_button.collidepoint(mouse_pos[0], mouse_pos[1]):
            color = BLACK
            if mouse_down and not mouse_was_down:
                if keys_down[pygame.K_LSHIFT] or keys_down[pygame.K_RSHIFT] or keys_down[pygame.K_LCTRL] or keys_down[pygame.K_RCTRL]:
                    o_player -= 1
                else:
                    o_player += 1
        o_player %= len(bots)
        pygame.draw.rect(screen, color, o_toggle_button,
                         width=0, border_radius=10)
        # pygame.draw.rect(screen, WHITE,
        #                 o_toggle_button, width=2, border_radius=10)
        pygame.draw.ellipse(
            screen, GREEN, pygame.Rect(30, 130, 65, 65), width=2)
        txt = bots[o_player]['name']
        text = big_font.render(txt, True, WHITE)
        screen.blit(text, (125, 125+75/2-big_font.size(txt)[1]/2))
        txt = VERSION
        text = small_font.render(txt, True, WHITE)
        screen.blit(text, (x_size-15-small_font.size(txt)
                    [0], y_size-15-small_font.size(txt)[1]))

        # pygame.draw.rect(screen, BLACK, pygame.Rect(
        #    0, 0, x_size, y_size), width=10)
        to_wait = frame_end-time.time()
        if to_wait > 0:
            time.sleep(to_wait)
        pygame.display.flip()
        mouse_was_down = mouse_down


mousewasdown = True

def main():
    global global_text
    global bot_generator
    global hint_position_x
    global hint_position_y
    global replay
    global mousewasdown
    global turn_times
    global game_running
    global win
    global win_x_1
    global win_x_2
    global win_y_1
    global win_y_2
    global next_robot_turn_allowed
    global last_x
    global last_y
    global x_memory
    global o_memory
    prev_mouse_x = 0
    prev_mouse_y = 0
    framerate = 10
    no_move = 0
    calculating_hint = None
    if DEBUG_RENDERING:
        render_grid_x = calculate_grid_intersection_values(grid, 'x')
        render_grid_o = calculate_grid_intersection_values(grid, 'o')
    running = True
    prevframe = time.time()
    past_fpss = []
    turn = 'x'
    clicklock = True
    turn_num = 0
    was_calculating = False
    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if prev_mouse_x != mouse_x:
            framerate = 60
            no_move = 0
        elif prev_mouse_y != mouse_y:
            framerate = 60
            no_move = 0
        else:
            no_move += 1
            if no_move >= 200:
                framerate = 3
            elif no_move >= 100:
                framerate = 25*0.1+framerate*0.9
        prev_mouse_x = mouse_x
        prev_mouse_y = mouse_y
        if calculating_hint != None or bot_generator != None or was_calculating:
            frame_end = 0
            framerate = 60
        else:
            frame_end = time.time()+1/framerate
        mousedown = pygame.mouse.get_pressed(num_buttons=3)[0]
        if mousewasdown != mousedown:
            framerate = 60
            no_move = 0
        if calculating_hint != None:
            end_time = time.time()+BOT_THINKING_TIME_ALLOWED
            res = None
            while time.time() < end_time and res == None:
                res = next(calculating_hint)
            if res != None:
                hint_position_x = res[0]
                hint_position_y = res[1]
                calculating_hint = None
        if turn == 'x':
            turnbot = X_BOT
        else:
            turnbot = O_BOT
        timediff = time.time()-prevframe
        if timediff == 0:
            timediff += 1
        prevframe = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_UP:
                    if collide_with_y != None:
                        try:
                            pygame.mouse.set_pos(grid_coords[collide_with_x][collide_with_y-1][0]/2+grid_coords[collide_with_x][collide_with_y-1]
                                                [2]/2, grid_coords[collide_with_x][collide_with_y-1][1]/2+grid_coords[collide_with_x][collide_with_y-1][3]/2)
                        except: pass
                if event.key == pygame.K_DOWN:
                    if collide_with_y != None:
                        try:
                            pygame.mouse.set_pos(grid_coords[collide_with_x][collide_with_y+1][0]/2+grid_coords[collide_with_x][collide_with_y+1]
                                                [2]/2, grid_coords[collide_with_x][collide_with_y+1][1]/2+grid_coords[collide_with_x][collide_with_y+1][3]/2)
                        except: pass
                if event.key == pygame.K_LEFT:
                    if collide_with_y != None:
                        try:
                            pygame.mouse.set_pos(grid_coords[collide_with_x-1][collide_with_y][0]/2+grid_coords[collide_with_x-1][collide_with_y]
                                                [2]/2, grid_coords[collide_with_x-1][collide_with_y][1]/2+grid_coords[collide_with_x-1][collide_with_y][3]/2)
                        except: pass
                if event.key == pygame.K_RIGHT:
                    if collide_with_y != None:
                        try:
                            pygame.mouse.set_pos(grid_coords[collide_with_x+1][collide_with_y][0]/2+grid_coords[collide_with_x+1][collide_with_y]
                                                [2]/2, grid_coords[collide_with_x+1][collide_with_y][1]/2+grid_coords[collide_with_x+1][collide_with_y][3]/2)
                        except: pass
        screen.fill(BACKGROUND)
        for line in vert_lines:
            pygame.draw.line(screen, GREY, (line, y_size /
                             2-height/2), (line, y_size/2+height/2), width=1)
        for line in horiz_lines:
            pygame.draw.line(screen, GREY, (x_size /
                             2-width/2, line), (x_size/2+width/2, line), width=1)
        collide_with_x = None
        collide_with_y = None
        #print(framerate)
        for x in range(GRID_SIZE_X):
            for y in range(GRID_SIZE_Y):
                square_rect = pygame.Rect((grid_coords[x][y][0], grid_coords[x][y][1]), (
                    grid_coords[x][y][2]-grid_coords[x][y][0], grid_coords[x][y][3]-grid_coords[x][y][1]))
                if square_rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(screen, BACKGROUND_DARK, square_rect)
                    collide_with_x = x
                    collide_with_y = y
                if x == last_x and y == last_y:
                    draw_width = 3
                    redcolor = RED_LIGHT
                    greencolor = GREEN_LIGHT
                else:
                    draw_width = 1
                    redcolor = RED
                    greencolor = GREEN
                if grid[x][y] == 'x':
                    pygame.draw.line(screen, redcolor, (grid_coords[x][y][0], grid_coords[x][y][1]), (
                        grid_coords[x][y][2], grid_coords[x][y][3]), width=draw_width)
                    pygame.draw.line(screen, redcolor, (grid_coords[x][y][0], grid_coords[x][y][3]), (
                        grid_coords[x][y][2], grid_coords[x][y][1]), width=draw_width)
                elif grid[x][y] == 'o':
                    pygame.draw.ellipse(
                        screen, greencolor, square_rect, width=draw_width)
                elif DEBUG_RENDERING:
                    txt = str(max(render_grid_x[x][y], render_grid_o[x][y]))
                    text = small_font.render(txt, True, WHITE)
                    screen.blit(
                        text, (grid_coords[x][y][0], grid_coords[x][y][1]))
                    #txt = str(render_grid_x[x][y])
                    #text = small_font.render(txt, True, RED)
                    # screen.blit(
                    #    text, (grid_coords[x][y][0], grid_coords[x][y][1]))
                    #txt = str(render_grid_o[x][y])
                    #text = small_font.render(txt, True, GREEN)
                    # screen.blit(
                    #    text, (grid_coords[x][y][2]-small_font.size(txt)[0], grid_coords[x][y][3]-small_font.size(txt)[1]))
        draw_width = 2
        if turn == 'x' and hint_position_x != None:
            pygame.draw.line(screen, RED_DARK, (grid_coords[hint_position_x][hint_position_y][0], grid_coords[hint_position_x][hint_position_y][1]), (
                grid_coords[hint_position_x][hint_position_y][2], grid_coords[hint_position_x][hint_position_y][3]), width=draw_width)
            pygame.draw.line(screen, RED_DARK, (grid_coords[hint_position_x][hint_position_y][0], grid_coords[hint_position_x][hint_position_y][3]), (
                grid_coords[hint_position_x][hint_position_y][2], grid_coords[hint_position_x][hint_position_y][1]), width=draw_width)
        if turn == 'o' and hint_position_x != None:
            square_rect = pygame.Rect((grid_coords[hint_position_x][hint_position_y][0], grid_coords[hint_position_x][hint_position_y][1]), (
                grid_coords[hint_position_x][hint_position_y][2]-grid_coords[hint_position_x][hint_position_y][0], grid_coords[hint_position_x][hint_position_y][3]-grid_coords[hint_position_x][hint_position_y][1]))
            pygame.draw.ellipse(
                screen, GREEN_DARK, square_rect, width=draw_width)
        if win == '_':
            if turnbot == None:
                was_calculating = False
                if pygame.mouse.get_pressed(num_buttons=3)[0] or pygame.key.get_pressed()[pygame.K_RETURN]:
                    if clicklock:
                        continue
                    clicklock = True
                    if collide_with_x == None or collide_with_y == None:
                        continue
                    if grid[collide_with_x][collide_with_y] != '_':
                        continue
                    grid[collide_with_x][collide_with_y] = turn
                    global_text = ''
                    if DEBUG_RENDERING:
                        render_grid_x = calculate_grid_intersection_values(
                            grid, 'x')
                        render_grid_o = calculate_grid_intersection_values(
                            grid, 'o')
                    hint_position_x = None
                    hint_position_y = None
                    calculating_hint = None
                    if save_replay:
                        replay += (str(collide_with_x) +
                                   ':'+str(collide_with_y))+','
                        with open(replay_file, 'w') as f:
                            f.write(replay.strip(','))
                    last_x = collide_with_x
                    last_y = collide_with_y
                    scan_for_win(grid)
                    if win == '_':
                        if turn == 'x':
                            turn = 'o'
                        else:
                            turn = 'x'
                    else:
                        replay = replay.strip(',')
                        if len(replay.split('\n')) != 4:
                            replay += '\n'+{'-': '0', 'x': '1',
                                            'o': '2'}[win]
                            if save_replay:
                                with open(replay_file, 'w') as f:
                                    f.write(replay)
                    if save_replay:
                        next_robot_turn_allowed = time.time()+BOT_PLAY_DELAY
                    else:
                        next_robot_turn_allowed = time.time()+REPLAY_PLAY_DELAY
                    turn_num += 1
                else:
                    clicklock = False
            else:
                if next_robot_turn_allowed <= time.time():
                    if bot_generator == None:
                        bot_generator = turnbot(grid, turn)
                    end_time = time.time()+BOT_THINKING_TIME_ALLOWED
                    res = None
                    while time.time()<end_time and res == None:
                        res = next(bot_generator)
                    #print(res)
                    if type(res) == str:
                        global_text = res
                    elif res != None:
                        coords_to_place = res
                        bot_generator = None
                        was_calculating = True
                        turn_num += 1
                        if grid[coords_to_place[0]][coords_to_place[1]] != '_':
                            print(
                                'Error: robot ('+turn+') attempted to make to make an illegal move.')
                            print(coords_to_place)
                            bot_generator = None
                            win = '-'
                            for x in range(len(grid)):
                                line = []
                                for y in range(len(grid[0])):
                                    line.append(grid[x][y])
                                print(' '.join(line))
                        else:
                            grid[coords_to_place[0]][coords_to_place[1]] = turn
                            global_text = ''
                        if DEBUG_RENDERING:
                            render_grid_x = calculate_grid_intersection_values(
                                grid, 'x')
                            render_grid_o = calculate_grid_intersection_values(
                                grid, 'o')
                        hint_position_x = None
                        hint_position_y = None
                        if save_replay:
                            replay += (str(coords_to_place[0]) +
                                    ':'+str(coords_to_place[1]))+','
                        last_x = coords_to_place[0]
                        last_y = coords_to_place[1]
                        scan_for_win(grid)
                        constant_score_to_x = value_towards_x(grid)
                        if win == '_':
                            if turn == 'x':
                                turn = 'o'
                            else:
                                turn = 'x'
                        if save_replay:
                            next_robot_turn_allowed = time.time()+BOT_PLAY_DELAY
                        else:
                            next_robot_turn_allowed = time.time()+REPLAY_PLAY_DELAY
        exit_button_height = int(y_size*(1-USABLE_AMOUNT_OF_SCREEN-0.02))
        exit_button_rect = pygame.Rect(
            x_size-(exit_button_height*2.15), 0, exit_button_height*2.15, exit_button_height)
        if exit_button_rect.collidepoint(mouse_x, mouse_y):
            color = RED_DARK
            x_color = GREY
            if mousedown and not mousewasdown:
                running = False
                replay = replay.strip(',')
                if len(replay.split('\n')) != 4:
                    replay += '\n'+{'-': '0', 'x': '1',
                                    'o': '2', '_': '0'}[win]
                if save_replay:
                    with open(replay_file, 'w') as f:
                        f.write(replay)
        else:
            color = RED
            x_color = WHITE
        pygame.draw.rect(screen, color, exit_button_rect,
                         border_bottom_left_radius=10)
        button_center_x = x_size - \
            (exit_button_height*2.15)+(exit_button_height*2.15)/2
        button_center_y = exit_button_height/2
        x_button_length = button_center_y*0.7
        pygame.draw.line(screen, x_color, (button_center_x-x_button_length, button_center_y-x_button_length),
                         (button_center_x+x_button_length, button_center_y+x_button_length), width=2)
        pygame.draw.line(screen, x_color, (button_center_x+x_button_length, button_center_y-x_button_length),
                         (button_center_x-x_button_length, button_center_y+x_button_length), width=2)
        past_fpss.append(1/timediff)
        while len(past_fpss) > 120:
            past_fpss.pop(0)
        avg_fps = 0
        for fps in past_fpss:
            avg_fps += fps
        if win == '_':
            if turn == 'x':
                color = RED
            else:
                color = GREEN
            banner_height = min(
                y_size*(1-USABLE_AMOUNT_OF_SCREEN-0.02), small_font.size(VERSION)[1]+35)
            pygame.draw.rect(screen, color, pygame.Rect(
                0, y_size-banner_height, x_size, banner_height))
            # pygame.draw.rect(screen, color, pygame.Rect(
            #    0, 0, x_size, y_size), width=10)
        if save_replay and calculating_hint == None:
            if (turn == 'x' and X_BOT == None) or (turn == 'o' and O_BOT == None):
                hint_button_height = int(
                    y_size*(1-USABLE_AMOUNT_OF_SCREEN-0.02))
                txt = 'Hint pls'
                hint_button_rect = pygame.Rect(
                    0, y_size-hint_button_height-1, small_font.size(txt)[0]+20, hint_button_height+1)
                if hint_button_rect.collidepoint(mouse_x, mouse_y):
                    color = BACKGROUND_DARK
                    text_color = GREY
                    if mousedown and not mousewasdown:
                        calculating_hint = bot_5(grid, turn)
                else:
                    color = BACKGROUND
                    text_color = WHITE
                pygame.draw.rect(screen, color, hint_button_rect)
                text = small_font.render(txt, True, text_color)
                screen.blit(
                    text, (10, y_size-hint_button_height/2-small_font.size(txt)[1]/2))
        if win != '_':
            was_calculating = False
        if win == '-':
            txt = "draw!"
            text = small_font.render(txt, True, WHITE)
            screen.blit(text, (10, 10))
        else:
            if win != '_':
                pygame.draw.line(screen, WHITE,
                                 (win_x_1, win_y_1), (win_x_2, win_y_2), width=3)
            if turn == 'x':
                pygame.draw.line(screen, RED, (15, 15),
                                 (height_of_label+15, height_of_label+15), width=2)
                pygame.draw.line(
                    screen, RED, (15, height_of_label+15), (height_of_label+15, 15), width=2)
            elif turn == 'o':
                pygame.draw.ellipse(screen, GREEN, pygame.Rect(
                    15, 15, height_of_label, height_of_label), width=2)
            if win == '_':
                txt = "'s turn "
            else:
                txt = " has won! "
            if turn == 'x':
                if save_replay:
                    txt += '('+bots[x_player]['name']+') '
                else:
                    txt += '('+replay_name_x+') '
            elif turn == 'o':
                if save_replay:
                    txt += '('+bots[o_player]['name']+') '
                else:
                    txt += '('+replay_name_o+') '
            txt += global_text
            #print(global_text)
            text = small_font.render(txt, True, WHITE)
            screen.blit(text, (25+height_of_label, 15 +
                        height_of_label/2 - small_font.size(txt)[1]/2))
        txt = VERSION
        text = small_font.render(txt, True, WHITE)
        screen.blit(text, (x_size-15-small_font.size(txt)
                    [0], y_size-15-small_font.size(txt)[1]))
        mousewasdown = mousedown
        to_wait = frame_end-time.time()
        if calculating_hint == None and bot_generator == None and to_wait > 0:
            time.sleep(to_wait)
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)
    #screen = pygame.display.set_mode((1500, 900))
    x_size, y_size = screen.get_size()
    height_of_label = int((y_size-y_size*USABLE_AMOUNT_OF_SCREEN)/3)
    small_font = pygame.font.SysFont("calibri", int(
        (y_size-y_size*USABLE_AMOUNT_OF_SCREEN)/3))
    big_font = pygame.font.SysFont("calibri", 70)
    grid = []
    width = GRID_SIZE_X
    height = GRID_SIZE_Y
    if width > height:
        height /= width
        width /= width
    elif width < height:
        width /= height
        height /= height
    else:
        width = 1
        height = 1
    #subprocess.run(["curl", "--insecure", "https://raw.githubusercontent.com/misterjones69420/project-yes/main/create_install.py", "-o", "create_install.py"])
    #subprocess.run(["python", "create_install.py"])
    x_size_with_padding = x_size*USABLE_AMOUNT_OF_SCREEN
    y_size_with_padding = y_size-x_size+x_size*USABLE_AMOUNT_OF_SCREEN
    width_to_screen = width/x_size_with_padding
    height_to_screen = height/y_size_with_padding
    if width_to_screen > height_to_screen:
        coefficient = 1/width_to_screen
    else:
        coefficient = 1/height_to_screen
    width *= coefficient
    height *= coefficient
    square_size = width / GRID_SIZE_X

    vert_lines = []
    horiz_lines = []
    for i in range(GRID_SIZE_X+1):
        vert_lines.append(width*i/(GRID_SIZE_X)+x_size/2-width/2)
    for i in range(GRID_SIZE_Y+1):
        horiz_lines.append(height*i/(GRID_SIZE_Y)+y_size/2-height/2)

    grid_coords = {}
    for x in range(GRID_SIZE_X):
        grid_coords[x] = {}
        for y in range(GRID_SIZE_Y):
            grid_coords[x][y] = (
                square_size*x+x_size/2-width/2+square_size*SQUARE_PADDING,
                square_size*y+y_size/2-height/2+square_size*SQUARE_PADDING,
                square_size*(x+1)+x_size/2-width/2 -
                square_size*SQUARE_PADDING+1,
                square_size*(y+1)+y_size/2-height/2 -
                square_size*SQUARE_PADDING+1,
            )
    if save_replay:
        while game_running:
            setup()
            menu()
            if not game_running:
                break
            main()
    else:
        setup()
        main()

    # setup()
    # main()

    pygame.quit()
