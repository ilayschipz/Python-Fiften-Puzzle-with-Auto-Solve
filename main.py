import os, random, time

#####################################################################################

LOG = open("log.txt", "w+")
SIZE = -1
COLUMN_WIDTH = 3
SCREEN_WIDTH = SIZE * (COLUMN_WIDTH + 2)
AUTO_SOLVE = False
EVEN = 0
ODD = 1

#####################################################################################


def main():
	board = generate_board()
	while not validate(board):
		print_board(board)
		if player_move(board): break
		if AUTO_SOLVE: autosolve(board)
	if validate(board): print_victory(board)
	print('\n', center_string("....Exiting Program."))
	LOG.close()


#####################################################################################


def clear_console():
	# For Windows
	if os.name == 'nt':
		_ = os.system('cls')
	# For macOS and Linux
	else:
		_ = os.system('clear')


#####################################################################################


def generate_board():
	# Adjust global settings
	global SIZE, COLUMN_WIDTH, SCREEN_WIDTH
	while SIZE < 1:
		try:
			SIZE = int(input(center_string("What size board? (1 to 9): ")))
		except ValueError:
			print("Invalid input.")
	SCREEN_WIDTH = SIZE * (COLUMN_WIDTH + 1)

	# Prepare pieces and board
	pieces = list(range(SIZE * SIZE))
	board = [[] for i in range(SIZE)]

	# Variables for calculating solvability
	offset = -1
	inversions = 0
	row_of_blank = -1

	# Loop until all pieces are placed
	while (len(pieces) > 0):
		next_index = random.randint(0, len(pieces) - 1)
		next_piece = pieces.pop(next_index)
		next_row = SIZE - len(pieces) // SIZE - 1

		# Must keep track of blank for solvability calculations
		if next_piece == 0:
			offset = 0
			row_of_blank = SIZE - next_row

		# Number of inversions depends on position in list. Offset is for blank (0)
		board[next_row].append(next_piece)
		inversions += next_index + offset

	# See: https://www.geeksforgeeks.org/check-instance-15-puzzle-solvable/
	if not ((inversions % 2 == EVEN and
	         (row_of_blank % 2 == ODD or SIZE % 2 == ODD)) or
	        (inversions % 2 == ODD and row_of_blank % 2 == EVEN)):

		#Switch first or last two pieces depending on where blank is
		if row_of_blank != SIZE:
			temp = board[0][0]
			board[0][0] = board[0][1]
			board[0][1] = temp
		else:
			temp = board[SIZE - 1][SIZE - 1]
			board[SIZE - 1][SIZE - 1] = board[SIZE - 1][SIZE - 2]
			board[SIZE - 1][SIZE - 2] = temp

	return board


#####################################################################################


def adjust_board(board, move):
	x = y = 0
	invalid_move = False

	# Find location of blank
	for i in range(SIZE):
		for j in range(SIZE):
			if board[i][j] == 0:
				x = j
				y = i

	# For shifting a piece UP
	if move == 'W':
		if y + 1 < SIZE:
			board[y][x] = board[y + 1][x]
			board[y + 1][x] = 0
		else:
			invalid_move = True

	# For shifting a piece LEFT
	elif move == 'A':
		if x + 1 < SIZE:
			board[y][x] = board[y][x + 1]
			board[y][x + 1] = 0
		else:
			invalid_move = True

	# For shifting a piece DOWN
	elif move == 'S':
		if y > 0:
			board[y][x] = board[y - 1][x]
			board[y - 1][x] = 0
		else:
			invalid_move = True

	# For shifting a piece RIGHT
	elif move == 'D':
		if x > 0:
			board[y][x] = board[y][x - 1]
			board[y][x - 1] = 0
		else:
			invalid_move = True

	# For if input is a number. Check if piece is adjacent then move
	else:
		adjacent = False
		for i in range(SIZE):
			for j in range(SIZE):
				if board[i][j] == move:
					if ((abs(x - j) == 1 and abs(y - i) == 0)
					    or (abs(x - j) == 0 and abs(y - i) == 1)):
						board[y][x] = board[i][j]
						board[i][j] = 0
						adjacent = True
				if adjacent: break
			if adjacent: break
		if not adjacent: invalid_move = True

	# If the move is invalid, inform the player and requery input
	if invalid_move:
		print_board(board)
		print(center_string("INVALID MOVE: No such adjacent square."))
		if AUTO_SOLVE: return True
		else: player_move(board)


