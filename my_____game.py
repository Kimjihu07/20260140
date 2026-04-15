import pygame
import random
import sys
import os

# ==== 1. 파이게임 초기화 및 최고기록 로드 ====
pygame.init()

SCORE_FILE = "highscore.txt"
def load_highscore():
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_highscore(score):
    with open(SCORE_FILE, "w") as f:
        f.write(str(score))

# 2. 기본 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("전설의 똥 피하기 💩 - 마우스 마스터 에디션")
clock = pygame.time.Clock()

render_surf = pygame.Surface((WIDTH, HEIGHT))

# 3. 색상 팔레트
WHITE = (255, 255, 255)
BLACK = (30, 30, 40)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 220, 0)
RED = (255, 50, 50)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
GRAY = (150, 150, 150)
PURPLE = (160, 32, 240) 

# 4. 폰트 설정
font_large = pygame.font.SysFont("malgungothic", 80)
font_medium = pygame.font.SysFont("malgungothic", 40)
font_small = pygame.font.SysFont("malgungothic", 30)
font_mini = pygame.font.SysFont("malgungothic", 20)

def draw_text(surf, text, font, color, x, y, center=True):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center: rect.center = (x, y)
    else: rect.topleft = (x, y)
    surf.blit(surface, rect)

def draw_poop(surf, x, y, size):
    center_x = int(x + size // 2)
    pygame.draw.circle(surf, BROWN, (center_x, int(y + size - size * 0.2)), int(size // 2))
    pygame.draw.circle(surf, BROWN, (center_x, int(y + size // 2)), int(size * 0.4))
    pygame.draw.circle(surf, BROWN, (center_x, int(y + size * 0.2)), int(size * 0.25))

def draw_player(surf, x, y, size, is_hurt, is_dashing, is_exhausted):
    if is_dashing and not is_hurt and not is_exhausted:
        pygame.draw.circle(surf, (255, 255, 150), (int(x), int(y)), size // 2 + 5, 2)
        
    body_color = (200, 180, 0) if is_exhausted else YELLOW
    pygame.draw.circle(surf, body_color, (int(x), int(y)), size // 2)
    
    if is_hurt:
        pygame.draw.line(surf, BLACK, (x - 8, y - 8), (x - 2, y - 2), 2)
        pygame.draw.line(surf, BLACK, (x - 2, y - 8), (x - 8, y - 2), 2)
        pygame.draw.line(surf, BLACK, (x + 2, y - 8), (x + 8, y - 2), 2)
        pygame.draw.line(surf, BLACK, (x + 8, y - 8), (x + 2, y - 2), 2)
    elif is_exhausted:
        pygame.draw.line(surf, BLACK, (x - 8, y - 5), (x - 2, y - 5), 2)
        pygame.draw.line(surf, BLACK, (x + 2, y - 5), (x + 8, y - 5), 2)
        pygame.draw.circle(surf, BLACK, (int(x), int(y) + 5), 3)
    else:
        pygame.draw.circle(surf, BLACK, (int(x) - 5, int(y) - 5), 3)
        pygame.draw.circle(surf, BLACK, (int(x) + 5, int(y) - 5), 3)
        mouth_size = 6 if is_dashing else 4
        pygame.draw.circle(surf, BLACK, (int(x), int(y) + 5), mouth_size)

def draw_heart(surf, x, y, size):
    pygame.draw.circle(surf, RED, (x - size//4, y - size//4), size//4)
    pygame.draw.circle(surf, RED, (x + size//4, y - size//4), size//4)
    pygame.draw.polygon(surf, RED, [(x - size//2, y - size//4 + 1), (x + size//2, y - size//4 + 1), (x, y + size//2)])

def spawn_particles(particles, x, y, color, count=10, speed_mult=1.0):
    for _ in range(count):
        particles.append({
            'x': x, 'y': y,
            'dx': random.uniform(-5, 5) * speed_mult, 
            'dy': random.uniform(-8, -2) * speed_mult,
            'life': random.randint(20, 40), 
            'color': color, 
            'size': random.randint(4, 8)
        })

def main():
    global screen
    
    state = "MENU"
    is_fullscreen = False
    high_score = load_highscore()
    new_record = False

    player_size = 40
    player_x = WIDTH // 2
    player_y = HEIGHT - 50
    base_speed = 8
    dash_speed = 16
    hp = 3
    max_hp = 3
    invincible_timer = 0
    
    max_stamina = 100.0
    stamina = max_stamina
    stamina_drain = 3.0
    stamina_regen = 0.6
    exhausted_timer = 0

    max_time_power = 100.0
    time_power = max_time_power
    time_drain = 1.2
    time_regen = 0.2

    poops = []
    items = []
    particles = []
    giant_warnings = []
    clouds = [[random.randint(0, WIDTH), random.randint(50, 300), random.randint(40, 80), random.uniform(0.5, 1.5)] for _ in range(5)]

    score = 0
    virtual_frame = 0.0
    screen_shake = 0

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN) if is_fullscreen else pygame.display.set_mode((WIDTH, HEIGHT))
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "MENU":
                    state = "PLAY"
                elif state == "GAMEOVER":
                    main(); return

        if state == "PLAY":
            if invincible_timer > 0: invincible_timer -= 1
            if screen_shake > 0: screen_shake -= 1

            # --- 마우스 조작 기반 이동 및 스킬 로직 ---
            is_slowmo = mouse_buttons[2] and time_power > 0 and exhausted_timer == 0 # 우클릭
            
            if is_slowmo:
                game_speed = 0.3
                time_power -= time_drain
                if time_power < 0: time_power = 0
            else:
                game_speed = 1.0
                time_power = min(max_time_power, time_power + time_regen)

            virtual_frame += game_speed
            current_v_frame = int(virtual_frame)

            # --- 플레이어 이동 (마우스 추적) ---
            if exhausted_timer > 0:
                exhausted_timer -= 1
                stamina += stamina_regen
                is_dashing = False
            else:
                wants_dash = mouse_buttons[0] # 좌클릭
                if wants_dash and stamina > 0:
                    is_dashing = True
                    current_speed = dash_speed
                    stamina -= stamina_drain
                    if stamina <= 0:
                        stamina = 0
                        exhausted_timer = 40
                else:
                    is_dashing = False
                    current_speed = base_speed
                    stamina += stamina_regen
                    stamina = min(max_stamina, stamina)

                # 마우스 커서 방향으로 이동
                dx = mouse_pos[0] - player_x
                if abs(dx) > 5: # 미세 떨림 방지
                    move_dist = min(abs(dx), current_speed)
                    player_x += (1 if dx > 0 else -1) * move_dist

            # 경계 제한
            player_x = max(player_size // 2, min(WIDTH - player_size // 2, player_x))

            # --- 게임 로직 (똥 생성, 충돌 등) ---
            # (기존 로직 유지, 가상 프레임 기반)
            spawn_rate = max(4, 25 - (score // 300))
            if int(virtual_frame) > int(virtual_frame - game_speed):
                if current_v_frame % spawn_rate == 0:
                    size = random.randint(30, 60)
                    speed = random.uniform(5, 9) + (score // 400)
                    poops.append({'x': random.randint(0, WIDTH - size), 'y': -size, 'size': size, 'speed': speed})

                if score > 500 and current_v_frame % 400 == 0:
                    warning_x = random.randint(0, WIDTH - 180)
                    giant_warnings.append({'x': warning_x, 'timer': 100, 'size': 180})

                if current_v_frame % 200 == 0:
                    item_type = 'heart' if random.random() < 0.15 and hp < max_hp else 'coin'
                    items.append({'x': random.randint(20, WIDTH - 20), 'y': -30, 'size': 20, 'speed': 4, 'type': item_type})

            # 경보 및 똥 이동/충돌 처리
            alive_warnings = []
            for w in giant_warnings:
                w['timer'] -= game_speed
                if w['timer'] <= 0:
                    poops.append({'x': w['x'], 'y': -w['size'], 'size': w['size'], 'speed': 18.0})
                    screen_shake = 10
                else: alive_warnings.append(w)
            giant_warnings = alive_warnings

            player_rect = pygame.Rect(player_x - 15, player_y - 15, 30, 30)

            alive_poops = []
            for p in poops:
                p['y'] += p['speed'] * game_speed
                padding = 20 if p['size'] < 100 else 40
                poop_rect = pygame.Rect(p['x'] + padding//2, p['y'] + padding//2, p['size'] - padding, p['size'] - padding)
                
                if player_rect.colliderect(poop_rect) and invincible_timer == 0:
                    hp -= 1
                    invincible_timer = 90
                    screen_shake = 25      
                    spawn_particles(particles, player_x, player_y, BROWN, 40)
                    if hp <= 0:
                        state = "GAMEOVER"
                        if score > high_score:
                            high_score = score
                            save_highscore(high_score)
                            new_record = True
                elif p['y'] > HEIGHT:
                    score += 50 if p['size'] > 100 else 10
                    spawn_particles(particles, p['x'] + p['size']//2, HEIGHT, (100, 80, 60), 5 if p['size'] < 100 else 30)
                else: alive_poops.append(p)
            poops = alive_poops

            # 아이템/파티클/구름 (기존 로직)
            items = [i for i in items if i['y'] < HEIGHT]
            for i in items:
                i['y'] += i['speed'] * game_speed
                if player_rect.colliderect(pygame.Rect(i['x']-20, i['y']-20, 40, 40)):
                    if i['type'] == 'coin': score += 100
                    else: hp = min(max_hp, hp + 1)
                    i['y'] = HEIGHT + 100

            alive_particles = []
            for p in particles:
                p['x'] += p['dx'] * game_speed
                p['y'] += p['dy'] * game_speed
                p['dy'] += 0.3 * game_speed
                p['life'] -= game_speed
                if p['life'] > 0: alive_particles.append(p)
            particles = alive_particles

            for c in clouds:
                c[0] += c[3] * game_speed
                if c[0] - c[2] > WIDTH: c[0] = -c[2]

        # ==== 3. 화면 그리기 ====
        render_surf.fill(SKY_BLUE)
        for c in clouds: pygame.draw.circle(render_surf, WHITE, (int(c[0]), int(c[1])), c[2])

        if state == "MENU":
            draw_text(render_surf, "MOUSE MASTER DODGE", font_large, BROWN, WIDTH//2, HEIGHT//2 - 120)
            draw_text(render_surf, f"HIGH SCORE: {high_score}", font_small, GOLD, WIDTH//2, HEIGHT//2 - 60)
            draw_text(render_surf, "클릭하여 시작하세요!", font_medium, BLACK, WIDTH//2, HEIGHT//2)
            draw_text(render_surf, "이동: 마우스 커서", font_small, BLACK, WIDTH//2, HEIGHT//2 + 60)
            draw_text(render_surf, "부스터: 마우스 좌클릭", font_small, RED, WIDTH//2, HEIGHT//2 + 95)
            draw_text(render_surf, "슬로우 모션: 마우스 우클릭", font_small, PURPLE, WIDTH//2, HEIGHT//2 + 130)

        elif state in ["PLAY", "GAMEOVER"]:
            # 경보/아이템/똥/플레이어 그리기 (기존 로직 유지)
            for w in giant_warnings:
                s = pygame.Surface((w['size'], HEIGHT), pygame.SRCALPHA)
                s.fill((255, 0, 0, 100))
                render_surf.blit(s, (w['x'], 0))
            
            for i in items:
                if i['type'] == 'coin': pygame.draw.circle(render_surf, GOLD, (int(i['x']), int(i['y'])), i['size'])
                else: draw_heart(render_surf, int(i['x']), int(i['y']), i['size'] * 2)

            for p in poops: draw_poop(render_surf, p['x'], p['y'], p['size'])
            for p in particles: pygame.draw.rect(render_surf, p['color'], (int(p['x']), int(p['y']), p['size'], p['size']))

            if invincible_timer == 0 or (invincible_timer // 5) % 2 == 0:
                draw_player(render_surf, player_x, player_y, player_size, invincible_timer > 0, is_dashing, exhausted_timer > 0)

            if state == "PLAY" and is_slowmo:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 40, 70))
                render_surf.blit(overlay, (0, 0))
                draw_text(render_surf, "SLOW MOTION", font_medium, CYAN, WIDTH // 2, 80)

            # UI
            draw_text(render_surf, f"SCORE: {score}", font_medium, BLACK, 20, 20, center=False)
            pygame.draw.rect(render_surf, BLACK, (20, 75, 154, 15), border_radius=5)
            pygame.draw.rect(render_surf, (CYAN if exhausted_timer==0 else GRAY), (22, 77, int(stamina*1.5), 11), border_radius=5)
            pygame.draw.rect(render_surf, BLACK, (20, 100, 154, 15), border_radius=5)
            pygame.draw.rect(render_surf, PURPLE, (22, 102, int(time_power*1.5), 11), border_radius=5)
            
            for i in range(max_hp):
                x_pos = WIDTH - 120 + (i * 40)
                if i < hp: draw_heart(render_surf, x_pos, 40, 30)
                else: pygame.draw.circle(render_surf, (100, 100, 100), (x_pos, 40), 10)

        if state == "GAMEOVER":
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.fill(BLACK); overlay.set_alpha(180)
            render_surf.blit(overlay, (0, 0))
            draw_text(render_surf, "GAME OVER", font_large, RED, WIDTH // 2, HEIGHT // 2 - 50)
            draw_text(render_surf, f"SCORE: {score} {' (NEW!)' if new_record else ''}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text(render_surf, "다시 하려면 클릭하세요", font_small, YELLOW, WIDTH // 2, HEIGHT // 2 + 80)

        # 화면 출력 (쉐이크 효과 포함)
        off_x = random.randint(-screen_shake, screen_shake)
        off_y = random.randint(-screen_shake, screen_shake)
        screen.fill(BLACK)
        screen.blit(render_surf, (off_x, off_y))
        pygame.display.flip()

if __name__ == "__main__":
    main()