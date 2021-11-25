import subprocess
import copy
import time
import random
import math
#import requests
#import cProfile
import sys
#GRID_SIZE_X = 32
#GRID_SIZE_Y = 18
GRID_SIZE_X = 16*3
GRID_SIZE_Y = 9*3
#GRID_SIZE_X = 64
#GRID_SIZE_Y = 36
#GRID_SIZE_X = 69
#GRID_SIZE_Y = 420
#GRID_SIZE_X = 116
#GRID_SIZE_Y = 72
USABLE_AMOUNT_OF_SCREEN = 0.94
SQUARE_PADDING = 0.05
BOT_PLAY_DELAY = 0.1
REPLAY_PLAY_DELAY = 1.5

RED = (236, 65, 69)
GREEN = (61, 165, 96)


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--trusted-host", "pypi.org",
                          "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", package])


try:
    import pygame
except:
    install("pygame")
    import pygame
try:
    import ujson as json
except:
    import json

if len(sys.argv) == 2:
    replay_file = sys.argv[1]
    with open(replay_file, 'r') as f:
        replay = f.read().strip().split(':')
    save_replay = False
else:
    save_replay = True
    replay = []

if save_replay:
    replay_file = str(int(time.time()))+'.replay'

win = '_'
win_x_1 = None
win_y_2 = None
win_x_2 = None
win_y_2 = None

turn_times = []

replay_counter = -1


def to_line_3(string):
    out = []
    for char in string:
        out.append(char)
    return out


def get_of_grid_3(grid, pos):
    if pos[0] < 0 or pos[0] > len(grid)-1 or pos[1] < 0 or pos[1] > len(grid[0])-1:
        return 'n'
    else:
        return grid[pos[0]][pos[1]]


def get_line_3(grid, pos, dist, dir, invert=False):
    out = []
    for i in range(dist):
        curpos = (pos[0]+dir[0]*i, pos[1]+dir[1]*i)
        item = get_of_grid_3(grid, curpos)
        if invert:
            if item == 'x':
                out.append('o')
            elif item == 'o':
                out.append('x')
            else:
                out.append(item)
        else:
            out.append(item)
    return out


def intersect_lines(l1, l2):
    if len(l1) != len(l2):
        return False
    for i in range(len(l1)):
        if l1[i] != '-' and l2[i] != '-' and l1[i] != l2[i]:
            return False
    return True


def eval_line_3(line_ingrid):
    lines = [
        {'value': 'inf', 'line': to_line_3('-xxxx_---')},
        {'value': 'inf', 'line': to_line_3('--xxx_x--')},
        {'value': 'inf', 'line': to_line_3('---xx_xx-')},
        {'value': 13,    'line': to_line_3('---oo_oo-')},
        {'value': 12,    'line': to_line_3('--ooo_o--')},
        {'value': 11,    'line': to_line_3('xoooo_---')},
        {'value': 9,     'line': to_line_3('-_xxx__--')},
        {'value': 9,     'line': to_line_3('--_xx_x_-')},
        {'value': 8,     'line': to_line_3('---oo_o--')},
        {'value': 7,     'line': to_line_3('-_ooo_---')},
        {'value': 5,     'line': to_line_3('-__xx___-')},
        {'value': 5,     'line': to_line_3('--__x_x__')},
        {'value': 4,     'line': to_line_3('-xooo__--')},
        {'value': 4,     'line': to_line_3('--_xx__--')},
        {'value': 4,     'line': to_line_3('---_x_x_-')},
        {'value': 3,     'line': to_line_3('----o_o--')},
        {'value': 2,     'line': to_line_3('---oo_---')},
        {'value': 1,     'line': to_line_3('----x_---')},
        #{'value': 0,    'line': to_line_3('----o_---')},
    ]
    value = 0
    for line_inlist in lines:
        if intersect_lines(line_ingrid, line_inlist['line']):
            if line_inlist['value'] == 'inf':
                return 'inf'
            else:
                value += 3**line_inlist['value']
    return value


