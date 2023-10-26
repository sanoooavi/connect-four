import math

import numpy as np
import pygame

# color RGB

BOARD_COLOR = "#F6F0B9"
BLACK = "#1E1111"
PLayer_color = "#E10202"
AI_color = "#1119FF"
ROW_COUNT = 6
COLUMN_COUNT = 7
Square_size = 90
RADIUS = 30
Player_symbol = 1
AI_Symbol = 2


class Board:

    def __init__(self, board_template=np.zeros((ROW_COUNT, COLUMN_COUNT))):
        self.board = board_template

    # def get_board(self):
    #     return self.board

    def put_piece(self, row, col, piece):
        self.board[row][col] = piece

    def get_next_open_row(self, col):
        ans = -1
        for r in range(ROW_COUNT - 1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return ans

    def in_bounds(self, r, c):
        return 0 <= r < ROW_COUNT and 0 <= c < COLUMN_COUNT

    def check_if_winner(self, row, col, symbol):
        res = False
        if row == -1 and col == -1:
            for r in range(ROW_COUNT):
                for c in range(COLUMN_COUNT):
                    ans = self.check_if_winner(r, c, symbol)
                    if ans:
                        print(symbol)
                        print(f"hoho True in{r} and {c}")
                    if ans:
                        return True
            return False

        last_row = row
        last_col = col
        last_letter = symbol
        if self.board[last_row][last_col] != symbol:
            return False
        # [r, c] direction, matching letter count, locked bool
        directions = [[[-1, 0], 0, True],
                      [[1, 0], 0, True],
                      [[0, -1], 0, True],
                      [[0, 1], 0, True],
                      [[-1, -1], 0, True],
                      [[1, 1], 0, True],
                      [[-1, 1], 0, True],
                      [[1, -1], 0, True]]

        # Search outwards looking for matching pieces
        for a in range(3):
            for d in directions:
                r = last_row + (d[0][0] * (a + 1))
                c = last_col + (d[0][1] * (a + 1))

                if d[2] and self.in_bounds(r, c) and self.board[r][c] == last_letter:
                    d[1] += 1
                else:
                    # Stop searching in this direction
                    d[2] = False

        # Check possible direction pairs for '4 pieces in a row'
        for i in range(0, 8, 2):
            if directions[i][1] + directions[i + 1][1] >= 3:
                return True
        return False

    def get_valid_locations(self):
        valid_locations = []
        for col in range(COLUMN_COUNT):
            if (r := self.get_next_open_row(col)) != -1:
                valid_locations.append((r, col))
        return valid_locations

    def evaluate_score(self, row_4, symbol):
        score = 0
        opp_symbol = AI_Symbol
        if symbol == AI_Symbol:
            opp_symbol = Player_symbol

        # if our symbol count is 4 then +100
        if row_4.count(symbol) == 4:
            score += 10000
        elif row_4.count(symbol) == 3 and row_4.count(0) == 1:
            score += 100
        elif row_4.count(symbol) == 2 and row_4.count(0) == 2:
            score += 40
        if row_4.count(opp_symbol) == 3 and row_4.count(0) == 1:
            score -= 120
        elif row_4.count(opp_symbol) == 2 and row_4.count(0) == 2:
            score -= 20
        # elif row_4.count(opp_symbol) == 2 and row_4.count(0) == 1:
        #     score -= 1
        return score

    def get_state_score(self, symbol):
        score = 0
        #
        # ## Score center column
        # center_array = [int(i) for i in list(new_board[:, COLUMN_COUNT // 2])]
        # center_count = center_array.count(symbol)
        # score += center_count * 3

        ## Score Horizontal
        for r in range(ROW_COUNT):
            row_array = [int(i) for i in list(self.board[r, :])]
            for c in range(COLUMN_COUNT - 3):
                score += self.evaluate_score(row_array[c:c + 4], symbol)

        ## Score Vertical
        for c in range(COLUMN_COUNT):
            col_array = [int(i) for i in list(self.board[:, c])]
            for r in range(ROW_COUNT - 3):
                score += self.evaluate_score(col_array[r:r + 4], symbol)

        ## Score posiive sloped diagonal
        for r in range(ROW_COUNT - 3):
            for c in range(COLUMN_COUNT - 3):
                score += self.evaluate_score([self.board[r + i][c + i] for i in range(4)], symbol)
                score += self.evaluate_score([self.board[r + 3 - i][c + i] for i in range(4)], symbol)

        return score

    def pick_best_move(self, symbol):
        valid_locations = self.get_valid_locations()
        best_score = -math.inf
        # b_row, b_col = random.choice(valid_locations)
        for place in valid_locations:

            board_copy = Board(self.board.copy())
            board_copy.put_piece(place[0], place[1], AI_Symbol)
            # put_piece(temp_board, place[0], place[1], symbol)
            score = board_copy.get_state_score(symbol)
            print(f"{place} and score is {score}")
            if score > best_score:
                best_score = score
                best_col = place[1]
                best_row = place[0]
        return best_row, best_col

    def draw_board(self, screen):
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                pygame.draw.rect(screen, BOARD_COLOR,
                                 (c * Square_size, (r + 1) * Square_size, Square_size, Square_size))
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                if self.board[r][c] == Player_symbol:
                    pygame.draw.circle(screen, PLayer_color, (
                        int(c * Square_size + Square_size / 2), int((r + 1) * Square_size + Square_size / 2)), RADIUS)
                elif self.board[r][c] == AI_Symbol:
                    pygame.draw.circle(screen, AI_color, (
                        int(c * Square_size + Square_size / 2), int((r + 1) * Square_size + Square_size / 2)), RADIUS)
                else:
                    pygame.draw.circle(screen, BLACK, (
                        int(c * Square_size + Square_size / 2), int((r + 1) * Square_size + Square_size / 2)), RADIUS)
        pygame.display.update()

    def minimax(self, depth, alpha, beta, maximizingPlayer, in_row, in_col):
        valid_locations = self.get_valid_locations()
        if depth == 0:
            return None, None, self.get_state_score(AI_Symbol)
        if self.check_if_winner(in_row, in_col, AI_Symbol):
            return None, None, 100000000000000 - depth
        elif self.check_if_winner(in_row, in_col, Player_symbol):
            return None, None, -10000000000000
        elif len(valid_locations) == 0:  # Game is over, no more valid moves
            return None, None, 0

        if maximizingPlayer:
            value = -math.inf
            # column = random.choice(valid_locations)
            for place in valid_locations:
                board_copy = Board(self.board.copy())
                board_copy.put_piece(place[0], place[1], AI_Symbol)
                new_score = board_copy.minimax(depth - 1, alpha, beta, False, place[0], place[1])[2]
              #  print(f"{new_score} and row is {place[0]} and col is {place[1]}")
                if new_score > value:
                    value = new_score
                    column = place[1]
                    row = place[0]
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return row, column, value

        else:  # Minimizing player
            value = math.inf
            for place in valid_locations:
                board_copy = Board(self.board.copy())
                board_copy.put_piece(place[0], place[1], Player_symbol)
                new_score = board_copy.minimax(depth - 1, alpha, beta, True, place[0], place[1])[2]
                if new_score < value:
                    value = new_score
                    column = place[1]
                    row = place[0]
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return row, column, value

    def print_board(self):
        print(self.board)
