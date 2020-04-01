import sys
import json
import math

from search.util import print_move, print_boom, print_board


def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)
        board_dict = input(data)
        full_board = full_board_dict(board_dict)
        print_board(full_board)
        play(board_dict['white'], board_dict['black'])
        full_board = full_board_dict(board_dict)
        print_board(full_board)

    # TODO: find and print winning action sequence

def play(white, black):
    while (len(white) != 0 or len(black) != 0):
        piece_stack, piece, n_enemy, enemy = nearest_pair(white, black)
        goal = optimal_position(black, len(white))
        nearest_pairs = nearest_location(white, goal)
        nearest_pairs = nearest_pairs.pop()
        piece = nearest_pairs[0]
        goal = nearest_pairs[-1][-1]
        optimal_path = path(piece, goal, black)

        piece_value = white.pop(piece)
        possible_move = check_move(piece, optimal_path[1])
        piece = move(piece, possible_move, piece_stack)
        white.update({piece: piece_value})
        area_explosion = boom_area(piece)

        if (piece == goal):
            if boomable(area_explosion, enemy):
                white_list = boom_link(piece, white)
                black_list = boom_link(piece, black)

                for i in white_list:
                    white.pop(i)
                for j in black_list:
                    black.pop(j)

                white.pop(piece)
                print_boom(piece[0], piece[1])
                continue

    return

# Input board pieces into nested dictionary
def input(data):
    board_dict = dict()

    for i in data:
        i_dict = dict()
        coordinates = data.get(i)
        for j in coordinates:
            n,x,y = j
            i_dict[(x,y)] = str(n)+i[0]
        board_dict[i] = i_dict

    return board_dict

# Simplify board_dict into a single dictionary for print_board
def full_board_dict(board_dict):
    full_board = dict()
    for i in board_dict:
        pieces = board_dict.get(i)
        full_board.update(pieces)

    return full_board

# Move action
def move(piece, possible_move, n_piece, n_distance = 1):
    x_a,y_a = piece
    x_b,y_b = piece
    x2,y2 = possible_move
    direction_x = 0
    direction_y = 0

    if (direction(possible_move) == 'x'):
        if x2 > 0:
            direction_x = 1
        elif x2 < 0:
            direction_x = -1

        if (direction_x != 0) and ((x_a + direction_x) in range(8)):
            x_b = x_a + direction_x
            x2 -= direction_x

    else:
        if y2 > 0:
            direction_y = 1
        elif y2 < 0:
            direction_y = -1

        if (direction_y != 0) and ((y_a + direction_y) in range(8)):
            y_b = y_b + direction_y
            y2 -= direction_y

    if (x_a != x_b or y_a != y_b):
        print_move(n_piece, x_a, y_a, x_b, y_b)

    return (x_b, y_b)

def backtracking(path, previous_coordinates, visited, previous):
    backtrack = previous_coordinates
    backtrack_list = []
    if (previous_coordinates not in path):
        while(backtrack not in path):
            backtrack_list.append(backtrack)
            backtrack = previous[visited.index(previous_coordinates)]

            n = 0
            for i in reversed(backtrack_list):
                path[(len(path)-len(backtrack_list)) + n] = i
                n += 1

    else:
        while(len(path)-1 > path.index(previous_coordinates)):
            path.pop()

    return path


