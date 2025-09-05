import pygame
import random

pygame.init()

# Размеры окна
width, height = 600, 400
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Макака ворует деньги")

# Цвета
gray = (200, 200, 200)
brown = (139, 69, 19)       # Макака
gold = (255, 215, 0)        # Деньги - жёлтые
light_blue = (135, 206, 250) # Алмаз - голубой
black = (0, 0, 0)

clock = pygame.time.Clock()
monkey_size = 30
money_size = 20
diamond_size = 25
speed = 5

font = pygame.font.SysFont(None, 36)

def draw_monkey(x, y):
    pygame.draw.rect(win, brown, (x, y, monkey_size, monkey_size))

def draw_money(x, y):
    pygame.draw.rect(win, gold, (x, y, money_size, money_size))

def draw_diamond(x, y):
    # Рисуем алмаз ромбом (прямоугольник, повернутый на 45 градусов)
    diamond_points = [
        (x + diamond_size // 2, y),
        (x + diamond_size, y + diamond_size // 2),
        (x + diamond_size // 2, y + diamond_size),
        (x, y + diamond_size // 2)
    ]
    pygame.draw.polygon(win, light_blue, diamond_points)

def show_score(score):
    text = font.render(f"Счёт: {score}", True, black)
    win.blit(text, (10, 10))

def game_loop():
    x, y = width // 2, height // 2
    x_change, y_change = 0, 0

    # Начальные позиции денег и алмаза
    money_x = random.randint(0, width - money_size)
    money_y = random.randint(0, height - money_size)

    diamond_x = random.randint(0, width - diamond_size)
    diamond_y = random.randint(0, height - diamond_size)

    score = 0

    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -speed
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = speed
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -speed
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = speed
                    x_change = 0

        x += x_change
        y += y_change

        # Ограничение выхода за границы
        x = max(0, min(x, width - monkey_size))
        y = max(0, min(y, height - monkey_size))

        win.fill(gray)

        draw_monkey(x, y)
        draw_money(money_x, money_y)
        draw_diamond(diamond_x, diamond_y)
        show_score(score)

        # Проверка столкновения макаки с деньгами
        monkey_rect = pygame.Rect(x, y, monkey_size, monkey_size)
        money_rect = pygame.Rect(money_x, money_y, money_size, money_size)
        diamond_rect = pygame.Rect(diamond_x, diamond_y, diamond_size, diamond_size)

        if monkey_rect.colliderect(money_rect):
            score += 1
            money_x = random.randint(0, width - money_size)
            money_y = random.randint(0, height - money_size)

        # Проверка столкновения макаки с алмазом
        if monkey_rect.colliderect(diamond_rect):
            score += 3
            diamond_x = random.randint(0, width - diamond_size)
            diamond_y = random.randint(0, height - diamond_size)

        pygame.display.update()

    pygame.quit()

game_loop()
