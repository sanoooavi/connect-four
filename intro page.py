import math
import sys

import pygame

from Game import Board

buttons = []

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


class Button:
    def __init__(self, text, width, height, pos, elevation, font):
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]

        # top rectangle
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_color = '#475F77'
        # bottom rectangle
        self.bottom_rect = pygame.Rect(pos, (width, height))
        self.bottom_color = '#354B5E'
        # text
        self.text = text
        self.text_surf = font.render(text, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)
        buttons.append(self)

    def draw(self):
        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(screen, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(screen, self.top_color, self.top_rect, border_radius=12)
        screen.blit(self.text_surf, self.text_rect)

    def check_click(self):
        stay_in_page = 1
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                stay_in_page = 0
            else:
                self.dynamic_elecation = self.elevation

        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'
        return stay_in_page


if __name__ == "__main__":
    # pygame configuration
    pygame.init()
    screen = pygame.display.set_mode((630, 630))
    pygame.display.set_caption('Connect 4')
    button_font = pygame.font.SysFont('Monospace', 20)
    Title_font = pygame.font.SysFont('Monospace', 100)
    clock = pygame.time.Clock()
    # button configuration
    button1 = Button('1 PLayer _ Easy', 300, 50, (165, 250), 5, font=button_font)
    button2 = Button('1 PLayer _ Hard', 300, 50, (165, 310), 5, font=button_font)
    button4 = Button('Quit', 300, 50, (165, 370), 5, font=button_font)
    # board configuration
    board = Board()
    # game mode set
    in_intro_page = 1
    easy_one_player = hard_one_player = 0
    turns = ['AI', 'Player']
    turn = 1
    game_over = False
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if in_intro_page:
            screen.fill('#DCDDD8')
            screen.blit(Title_font.render("Connect 4!", True, (0, 0, 0)), (20, 100))
            for i in range(len(buttons)):
                buttons[i].draw()
            for i in range(len(buttons)):
                in_intro_page = buttons[i].check_click()
                if in_intro_page == 0:
                    # 0 is AI and 1 is Human
                    # turn = random.randint(0, 1)
                    if i == 0:
                        easy_one_player = 1
                    elif i == 1:
                        hard_one_player = 1
                    elif i == 2:
                        sys.exit()
                    break
            pygame.display.update()

        else:
            screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, BLACK, (0, 0, 700, Square_size))
                    pos_x = event.pos[0]
                    if turns[turn] == 'Player':
                        pygame.draw.circle(screen, PLayer_color, (pos_x, 50), RADIUS)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # pygame.draw.rect(screen, BLACK, (0, 0, 700, Square_size))
                    # Ask for Player 1 Input
                    if turns[turn] == 'Player':
                        pos_x = event.pos[0]
                        col = int(math.floor(pos_x / Square_size))
                        if (row := board.get_next_open_row(col)) != -1:
                            board.put_piece(row, col, Player_symbol)
                            if board.check_if_winner(row, col, Player_symbol):
                                label = button_font.render("Player wins!!", True, PLayer_color)
                                screen.blit(label, (40, 10))
                                game_over = True
                            turn = (turn + 1) % 2
                        print("after player: ")
                        board.print_board()
                board.draw_board(screen)

            if turns[turn] == 'AI' and not game_over:
                row = col = None
                if easy_one_player:
                    pygame.time.wait(500)
                    row, col = board.pick_best_move(AI_Symbol)
                    board.put_piece(row, col, AI_Symbol)
                    print("easy")
                elif hard_one_player:
                    print("hard")
                    row, col, minimax_score = board.minimax(6, -math.inf, math.inf, True, -1, -1)
                    board.put_piece(row, col, AI_Symbol)
                print(f"row is {row} and col is {col}")
                if board.check_if_winner(row, col, AI_Symbol):
                    label = button_font.render("AI wins!!", True, AI_color)
                    screen.blit(label, (280, 20))
                    game_over = True
                turn = (turn + 1) % 2
                board.print_board()
                board.draw_board(screen)

        if game_over:
            pygame.time.wait(3000)