def path(piece, goal, black):
    queue = []
    steps = []
    previous = []
    visited = []
    path = []
    dest = []

    possible_move = check_move(piece, goal)
    coordinates = piece
    queue = next_move(queue, coordinates, goal, black)
    queue.sort(reverse = True)
    previous.append(None)
    visited.append(coordinates)
    steps.append(0)
    path.append(coordinates)
    previous_coordinates = coordinates
    while(len(queue) != 0):
        if (path[-1] == goal):
            break
        node = queue.pop()
        previous_coordinates = node[1]
        coordinates = node[-1]
        if (coordinates not in visited):
            previous.append(previous_coordinates)
            visited.append(coordinates)
            step = visited.index(previous_coordinates)
            num_steps = steps[step]+1
            steps.append(num_steps)

            # backtracking
            path = backtracking(path, previous_coordinates,
                    visited, previous)
            path.append(coordinates)
            queue = next_move(queue, coordinates, goal, black)

        else:
            old_step = steps[visited.index(coordinates)]
            new_step = steps[visited.index(previous_coordinates)]+1
            if (new_step < old_step):
                previous[visited.index(coordinates)] = previous_coordinates
                steps[visited.index(coordinates)] = new_step
                path_replace = path.index(previous_coordinates)
                path = backtracking(path, previous_coordinates,
                        visited, previous)
                path.append(coordinates)
                queue = next_move(queue, coordinates, goal, black)

            elif (new_step > old_step):
                previous_coordinates = previous[visited.index(coordinates)]
                if (coordinates not in path):
                    path = backtracking(path, previous_coordinates,
                            visited, previous)
                    path.append(coordinates)

                    queue = next_move(queue, coordinates, goal, black)

        queue.sort(reverse = True)

    return path


def next_move(queue, coordinates, goal_coordinates, black):

    # right
    if (coordinates[0]+1 in range(8)):
        right = (coordinates[0]+1, coordinates[1])
        if (right not in black):
            possible_move_right = check_move(right, goal_coordinates)
            num_steps = (turn_positive(possible_move_right[0]) +
                        turn_positive(possible_move_right[1]))
            queue.append([num_steps, coordinates, right])

    # left
    if (coordinates[0]-1 in range(8)):
        left = (coordinates[0]-1, coordinates[1])
        if (left not in black):
            possible_move_left = check_move(left, goal_coordinates)
            num_steps = (turn_positive(possible_move_left[0]) +
                        turn_positive(possible_move_left[1]))
            queue.append([num_steps, coordinates, left])

    # up
    if ((coordinates[1]+1) in range(8)):
        up = (coordinates[0], coordinates[1]+1)
        if (up not in black):
            possible_move_up = check_move(up, goal_coordinates)
            num_steps = (turn_positive(possible_move_up[0]) +
                        turn_positive(possible_move_up[1]))
            queue.append([num_steps, coordinates, up])

    # down
    if (coordinates[1]-1 in range(8)):
        down = (coordinates[0], coordinates[1]-1)
        if (down not in black):
            possible_move_down = check_move(down, goal_coordinates)
            num_steps = (turn_positive(possible_move_down[0]) +
                        turn_positive(possible_move_down[1]))
            queue.append([num_steps, coordinates, down])

    return queue

def turn_positive(x):
    if x < 0:
        x *= -1
    return x

# Decide to move in x direction or y direction
def direction(possible_move):
    x, y = possible_move
    if (x < 0):
        x = x * -1
    if (y < 0):
        y = y * -1

    if (x<y):
        return 'y'

    return 'x'

# Deciding path for piece
def check_move(piece, enemy):
    x1,y1 = piece
    x2,y2 = enemy
    possible_move = (x2-x1, y2-y1)

    return possible_move

# Area of explosion of piece
def boom_area(piece):
    x,y = piece
    area = [(x+1,y), (x+1,y-1), (x,y-1), (x-1,y-1), (x-1,y), (x-1,y+1),
            (x,y+1), (x+1,y+1)]

    return area

def boomable(area, enemy):
    if enemy in area:
        return True

    return False

def boom_link(coordinates, team):
    queue = []
    target = set()
    for i in team:
        if (i in boom_area(coordinates)):
            target.add(i)
            queue.append(i)

    while(len(queue) != 0):
        for i in team:
            if (i in boom_area(queue[0])) and (i not in target):
                target.add(i)
                queue.append(i)
        queue.pop(0)

    return target

