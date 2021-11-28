import random
import math
import sys
import subprocess


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--trusted-host", "pypi.org",
                          "--trusted-host", "pypi.python.org", "--trusted-host", "files.pythonhosted.org", package])


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
replay_counter = -1
replay = ''
replay_playback = []
USABLE_AMOUNT_OF_SCREEN = 0.94
SQUARE_PADDING = 0.05
BOT_PLAY_DELAY = 0.1
REPLAY_PLAY_DELAY = 0.5
VERSION = 'v1.8'

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
        {'line': to_line_3('_xxxx_'), 'val': 2},
        {'line': to_line_3('_xxxxo'), 'val': 1.5},
        {'line': to_line_3('oxxxx_'), 'val': 1.5},
        {'line': to_line_3('__xxx__'), 'val': 1},
        {'line': to_line_3('_x_x_x_'), 'val': 1},
        {'line': to_line_3('_x__xx_'), 'val': 1},
        {'line': to_line_3('_xx__x_'), 'val': 1},
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


def bot_4(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    possible_positions = get_possible_positions(grid)
    if len(possible_positions) == 1:
        return possible_positions[0]
    random.shuffle(possible_positions)
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


def bot_5(grid, playing_as):
    opponent = 'x'
    if playing_as == 'x':
        opponent = 'o'
    cp_grid = json.loads(json.dumps(grid))
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
                    possible_positions.append((x-1, y-1))
                if up_good and grid[x][y-1] == '_':
                    possible_positions.append((x, y-1))
                if right_good and up_good and grid[x+1][y-1] == '_':
                    possible_positions.append((x+1, y-1))
                if left_good and grid[x-1][y] == '_':
                    possible_positions.append((x-1, y))
                if right_good and grid[x+1][y] == '_':
                    possible_positions.append((x+1, y))
                if down_good and left_good and grid[x-1][y+1] == '_':
                    possible_positions.append((x-1, y+1))
                if down_good and grid[x][y+1] == '_':
                    possible_positions.append((x, y+1))
                if right_good and down_good and grid[x+1][y+1] == '_':
                    possible_positions.append((x+1, y+1))
    if len(possible_positions) == 0:
        return (GRID_SIZE_X//2, GRID_SIZE_Y//2)
    lines = [
        to_line_3('---xx_xx-'),
        to_line_3('--xxx_x--'),
        to_line_3('-xxxx_---'),
        to_line_3('--xoo_oo-'),
        to_line_3('-xooo_o--'),
        to_line_3('xoooo_---'),
        # to_line_3('x-ooo_o--'),
        # to_line_3('--ooo_o--'),
        # to_line_3('--_xx_x_-'),
        # to_line_3('-_xxx__--'),
        # to_line_3('-_ooo__--'),
        # to_line_3('-_ooo_---'),
        # to_line_3('--_oo_o_-'),
        # to_line_3('---oo_o_-'),
        # to_line_3('--_oo_o--'),
    ]
    random.shuffle(possible_positions)
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
    #stress_from_me = calculate_stress(grid, playing_as)
    #stress_from_opponent = calculate_stress(grid, playing_as)
    threat_moves = []
    threatened_moves = []
    for pos in possible_positions:
        cp_grid[pos[0]][pos[1]] = playing_as
        calc = calculate_stress(cp_grid, playing_as)
        threat_moves.append({'pos': pos, 'val': calc})
        if calc >= 2:
            return pos
        cp_grid[pos[0]][pos[1]] = '_'
    for pos in possible_positions:
        cp_grid[pos[0]][pos[1]] = opponent
        calc = calculate_stress(cp_grid, opponent)
        threatened_moves.append({'pos': pos, 'val': calc})
        cp_grid[pos[0]][pos[1]] = '_'
    threat_moves = sorted(threat_moves, key=lambda d: d['val'])
    threatened_moves = sorted(threatened_moves, key=lambda d: d['val'])
    moves = []
    if threat_moves[-1]['val'] >= 2:
        for move in threat_moves:
            if move['val'] == threat_moves[-1]['val']:
                moves.append(move['pos'])
        return random.choice(moves)
    elif threatened_moves[-1]['val'] >= 2:
        for move in threatened_moves:
            if move['val'] == threatened_moves[-1]['val']:
                moves.append(move['pos'])
        return random.choice(moves)
    elif threatened_moves[-1]['val'] >= 1.5:
        for move in threatened_moves:
            if move['val'] == threatened_moves[-1]['val']:
                moves.append(move['pos'])
        return random.choice(moves)
    # elif threat_moves[-1]['val'] >= 1:
    #    for move in threat_moves:
    #        if move['val'] == threat_moves[-1]['val']:
    #            moves.append(move['pos'])
    #    return random.choice(moves)
    if playing_as == 'x':
        maximizing_player = True
    else:
        maximizing_player = False
    out = minimax(grid, 2, -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                  100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, maximizing_player, True, get_scoregrid(grid, 4, 2), [], 4, 2)
    return (int(out[0]), int(out[1]))


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
                if x > 1:
                    left_good = True
                if y < GRID_SIZE_Y-1:
                    down_good = True
                if y > 1:
                    up_good = True
                if up_good and left_good and grid[x-1][y-1] == '_':
                    possible_positions.append((x-1, y-1))
                if up_good and grid[x][y-1] == '_':
                    possible_positions.append((x, y-1))
                if right_good and up_good and grid[x+1][y-1] == '_':
                    possible_positions.append((x+1, y-1))
                if left_good and grid[x-1][y] == '_':
                    possible_positions.append((x-1, y))
                if right_good and grid[x+1][y] == '_':
                    possible_positions.append((x+1, y))
                if down_good and left_good and grid[x-1][y+1] == '_':
                    possible_positions.append((x-1, y+1))
                if down_good and grid[x][y+1] == '_':
                    possible_positions.append((x, y+1))
                if right_good and down_good and grid[x+1][y+1] == '_':
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
        return possible_positions[0]
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
                for y in range(-1, 2):
                    if x != 0 or y != 0:
                        dir = (x, y)
                        lines_to_check.append(get_line_3(
                            grid, (pos[0]-dir[0]*5, pos[1]-dir[1]*5), 9, dir, playing_as == 'o'))
            for line in lines_to_check:
                if intersect_lines(line_to_defo, line):
                    return pos
    # return random.choice(possible_positions)
    if playing_as == 'x':
        maximizing_player = True
    else:
        maximizing_player = False
    out = minimax(grid, 1, -100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000,
                  100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000, maximizing_player, True, get_scoregrid(grid, 4, 2), [], 4, 2)
    return (int(out[0]), int(out[1]))


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