#####################################################################################


def validate(board):
	# A winning board will have all consecutive numbers
	consecutive = 0
	for i in range(SIZE):
		for j in range(SIZE):
			if i == SIZE - 1 and j == SIZE - 1:  # If final piece is reached, return victory
				return True
			elif board[i][j] == consecutive + 1:
				consecutive = consecutive + 1
			else:
				return False


#####################################################################################


def player_move(board):
	global AUTO_SOLVE
	while True:
		move = input('\n' + center_string(
		    "Where would you like to move? (w|a|s|d|q|auto)")).upper()

		# Attempt to parse input into an integer
		try:
			move = int(move)
			break

		# Otherwise check for other valid inputs
		except ValueError:
			if move == 'W' or move == 'A' or move == 'S' or move == 'D': break
			elif move == 'Q' or move == 'E' or move == "QUIT" or move == "EXIT":
				return True
			elif move == "AUTO" or move == "AUTOSOLVE" or move == "AUTO SOLVE" or move == "AS" or move == "SOLVE":
				AUTO_SOLVE = True
		if AUTO_SOLVE: return False

		# The move is invalid if still in loop. Inform player of acceptable input.
		print_board(board)
		print(
		    center_string(
		        "INVALID MOVE: Please input WASD or adjacent block number."))
	return adjust_board(board, move)


#####################################################################################


