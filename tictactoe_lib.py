import random
import math
import sys
import subprocess
import time


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--trusted-host", "pypi.org",
                          "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", package])


INFLATED_OFFSETS = [(-2, -2), (0, -2), (2, -2), (-2, 0), (2, 0), (-2, 2), (0, 2),
                    (2, 2), (-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]

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

x_mem = None
o_mem = None

global_text = ''

replay_name_x = ''
replay_name_o = ''
replay_counter = -1
replay = ''
replay_playback = []
USABLE_AMOUNT_OF_SCREEN = 0.94
SQUARE_PADDING = 0.05
BOT_PLAY_DELAY = 0.05
REPLAY_PLAY_DELAY = 1
VERSION = 'v2.1.1'
ALLDIRS = [(-1, 1), (0, 1), (1, 1), (-1, 0),
           (1, 0), (-1, -1), (0, -1), (1, -1)]

#GRID_SIZE_X = 16*3
#GRID_SIZE_Y = 9*3

GRID_SIZE_X = 20
GRID_SIZE_Y = 20

RED = (236, 65, 69)
GREEN = (61, 165, 96)
RED_LIGHT = (242, 87, 87)
GREEN_LIGHT = (87, 242, 135)
RED_DARK = (236//2, 65//2, 69//2)
GREEN_DARK = (61//2, 165//2, 96//2)
WHITE = (246, 246, 246)
BACKGROUND = (44, 47, 51)
BACKGROUND_DARK = (35, 39, 42)
BLACK = (35//2, 39//2, 42//2)
GREY = (80, 80, 80)


def scan_for_win_and_return(grid):
    fail = False
    win = '_'
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
                    break
            if vertical_check:
                if grid[x][y] == grid[x][y+1] and grid[x][y] == grid[x][y+2] and grid[x][y] == grid[x][y+3] and grid[x][y] == grid[x][y+4]:
                    win = grid[x][y]
                    break
            if diagonal_check_upwards:
                if grid[x][y] == grid[x+1][y+1] and grid[x][y] == grid[x+2][y+2] and grid[x][y] == grid[x+3][y+3] and grid[x][y] == grid[x+4][y+4]:
                    win = grid[x][y]
                    break
            if diagonal_check_downwards:
                if grid[x][y] == grid[x+1][y-1] and grid[x][y] == grid[x+2][y-2] and grid[x][y] == grid[x+3][y-3] and grid[x][y] == grid[x+4][y-4]:
                    win = grid[x][y]
                    break
    if win == '_' and fail == False:
        win = '-'
    return win


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
        {'value': 'inf',  'line': to_line_3('---oo_oo-')},
        {'value': 'inf',  'line': to_line_3('--ooo_o--')},
        {'value': 'inf',  'line': to_line_3('xoooo_---')},
        {'value': 'inf',  'line': to_line_3('noooo_---')},
        {'value': 14,     'line': to_line_3('-_xxx__--')},
        {'value': 10,     'line': to_line_3('-_xxx_n--')},
        {'value': 14,     'line': to_line_3('--_xx_x_-')},
        {'value': 13,     'line': to_line_3('---oo_o--')},
        {'value': 12,     'line': to_line_3('-_ooo_---')},
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
    possible_positions = get_possible_positions(grid)
    if len(possible_positions) == 0:
        if return_sorted:
            yield [{'pos': [GRID_SIZE_X//2, GRID_SIZE_Y//2], 'val': 0}]
        yield ([GRID_SIZE_X//2, GRID_SIZE_Y//2])
    positions_to_go = []
    for position in possible_positions:
        eval = eval_pos_3(grid, position, playing_as)
        if eval == 'inf':
            if return_sorted:
                yield [{'pos': position, 'val': 100000000000000000000000000000000}]
            yield position
        else:
            positions_to_go.append({'pos': position, 'val': eval})
    positions_to_go = sorted(positions_to_go, key=lambda d: d['val'])
    if return_sorted:
        yield positions_to_go
    yield positions_to_go[-1]['pos']


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
    yield
    out = minimax(grid, 2, -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                  100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, maximizing_player, True, get_scoregrid(grid, 4, 2), [], 4, 2)
    yield (int(out[0]), int(out[1]))


def minimax(grid, depth, alpha, beta, maximizing_player, return_pos, original_scoregrid, placements, coeff1, coeff2):
    if depth == 0:
        return sum_up_scoregrid(update_scoregrid(grid, original_scoregrid, placements, coeff1, coeff2))
    playing_as = 'o'
    if maximizing_player:
        playing_as = 'x'
    possible_positions_with_val = next(
        bot_3(grid, playing_as, return_sorted=True))
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


def calculate_stress(grid, stress_from, return_on=1000000000000):
    #positions = get_list_of_grid(grid)
    # positions = inflate_gridlist(
    #    positions, GRID_SIZE_X-1, GRID_SIZE_Y-1, amount=2, offset_x=-3, offset_y=-3)
    lines = [
        {'line': to_line_3('_xxxx_'), 'val': 2},
        {'line': to_line_3('_xxxxo'), 'val': 1.5},
        {'line': to_line_3('oxxxx_'), 'val': 1.5},
        {'line': to_line_3('__xxx__'), 'val': 1},
        #{'line': to_line_3('_x_x_x_'), 'val': 1},
        #{'line': to_line_3('_x__xx_'), 'val': 1},
        #{'line': to_line_3('_xx__x_'), 'val': 1},
        {'line': to_line_3('o_xxx_'), 'val': 1},  # ?
        {'line': to_line_3('_x_xx_'), 'val': 1},
        {'line': to_line_3('_xxx_o'), 'val': 1},  # ?
        {'line': to_line_3('_xx_x_'), 'val': 1},
    ]
    positions = []
    total_stress = 0
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            for dir in [(1, -1), (1, 0), (1, 1), (0, 1)]:
                line_1 = get_line_3(grid, (x, y), 6, dir, stress_from == 'o')
                line_2 = get_line_3(grid, (x, y), 7, dir, stress_from == 'o')
                for stress_yes in lines:
                    if intersect_lines(stress_yes['line'], line_1) or intersect_lines(stress_yes['line'], line_2):
                        total_stress += stress_yes['val']
                    if total_stress >= return_on:
                        return total_stress
    return total_stress


def calculate_stress_2(grid, stress_from):
    to_test = []
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            if grid[x][y] != '_':
                to_test.append((x, y))
    for pos in to_test:
        pass


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


def bot_quasi_3(grid, playing_as):
    if playing_as == 'x':
        opponent = 'o'
    else:
        opponent = 'x'
    possible_positions = get_possible_positions(grid)
    if len(possible_positions) == 0:
        yield (len(grid)//2, len(grid[0])//2)
    positions_to_go = []
    for position in possible_positions:
        yield
        eval = eval_pos_3(grid, position, playing_as)
        if eval == 'inf':
            yield position
        else:
            positions_to_go.append({'pos': position, 'val': eval})
    positions_to_go = sorted(positions_to_go, key=lambda d: d['val'])
    cp_grid = json.loads(json.dumps(grid))
    opponent_stress = calculate_stress(grid, opponent)
    if opponent_stress < 1:
        for pos in possible_positions:
            yield
            cp_grid[pos[0]][pos[1]] = playing_as
            if calculate_stress(cp_grid, playing_as) >= 2:
                yield pos
            cp_grid[pos[0]][pos[1]] = '_'
        for pos in possible_positions:
            yield
            cp_grid[pos[0]][pos[1]] = opponent
            if calculate_stress(cp_grid, opponent) >= 2:
                yield pos
            cp_grid[pos[0]][pos[1]] = '_'

    yield positions_to_go[-1]['pos']


def bot_4(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    possible_positions = get_possible_positions(grid)
    if len(possible_positions) == 1:
        yield possible_positions[0]
    random.shuffle(possible_positions)
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_xxx_---'),
        to_line_3('--_xx_x_-'),
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
                    yield pos
    stress = calculate_stress(grid, opponent, return_on=2)
    cp_grid = json.loads(json.dumps(grid))
    if stress < 1:
        for pos in possible_positions:
            yield
            cp_grid[pos[0]][pos[1]] = playing_as
            if calculate_stress(cp_grid, playing_as, return_on=2) >= 2:
                yield pos
            cp_grid[pos[0]][pos[1]] = '_'
    for pos in possible_positions:
        yield
        cp_grid[pos[0]][pos[1]] = opponent
        if calculate_stress(cp_grid, opponent, return_on=2) >= 2:
            yield pos
        cp_grid[pos[0]][pos[1]] = '_'
    if playing_as == 'x':
        maximizing_player = True
    else:
        maximizing_player = False
    yield
    out = minimax(grid, 2, -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                  100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, maximizing_player, True, get_scoregrid(grid, 4, 2), [], 4, 2)
    yield (int(out[0]), int(out[1]))


def bot_5(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    cp_grid = json.loads(json.dumps(grid))
    possible_positions = get_possible_positions(grid)
    random.shuffle(possible_positions)
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_xxx_---'),
        to_line_3('--_xx_x_-'),
        to_line_3('-_ooo_---'),
        to_line_3('--_oo_o_-'),
        to_line_3('---oo_o_-'),
        to_line_3('--_oo_o--'),
    ]
    for line_to_defo in lines:
        for pos in possible_positions:
            lines_to_check = []
            for x in range(-1, 2):
                yield
                for y in range(-1, 2):
                    if x != 0 or y != 0:
                        dir = (x, y)
                        lines_to_check.append(get_line_3(
                            grid, (pos[0]-dir[0]*5, pos[1]-dir[1]*5), 9, dir, playing_as == 'o'))

            for line in lines_to_check:
                if intersect_lines(line_to_defo, line):
                    yield pos
    yield
    quiq = Quiqfinder(grid, playing_as)
    if quiq != None:
        yield quiq
    yield
    quiq = Quiqfinder(grid, opponent)
    if quiq != None:
        yield quiq
    for pos in possible_positions:
        yield
        x = pos[0]
        y = pos[1]
        cp_grid[x][y] = playing_as
        if Quiqfinder(cp_grid, playing_as) != None:
            yield pos
        cp_grid[x][y] = '_'
    for pos in possible_positions:
        yield
        x = pos[0]
        y = pos[1]
        cp_grid[x][y] = opponent
        if calculate_stress(cp_grid, opponent, return_on=2) >= 2:
            yield pos
        cp_grid[x][y] = '_'
    for pos in possible_positions:
        yield
        x = pos[0]
        y = pos[1]
        cp_grid[x][y] = opponent
        if Quiqfinder(cp_grid, opponent) != None:
            yield pos
        cp_grid[x][y] = '_'
    if playing_as == 'x':
        maximizing_player = True
    else:
        maximizing_player = False
    yield
    out = minimax(grid, 2, -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                  100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, maximizing_player, True, get_scoregrid(grid, 4, 2), [], 4, 2)
    yield (int(out[0]), int(out[1]))


def get_possible_positions(grid):
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
                if x > 0:
                    left_good = True
                if y < GRID_SIZE_Y-1:
                    down_good = True
                if y > 0:
                    up_good = True
                if up_good and left_good and grid[x-1][y-1] == '_':
                    if (x-1, y-1) not in possible_positions:
                        possible_positions.append((x-1, y-1))
                if up_good and grid[x][y-1] == '_':
                    if (x, y-1) not in possible_positions:
                        possible_positions.append((x, y-1))
                if right_good and up_good and grid[x+1][y-1] == '_':
                    if (x+1, y-1) not in possible_positions:
                        possible_positions.append((x+1, y-1))
                if left_good and grid[x-1][y] == '_':
                    if (x-1, y) not in possible_positions:
                        possible_positions.append((x-1, y))
                if right_good and grid[x+1][y] == '_':
                    if (x+1, y) not in possible_positions:
                        possible_positions.append((x+1, y))
                if down_good and left_good and grid[x-1][y+1] == '_':
                    if (x+1, y+1) not in possible_positions:
                        possible_positions.append((x-1, y+1))
                if down_good and grid[x][y+1] == '_':
                    if (x, y+1) not in possible_positions:
                        possible_positions.append((x, y+1))
                if right_good and down_good and grid[x+1][y+1] == '_':
                    if (x+1, y+1) not in possible_positions:
                        possible_positions.append((x+1, y+1))
    if len(possible_positions) == 0:
        return [(GRID_SIZE_X//2, GRID_SIZE_Y//2)]
    return possible_positions


def Kabir(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    possible_positions = get_possible_positions(grid)
    if len(possible_positions) == 1:
        yield possible_positions[0]
    lines = [
        # to_line_3('---xx_xx-'),
        to_line_3('-xxxx_---'),
        to_line_3('--xxx_x--'),
        to_line_3('--xoo_oo-'),
        to_line_3('---oo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_ooo_---'),
    ]
    for line_to_defo in lines:
        for pos in possible_positions:
            lines_to_check = []
            for x in range(-1, 2):
                yield
                for y in range(-1, 2):
                    if x != 0 or y != 0:
                        dir = (x, y)
                        lines_to_check.append(get_line_3(
                            grid, (pos[0]-dir[0]*5, pos[1]-dir[1]*5), 9, dir, playing_as == 'o'))
            for line in lines_to_check:
                if intersect_lines(line_to_defo, line):
                    yield pos
    # return random.choice(possible_positions)
    if playing_as == 'x':
        maximizing_player = True
    else:
        maximizing_player = False
    yield
    out = minimax(grid, 1, -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                  100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, maximizing_player, True, get_scoregrid(grid, 4, 2), [], 4, 2)
    yield (int(out[0]), int(out[1]))


def stress_depth_search(grid, placing_as, depth=2, return_move=True):
    cp_grid = json.loads(json.dumps(grid))
    opponent = 'x'
    if placing_as == 'x':
        opponent = 'o'
    if depth == 0:
        return {'x': calculate_stress(grid, 'x'), 'o': calculate_stress(grid, 'o')}
    if return_move:
        ress = []
    tot = {'x': 0, 'o': 0}
    possible_poss = bot_3(grid, placing_as, return_sorted=True)
    possible_poss.reverse()
    possible_positions = []
    for pos in possible_poss:
        possible_positions.append(pos['pos'])
    for pos in possible_positions:
        cp_grid[pos[0]][pos[1]] = placing_as
        if calculate_stress(cp_grid, placing_as) >= 2:
            if return_move:
                return pos
            return {placing_as: 2, opponent: calculate_stress(grid, opponent)}
        else:
            search = stress_depth_search(cp_grid, opponent, depth-1, False)
            if return_move:
                ress.append({'pos': pos, 'res': search})
            tot['x'] += search['x']
            tot['o'] += search['o']
        cp_grid[pos[0]][pos[1]] = '_'
    if return_move:
        ress = sorted(ress, key=lambda d: d['res']['x']-d['res']['o'])
        if placing_as == 'x':
            return ress[-1]['pos']
        else:
            return ress[0]['pos']
    return tot


def win_elimination_depth_search(grid, playing_as, placing_as, depth, return_whole_nogo):
    playing_opponent = 'x'
    if playing_as == 'x':
        playing_opponent = 'o'
    placing_opponent = 'x'
    if placing_as == 'x':
        placing_opponent = 'o'
    cp_grid = json.loads(json.dumps(grid))
    no_go = []
    #poss = bot_3(grid, placing_as, return_sorted=True)
    # poss.reverse()
    # for pos_and_val in poss:
    #pos = pos_and_val['pos']
    for pos in get_possible_positions(grid):
        cp_grid[pos[0]][pos[1]] = placing_as
        if playing_as == placing_as:
            if depth != 0:
                if len(win_elimination_depth_search(cp_grid, placing_as, placing_opponent, depth-1, False)) != 0:
                    no_go.append(pos)
                    if not return_whole_nogo:
                        return no_go
        elif scan_for_win_and_return(cp_grid) == playing_opponent:
            no_go.append(pos)
            if not return_whole_nogo:
                return no_go
        else:
            if depth != 0:
                if len(win_elimination_depth_search(cp_grid, placing_as, placing_opponent, depth-1, False)) != 0:
                    no_go.append(pos)
                    if not return_whole_nogo:
                        return no_go
        cp_grid[pos[0]][pos[1]] = '_'
    return no_go


def invertDir(dir):
    return (-dir[0], -dir[1])


def dirToStr(dir):
    return str(dir[0])+'x'+str(dir[1])


def Quiqfinder(grid, placing_as):
    patterns = [
        #      placing: V
        to_line_3('-_xxx_o--'),
        to_line_3('--_xx_xo-'),
        to_line_3('---_x_xxo'),
        to_line_3('-oxxx__--'),
        to_line_3('-x_xx_o--'),
        to_line_3('--x_x_xo-'),
        to_line_3('---x__xxo'),
        to_line_3('oxxx__---'),
        to_line_3('-xx_x_o--'),
        to_line_3('--xx__xo-'),
        to_line_3('-oxx__x--'),
        to_line_3('oxx_x_---'),
        to_line_3('-__xx___-'),
        to_line_3('--__x_x__'),
        to_line_3('-_x_x__--'),
        to_line_3('--_x__x_-'),
        to_line_3('-_xx___--'),
        # to_line_3('_x_x___--'),
        # to_line_3('--_x___x_'),
        # to_line_3('_xx____--'),
        # to_line_3('_x__x__--'),
        # to_line_3('-_x___x_-'),
    ]
    #x_s = list(range(len(grid)))
    #y_s = list(range(len(grid[0])))
    # random.shuffle(x_s)
    # random.shuffle(y_s)
    # for x in x_s:
    #    for y in y_s:
    for pos in get_inflated_pos(grid):
        x, y = pos
        matched = {}
        for dir in ALLDIRS:
            matched[dirToStr(dir)] = None
        cnt = 0
        for dir in ALLDIRS:
            line = get_line_3(
                grid, (x-dir[0]*5, y-dir[1]*5), 9, dir, placing_as == 'o')
            for i, pattern in enumerate(patterns):
                if matched[dirToStr(invertDir(dir))] != i:
                    if intersect_lines(pattern, line):
                        matched[dirToStr(dir)] = i
                        cnt += 1
                        if cnt >= 2:
                            return (x, y)
    return None


def calculate_grid_intersection_values(grid, calculating_for):
    value_grid = []
    for x in range(len(grid)):
        value_grid.append([1]*len(grid[0]))
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            for dir in [(1, 1), (1, 0), (1, -1), (0, -1)]:
                line = get_line_3(grid, (x, y), 5, dir, False)
                x_count = 1
                cnt = 0
                for element in line:
                    if element == calculating_for:
                        x_count += 1
                        cnt += 1
                        continue
                    elif element == '_':
                        cnt += 1
                        continue
                    else:
                        break
                if cnt == 5 and x_count != 0:
                    for i in range(5):
                        if line[i] == '_':
                            value_grid[x+dir[0]*i][y+dir[1]*i] *= x_count
                            value_grid[x+dir[0]*i][y+dir[1]*i] *= x_count
                        else:
                            value_grid[x+dir[0]*i][y+dir[1]*i] = 0
    return value_grid


def bot_proto_6(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    cp_grid = json.loads(json.dumps(grid))
    possible_positions = get_possible_positions(grid)
    random.shuffle(possible_positions)
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_xxx_---'),
        to_line_3('--_xx_x_-'),
        to_line_3('-_ooo_---'),
        to_line_3('--_oo_o_-'),
        to_line_3('---oo_o_-'),
        to_line_3('--_oo_o--'),
    ]
    for line_to_defo in lines:
        yield
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
                    yield pos
    poss = []
    for x, line in enumerate(calculate_grid_intersection_values(grid, 'x')):
        yield
        for y, col in enumerate(line):
            poss.append({'pos': (x, y), 'val': col})
    for x, line in enumerate(calculate_grid_intersection_values(grid, 'o')):
        yield
        for y, col in enumerate(line):
            poss.append({'pos': (x, y), 'val': col})
    poss = sorted(poss, key=lambda d: d['val'])
    poss.reverse()
    yield
    positions_to_go = []
    for pos in poss:
        if pos['val'] >= poss[0]['val']:
            positions_to_go.append(pos['pos'])
        else:
            break
    yield random.choice(positions_to_go)


def over_dedicated_bot(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    cp_grid = json.loads(json.dumps(grid))
    possible_positions = get_possible_positions(grid)
    random.shuffle(possible_positions)
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_xxx_---'),
        to_line_3('--_xx_x_-'),
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
                    yield pos
    if playing_as == 'x':
        global x_mem
        my_mem = x_mem
    if playing_as == 'o':
        global o_mem
        my_mem = o_mem
    if my_mem != None:
        for i in range(5):
            pos_x = my_mem['start_x']+my_mem['dir_x']*i
            pos_y = my_mem['start_y']+my_mem['dir_y']*i
            if get_of_grid_3(grid, (pos_x, pos_y)) not in [playing_as, '_']:
                my_mem = None
                break
    yield
    if my_mem == None:
        fives = []
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                for dir in [(1, 1), (1, 0), (1, -1), (0, -1)]:
                    line = get_line_3(grid, (x, y), 5, dir, False)
                    x_count = 0
                    cnt = 0
                    for element in line:
                        if element == playing_as:
                            x_count += 1
                            cnt += 1
                            continue
                        elif element == '_':
                            cnt += 1
                            continue
                        else:
                            break
                    if cnt == 5 and x_count != 0:
                        # print('yes')
                        fives.append(
                            {'start_x': x, 'start_y': y, 'dir_x': dir[0], 'dir_y': dir[1], 'val': x_count})
        if len(fives) == 0:
            yield random.choice(get_possible_positions(grid))
        fives = sorted(fives, key=lambda d: d['val'])
        my_mem = fives[-1]
    positions_to_go = []
    yield
    for i in range(5):
        pos_x_left = my_mem['start_x']+my_mem['dir_x']*(i-1)
        pos_y_left = my_mem['start_y']+my_mem['dir_y']*(i-1)
        pos_x = my_mem['start_x']+my_mem['dir_x']*i
        pos_y = my_mem['start_y']+my_mem['dir_y']*i
        pos_x_right = my_mem['start_x']+my_mem['dir_x']*(i+1)
        pos_y_right = my_mem['start_y']+my_mem['dir_y']*(i+1)
        if i == 0:
            # and get_of_grid_3(grid, (pos_x_right, pos_y_right)) == playing_as:
            if get_of_grid_3(grid, (pos_x, pos_y)) == '_':
                positions_to_go.append((pos_x, pos_y))
        elif i == 4:
            # and get_of_grid_3(grid, (pos_x_left, pos_y_left)) == playing_as:
            if get_of_grid_3(grid, (pos_x, pos_y)) == '_':
                positions_to_go.append((pos_x, pos_y))
        elif i == 2:
            if get_of_grid_3(grid, (my_mem['start_x']+my_mem['dir_x']*0, my_mem['start_y']+my_mem['dir_y']*0)) != '_' and get_of_grid_3(grid, (my_mem['start_x']+my_mem['dir_x']*4, my_mem['start_y']+my_mem['dir_y']*4)) != '_':
                positions_to_go.append((pos_x, pos_y))

        else:
            if get_of_grid_3(grid, (pos_x, pos_y)) == '_' and (get_of_grid_3(grid, (pos_x_left, pos_y_left)) == playing_as or get_of_grid_3(grid, (pos_x_right, pos_y_right)) == playing_as):
                positions_to_go.append((pos_x, pos_y))
    yield random.choice(positions_to_go)


def get_inflated_pos(grid):
    out = []
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            if get_of_grid_3(grid, (x, y)) != '_':
                continue
            for offset in INFLATED_OFFSETS:
                x_offset = offset[0]
                y_offset = offset[1]
                #print(x+x_offset, y+y_offset)
                if get_of_grid_3(grid, (x+x_offset, y+y_offset)) in ['x', 'o']:
                    out.append((x, y))
                    break
            # for x_offset in range(-2, 3):
            #    for y_offset in range(-2, 3):
            #        if x_offset == 0 and y_offset == 0:
            #            continue
            #        if get_of_grid_3(grid, (x+x_offset, y+y_offset)) in ['x', 'o']:
            #            out.append((x, y))
            #            done = True
            #            break
            #    if done:
            #        break
    # print(out)
    if len(out) == 0:
        out.append((len(grid)//2, len(grid[0])//2))
    return out


def easy_bot(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    cp_grid = json.loads(json.dumps(grid))
    possible_positions = get_possible_positions(grid)
    random.shuffle(possible_positions)
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_xxx_---'),
        to_line_3('--_xx_x_-'),
        to_line_3('-_ooo_---'),
        to_line_3('--_oo_o_-'),
        to_line_3('---oo_o_-'),
        to_line_3('--_oo_o--'),
    ]
    for line_to_defo in lines:
        yield
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
                    yield pos
    yield random.choice(get_inflated_pos(grid))


def manzoh_bot(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    cp_grid = json.loads(json.dumps(grid))
    possible_positions = get_possible_positions(grid)
    random.shuffle(possible_positions)
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_xxx_---'),
        to_line_3('--_xx_x_-'),
        to_line_3('-_ooo_---'),
        to_line_3('--_oo_o_-'),
        to_line_3('---oo_o_-'),
        to_line_3('--_oo_o--'),
    ]
    for line_to_defo in lines:
        yield
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
                    yield pos
    yield
    quiq = Quiqfinder(grid, opponent)
    if quiq != None:
        yield quiq
    yield
    corners = [(0, 0), (0, len(grid[0])-1), (len(grid)-1, 0),
               (len(grid)-1, len(grid[0])-1)]
    random.shuffle(corners)
    for corner in corners:
        if grid[corner[0]][corner[1]] == '_':
            yield corner
    yield random.choice(get_inflated_pos(grid))


def meh_bot(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_xxx_---'),
        to_line_3('--_xx_x_-'),
        to_line_3('-_ooo_---'),
        to_line_3('--_oo_o_-'),
        to_line_3('---oo_o_-'),
        to_line_3('--_oo_o--'),
    ]
    for line_to_defo in lines:
        for pos in get_possible_positions(grid):
            lines_to_check = []
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x != 0 or y != 0:
                        dir = (x, y)
                        lines_to_check.append(get_line_3(
                            grid, (pos[0]-dir[0]*5, pos[1]-dir[1]*5), 9, dir, playing_as == 'o'))
            for line in lines_to_check:
                if intersect_lines(line_to_defo, line):
                    yield pos
    quiq = Quiqfinder(grid, playing_as)
    if quiq != None:
        print('self quiq')
        yield quiq
    yield
    quiq = Quiqfinder(grid, opponent)
    if quiq != None:
        print('opponent quiq')
        yield quiq
    yield
    yield random.choice(get_inflated_pos(grid))


def find_instinctual_moves(grid, placing_as):
    positions = []
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('-__xx___-'),
        to_line_3('--__x_x__'),
        to_line_3('x_ooo__--'),
        to_line_3('x_ooo_---'),
        to_line_3('-xooo__--'),
        to_line_3('__ooo__--'),
    ]
    for pos in get_possible_positions(grid):
        done = False
        for dir in ALLDIRS:
            line = get_line_3(grid, pos, 9, dir, placing_as == 'o')
            for pattern in lines:
                if intersect_lines(line, pattern):
                    positions.append(pos)
                    done = True
                    break
            if done:
                break
    return positions


def get_all_grid_poss(x_len, y_len):
    for x in range(x_len):
        for y in range(y_len):
            yield (x, y)


def determine_win(grid, placing_as, testing_for, depth):
    opponent_placing = 'x'
    opponent_testing = 'x'
    if placing_as == 'x':
        opponent_placing = 'o'
    if testing_for == 'x':
        opponent_testing = 'o'
    if depth == 0:
        lines = [
            to_line_3('_xxxx-'),
            to_line_3('__xxx_'),
            to_line_3('xxx_x-'),
            to_line_3('xx_xx-'),
            to_line_3('_xx_x_'),
        ]
        for pos in get_all_grid_poss(len(grid), len(grid[0])):
            for dir in ALLDIRS:
                line = get_line_3(grid, pos, 6, dir, placing_as == 'o')
                for pattern in lines:
                    if intersect_lines(line, pattern):
                        return True
        return False
    else:
        cp_grid = json.loads(json.dumps(grid))
        im = find_instinctual_moves(grid, placing_as)
        if placing_as == testing_for:
            if len(im) == 0:
                return False
            for move in im:
                cp_grid[move[0]][move[1]] = placing_as
                if determine_win(grid, opponent_placing, testing_for, depth-1):
                    return True
                cp_grid[move[0]][move[1]] = '_'
            return False
        else:
            if len(im) == 0:
                return False
            for move in im:
                cp_grid[move[0]][move[1]] = placing_as
                if not determine_win(grid, opponent_placing, testing_for, depth):
                    return False
                cp_grid[move[0]][move[1]] = '_'
            return True


def bot_7(grid, playing_as):
    global global_text
    global_text = ''
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    cp_grid = json.loads(json.dumps(grid))
    possible_positions = get_possible_positions(grid)
    random.shuffle(possible_positions)
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        to_line_3('noooo_---'),
        to_line_3('x-ooo_o--'),
        to_line_3('--ooo_o--'),
        to_line_3('-_xxx_---'),
        to_line_3('--_xx_x_-'),
        to_line_3('-_ooo_---'),
        to_line_3('--_oo_o_-'),
        to_line_3('---oo_o_-'),
        to_line_3('--_oo_o--'),
    ]
    for line_to_defo in lines:
        yield
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
                    yield pos
    yield
    cp_grid = json.loads(json.dumps(grid))
    # for pos in get_all_grid_poss(len(grid), len(grid[0])):
    #    yield
    #    if grid[pos[0]][pos[1]] == '_':
    #        cp_grid[pos[0]][pos[1]] = playing_as
    #        if determine_win(grid, playing_as, playing_as, 4):
    #            yield pos
    #        cp_grid[pos[0]][pos[1]] = '_'
    quiq = Quiqfinder(grid, playing_as)
    if quiq != None:
        yield quiq
    quiq = Quiqfinder(grid, opponent)
    if quiq != None:
        yield quiq
    poss = get_inflated_pos(grid)
    # print(poss)
    i = 0
    quiq_time = 0
    stress_time = 0

    for pos in poss:
        i += 1
        global_text = str(i)+' / '+str(len(poss)*4)
        print(str(i)+' / '+str(len(poss)*4))
        yield global_text
        if grid[pos[0]][pos[1]] == '_':
            cp_grid[pos[0]][pos[1]] = playing_as
            if calculate_stress(cp_grid, playing_as, return_on=1) >= 1 and Quiqfinder(cp_grid, playing_as) != None:
                print('epic opportunity found')
                yield pos
            cp_grid[pos[0]][pos[1]] = '_'
    for pos in poss:
        i += 1
        global_text = str(i)+' / '+str(len(poss)*4)
        print(str(i)+' / '+str(len(poss)*4))
        yield global_text
        if grid[pos[0]][pos[1]] == '_':
            cp_grid[pos[0]][pos[1]] = opponent
            if calculate_stress(cp_grid, opponent, return_on=1) >= 1 and Quiqfinder(cp_grid, opponent) != None:
                print('danger found')
                yield pos
            cp_grid[pos[0]][pos[1]] = '_'
    for pos in poss:
        i += 1
        global_text = str(i)+' / '+str(len(poss)*4)
        print(str(i)+' / '+str(len(poss)*4))
        yield global_text
        x = pos[0]
        y = pos[1]
        cp_grid[x][y] = playing_as
        if Quiqfinder(cp_grid, playing_as) != None:
            yield pos
        cp_grid[x][y] = '_'
    for pos in poss:
        i += 1
        global_text = str(i)+' / '+str(len(poss)*4)
        print(str(i)+' / '+str(len(poss)*4))
        yield global_text
        x = pos[0]
        y = pos[1]
        cp_grid[x][y] = opponent
        if calculate_stress(cp_grid, opponent, return_on=2) >= 2:
            yield pos
        cp_grid[x][y] = '_'

    bot = bot_proto_6(grid, playing_as)
    while True:
        yield next(bot)
    # yield next(bot_3(grid, playing_as))
