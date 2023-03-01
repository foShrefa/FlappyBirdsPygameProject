import pygame
import random
import sys
import sqlite3
import datetime
import os

pygame.init()

clock = pygame.time.Clock()

size = WIDTH, HEIGHT = 1200, 750
FPS = 60
screen = pygame.display.set_mode(size)

pygame.display.set_caption('Flappy Bird')

font = pygame.font.SysFont('inkfree', 60)


ground_move = 0
background_move = 0
speed = 3
pipe_gap = 140
pipe_delay = 1500
last_pipe = pygame.time.get_ticks() - pipe_delay
paused_time = 0
score = 0
update_database = True
flying = False
game_over = False
game_paused = False
pass_pipe = False
date = ""
time = ""


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)

    if colorkey is not None:

        if colorkey == -1:
            colorkey = image.get_at((0, 0))

        image.set_colorkey(colorkey)

    else:
        image = image.convert_alpha()

    return image


fon = load_image('fon.png')
ground_img = load_image('ground.png')
restart_button = load_image('btn1.png')
menu_button = pygame.transform.scale(load_image('btn2.png'), (122, 42))
pause_button = pygame.transform.scale(load_image('btn3.png'), (50, 50))
start_button = pygame.transform.scale(load_image('btn4.png'), (150, 53))
score_button = pygame.transform.scale(load_image('btn5.png'), (150, 53))
exit_button = pygame.transform.scale(load_image('btn6.png'), (147, 50))
continue_button = pygame.transform.scale(load_image('btn7.png'), (122, 42))
back_to_game_button = pygame.transform.scale(load_image('btn8.png'), (50, 50))
back_button = pygame.transform.scale(load_image('btn9.png'), (60, 64))
main_title = pygame.transform.scale(load_image('maintitle.png'), (356, 96))
death_title = pygame.transform.scale(load_image('deathtitle.png'), (388, 88))
panel = pygame.transform.scale(load_image('panel.png'), (791, 406))
clear_button = pygame.transform.scale(load_image('clear.png'), (170, 64))



class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


    def pressed(self):
        action = False
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):

            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action


button1 = Button(539, 360, restart_button)
button2 = Button(539, 435, menu_button)
button3 = Button(4, 4, pause_button)
button4 = Button(525, 315, start_button)
button5 = Button(525, 395, score_button)
button6 = Button(528, 480, exit_button)
button7 = Button(539, 285, continue_button)
button8 = Button(4, 4, back_to_game_button)
button9 = Button(6, 6, back_button)
button10 = Button(826, 550, clear_button)



def reset_game():
    pipe_group.empty()
    bird.rect.x = 100
    bird.rect.y = int(HEIGHT / 2)
    score = 0
    return score