def autosolve(board):
	next = 1
	moveable = [[True for i in range(SIZE)] for j in range(SIZE)]
	while next != SIZE * SIZE:
		while not validate(board):
			focus = next
			blank = piece = moveto = (0, 0)
			goal = ((next - 1) % SIZE, (next - 1) // SIZE)

			# Different strategy for second to last row
			if (next - 1) // SIZE == SIZE - 2:
				if ((next - 1) % SIZE == 0
				    or (next - 1) == board[goal[1]][goal[0] - 1]):
					focus += SIZE
				else:
					focus -= 1

			# Different strategy for second to last column
			else:
				if next % SIZE == SIZE - 1: focus += 1
				elif next % SIZE == 0:
					focus -= 1
					goal = (goal[0] - 1, goal[1] + 1)

			# Finishing move
			if focus == SIZE * SIZE:
				path_board(board, [(goal[0], goal[1] + 1)])
				break

			# Find where the blank and focus pieces are
			for i in range(SIZE):
				for j in range(SIZE):
					if board[i][j] == 0: blank = (j, i)
					if board[i][j] == focus: piece = (j, i)
			moveable[piece[1]][piece[0]] = False

			# Perform an action if a piece is at its desired position
			if piece == goal:

				# Resolve solvability for second to last row or column if stuck
				if focus == next + SIZE or focus == next + 1:
					moveto = (-1, -1)

					if focus == next + SIZE:
						check = (piece[0], piece[1] + 1)
						if (board[check[1]][check[0]] == next):
							moveto = (check[0] + 1, check[1])
						else:
							check = (blank[0] + 1, blank[1])
							if blank == (
							    piece[0], piece[1] +
							    1) and board[check[1]][check[0]] == next:
								moveable[check[1]][check[0]] = False
								moveto = (check[0] + 1, check[1])

					elif focus == next + 1:
						check = (piece[0] + 1, piece[1])
						if (board[check[1]][check[0]] == next):
							moveto = (check[0], check[1] + 1)
						else:
							check = (blank[0], blank[1] + 1)
							if (blank == (piece[0] + 1, piece[1])
							    and board[check[1]][check[0]] == next):
								moveable[check[1]][check[0]] = False
								moveto = (check[0], check[1] + 1)

					if moveto != (-1, -1):
						moveable[piece[1]][piece[0]] = True
						path = path_find(blank, moveto, moveable)
						path.append(check)
						path_board(board, path)
						moveable[check[1]][check[0]] = True
						continue

				elif focus == next - 1:
					lock = piece

					# Different Stategy for second to last row
					if (next - 1) // SIZE == SIZE - 2:
						goal = ((next - 1) % SIZE - 1, (next - 1) // SIZE + 1)
						lock = (piece[0] - 1, piece[1] + 1)
						path = path_find(blank, goal, moveable)
						path.append((goal[0], goal[1] - 1))
						path.append((goal[0] + 1, goal[1] - 1))
						next -= 1

					# Different Stategy for second to last column
					else:
						goal = ((next - 1) % SIZE, (next - 1) // SIZE)
						lock = (piece[0] + 1, piece[1] - 1)
						path = path_find(blank, goal, moveable)
						path.append((goal[0] - 1, goal[1]))
						path.append((goal[0] - 1, goal[1] + 1))

					# Execute Stategy
					path_board(board, path)
					moveable[piece[1]][piece[0]] = True
					moveable[lock[1]][lock[0]] = False
				break

			# Resolve solvability if on second to last row or column
			if next == board[goal[1]][goal[0]]:
				moveto = (goal[0] + 1, goal[1])
				moveable[piece[1]][piece[0]] = True
				path = path_find(blank, moveto, moveable)
				path.append(goal)
				if focus == next + SIZE: path.append((goal[0], goal[1] + 1))
				path_board(board, path)
				continue

			# Move blank adjacent to the piece we're shifting
			elif abs(piece[0] - goal[0]) < abs(piece[1] - goal[1]):
				if piece[1] > goal[1]: moveto = (piece[0], piece[1] - 1)
				elif piece[1] < goal[1]: moveto = (piece[0], piece[1] + 1)
			else:
				if piece[0] > goal[0]: moveto = (piece[0] - 1, piece[1])
				else: moveto = (piece[0] + 1, piece[1])
			path_board(board, path_find(blank, moveto, moveable))

			# Once adjacent, switch blank and piece
			path_board(board, [piece])
			moveable[piece[1]][piece[0]] = True

		# Iterate to the next consecutive number
		next += 1


#####################################################################################


def center_string(string):
	return (' ' * int((SCREEN_WIDTH - len(string)) / 2) + string)


#####################################################################################


def print_board(board):
	clear_console()
	time.sleep(0.001)

	graphic = "\n╔"
	graphic += ('═' * COLUMN_WIDTH + '╦') * (SIZE - 1)
	graphic += ("═" * COLUMN_WIDTH + '╗')

	for i in range(SIZE):
		graphic += "\n║"
		for j in range(SIZE):
			num = board[i][j]
			if num > 9 and num < 100: num = " {number}".format(number=num)
			if board[i][j] == 0: graphic += (' ' * COLUMN_WIDTH + '║')
			else:
				graphic += (
				    "{piece:^{width}}".format(piece=num, width=COLUMN_WIDTH) +
				    '║')

		if (i < SIZE - 1):
			graphic += "\n╠"
			graphic += ('═' * COLUMN_WIDTH + '╬') * (SIZE - 1)
			graphic += ('═' * COLUMN_WIDTH + '╣')

	graphic += "\n╚"
	graphic += ('═' * COLUMN_WIDTH + '╩') * (SIZE - 1)
	graphic += ('═' * COLUMN_WIDTH + '╝')

	print(graphic)
	LOG.write(graphic)


#####################################################################################


def print_victory(board):
	clear_console()
	time.sleep(0.1)
	print_board(board)
	print()
	print(center_string("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"))
	print(center_string("▓▓▓▓            ▓▓▓▓"))
	print(center_string("▓▓▓▓  YOU WIN!  ▓▓▓▓"))
	print(center_string("▓▓▓▓            ▓▓▓▓"))
	print(center_string("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"))


#####################################################################################


def print_route(start, goal, map, route_map, final_route):
	print()
	for i in range(SIZE):
		for j in range(SIZE):
			en_route = False
			try:
				final_route.index(route_map[i][j])
				en_route = True
			except ValueError:
				False
			if start == (j, i) or goal == (j, i): print('×', end=' ')
			elif not map[i][j]: print('█', end='█')
			elif route_map[i][j] == (j - 1, i): print('←', end=' ')
			elif route_map[i][j] == (j + 1, i): print('→', end=' ')
			elif route_map[i][j] == (j, i - 1): print('↑', end=' ')
			elif route_map[i][j] == (j, i + 1): print('↓', end=' ')
			else: print(' ', end=' ')
		print()

	print('\nROUTE: ×', end=' ')
	for i in range(1, len(final_route) - 1):
		x1 = final_route[i][0]
		y1 = final_route[i][1]
		x2 = final_route[i + 1][0]
		y2 = final_route[i + 1][1]
		if x2 - x1 == 1: print('→', end=' ')
		elif x1 - x2 == 1: print('←', end=' ')
		elif y2 - y1 == 1: print('↓', end=' ')
		elif y1 - y2 == 1: print('↑', end=' ')
	print('×')


#####################################################################################


def path_find(start, goal, map):
	closedset = []
	openset = [start]
	route_map = [[(-1, -1) for i in range(SIZE)] for j in range(SIZE)]
	tcost = [[9999999 for i in range(SIZE)]
	         for j in range(SIZE)]  # Current Travel Cost from Start
	hcost = [[9999999 for i in range(SIZE)]
	         for j in range(SIZE)]  # Heuristic Travel Cost  to  End

	tcost[start[1]][start[0]] = 0
	hcost[start[1]][start[0]] = calc_heuristic(
	    start, goal) + tcost[start[1]][start[0]]

	while openset:
		next = 0
		x = openset[0][0]
		y = openset[0][1]
		for i in range(1, len(openset)):
			x1 = openset[i][0]
			y1 = openset[i][1]
			if hcost[y1][x1] < hcost[y][x]:
				x = x1
				y = y1
				next = i

		if openset[next] == goal:
			#print_route(start,goal,map,route_map,path_route(route_map,goal))
			#time.sleep(2)
			return path_route(route_map, goal)

		neighbors = []
		if x > 0: neighbors.append((x - 1, y))
		if y > 0: neighbors.append((x, y - 1))
		if x < SIZE - 1: neighbors.append((x + 1, y))
		if y < SIZE - 1: neighbors.append((x, y + 1))

		for neighbor in neighbors:
			x1 = neighbor[0]
			y1 = neighbor[1]
			if not map[y1][x1]:
				closedset.append(neighbor)
				continue
			try:
				closedset.index(neighbor)
				continue
			except ValueError:
				new_tcost = tcost[y][x] + 1
				try:
					openset.index(neighbor)
					if new_tcost > tcost[y1][x1]: continue
				except ValueError:
					openset.append(neighbor)
				route_map[y1][x1] = openset[next]
				tcost[y1][x1] = new_tcost
				hcost[y1][x1] = new_tcost + calc_heuristic(neighbor, goal)

		closedset.append(openset.pop(next))
	return [(-1, -1)]


#####################################################################################


def path_route(route, next):
	final_route = []
	while next != (-1, -1):
		x = next[0]
		y = next[1]
		final_route.append(next)
		next = route[y][x]
	final_route.pop()
	final_route.reverse()
	return final_route


#####################################################################################


def path_board(board, path):
	for node in path:
		x = node[0]
		y = node[1]
		print_board(board)
		print('\n', center_string("Where would you like to move?"),
		      board[y][x])
		time.sleep(0.3)
		adjust_board(board, board[y][x])


#####################################################################################


def calc_heuristic(node, goal):
	return abs(node[0] - goal[0]) + abs(node[1] - goal[1])


#####################################################################################

main()
