import pygame

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("5픽셀 단위 이동 시스템")
clock = pygame.time.Clock()

# 색상 및 속성
BLUE = (0, 120, 255)
WHITE = (255, 255, 255)

# 2. 도형 객체 설정
pos_x, pos_y = WIDTH // 2, HEIGHT // 2
speed = 5  # 한 번에 움직일 거리 (5픽셀)
radius = 25

running = True
while running:
    screen.fill(WHITE)
    
    # 3. 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 4. 동시 키 입력 감지 (5픽셀씩 즉시 반영)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  pos_x -= speed
    if keys[pygame.K_RIGHT]: pos_x += speed
    if keys[pygame.K_UP]:    pos_y -= speed
    if keys[pygame.K_DOWN]:  pos_y += speed

    # 5. 화면 밖으로 나가지 못하게 제한 (경계 처리)
    # x축 제한
    if pos_x < radius:
        pos_x = radius
    elif pos_x > WIDTH - radius:
        pos_x = WIDTH - radius
        
    # y축 제한
    if pos_y < radius:
        pos_y = radius
    elif pos_y > HEIGHT - radius:
        pos_y = HEIGHT - radius

    # 6. 그리기
    pygame.draw.circle(screen, BLUE, (int(pos_x), int(pos_y)), radius)
    
    pygame.display.flip()
    clock.tick(60) # 초당 60프레임 (부드러운 화면 유지를 위해 필요)

pygame.quit()