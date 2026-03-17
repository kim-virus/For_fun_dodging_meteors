import pygame
import random
import sys

# ──────────────────────────────────────────────
# 상수 설정 (Constants)
# ──────────────────────────────────────────────
SCREEN_WIDTH  = 600
SCREEN_HEIGHT = 700
FPS           = 60
TITLE         = "dodging meteors"

# 색상
WHITE   = (255, 255, 255)
BLACK   = (  0,   0,   0)
GRAY    = (180, 180, 180)
SKYBLUE = ( 30,  30,  60)   # 배경색

PLAYER_COLOR = ( 50, 200, 255)
METEOR_COLOR = (200,  80,  40)
TEXT_COLOR   = (255, 255, 200)

# 플레이어
PLAYER_WIDTH  = 50
PLAYER_HEIGHT = 30
PLAYER_SPEED  = 6

# 운석
METEOR_WIDTH      = 40
METEOR_HEIGHT     = 40
METEOR_INIT_SPEED = 10     # 초기 낙하 속도
METEOR_SPEED_MAX  = 100     # 최대 낙하 속도
SPEED_INCREMENT   = 0.004  # 매 프레임마다 속도 증가량 (난이도 곡선)
SPAWN_INTERVAL    = 90     # 운석 생성 간격 (프레임 단위)
SPAWN_MIN_GAP     = 30     # 생성 간격 최솟값 (프레임)


# ──────────────────────────────────────────────
# 3단계: Player 클래스
# ──────────────────────────────────────────────
class Player:
    def __init__(self):
        self.width  = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH  // 2 - self.width  // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = PLAYER_SPEED
        self.rect  = pygame.Rect(self.x, self.y, self.width, self.height)

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed

        # 화면 경계 제한
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.rect.x = self.x

    def draw(self, surface):
        # ── 이미지 사용 시 아래 주석을 해제하고 색상 사각형 코드를 제거하세요 ──
        # img = pygame.image.load("assets/player.png").convert_alpha()
        # img = pygame.transform.scale(img, (self.width, self.height))
        # surface.blit(img, (self.x, self.y))
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect, border_radius=6)
        # 간단한 디테일 (조종석 효과)
        cockpit = pygame.Rect(self.x + self.width // 2 - 8, self.y - 12, 16, 14)
        pygame.draw.rect(surface, (100, 230, 255), cockpit, border_radius=4)


# ──────────────────────────────────────────────
# 4단계: Meteor 클래스
# ──────────────────────────────────────────────
class Meteor:
    def __init__(self, speed):
        self.width  = METEOR_WIDTH
        self.height = METEOR_HEIGHT
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height          # 화면 위에서 시작
        self.speed  = speed
        self.passed = False            # 점수 처리 여부
        self.rect   = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

    def draw(self, surface):
        # ── 이미지 사용 시 아래 주석을 해제하고 색상 사각형 코드를 제거하세요 ──
        # img = pygame.image.load("assets/meteor.png").convert_alpha()
        # img = pygame.transform.scale(img, (self.width, self.height))
        # surface.blit(img, (self.x, self.y))
        pygame.draw.ellipse(surface, METEOR_COLOR, self.rect)
        # 간단한 하이라이트
        highlight = pygame.Rect(self.x + 8, self.y + 6, 10, 6)
        pygame.draw.ellipse(surface, (230, 140, 80), highlight)


# ──────────────────────────────────────────────
# 5단계: MeteorSpawner 클래스
# ──────────────────────────────────────────────
class MeteorSpawner:
    def __init__(self):
        self.timer    = 0
        self.interval = SPAWN_INTERVAL   # 현재 생성 간격 (프레임)

    def update(self, meteors, current_speed):
        self.timer += 1
        if self.timer >= self.interval:
            self.timer = 0
            meteors.append(Meteor(current_speed))
            # 난이도가 오를수록 생성 간격 단축
            self.interval = max(SPAWN_MIN_GAP, SPAWN_INTERVAL - int(current_speed) * 4)


# ──────────────────────────────────────────────
# 9단계: 게임 상태 관리 + 전체 게임 클래스
# ──────────────────────────────────────────────
class Game:
    STATE_PLAYING   = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock   = pygame.time.Clock()

        # 폰트
        self.font_large  = pygame.font.SysFont(None, 64)
        self.font_medium = pygame.font.SysFont(None, 38)
        self.font_small  = pygame.font.SysFont(None, 28)

        self._reset()

    def _reset(self):
        self.state         = Game.STATE_PLAYING
        self.player        = Player()
        self.meteors       = []
        self.spawner       = MeteorSpawner()
        self.score         = 0
        self.current_speed = METEOR_INIT_SPEED   # 8단계: 난이도 속도 변수

    # ── 6단계: 충돌 판정 ──────────────────────
    def _check_collisions(self):
        for meteor in self.meteors:
            if self.player.rect.colliderect(meteor.rect):
                self.state = Game.STATE_GAME_OVER

    # ── 7단계: 점수 처리 ──────────────────────
    def _update_score(self):
        for meteor in self.meteors:
            if not meteor.passed and meteor.y > self.player.y + PLAYER_HEIGHT:
                meteor.passed = True
                self.score += 1

    # ── 8단계: 난이도 상승 ────────────────────
    def _update_difficulty(self):
        if self.current_speed < METEOR_SPEED_MAX:
            self.current_speed += SPEED_INCREMENT

    # ── 이벤트 처리 ──────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == Game.STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self._reset()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    # ── 업데이트 ─────────────────────────────
    def _update(self):
        if self.state != Game.STATE_PLAYING:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        self._update_difficulty()
        self.spawner.update(self.meteors, self.current_speed)

        for meteor in self.meteors:
            meteor.update()

        # 화면 아래로 벗어난 운석 제거
        self.meteors = [m for m in self.meteors if not m.is_off_screen()]

        self._update_score()
        self._check_collisions()

    # ── 렌더링 ───────────────────────────────
    def _draw_playing(self):
        self.screen.fill(SKYBLUE)
        self.player.draw(self.screen)
        for meteor in self.meteors:
            meteor.draw(self.screen)

        # HUD: 점수
        score_surf = self.font_medium.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_surf, (10, 10))

        # HUD: 현재 속도 (난이도 확인용)
        spd_surf = self.font_small.render(
            f"Speed: {self.current_speed:.1f}", True, GRAY
        )
        self.screen.blit(spd_surf, (10, 46))

    def _draw_game_over(self):
        self.screen.fill(BLACK)

        title_surf = self.font_large.render("GAME OVER", True, METEOR_COLOR)
        score_surf = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        restart_surf = self.font_small.render("R  — 다시 시작", True, GRAY)
        quit_surf    = self.font_small.render("ESC — 종료", True, GRAY)

        cx = SCREEN_WIDTH // 2
        self.screen.blit(title_surf,   title_surf.get_rect(center=(cx, 230)))
        self.screen.blit(score_surf,   score_surf.get_rect(center=(cx, 310)))
        self.screen.blit(restart_surf, restart_surf.get_rect(center=(cx, 390)))
        self.screen.blit(quit_surf,    quit_surf.get_rect(center=(cx, 425)))

    def _draw(self):
        if self.state == Game.STATE_PLAYING:
            self._draw_playing()
        elif self.state == Game.STATE_GAME_OVER:
            self._draw_game_over()
        pygame.display.flip()

    # ── 메인 루프 (2단계: 게임 루프) ─────────
    def run(self):
        while True:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)   # 2단계: FPS 고정


# ──────────────────────────────────────────────
# 진입점
# ──────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()