def eval_pos_3(grid, pos, playing_as):
    sum = 0
    lines_to_check = []
    for x in range(-1, 2):
        for y in range(-1, 2):
            if x != 0 or y != 0:
                dir = (x, y)
                lines_to_check.append(get_line_3(
                    grid, (pos[0]-dir[0]*5, pos[1]-dir[1]*5), 9, dir, playing_as == 'o'))
    for line in lines_to_check:
        calc = eval_line_3(line)
        if calc == 'inf':
            return 'inf'
        else:
            sum += calc
    return sum


def bot_3(grid, playing_as, return_sorted=False):
    possible_positions = []
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            if grid[x][y] != '_':
                left_good = False
                right_good = False
                up_good = False
                down_good = False
                if x < GRID_SIZE_X-1:
                    right_good = True
                if x > 1:
                    left_good = True
                if y < GRID_SIZE_Y-1:
                    down_good = True
                if y > 1:
                    up_good = True
                if up_good and left_good and grid[x-1][y-1] == '_':
                    possible_positions.append([x-1, y-1])
                if up_good and grid[x][y-1] == '_':
                    possible_positions.append([x, y-1])
                if right_good and up_good and grid[x+1][y-1] == '_':
                    possible_positions.append([x+1, y-1])
                if left_good and grid[x-1][y] == '_':
                    possible_positions.append([x-1, y])
                if right_good and grid[x+1][y] == '_':
                    possible_positions.append([x+1, y])
                if down_good and left_good and grid[x-1][y+1] == '_':
                    possible_positions.append([x-1, y+1])
                if down_good and grid[x][y+1] == '_':
                    possible_positions.append([x, y+1])
                if right_good and down_good and grid[x+1][y+1] == '_':
                    possible_positions.append([x+1, y+1])
    if len(possible_positions) == 0:
        if return_sorted:
            return [{'pos': [GRID_SIZE_X//2, GRID_SIZE_Y//2], 'val': 0}]
        return ([GRID_SIZE_X//2, GRID_SIZE_Y//2])
    positions_to_go = []
    for position in possible_positions:
        eval = eval_pos_3(grid, position, playing_as)
        if eval == 'inf':
            if return_sorted:
                return [{'pos': position, 'val': 100000000000000000000000000000000}]
            return position
        else:
            positions_to_go.append({'pos': position, 'val': eval})
    positions_to_go = sorted(positions_to_go, key=lambda d: d['val'])
    if return_sorted:
        return positions_to_go
    return positions_to_go[-1]['pos']


def replay_bot(grid, playing_as):
    global win
    global replay_counter
    replay_counter += 1
    a = replay[replay_counter].split(',')
    if replay_counter+1 >= len(replay):
        win = '-'
    return (int(a[0]), int(a[1]))


def get_score_of(grid, x, y, coeff1, coeff2):
    score = 0
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
        o_count = 0
        x_count = 0
        for i in range(5):
            if grid[x+i][y] == 'x':
                x_count += 1
            if grid[x+i][y] == 'o':
                o_count += 1
        if o_count == 0:
            score += coeff1**(x_count*coeff2)
        if x_count == 0:
            score -= coeff1**(o_count*coeff2)
    if vertical_check:
        o_count = 0
        x_count = 0
        for i in range(5):
            if grid[x][y+i] == 'x':
                x_count += 1
            if grid[x][y+i] == 'o':
                o_count += 1
        if o_count == 0:
            score += coeff1**(x_count*coeff2)
        if x_count == 0:
            score -= coeff1**(o_count*coeff2)
    if diagonal_check_upwards:
        o_count = 0
        x_count = 0
        for i in range(5):
            if grid[x+i][y+i] == 'x':
                x_count += 1
            if grid[x+i][y+i] == 'o':
                o_count += 1
        if o_count == 0:
            score += coeff1**(x_count*coeff2)
        if x_count == 0:
            score -= coeff1**(o_count*coeff2)
    if diagonal_check_downwards:
        o_count = 0
        x_count = 0
        for i in range(5):
            if grid[x+i][y-i] == 'x':
                x_count += 1
            if grid[x+i][y-i] == 'o':
                o_count += 1
        if o_count == 0:
            #score += x_count**4
            if x_count == 1:
                score += 1
            else:
                score += coeff1**(x_count*coeff2)
        if x_count == 0:
            #score -= o_count**4
            if o_count == 1:
                score -= 1
            else:
                score -= coeff1**(o_count*coeff2)
    return score


def value_towards_x(grid):
    score = 0
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            score += get_score_of(grid, x, y, 10, 1)
    return score


def get_scoregrid(grid, coeff1, coeff2):
    scoregrid = []
    for x in range(GRID_SIZE_X):
        scoregrid.append([])
        for y in range(GRID_SIZE_Y):
            scoregrid[x].append(get_score_of(
                grid, x, y, coeff1=coeff1, coeff2=coeff2))
    return scoregrid


def update_scoregrid(grid, scoregrid, places, coeff1, coeff2):
    to_update = []
    for place in places:
        x = place[0]
        y = place[1]
        for i in range(5):
            if (x-i, y) not in to_update:
                to_update.append((x-i, y))
            if (x, y-i) not in to_update:
                to_update.append((x, y-i))
            if (x-1, y-i) not in to_update:
                to_update.append((x-i, y-i))
            if (x-i, y+i) not in to_update:
                to_update.append((x-i, y+i))
    new_scoregrid = scoregrid
    for position in to_update:
        if position[0] < 0 or position[0] > GRID_SIZE_X-1 or position[1] < 0 or position[1] > GRID_SIZE_Y-1:
            continue
        new_scoregrid[position[0]][position[1]] = get_score_of(
            grid, position[0], position[1], coeff1=coeff1, coeff2=coeff2)
    return new_scoregrid


def sum_up_scoregrid(scoregrid):
    score = 0
    for x in scoregrid:
        for y in x:
            score += y
    return score


def bot_attempt_2(grid, playing_as):
    if playing_as == 'x':
        maximizing_player = True
    else:
        maximizing_player = False
    out = minimax(grid, 2, -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                  100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, maximizing_player, True, get_scoregrid(grid, 4, 2), [], 4, 2)
    return (int(out[0]), int(out[1]))


def minimax(grid, depth, alpha, beta, maximizing_player, return_pos, original_scoregrid, placements, coeff1, coeff2):
    if depth == 0:
        return sum_up_scoregrid(update_scoregrid(grid, original_scoregrid, placements, coeff1, coeff2))
    playing_as = 'o'
    if maximizing_player:
        playing_as = 'x'
    possible_positions_with_val = bot_3(grid, playing_as, return_sorted=True)
    possible_positions = []
    for pos in possible_positions_with_val:
        possible_positions.append(pos['pos'])
    if len(possible_positions) == 0:
        return ([GRID_SIZE_X//2, GRID_SIZE_Y//2])
    possible_positions = possible_positions[math.floor(
        len(possible_positions)*0.5):]
    bestPos = None
    if maximizing_player:
        maxEval = -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        for position in possible_positions:
            grid[position[0]][position[1]] = 'x'
            eval = minimax(grid, depth-1, alpha, beta, False,
                           False, original_scoregrid, placements+[position], coeff1, coeff2)
            grid[position[0]][position[1]] = '_'
            if eval > maxEval:
                maxEval = eval
                bestPos = position
            maxEval = max(maxEval, eval)
        if return_pos:
            if bestPos == None:
                return random.choice(possible_positions)
            return bestPos
        else:
            return maxEval
    else:
        minEval = 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        for position in possible_positions:
            grid[position[0]][position[1]] = 'o'
            stress = calculate_stress(grid, 'o')
            eval = minimax(grid, depth-1, alpha, beta, True, False,
                           original_scoregrid, placements+[position], coeff1, coeff2)
            grid[position[0]][position[1]] = '_'
            if eval < minEval:
                minEval = eval
                bestPos = position
        if return_pos:
            if bestPos == None:
                return random.choice(possible_positions)
            return bestPos
        else:
            return minEval


def calculate_stress(grid, stress_from):
    #positions = get_list_of_grid(grid)
    # positions = inflate_gridlist(
    #    positions, GRID_SIZE_X-1, GRID_SIZE_Y-1, amount=2, offset_x=-3, offset_y=-3)
    lines = [
        {'line': to_line_3('xxxx_'), 'val': 2},
        {'line': to_line_3('xxxxo'), 'val': 1},
        {'line': to_line_3('_xxx_'), 'val': 1},
        {'line': to_line_3('x_xx_'), 'val': 1},
    ]
    positions = []
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            positions.append((x, y))
    total_stress = 0
    for stress_yes in lines:
        for pos in positions:
            if grid[pos[0]][pos[1]] != '_':
                continue
            lines_to_check = []
            for dir in [(1, -1), (1, 0), (1, 1), (0, 1)]:
                lines_to_check.append(get_line_3(
                    grid, (pos[0]+dir[0], pos[1]+dir[1]), 5, dir, stress_from == 'o'))
            for line in lines_to_check:
                if intersect_lines(stress_yes['line'], line):
                    total_stress += stress_yes['val']
    return total_stress


def depth_search_4(grid, playing_as, placing_turn, depth, return_move=False):
    if depth == 0:
        return 0
    placing_opponent = 'x'
    if placing_turn == 'x':
        placing_opponent = 'o'
    playing_opponent = 'x'
    if playing_as == 'x':
        playing_opponent = 'o'
    stress_from_bot = calculate_stress(grid, playing_as)
    stress_from_opponent = calculate_stress(grid, playing_opponent)
    if not return_move:
        if stress_from_bot >= 2:
            return 1
        elif stress_from_opponent >= 2:
            return -1
    possible_positions = []
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            if grid[x][y] != '_':
                left_good = False
                right_good = False
                up_good = False
                down_good = False
                if x < GRID_SIZE_X-1:
                    right_good = True
                if x > 1:
                    left_good = True
                if y < GRID_SIZE_Y-1:
                    down_good = True
                if y > 1:
                    up_good = True
                if up_good and left_good and grid[x-1][y-1] == '_':
                    possible_positions.append([x-1, y-1])
                if up_good and grid[x][y-1] == '_':
                    possible_positions.append([x, y-1])
                if right_good and up_good and grid[x+1][y-1] == '_':
                    possible_positions.append([x+1, y-1])
                if left_good and grid[x-1][y] == '_':
                    possible_positions.append([x-1, y])
                if right_good and grid[x+1][y] == '_':
                    possible_positions.append([x+1, y])
                if down_good and left_good and grid[x-1][y+1] == '_':
                    possible_positions.append([x-1, y+1])
                if down_good and grid[x][y+1] == '_':
                    possible_positions.append([x, y+1])
                if right_good and down_good and grid[x+1][y+1] == '_':
                    possible_positions.append([x+1, y+1])
    tot = 0
    cnt = 0
    top = {'score': -10000000000000000000, 'pos': None}
    cp_grid = json.loads(json.dumps(grid))
    for pos in possible_positions:
        cp_grid[pos[0]][pos[1]] = placing_turn
        res = depth_search_4(cp_grid, playing_as, placing_opponent, depth-1)
        if res != 0:
            tot += res
            cnt += 1
        if res > top['score']:
            top['score'] = res
            top['pos'] = pos
        cp_grid[pos[0]][pos[1]] = '_'
    if return_move:
        if top['pos'] == None:
            return bot_attempt_2(grid, playing_as)
        return top['pos']
    if cnt == 0:
        return 0
    else:
        return tot/cnt


def bot_4(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    possible_positions = []
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            if grid[x][y] != '_':
                left_good = False
                right_good = False
                up_good = False
                down_good = False
                if x < GRID_SIZE_X-1:
                    right_good = True
                if x > 1:
                    left_good = True
                if y < GRID_SIZE_Y-1:
                    down_good = True
                if y > 1:
                    up_good = True
                if up_good and left_good and grid[x-1][y-1] == '_':
                    possible_positions.append([x-1, y-1])
                if up_good and grid[x][y-1] == '_':
                    possible_positions.append([x, y-1])
                if right_good and up_good and grid[x+1][y-1] == '_':
                    possible_positions.append([x+1, y-1])
                if left_good and grid[x-1][y] == '_':
                    possible_positions.append([x-1, y])
                if right_good and grid[x+1][y] == '_':
                    possible_positions.append([x+1, y])
                if down_good and left_good and grid[x-1][y+1] == '_':
                    possible_positions.append([x-1, y+1])
                if down_good and grid[x][y+1] == '_':
                    possible_positions.append([x, y+1])
                if right_good and down_good and grid[x+1][y+1] == '_':
                    possible_positions.append([x+1, y+1])
    if len(possible_positions) == 0:
        return ([GRID_SIZE_X//2, GRID_SIZE_Y//2])
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_ooo_---'),
        to_line_3('--_oo_o_-'),
        to_line_3('---oo_o_-'),
        to_line_3('--_oo_o--'),
    ]
    for line_to_defo in lines:
        for pos in possible_positions:
            lines_to_check = []
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x != 0 or y != 0:
                        dir = (x, y)
                        lines_to_check.append(get_line_3(
                            grid, (pos[0]-dir[0]*5, pos[1]-dir[1]*5), 9, dir, playing_as == 'o'))
            for line in lines_to_check:
                if intersect_lines(line_to_defo, line):
                    return pos
    stress = calculate_stress(grid, playing_as)
    cp_grid = json.loads(json.dumps(grid))
    if stress < 1:
        for pos in possible_positions:
            cp_grid[pos[0]][pos[1]] = opponent
            if calculate_stress(cp_grid, opponent) >= 2:
                return pos
            cp_grid[pos[0]][pos[1]] = '_'
    elif stress < 2:
        for pos in possible_positions:
            cp_grid[pos[0]][pos[1]] = playing_as
            if calculate_stress(cp_grid, playing_as) >= 2:
                return pos
            cp_grid[pos[0]][pos[1]] = '_'
    if playing_as == 'x':
        maximizing_player = True
    else:
        maximizing_player = False
    out = minimax(grid, 2, -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                  100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, maximizing_player, True, get_scoregrid(grid, 4, 2), [], 4, 2)
    return (int(out[0]), int(out[1]))


X_BOT = None
O_BOT = bot_attempt_2

bots = [{'name': 'Human', 'func': None}, {'name': 'Bot 2-3',
                                          'func': bot_attempt_2}, {'name': 'Bot 3', 'func': bot_3}, {'name': 'Bot 4', 'func': bot_4}]

pygame.init()

#screen = pygame.display.set_mode([800/9*16, 800])
screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)

x_size, y_size = screen.get_size()

height_of_label = int((y_size-y_size*USABLE_AMOUNT_OF_SCREEN)/3)

small_font = pygame.font.SysFont("calibri", int(
    (y_size-y_size*USABLE_AMOUNT_OF_SCREEN)/3))
big_font = pygame.font.SysFont("calibri", 70)
grid = []


def setup():
    global grid
    global win, win_x_1, win_x_2, win_y_1, win_y_2
    win = '_'
    win_x_1 = None
    win_y_2 = None
    win_x_2 = None
    win_y_2 = None
    grid = []
    for x in range(GRID_SIZE_X):
        grid.append([])
        for y in range(GRID_SIZE_Y):
            grid[x].append('_')


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
            square_size*(x+1)+x_size/2-width/2-square_size*SQUARE_PADDING+1,
            square_size*(y+1)+y_size/2-height/2-square_size*SQUARE_PADDING+1,
        )

if save_replay:
    next_robot_turn_allowed = time.time()+BOT_PLAY_DELAY
else:
    next_robot_turn_allowed = time.time()+REPLAY_PLAY_DELAY


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
o_player = 3


def menu():
    global X_BOT
    global O_BOT
    global x_player
    global o_player
    global game_running
    running = True
    while running:
        mouse_down = pygame.mouse.get_pressed(num_buttons=3)[0]
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
        screen.fill((44, 47, 51))
        play_rect = pygame.Rect(
            button_1_pos[0]-button_size[0]//2, button_1_pos[1]-button_size[1]//2, button_size[0], button_size[1])
        color = (34, 37, 41)
        if play_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            color = (0, 0, 0)
            if mouse_down and mouse_was_down:
                running = False
                X_BOT = bots[x_player]['func']
                O_BOT = bots[o_player]['func']
        pygame.draw.rect(screen, color, play_rect, width=0, border_radius=10)
        #pygame.draw.rect(screen, (255, 255, 255), play_rect, width=1, border_radius=10)
        txt = 'play'
        text = big_font.render(txt, True, (153, 170, 181))
        screen.blit(text, (button_1_pos[0]-big_font.size(txt)
                    [0]//2, button_1_pos[1]-big_font.size(txt)[1]//2))
        quit_rect = pygame.Rect(
            button_2_pos[0]-button_size[0]//2, button_2_pos[1]-button_size[1]//2, button_size[0], button_size[1])
        color = (34, 37, 41)
        if quit_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
            color = (0, 0, 0)
            if mouse_down and mouse_was_down:
                game_running = False
                running = False
        pygame.draw.rect(screen, color, quit_rect, width=0, border_radius=10)
        #pygame.draw.rect(screen, (255, 255, 255), quit_rect, width=1, border_radius=10)
        txt = 'quit'
        text = big_font.render(txt, True, (153, 170, 181))
        screen.blit(text, (button_2_pos[0]-big_font.size(txt)
                    [0]//2, button_2_pos[1]-big_font.size(txt)[1]//2))

        x_toggle_button = pygame.Rect(25, 25, 75, 75)
        color = (34, 37, 41)
        if x_toggle_button.collidepoint(mouse_pos[0], mouse_pos[1]):
            color = (0, 0, 0)
            if mouse_down and not mouse_was_down:
                x_player += 1
        x_player %= len(bots)
        pygame.draw.rect(screen, color, x_toggle_button,
                         width=0, border_radius=10)
        #pygame.draw.rect(screen, (255, 255, 255), x_toggle_button, width=1, border_radius=10)
        pygame.draw.line(screen, (255, 0, 0), (30, 30), (95, 95), width=2)
        pygame.draw.line(screen, (255, 0, 0), (30, 95), (95, 30), width=2)
        txt = bots[x_player]['name']
        text = big_font.render(txt, True, (153, 170, 181))
        screen.blit(text, (125, 25+75/2-big_font.size(txt)[1]/2))

        o_toggle_button = pygame.Rect(25, 125, 75, 75)
        color = (34, 37, 41)
        if o_toggle_button.collidepoint(mouse_pos[0], mouse_pos[1]):
            color = (0, 0, 0)
            if mouse_down and not mouse_was_down:
                o_player += 1
        o_player %= len(bots)
        pygame.draw.rect(screen, color, o_toggle_button,
                         width=0, border_radius=10)
        #pygame.draw.rect(screen, (255, 255, 255), o_toggle_button, width=1, border_radius=10)
        pygame.draw.ellipse(
            screen, GREEN, pygame.Rect(30, 130, 65, 65), width=2)
        txt = bots[o_player]['name']
        text = big_font.render(txt, True, (153, 170, 181))
        screen.blit(text, (125, 125+75/2-big_font.size(txt)[1]/2))

        pygame.display.flip()
        mouse_was_down = mouse_down


def main():
    global turn_times
    global win
    global win_x_1
    global win_x_2
    global win_y_1
    global win_y_2
    global next_robot_turn_allowed
    global last_x
    global last_y
    running = True
    prevframe = time.time()
    past_fpss = []
    turn = 'x'
    clicklock = True
    turn_num = 0
    while running:
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_UP:
                    if collide_with_y != None:
                        pygame.mouse.set_pos(grid_coords[collide_with_x][collide_with_y-1][0]/2+grid_coords[collide_with_x][collide_with_y-1]
                                             [2]/2, grid_coords[collide_with_x][collide_with_y-1][1]/2+grid_coords[collide_with_x][collide_with_y-1][3]/2)
                if event.key == pygame.K_DOWN:
                    if collide_with_y != None:
                        pygame.mouse.set_pos(grid_coords[collide_with_x][collide_with_y+1][0]/2+grid_coords[collide_with_x][collide_with_y+1]
                                             [2]/2, grid_coords[collide_with_x][collide_with_y+1][1]/2+grid_coords[collide_with_x][collide_with_y+1][3]/2)
                if event.key == pygame.K_LEFT:
                    if collide_with_y != None:
                        pygame.mouse.set_pos(grid_coords[collide_with_x-1][collide_with_y][0]/2+grid_coords[collide_with_x-1][collide_with_y]
                                             [2]/2, grid_coords[collide_with_x-1][collide_with_y][1]/2+grid_coords[collide_with_x-1][collide_with_y][3]/2)
                if event.key == pygame.K_RIGHT:
                    if collide_with_y != None:
                        pygame.mouse.set_pos(grid_coords[collide_with_x+1][collide_with_y][0]/2+grid_coords[collide_with_x+1][collide_with_y]
                                             [2]/2, grid_coords[collide_with_x+1][collide_with_y][1]/2+grid_coords[collide_with_x+1][collide_with_y][3]/2)
        screen.fill((44, 47, 51))
        for line in vert_lines:
            pygame.draw.line(screen, (153, 170, 181), (line, y_size /
                             2-height/2), (line, y_size/2+height/2), width=1)
        for line in horiz_lines:
            pygame.draw.line(screen, (153, 170, 181), (x_size /
                             2-width/2, line), (x_size/2+width/2, line), width=2)
        collide_with_x = None
        collide_with_y = None
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for x in range(GRID_SIZE_X):
            for y in range(GRID_SIZE_Y):
                square_rect = pygame.Rect((grid_coords[x][y][0], grid_coords[x][y][1]), (
                    grid_coords[x][y][2]-grid_coords[x][y][0], grid_coords[x][y][3]-grid_coords[x][y][1]))
                if square_rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(screen, (35, 39, 42), square_rect)
                    collide_with_x = x
                    collide_with_y = y
                if x == last_x and y == last_y:
                    draw_width = 2
                else:
                    draw_width = 1
                if grid[x][y] == 'x':
                    pygame.draw.line(screen, RED, (grid_coords[x][y][0], grid_coords[x][y][1]), (
                        grid_coords[x][y][2], grid_coords[x][y][3]), width=draw_width)
                    pygame.draw.line(screen, RED, (grid_coords[x][y][0], grid_coords[x][y][3]), (
                        grid_coords[x][y][2], grid_coords[x][y][1]), width=draw_width)
                elif grid[x][y] == 'o':
                    pygame.draw.ellipse(
                        screen, GREEN, square_rect, width=draw_width)
        if win == '_':
            if turnbot == None:
                if pygame.mouse.get_pressed(num_buttons=3)[0] or pygame.key.get_pressed()[pygame.K_RETURN]:
                    if clicklock:
                        continue
                    clicklock = True
                    if collide_with_x == None or collide_with_y == None:
                        continue
                    if grid[collide_with_x][collide_with_y] != '_':
                        continue
                    grid[collide_with_x][collide_with_y] = turn
                    if save_replay:
                        replay.append(str(collide_with_x) +
                                      ','+str(collide_with_y))
                        # with open(replay_file, 'w') as f:
                        #    f.write(':'.join(replay))
                    last_x = collide_with_x
                    last_y = collide_with_y
                    scan_for_win(grid)
                    if win == '_':
                        if turn == 'x':
                            turn = 'o'
                        else:
                            turn = 'x'
                    if save_replay:
                        next_robot_turn_allowed = time.time()+BOT_PLAY_DELAY
                    else:
                        next_robot_turn_allowed = time.time()+REPLAY_PLAY_DELAY
                    turn_num += 1
                else:
                    clicklock = False
            else:
                if next_robot_turn_allowed <= time.time():
                    turn_num += 1
                    strikes = 0
                    while strikes < 4:
                        robot_calc_start_time = time.time()
                        coords_to_place = turnbot(grid, turn)
                        turn_times.append(time.time()-robot_calc_start_time)
                        avg = 0
                        for tim in turn_times:
                            avg += tim
                        if grid[coords_to_place[0]][coords_to_place[1]] != '_':
                            strikes += 1
                            print(
                                'Error: robot ('+turn+') attempted to make to make an illegal move. ('+str(strikes)+' strikes)')
                            print(coords_to_place)
                            continue
                        grid[coords_to_place[0]][coords_to_place[1]] = turn
                        if save_replay:
                            replay.append(str(coords_to_place[0]) +
                                          ','+str(coords_to_place[1]))
                            # with open(replay_file, 'w') as f:
                            #    f.write(':'.join(replay))
                        last_x = coords_to_place[0]
                        last_y = coords_to_place[1]
                        scan_for_win(grid)
                        constant_score_to_x = value_towards_x(grid)
                        if win == '_':
                            if turn == 'x':
                                turn = 'o'
                            else:
                                turn = 'x'
                        break
                    if save_replay:
                        next_robot_turn_allowed = time.time()+BOT_PLAY_DELAY
                    else:
                        next_robot_turn_allowed = time.time()+REPLAY_PLAY_DELAY
                    if strikes > 3:
                        win = '-'
        past_fpss.append(1/timediff)
        while len(past_fpss) > 120:
            past_fpss.pop(0)
        avg_fps = 0
        for fps in past_fpss:
            avg_fps += fps
        if win == '-':
            txt = "draw!"
            text = small_font.render(txt, True, (153, 170, 181))
            screen.blit(text, (10, 10))
        else:
            if win != '_':
                pygame.draw.line(screen, (153, 170, 181),
                                 (win_x_1, win_y_1), (win_x_2, win_y_2), width=3)
            if turn == 'x':
                pygame.draw.line(screen, (236, 65, 69), (10, 10),
                                 (height_of_label+10, height_of_label+10), width=2)
                pygame.draw.line(
                    screen, (236, 65, 69), (10, height_of_label+10), (height_of_label+10, 10), width=2)
            elif turn == 'o':
                pygame.draw.ellipse(screen, (61, 165, 96), pygame.Rect(
                    10, 10, height_of_label, height_of_label), width=2)
            if win == '_':
                txt = "'s turn "
            else:
                txt = " has won! "
            if turn == 'x':
                txt += '('+bots[x_player]['name']+')'
            elif turn == 'o':
                txt += '('+bots[o_player]['name']+')'
            text = small_font.render(txt, True, (153, 170, 181))
            screen.blit(text, (15+height_of_label, 10))

        pygame.display.flip()


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
