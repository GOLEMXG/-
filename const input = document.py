import pygame
import random
import urllib.request
import io
import math
import sys
import time
import json


pygame.init()
width, height = 1920, 1080
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Убей пещерного монстра")


gray = (200, 200, 200)
gold = (255, 215, 0)
red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)
white = (255, 255, 255)
shop_bg_color = (180, 180, 180)
admin_bg_color = (30, 30, 30)  # Темный фон для админ меню
clock = pygame.time.Clock()


monster_size = 80
money_size = 40
diamond_size = 40
speed = 8  # будет изменяться админом
enemy_speed = 4
enemy_size = 70


font = pygame.font.SysFont(None, 48)
game_over_font = pygame.font.SysFont(None, 72)
menu_font = pygame.font.SysFont(None, 80)
shop_font = pygame.font.SysFont(None, 30)


SAVE_FILE = "savegame.json"


attack_cooldown_levels = [9000, 8000, 7000, 6000, 5000, 4000, 3000, 2000, 1000]
attack_cooldown_prices = [50, 100, 200, 300, 500, 800, 1200, 1500, 2000]
hp_regen_levels = [9000, 8000, 7000, 6000, 5000, 4000, 3000, 2000, 1000]
hp_regen_prices = [50, 100, 200, 300, 500, 800, 1200, 1500, 2000]


def load_image_from_url(url, size, retries=1, delay=0.5, timeout=2.0):
    headers = {'User-Agent': 'Mozilla/5.0'}
    last_err = None
    for _ in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                image_data = response.read()
            image_file = io.BytesIO(image_data)
            image = pygame.image.load(image_file).convert_alpha()
            return pygame.transform.scale(image, size)
        except Exception as e:
            last_err = e
            time.sleep(delay)
    print(f"Не удалось загрузить изображение с {url}: {last_err}. Использую плейсхолдер.")
    return None


monster_image_url = "https://img.itch.zone/aW1nLzE1MDU5MTE3LnBuZw==/original/q6WAbp.png"
money_image_url = "https://www.clipartmax.com/png/full/395-3953417_clip-art-pixel-art-money-clip-art-pixel-art-money.png"
diamond_image_url = "https://lootx.com/assets/images-giveaways/psx-gem.png"

monster_image = load_image_from_url(monster_image_url, (monster_size, monster_size))
money_image = load_image_from_url(money_image_url, (money_size, money_size))
diamond_image = load_image_from_url(diamond_image_url, (diamond_size, diamond_size))


game_bg_url = "https://media.thingtrunk.com/press-kit/book-of-demons/images/bod_artwork_07.png"
game_bg_image = load_image_from_url(game_bg_url, (width, height))

# Список врагов с параметрами и URL их картинок
enemies = [
    {
        "name": "Монстр",
        "hp": 20,
        "attack": 10,
        "image_url": "https://pixelartmaker-data-78746291193.nyc3.digitaloceanspaces.com/image/2440a3082694594.png"
    },
    {
        "name": "Скелет",
        "hp": 40,
        "attack": 20,
        "image_url": "file:///C:/Users/admin/Pictures/New%20Piskel.png"
    },
    {
        "name": "Зомби",
        "hp": 60,
        "attack": 30,
        "image_url": "file:///C:/Users/admin/Pictures/New%20Piskel%20(1).png"
    },
    {
        "name": "Приведение",
        "hp": 80,
        "attack": 40,
        "image_url": "file:///C:/Users/admin/Pictures/New%20Piskel%20(2).png"  # Пример, при необходимости замените
    },
    {
        "name": "Дракон",
        "hp": 100,
        "attack": 80,
        "image_url": "https://avatars.mds.yandex.net/i?id=748542c47ea86b5dd9723f64008654c9_sr-4633509-images-thumbs&n=13"  # Пример, при необходимости замените
    },
]

# Загрузка изображений врагов
def load_enemy_images():
    for enemy in enemies:
        img = load_image_from_url(enemy["image_url"], (enemy_size, enemy_size))
        if img is None:
            placeholder = pygame.Surface((enemy_size, enemy_size))
            placeholder.fill(red)
            enemy["image"] = placeholder
        else:
            enemy["image"] = img