class Flappy_Bird(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(3):
            sprite = pygame.transform.scale(load_image(f'birdy{i + 1}.png'), (51, 36))
            self.images.append(sprite)
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.fall = 0
        self.clicked = False

    def update(self):

        if flying:
            self.fall += 0.6

            if self.fall > 12:
                self.fall = 12

            if self.rect.bottom < 675:
                self.rect.y += int(self.fall)

        if not game_over:

            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked\
                    and not game_paused:
                if not button3.pressed():
                    self.clicked = True
                    self.fall = -10

            if pygame.mouse.get_pressed()[0] == 0 and not game_paused:
                if not button3.pressed():
                    self.clicked = False

            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1

                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            self.image = pygame.transform.rotate(self.images[self.index], self.fall * -2)

        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Pipe(pygame.sprite.Sprite):

    def __init__(self, pos, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(load_image('pipe.png'), (80, 650))
        self.rect = self.image.get_rect()

        if pos == 'up':
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]

        elif pos == 'down':
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= speed
        if self.rect.right < 0:
            self.kill()


def terminate():
    pygame.quit()
    sys.exit()


def main_menu():
    con = sqlite3.connect("flappy_bird_score.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM score_list ORDER BY score DESC").fetchall()
    con.commit()
    con.close()

    screen.blit(fon, (background_move, 0))
    screen.blit(ground_img, (ground_move, 675))
    screen.blit(main_title, (422, 150))
    font = pygame.font.SysFont('lucidasans', 35)
    text_color = (217, 169, 75)
    score_menu_opened = False

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT\
                    or button6.pressed():
                terminate()

            elif button5.pressed():
                score_menu_opened = True

            elif button4.pressed():
                return

        if score_menu_opened:
            screen.blit(fon, (background_move, 0))
            screen.blit(ground_img, (ground_move, 675))
            screen.blit(panel, ((WIDTH - 791) / 2, (HEIGHT - 406) / 2 - 50))
            text_coord = 133
            string_number = 0

            for elem in result:
                string_number += 1
                score_string = f"{string_number}."
                for value in elem:
                    score_string = score_string + "         " + str(value)
                string_rendered = font.render(score_string, 1, pygame.Color(text_color))
                intro_rect = string_rendered.get_rect()
                text_coord += 18
                intro_rect.top = text_coord
                intro_rect.x = 255
                text_coord += intro_rect.height
                screen.blit(string_rendered, intro_rect)

            if button9.pressed():
                screen.blit(fon, (background_move, 0))
                screen.blit(ground_img, (ground_move, 675))
                screen.blit(main_title, (422, 150))
                score_menu_opened = False

            elif button10.pressed():
                con = sqlite3.connect("flappy_bird_score.db")
                cur = con.cursor()
                cur.execute("""DELETE from score_list""")
                result = []
                con.commit()
                con.close()

        pygame.display.flip()
        clock.tick(FPS)


def score_menu():
    screen.blit(fon, (background_move, 0))
    screen.blit(ground_img, (ground_move, 675))

    while True:
        if button1.pressed():
            return
    pygame.display.flip()
    clock.tick(FPS)


pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

bird = Flappy_Bird(100, int(HEIGHT / 2))

bird_group.add(bird)

main_menu()
run = True

while run:
    clock.tick(FPS)

    screen.blit(fon, (background_move, 0))

    pipe_group.draw(screen)
    bird_group.draw(screen)
    bird_group.update()

    screen.blit(ground_img, (ground_move, 675))

    if len(pipe_group) > 0:

        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and not pass_pipe:
            pass_pipe = True

        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    img = font.render(str(score), True, (255, 255, 255))
    screen.blit(img, (int(WIDTH / 2), 20))

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or bird.rect.top < 0:
        game_over = True

    if bird.rect.bottom >= 675:
        game_over = True
        flying = False

    if flying and not game_over:
        time_now = pygame.time.get_ticks() - paused_time

        if time_now - last_pipe > pipe_delay:
            pipe_height = random.randint(-150, 150)
            top_pipe = Pipe("up", WIDTH, int(HEIGHT / 2) + pipe_height)
            btm_pipe = Pipe("down", WIDTH, int(HEIGHT / 2) + pipe_height)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        pipe_group.update()

        ground_move -= speed

        if abs(ground_move) > 35:
            ground_move = 0

        background_move -= speed // 3

        if abs(background_move) > 864:
            background_move = 0

    if not game_over and not game_paused:
        if button3.pressed() or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            start_time = pygame.time.get_ticks()
            game_paused = True
            flying = False

    if game_over:
        screen.blit(death_title, (406, 200))

        if update_database:
            update_database = False
            con = sqlite3.connect("flappy_bird_score.db")
            cur = con.cursor()
            date = f"'{str(datetime.date.today())}'"
            time = f"'{str(datetime.datetime.now().time())[:5]}'"
            cur.execute(f"""INSERT INTO score_list(date, time, score)
            VALUES({date}, {time}, {score})""")
            sorted_score = cur.execute("SELECT * FROM score_list ORDER BY score DESC").fetchall()
            cur.execute("DELETE from score_list")
            for elem in sorted_score:
                cur.execute(f"""INSERT INTO score_list(date, time, score)
                VALUES("{elem[0]}", "{elem[1]}", {elem[2]})""")
            cur.execute("DELETE from score_list WHERE rowid > 5")
            con.commit()
            con.close()

        if button1.pressed():
            game_over = False
            update_database = True
            score = reset_game()

        if button2.pressed():
            game_over = False
            update_database = True
            score = reset_game()
            main_menu()

    if game_paused:

        if button7.pressed():
            flying = True
            game_paused = False
            paused_time += pygame.time.get_ticks() - start_time

        elif button1.pressed():
            score = reset_game()
            game_paused = False
            paused_time += pygame.time.get_ticks() - start_time

        elif button2.pressed():
            score = reset_game()
            game_paused = False
            main_menu()
            paused_time += pygame.time.get_ticks() - start_time

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over\
                and not game_paused:
            flying = True

    pygame.display.update()

pygame.quit()