def optimal_position(black, n_white):
    optimal_list = []
    allies = n_white-1
    optimal_coordinates = []
    enemies = []

    for i in range(n_white):
        optimal_coordinates.append([])

    for i in range(8):
        for j in range(8):
            coordinates = (i,j)
            enemy_target = boom_link(coordinates, black)
            count = len(enemy_target)
            if (count > 0):
                if (count == len(black) or allies > 0):
                    optimal_coordinates
                    optimal_list.append([count, coordinates])
                    enemies.append(list(enemy_target))

    enemy_list = []
    selected_enemy = []
    enemy_count = 0
    i = 0
    j = 1
    index = []

    if (n_white == 1):
        for i in optimal_list:
            if (i[0] == len(black)):
                selected_enemy.append(i)

    else:
        while (i<len(optimal_list)-1):
            current = optimal_list[i]
            next = optimal_list[i+j]

            if (len(enemy_list) < 1):
                for k in enemies[i]:
                    enemy_list.append(k)
                index.append(i)
                enemy_count += current[0]

            if ((enemy_count + next[0]) <= len(black)):
                same = False
                for l in enemies[i+j]:
                    if (l in enemy_list):
                        same = True
                if (same == False):
                    for k in enemies[i+j]:
                        enemy_list.append(k)
                    enemy_count += next[0]
                    index.append(i+j)

            if (enemy_count == len(black) and len(index) <= n_white):
                potential_goal = []
                for k in index:
                    potential_goal.append(optimal_list[k])
                selected_enemy.append(potential_goal)
                number = index.pop()
                for k in range(len(enemies[number])):
                    enemy_list.pop()
                enemy_count -= len(enemies[number])
                j = number + 1 - i

            else:
                j += 1

            if ((i+j) >= len(optimal_list)):

                number = index.pop()
                for k in range(len(enemies[number])):
                    enemy_list.pop()
                enemy_count -= len(enemies[number])

                if (number == len(optimal_list)-1):
                    number = index.pop()
                    for k in range(len(enemies[number])):
                        enemy_list.pop()
                    enemy_count -= len(enemies[number])

                    if (len(index) < 1):
                        i += 1
                        j = 0 - i
                    else:
                        j = number + 1 - i

                else:
                    if (len(index) < 1):
                        i += 1
                        j = 0 - i
                    else:
                        j = number + 1 - i

    return selected_enemy

def nearest_location(team, goal):
    shortest_distance = []

    if (len(team) == 1):
        for i in team:
            for combinations in goal:
                distance = euclidean_distance(i, combinations[-1])
                shortest_distance.append([distance, [i, combinations]])

    else:
        for combinations in goal:
            pairs = [[i, j] for i in team
                            for j in combinations]
            best_pairs = float("inf")
            for i in pairs:
                for j in pairs:
                    if (i[0] != j[0] and i[-1][-1] != j[-1][-1]):
                        distance1 = euclidean_distance(i[0], j[0])
                        distance2 = euclidean_distance(i[-1][-1], j[-1][-1])
                        total_distance = distance1 + distance2
                        if (total_distance < best_pairs):
                            best_pairs = total_distance
                            best_pairs_info = [best_pairs, i, j]

            shortest_distance.append(best_pairs_info)

    shortest_distance.sort()

    return shortest_distance[0]

def euclidean_distance(piece, enemy):
    x1,y1 = piece
    x2,y2 = enemy
    distance = math.sqrt(((x1-x2) ** 2) + ((y1-y2) ** 2))

    return distance

def nearest_pair(pieces, enemies):
    shortest_distance = euclidean_distance((0,0),(7,7)) + 1
    for i in pieces:
        for j in enemies:
            distance = euclidean_distance(i, j)
            if (distance < shortest_distance):
                shortest_distance = distance
                piece = i
                enemy = j
                piece_value = pieces.get(i)
                n_piece = int(piece_value[0])
                enemy_value = pieces.get(j)
                n_enemy = int(piece_value[0])

    return n_piece, piece, n_enemy, enemy

if __name__ == '__main__':
    main()