def draw_health_bar(x, y, current_hp, max_hp, bar_width, bar_height):
    ratio = max(0, min(current_hp, max_hp)) / max_hp
    pygame.draw.rect(win, (80, 20, 20), (x, y, bar_width, bar_height))
    if ratio >= 0.66:
        fill_color = green
    elif ratio >= 0.33:
        fill_color = (240, 200, 40)  # жёлтый
    else:
        fill_color = red
    pygame.draw.rect(win, fill_color, (x, y, int(bar_width * ratio), bar_height))
    pygame.draw.rect(win, black, (x, y, bar_width, bar_height), 2)


def draw_monster(x, y):
    if monster_image:
        win.blit(monster_image, (x, y))
    else:
        pygame.draw.rect(win, (139, 69, 19), (x, y, monster_size, monster_size))


def draw_money(x, y):
    if money_image:
        win.blit(money_image, (x, y))
    else:
        pygame.draw.rect(win, gold, (x, y, money_size, money_size))


def draw_diamond(x, y):
    if diamond_image:
        win.blit(diamond_image, (x, y))
    else:
        pygame.draw.polygon(win, (135, 206, 250), [
            (x + diamond_size // 2, y),
            (x + diamond_size, y + diamond_size // 2),
            (x + diamond_size // 2, y + diamond_size),
            (x, y + diamond_size // 2)
        ])

# Изменена с добавлением изображения врага
def draw_enemy(x, y, hp, attack, enemy_image):
    if enemy_image:
        win.blit(enemy_image, (x, y))
    else:
        pygame.draw.rect(win, red, (x, y, enemy_size, enemy_size))
    hp_text = font.render(f"HP: {hp}", True, white)
    att_text = font.render(f"Атк: {attack}", True, white)
    win.blit(hp_text, (x, y - 80))
    win.blit(att_text, (x, y - 50))


def show_score(score, hp, attack_damage, money_count, diamond_count, currency_multiplier):
    mult_text = f"x{currency_multiplier}"
    text = font.render(
        f"Валюта: {score}  HP: {hp}  Урон: {attack_damage}  Деньги: {money_count}  Алмазы: {diamond_count}  Множитель валюты: {mult_text}",
        True, white)
    win.blit(text, (4, 4))


def show_game_over(message):
    t1 = game_over_font.render("Игра окончена!", True, red)
    t2 = font.render(message, True, white)
    t3 = font.render("Нажмите R для рестарта, Q для выхода", True, white)
    r1 = t1.get_rect(center=(width // 2, height // 2 - 60))
    r2 = t2.get_rect(center=(width // 2, height // 2))
    r3 = t3.get_rect(center=(width // 2, height // 2 + 60))
    win.blit(t1, r1)
    win.blit(t2, r2)
    win.blit(t3, r3)
    pygame.display.update()


def save_game(state):
    try:
        data = state.copy()
        data['money_positions'] = [list(pos) for pos in data['money_positions']]
        data['diamond_positions'] = [list(pos) for pos in data['diamond_positions']]
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print("Ошибка сохранения:", e)


def load_game():
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            data['money_positions'] = [tuple(pos) for pos in data['money_positions']]
            data['diamond_positions'] = [tuple(pos) for pos in data['diamond_positions']]
            return data
    except Exception as e:
        print("Ошибка загрузки сохранения или сохранения нет:", e)
        return None


def reset_game():
    global speed
    speed = 8
    x, y = width // 2, height // 2
    money_positions = [(random.randint(0, width - money_size), random.randint(0, height - money_size))]
    diamond_positions = [(random.randint(0, width - diamond_size), random.randint(0, height - diamond_size))]
    enemy_x = random.randint(0, width - enemy_size)
    enemy_y = random.randint(0, height - enemy_size)
    score = 0
    alive = True
    monkey_hp = 20  # HP игрока (без уровней)
    enemy_level = 0  # стартовый уровень врага
    enemy_data = enemies[enemy_level]
    enemy_hp = enemy_data["hp"]
    enemy_attack = enemy_data["attack"]
    enemy_image = enemy_data["image"]
    
    return dict(
        x=x, y=y,
        money_positions=money_positions,
        diamond_positions=diamond_positions,
        enemy_x=enemy_x, enemy_y=enemy_y,
        score=score, alive=alive,
        monkey_hp=monkey_hp, enemy_hp=enemy_hp, enemy_attack=enemy_attack,
        enemy_level=enemy_level, enemy_image=enemy_image,
        last_monkey_attack_time=0,
        last_enemy_attack_time=0,
        last_monkey_regen_time=0,
        base_hp_price=20,
        hp_owned=0,
        attack_damage=1,
        base_attack_price=10,
        attack_owned=0,
        current_money_price=30,
        money_owned=1,
        current_diamond_price=50,
        diamond_owned=1,
        currency_multiply_levels=[2, 4, 8, 16, 32, 64, 128, 256],
        currency_multiply_prices=[100, 200, 400, 1600, 3200, 6400, 12800, 25600],
        currency_multiply_index=0,
        currency_multiplier=1,
        attack_cooldown_index=0,
        hp_regen_index=0,
        move_x=0,
        move_y=0,
        enemy_base_hp=enemy_hp,
        enemy_base_attack=enemy_attack,
        confirm_exit=False,
        last_dir_key=None,
        last_dir_time=0
    )

def draw_text_center(text, y, font_, color):
    s = font_.render(text, True, color)
    r = s.get_rect(center=(width // 2, y))
    win.blit(s, r)

menu_bg_url = "https://i.pinimg.com/originals/ac/38/4a/ac384ae8e8204ee86c9279a8d9924bef.png"
menu_bg_image = load_image_from_url(menu_bg_url, (width, height))

def menu():
    selected = 0
    options = ['Начать игру', 'Продолжить игру', 'Выйти']
    while True:
        if menu_bg_image:
            win.blit(menu_bg_image, (0, 0))
        else:
            win.fill(gray)
        draw_text_center("Убей пещерного монстра", 200, menu_font, white)
        for i, option in enumerate(options):
            color = white if i != selected else (200, 200, 200)
            text_surf = font.render(option, True, color)
            text_rect = text_surf.get_rect(center=(width // 2, 350 + i * 60))
            win.blit(text_surf, text_rect)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if options[selected] == 'Начать игру':
                        return None
                    elif options[selected] == 'Продолжить игру':
                        return load_game()
                    else:
                        pygame.quit()
                        sys.exit()

def input_password():
    input_box = pygame.Rect(width // 2 - 150, height // 2 - 30, 300, 60)
    user_text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return user_text
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    if event.unicode.isdigit() and len(user_text) < 6:
                        user_text += event.unicode
        win.fill(admin_bg_color)
        draw_text_center("Введите пароль администратора", height // 2 - 80, font, white)
        pygame.draw.rect(win, white, input_box, 2)
        txt_surface = font.render(user_text, True, white)
        win.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        pygame.display.flip()
        clock.tick(30)

def admin_menu(state):
    global speed
    selected = 0
    options = [
        "+5000 Валюты",
        "Установить HP = 5000",
        "Установить Урон = 5000",
        "Установить Скорость = 10",
        "Выйти из админ меню"
    ]
    while True:
        win.fill(admin_bg_color)
        draw_text_center("Меню администратора", 150, menu_font, white)
        for i, option in enumerate(options):
            color = green if i == selected else white
            text_surf = font.render(option, True, color)
            text_rect = text_surf.get_rect(center=(width // 2, 250 + i * 50))
            win.blit(text_surf, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(state)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "+5000 Валюты":
                        state['score'] += 5000
                    elif options[selected] == "Установить HP = 5000":
                        state['monkey_hp'] = 5000
                        state['hp_owned'] = 4990
                    elif options[selected] == "Установить Урон = 5000":
                        state['attack_damage'] = 5000
                        state['attack_owned'] = 4999
                    elif options[selected] == "Установить Скорость = 10":
                        speed = 10
                    elif options[selected] == "Выйти из админ меню":
                        return

def move_enemy_towards_monster(enemy_x, enemy_y, monster_x, monster_y):
    dx = monster_x - enemy_x
    dy = monster_y - enemy_y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return enemy_x, enemy_y
    dx /= dist
    dy /= dist
    enemy_x += dx * enemy_speed
    enemy_y += dy * enemy_speed
    enemy_x = max(0, min(enemy_x, width - enemy_size))
    enemy_y = max(0, min(enemy_y, height - enemy_size))
    return enemy_x, enemy_y

def draw_shop(state):
    shop_surface = pygame.Surface((400, 560), pygame.SRCALPHA)
    shop_surface.fill((*shop_bg_color, 200))
    pygame.draw.rect(shop_surface, black, shop_surface.get_rect(), 3)
    title = shop_font.render("МАГАЗИН", True, black)
    shop_surface.blit(title, (130, 10))

    hp_text = shop_font.render(f"HP: {10 + state['hp_owned']}", True, black)    
    hp_price_text = shop_font.render(f"Цена: {state['base_hp_price']}", True, black)
    hp_button = pygame.Rect(20, 50, 360, 40)
    pygame.draw.rect(shop_surface, green if state['score'] >= state['base_hp_price'] else red, hp_button)
    pygame.draw.rect(shop_surface, black, hp_button, 2)
    shop_surface.blit(hp_text, (hp_button.x + 10, hp_button.y + 5))
    shop_surface.blit(hp_price_text, (hp_button.right - hp_price_text.get_width() - 10, hp_button.y + 5))

    attack_text = shop_font.render(f"Урон: {state['attack_damage']}", True, black)
    attack_price_text = shop_font.render(f"Цена: {state['base_attack_price']}", True, black)
    attack_button = pygame.Rect(20, 100, 360, 40)
    can_buy_attack = (state['score'] >= state['base_attack_price'] and state['attack_owned'] < 100)
    pygame.draw.rect(shop_surface, green if can_buy_attack else red, attack_button)
    pygame.draw.rect(shop_surface, black, attack_button, 2)
    shop_surface.blit(attack_text, (attack_button.x + 10, attack_button.y + 5))
    shop_surface.blit(attack_price_text, (attack_button.right - attack_price_text.get_width() - 10, attack_button.y + 5))

    money_text = shop_font.render(f"Деньги: {state['money_owned']}", True, black)
    money_price_text = shop_font.render(f"Цена: {state['current_money_price']}", True, black)
    money_button = pygame.Rect(20, 150, 360, 40)
    pygame.draw.rect(shop_surface, green if state['score'] >= state['current_money_price'] else red, money_button)
    pygame.draw.rect(shop_surface, black, money_button, 2)
    shop_surface.blit(money_text, (money_button.x + 10, money_button.y + 5))
    shop_surface.blit(money_price_text, (money_button.right - money_price_text.get_width() - 10, money_button.y + 5))

    diamond_text = shop_font.render(f"Алмазы: {state['diamond_owned']}", True, black)
    diamond_price_text = shop_font.render(f"Цена: {state['current_diamond_price']}", True, black)
    diamond_button = pygame.Rect(20, 200, 360, 40)
    pygame.draw.rect(shop_surface, green if state['score'] >= state['current_diamond_price'] else red, diamond_button)
    pygame.draw.rect(shop_surface, black, diamond_button, 2)
    shop_surface.blit(diamond_text, (diamond_button.x + 10, diamond_button.y + 5))
    shop_surface.blit(diamond_price_text, (diamond_button.right - diamond_price_text.get_width() - 10, diamond_button.y + 5))

    idx = state['currency_multiply_index']
    if idx >= len(state['currency_multiply_levels']):
        mult_text = f"Максимум ({state['currency_multiplier']}x)"
        mult_price = "-"
        can_buy_mult = False
    else:
        mult_text = f"{state['currency_multiply_levels'][idx]}x Валюта"
        mult_price = str(state['currency_multiply_prices'][idx])
        can_buy_mult = state['score'] >= int(mult_price)
    multi_button = pygame.Rect(20, 250, 360, 40)
    pygame.draw.rect(shop_surface, green if can_buy_mult else red, multi_button)
    pygame.draw.rect(shop_surface, black, multi_button, 2)
    mult_text_surf = shop_font.render(mult_text, True, black)
    mult_price_surf = shop_font.render(f"Цена: {mult_price}", True, black)
    shop_surface.blit(mult_text_surf, (multi_button.x + 10, multi_button.y + 5))
    shop_surface.blit(mult_price_surf, (multi_button.right - mult_price_surf.get_width() - 10, multi_button.y + 5))

    act_idx = state['attack_cooldown_index']
    if act_idx == len(attack_cooldown_levels) - 1:
        atk_cd_text = "Максимум (1 сек)"
        atk_cd_price = "-"
        can_buy_atk_cd = False
    else:
        atk_cd_text = f"Скорость удара: {attack_cooldown_levels[act_idx + 1] // 1000} сек"
        atk_cd_price = str(attack_cooldown_prices[act_idx + 1])
        can_buy_atk_cd = state['score'] >= attack_cooldown_prices[act_idx + 1]
    atk_cd_button = pygame.Rect(20, 300, 360, 40)
    pygame.draw.rect(shop_surface, green if can_buy_atk_cd else red, atk_cd_button)
    pygame.draw.rect(shop_surface, black, atk_cd_button, 2)
    atk_cd_text_surf = shop_font.render(atk_cd_text, True, black)
    atk_cd_price_surf = shop_font.render(f"Цена: {atk_cd_price}", True, black)
    shop_surface.blit(atk_cd_text_surf, (atk_cd_button.x + 10, atk_cd_button.y + 5))
    shop_surface.blit(atk_cd_price_surf, (atk_cd_button.right - atk_cd_price_surf.get_width() - 10, atk_cd_button.y + 5))

    hp_idx = state['hp_regen_index']
    if hp_idx == len(hp_regen_levels) - 1:
        hp_regen_text = "Максимум (1 сек)"
        hp_regen_price = "-"
        can_buy_hp_regen = False
    else:
        hp_regen_text = f"Скорость регена HP: {hp_regen_levels[hp_idx + 1] // 1000} сек"
        hp_regen_price = str(hp_regen_prices[hp_idx + 1])
        can_buy_hp_regen = state['score'] >= hp_regen_prices[hp_idx + 1]
    hp_regen_button = pygame.Rect(20, 350, 360, 40)
    pygame.draw.rect(shop_surface, green if can_buy_hp_regen else red, hp_regen_button)
    pygame.draw.rect(shop_surface, black, hp_regen_button, 2)
    hp_regen_text_surf = shop_font.render(hp_regen_text, True, black)
    hp_regen_price_surf = shop_font.render(f"Цена: {hp_regen_price}", True, black)
    shop_surface.blit(hp_regen_text_surf, (hp_regen_button.x + 10, hp_regen_button.y + 5))
    shop_surface.blit(hp_regen_price_surf, (hp_regen_button.right - hp_regen_price_surf.get_width() - 10, hp_regen_button.y + 5))

    instr1 = shop_font.render("Нажмите F для выхода или входа ", True, black)
    shop_surface.blit(instr1, (15, 410))

    win.blit(shop_surface, (width - 400, 20))

    offset_x, offset_y = width - 400, 20
    return (hp_button.move(offset_x, offset_y), attack_button.move(offset_x, offset_y),
            money_button.move(offset_x, offset_y), diamond_button.move(offset_x, offset_y),
            multi_button.move(offset_x, offset_y), atk_cd_button.move(offset_x, offset_y),
            hp_regen_button.move(offset_x, offset_y))

def shop_menu(state):
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(state)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:  # выход из магазина
                    return state
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                (hp_button, attack_button, money_button, diamond_button,
                 multi_button, atk_cd_button, hp_regen_button) = draw_shop(state)
                if hp_button.collidepoint(mouse_pos):
                    if state['score'] >= state['base_hp_price']:
                        state['score'] -= state['base_hp_price']
                        state['hp_owned'] += 1
                        state['base_hp_price'] = int(state['base_hp_price'] * 1.2)
                        state['monkey_hp'] = 10 + state['hp_owned']
                elif attack_button.collidepoint(mouse_pos):
                    if state['score'] >= state['base_attack_price'] and state['attack_owned'] < 100:
                        state['score'] -= state['base_attack_price']
                        state['attack_owned'] += 1
                        state['attack_damage'] += 1
                        state['base_attack_price'] = int(state['base_attack_price'] * 1.3)
                elif money_button.collidepoint(mouse_pos):
                    if state['score'] >= state['current_money_price']:
                        state['score'] -= state['current_money_price']
                        state['money_owned'] += 1
                        state['current_money_price'] = int(state['current_money_price'] * 1.4)
                        # Добавляем новую позицию валюты для спавна
                        state['money_positions'].append((
                            random.randint(0, width - money_size),
                            random.randint(0, height - money_size)
                        ))
                elif diamond_button.collidepoint(mouse_pos):
                    if state['score'] >= state['current_diamond_price']:
                        state['score'] -= state['current_diamond_price']
                        state['diamond_owned'] += 1
                        state['current_diamond_price'] = int(state['current_diamond_price'] * 1.5)
                        # Добавляем новую позицию алмаза для спавна
                        state['diamond_positions'].append((
                            random.randint(0, width - diamond_size),
                            random.randint(0, height - diamond_size)
                        ))
                elif multi_button.collidepoint(mouse_pos):
                    idx = state['currency_multiply_index']
                    if idx < len(state['currency_multiply_levels']):
                        price = state['currency_multiply_prices'][idx]
                        if state['score'] >= price:
                            state['score'] -= price
                            state['currency_multiply_index'] += 1
                            state['currency_multiplier'] = state['currency_multiply_levels'][state['currency_multiply_index'] - 1]
                elif atk_cd_button.collidepoint(mouse_pos):
                    idx = state['attack_cooldown_index']
                    if idx < len(attack_cooldown_levels) - 1:
                        price = attack_cooldown_prices[idx + 1]
                        if state['score'] >= price:
                            state['score'] -= price
                            state['attack_cooldown_index'] += 1
                elif hp_regen_button.collidepoint(mouse_pos):
                    idx = state['hp_regen_index']
                    if idx < len(hp_regen_levels) - 1:
                        price = hp_regen_prices[idx + 1]
                        if state['score'] >= price:
                            state['score'] -= price
                            state['hp_regen_index'] += 1

        if game_bg_image:
            win.blit(game_bg_image, (0, 0))
        else:
            win.fill(gray)

        draw_shop(state)
        pygame.display.update()

def draw_power_choice():
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    win.blit(overlay, (0, 0))
    title = font.render("Выберите суперсилу (только на 2 уровне):", True, white)
    win.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 120))
    opt1 = font.render("1 — Огонь: +5 урона и поджог (DoT)", True, white)
    opt2 = font.render("2 — Земля: -30% входящего урона", True, white)
    opt3 = font.render("3 — Чёрная магия: 20% вампиризм", True, white)
    win.blit(opt1, (width // 2 - opt1.get_width() // 2, height // 2 - 60))
    win.blit(opt2, (width // 2 - opt2.get_width() // 2, height // 2 - 20))
    win.blit(opt3, (width // 2 - opt3.get_width() // 2, height // 2 + 20))

def game_loop_with_state(state):
    global speed
    shop_open = False
    end_message = ""

    while True:
        clock.tick(30)
        current_time = pygame.time.get_ticks()

        move_x, move_y = 0, 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(state)
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if state.get('confirm_exit'):
                    if event.key == pygame.K_1:
                        save_game(state)
                        return  # в главное меню
                    elif event.key == pygame.K_2:
                        save_game(state)
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_ESCAPE:
                        state['confirm_exit'] = False
                    continue
                if event.key == pygame.K_f:
                    shop_open = not shop_open
                if state['alive'] and not shop_open:
                    if event.key == pygame.K_ESCAPE:
                        state['confirm_exit'] = True
                    elif event.key == pygame.K_TAB:
                        password = input_password()
                        if password == "1306":
                            admin_menu(state)
                        move_x, move_y = 0, 0
                    elif event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                        state['last_dir_key'] = event.key
                        state['last_dir_time'] = pygame.time.get_ticks()
                        if event.key == pygame.K_a:
                            state['move_x'] = -speed
                            state['move_y'] = 0
                        elif event.key == pygame.K_d:
                            state['move_x'] = speed
                            state['move_y'] = 0
                        elif event.key == pygame.K_w:
                            state['move_x'] = 0
                            state['move_y'] = -speed
                        elif event.key == pygame.K_s:
                            state['move_x'] = 0
                            state['move_y'] = speed

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and shop_open:
                mouse_pos = pygame.mouse.get_pos()
                (hp_button, attack_button, money_button, diamond_button,
                 multi_button, atk_cd_button, hp_regen_button) = draw_shop(state)
                if hp_button.collidepoint(mouse_pos):
                    if state['score'] >= state['base_hp_price']:
                        state['score'] -= state['base_hp_price']
                        state['hp_owned'] += 1
                        state['base_hp_price'] = int(state['base_hp_price'] * 1.2)
                        state['monkey_hp'] = 10 + state['hp_owned']
                elif attack_button.collidepoint(mouse_pos):
                    if state['score'] >= state['base_attack_price'] and state['attack_owned'] < 100:
                        state['score'] -= state['base_attack_price']
                        state['attack_owned'] += 1
                        state['attack_damage'] += 1
                        state['base_attack_price'] = int(state['base_attack_price'] * 1.3)
                elif money_button.collidepoint(mouse_pos):
                    if state['score'] >= state['current_money_price']:
                        state['score'] -= state['current_money_price']
                        state['money_owned'] += 1
                        state['current_money_price'] = int(state['current_money_price'] * 1.4)
                        state['money_positions'].append((
                            random.randint(0, width - money_size),
                            random.randint(0, height - money_size)
                        ))
                elif diamond_button.collidepoint(mouse_pos):
                    if state['score'] >= state['current_diamond_price']:
                        state['score'] -= state['current_diamond_price']
                        state['diamond_owned'] += 1
                        state['current_diamond_price'] = int(state['current_diamond_price'] * 1.5)
                        state['diamond_positions'].append((
                            random.randint(0, width - diamond_size),
                            random.randint(0, height - diamond_size)
                        ))
                elif multi_button.collidepoint(mouse_pos):
                    idx = state['currency_multiply_index']
                    if idx < len(state['currency_multiply_levels']):
                        price = state['currency_multiply_prices'][idx]
                        if state['score'] >= price:
                            state['score'] -= price
                            state['currency_multiply_index'] += 1
                            state['currency_multiplier'] = state['currency_multiply_levels'][state['currency_multiply_index'] - 1]
                elif atk_cd_button.collidepoint(mouse_pos):
                    idx = state['attack_cooldown_index']
                    if idx < len(attack_cooldown_levels) - 1:
                        price = attack_cooldown_prices[idx + 1]
                        if state['score'] >= price:
                            state['score'] -= price
                            state['attack_cooldown_index'] += 1
                elif hp_regen_button.collidepoint(mouse_pos):
                    idx = state['hp_regen_index']
                    if idx < len(hp_regen_levels) - 1:
                        price = hp_regen_prices[idx + 1]
                        if state['score'] >= price:
                            state['score'] -= price
                            state['hp_regen_index'] += 1

            elif event.type == pygame.KEYUP:
                pass

        # Пауза, если магазин открыт или диалог выхода
        if shop_open or state.get('confirm_exit'):
            if game_bg_image:
                win.blit(game_bg_image, (0, 0))
            else:
                win.fill(gray)
            for (mx, my) in state['money_positions']:
                draw_money(mx, my)
            for (dx, dy) in state['diamond_positions']:
                draw_diamond(dx, dy)
            draw_enemy(state['enemy_x'], state['enemy_y'], state['enemy_hp'], state['enemy_attack'], state['enemy_image'])
            draw_monster(state['x'], state['y'])
            draw_health_bar(state['x'], state['y'] - 15, state['monkey_hp'], 20, monster_size, 10)
            draw_health_bar(state['enemy_x'], state['enemy_y'] - 15, state['enemy_hp'], 20, enemy_size, 10)
            show_score(state['score'], state['monkey_hp'], state['attack_damage'], len(state['money_positions']), len(state['diamond_positions']), state['currency_multiplier'])
            if shop_open:
                draw_shop(state)
            if state.get('confirm_exit'):
                overlay = pygame.Surface((width, height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                win.blit(overlay, (0, 0))
                title = font.render("Выйти?", True, white)
                opt1 = font.render("1 — Главное меню", True, white)
                opt2 = font.render("2 — Выйти из игры", True, white)
                opt3 = font.render("Esc — Отмена", True, white)
                win.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 100))
                win.blit(opt1, (width // 2 - opt1.get_width() // 2, height // 2 - 40))
                win.blit(opt2, (width // 2 - opt2.get_width() // 2, height // 2))
                win.blit(opt3, (width // 2 - opt3.get_width() // 2, height // 2 + 40))
            pygame.display.update()
            continue

        # Обновление позиции игрока
        state['x'] += state.get('move_x', 0)
        state['y'] += state.get('move_y', 0)
        state['x'] = max(0, min(state['x'], width - monster_size))
        state['y'] = max(0, min(state['y'], height - monster_size))

        # Движение врага к игроку
        state['enemy_x'], state['enemy_y'] = move_enemy_towards_monster(
            state['enemy_x'], state['enemy_y'], state['x'], state['y']
        )
        monster_rect = pygame.Rect(state['x'], state['y'], monster_size, monster_size)
        enemy_rect = pygame.Rect(state['enemy_x'], state['enemy_y'], enemy_size, enemy_size)

        # Обработка валют и алмазов
        for i in range(len(state['money_positions'])):
            mx, my = state['money_positions'][i]
            money_rect = pygame.Rect(mx, my, money_size, money_size)
            if monster_rect.colliderect(money_rect):
                state['score'] += 2 * state['currency_multiplier']
                state['money_positions'][i] = (random.randint(0, width - money_size), random.randint(0, height - money_size))

        for i in range(len(state['diamond_positions'])):
            dx, dy = state['diamond_positions'][i]
            diamond_rect = pygame.Rect(dx, dy, diamond_size, diamond_size)
            if monster_rect.colliderect(diamond_rect):
                state['score'] += 4 * state['currency_multiplier']
                state['diamond_positions'][i] = (random.randint(0, width - diamond_size), random.randint(0, height - diamond_size))

        if monster_rect.colliderect(enemy_rect):
            if current_time - state['last_monkey_attack_time'] >= attack_cooldown_levels[state['attack_cooldown_index']]:
                dmg = state['attack_damage']
                state['enemy_hp'] -= dmg
                state['last_monkey_attack_time'] = current_time

            if current_time - state['last_enemy_attack_time'] >= 1000:
                incoming = state['enemy_attack']
                state['monkey_hp'] -= incoming
                state['last_enemy_attack_time'] = current_time

        # Проверка смерти врага и респавн с переходом на следующий уровень
        if state['enemy_hp'] <= 0:
            # Переход к следующему уровню врага, если есть
            if state['enemy_level'] < len(enemies) - 1:
                state['enemy_level'] += 1
            enemy_data = enemies[state['enemy_level']]
            state['enemy_hp'] = enemy_data["hp"]
            state['enemy_attack'] = enemy_data["attack"]
            state['enemy_image'] = enemy_data["image"]
            state['enemy_x'] = random.randint(0, width - enemy_size)
            state['enemy_y'] = random.randint(0, height - enemy_size)

            # Награды игроку
            state['monkey_hp'] += 5
            state['attack_damage'] += 5

        if state['monkey_hp'] <= 0:
            state['alive'] = False
            end_message = "Пещерный монстр убит!"

        if game_bg_image:
            win.blit(game_bg_image, (0, 0))
        else:
            win.fill(gray)

        for (mx, my) in state['money_positions']:
            draw_money(mx, my)
        for (dx, dy) in state['diamond_positions']:
            draw_diamond(dx, dy)

        draw_enemy(state['enemy_x'], state['enemy_y'], state['enemy_hp'], state['enemy_attack'], state['enemy_image'])
        draw_monster(state['x'], state['y'])
        draw_health_bar(state['x'], state['y'] - 15, state['monkey_hp'], 20, monster_size, 10)
        draw_health_bar(state['enemy_x'], state['enemy_y'] - 15, state['enemy_hp'], 20, enemy_size, 10)

        show_score(state['score'], state['monkey_hp'], state['attack_damage'], len(state['money_positions']),
                   len(state['diamond_positions']), state['currency_multiplier'])

        if shop_open:
            draw_shop(state)

        if not state['alive']:
            show_game_over(end_message)

        shop_button_rect = pygame.Rect(width - 240, 10, 230, 35)
        pygame.draw.rect(win, (*shop_bg_color, 220), shop_button_rect)
        pygame.draw.rect(win, black, shop_button_rect, 2)
        shop_text = shop_font.render("МАГАЗИН", True, black)
        win.blit(shop_text, (width - 230, 15))

        pygame.display.update()


def main():
    load_enemy_images()
    while True:
        loaded_state = menu()
        if loaded_state is None:
            state = reset_game()
        else:
            state = loaded_state
        game_loop_with_state(state)


if __name__ == "__main__":
    main()
