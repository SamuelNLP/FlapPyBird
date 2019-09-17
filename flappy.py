from itertools import cycle
import random
import sys

import pygame
from pygame.constants import QUIT, K_ESCAPE, KEYDOWN, K_SPACE, K_UP

FPS = 30
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
PIPE_GAP_SIZE = 100  # gap between upper and lower part of pipe
BASE_Y = SCREEN_HEIGHT * 0.79
# image, sound and hit mask  dicts
IMAGES, SOUNDS, HIT_MASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        "assets/sprites/redbird-upflap.png",
        "assets/sprites/redbird-midflap.png",
        "assets/sprites/redbird-downflap.png",
    ),
    # blue bird
    (
        "assets/sprites/bluebird-upflap.png",
        "assets/sprites/bluebird-midflap.png",
        "assets/sprites/bluebird-downflap.png",
    ),
    # yellow bird
    (
        "assets/sprites/yellowbird-upflap.png",
        "assets/sprites/yellowbird-midflap.png",
        "assets/sprites/yellowbird-downflap.png",
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    "assets/sprites/background-day.png",
    "assets/sprites/background-night.png",
)

# list of pipes
PIPES_LIST = ("assets/sprites/pipe-green.png", "assets/sprites/pipe-red.png")


def main():
    global SCREEN, FPS_CLOCK
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird")

    # numbers sprites for score display
    IMAGES["numbers"] = (
        pygame.image.load("assets/sprites/0.png").convert_alpha(),
        pygame.image.load("assets/sprites/1.png").convert_alpha(),
        pygame.image.load("assets/sprites/2.png").convert_alpha(),
        pygame.image.load("assets/sprites/3.png").convert_alpha(),
        pygame.image.load("assets/sprites/4.png").convert_alpha(),
        pygame.image.load("assets/sprites/5.png").convert_alpha(),
        pygame.image.load("assets/sprites/6.png").convert_alpha(),
        pygame.image.load("assets/sprites/7.png").convert_alpha(),
        pygame.image.load("assets/sprites/8.png").convert_alpha(),
        pygame.image.load("assets/sprites/9.png").convert_alpha(),
    )

    # game over sprite
    IMAGES["game_over"] = pygame.image.load(
        "assets/sprites/game_over.png"
    ).convert_alpha()
    # message sprite for welcome screen
    IMAGES["message"] = pygame.image.load(
        "assets/sprites/message.png"
    ).convert_alpha()
    # base (ground) sprite
    IMAGES["base"] = pygame.image.load(
        "assets/sprites/base.png"
    ).convert_alpha()

    sound_ext = ".ogg"

    SOUNDS["die"] = pygame.mixer.Sound("assets/audio/die" + sound_ext)
    SOUNDS["hit"] = pygame.mixer.Sound("assets/audio/hit" + sound_ext)
    SOUNDS["point"] = pygame.mixer.Sound("assets/audio/point" + sound_ext)
    SOUNDS["swoosh"] = pygame.mixer.Sound("assets/audio/swoosh" + sound_ext)
    SOUNDS["wing"] = pygame.mixer.Sound("assets/audio/wing" + sound_ext)

    while True:
        # select random background sprites
        rand_bg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES["background"] = pygame.image.load(
            BACKGROUNDS_LIST[rand_bg]
        ).convert()

        # select random player sprites
        rand_player = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES["player"] = (
            pygame.image.load(PLAYERS_LIST[rand_player][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[rand_player][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[rand_player][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipe_index = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES["pipe"] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipe_index]).convert_alpha(),
                False,
                True,
            ),
            pygame.image.load(PIPES_LIST[pipe_index]).convert_alpha(),
        )

        # hit_mask for pipes
        HIT_MASKS["pipe"] = (
            get_hit_mask(IMAGES["pipe"][0]),
            get_hit_mask(IMAGES["pipe"][1]),
        )

        # hit_mask for player
        HIT_MASKS["player"] = (
            get_hit_mask(IMAGES["player"][0]),
            get_hit_mask(IMAGES["player"][1]),
            get_hit_mask(IMAGES["player"][2]),
        )

        movement_info = show_welcome_animation()
        crash_info = main_game(movement_info)
        show_game_over_screen(crash_info)


def show_welcome_animation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to show on screen
    player_index = 0
    player_index_gen = cycle([0, 1, 2, 1])
    # iterator used to change player_index after every 5th iteration
    loop_iter = 0

    player_x = int(SCREEN_WIDTH * 0.2)
    player_y = int((SCREEN_HEIGHT - IMAGES["player"][0].get_height()) / 2)

    message_x = int((SCREEN_WIDTH - IMAGES["message"].get_width()) / 2)
    message_y = int(SCREEN_HEIGHT * 0.12)

    base_x = 0
    # amount by which base can maximum shift to left
    base_shift = IMAGES["base"].get_width() - IMAGES["background"].get_width()

    # player shm for up-down motion on welcome screen
    player_shm_vals = {"val": 0, "dir": 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (
                event.type == KEYDOWN and event.key == K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (
                event.key == K_SPACE or event.key == K_UP
            ):
                # make first flap sound and return values for mainGame
                SOUNDS["wing"].play()
                return {
                    "player_y": player_y + player_shm_vals["val"],
                    "base_x": base_x,
                    "player_index_gen": player_index_gen,
                }

        # adjust player_y, player_index, base_x
        if (loop_iter + 1) % 5 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 4) % base_shift)
        player_shm(player_shm_vals)

        # draw sprites
        SCREEN.blit(IMAGES["background"], (0, 0))
        SCREEN.blit(
            IMAGES["player"][player_index],
            (player_x, player_y + player_shm_vals["val"]),
        )
        SCREEN.blit(IMAGES["message"], (message_x, message_y))
        SCREEN.blit(IMAGES["base"], (base_x, BASE_Y))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def main_game(movement_info):
    score = player_index = loop_iter = 0
    player_index_gen = movement_info["player_index_gen"]
    player_x, player_y = int(SCREEN_WIDTH * 0.2), movement_info["player_y"]

    base_x = movement_info["base_x"]
    base_shift = IMAGES["base"].get_width() - IMAGES["background"].get_width()

    # get 2 new pipes to add to upper_pipes lower_pipes list
    new_pipe1 = get_random_pipe()
    new_pipe2 = get_random_pipe()

    # list of upper pipes
    upper_pipes = [
        {"x": SCREEN_WIDTH + 200, "y": new_pipe1[0]["y"]},
        {"x": SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), "y": new_pipe2[0]["y"]},
    ]

    # list of lower pipes
    lower_pipes = [
        {"x": SCREEN_WIDTH + 200, "y": new_pipe1[1]["y"]},
        {"x": SCREEN_WIDTH + 200 + (SCREEN_WIDTH / 2), "y": new_pipe2[1]["y"]},
    ]

    pipe_vel_x = -4

    # player velocity, max velocity, downward acceleration, acceleration on flap
    player_vel_y = -9

    # player's velocity along Y, default same as player_flapped
    player_max_vel_y = 10  # max vel along Y, max descend speed
    player_acc_y = 1  # players downward acceleration
    player_rot = 45  # player's rotation
    player_vel_rot = 3  # angular speed
    player_rot_thr = 20  # rotation threshold
    player_flap_acc = -9  # players speed on flapping
    player_flapped = False  # True when player flaps

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (
                event.type == KEYDOWN and event.key == K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if (
                event.type == KEYDOWN
                and (event.key == K_SPACE or event.key == K_UP)
                and player_y > -2 * IMAGES["player"][0].get_height()
            ):
                player_vel_y = player_flap_acc
                player_flapped = True
                SOUNDS["wing"].play()

        # check for crash here
        crash_test = check_crash(
            {"x": player_x, "y": player_y, "index": player_index},
            upper_pipes,
            lower_pipes,
        )
        if crash_test[0]:
            return {
                "y": player_y,
                "groundCrash": crash_test[1],
                "base_x": base_x,
                "upper_pipes": upper_pipes,
                "lower_pipes": lower_pipes,
                "score": score,
                "player_vel_y": player_vel_y,
                "player_rot": player_rot,
            }

        # check for score
        player_mid_pos = player_x + IMAGES["player"][0].get_width() / 2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe["x"] + IMAGES["pipe"][0].get_width() / 2
            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + 4:
                score += 1
                SOUNDS["point"].play()

        # player_index base_x change
        if (loop_iter + 1) % 3 == 0:
            player_index = next(player_index_gen)
        loop_iter = (loop_iter + 1) % 30
        base_x = -((-base_x + 100) % base_shift)

        # rotate the player
        if player_rot > -90:
            player_rot -= player_vel_rot

        # player's movement
        if player_vel_y < player_max_vel_y and not player_flapped:
            player_vel_y += player_acc_y
        if player_flapped:
            player_flapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            player_rot = 45

        player_height = IMAGES["player"][player_index].get_height()
        player_y += min(player_vel_y, BASE_Y - player_y - player_height)

        # move pipes to left
        for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
            u_pipe["x"] += pipe_vel_x
            l_pipe["x"] += pipe_vel_x

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upper_pipes[0]["x"] < 5:
            new_pipe = get_random_pipe()
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # remove first pipe if its out of the screen
        if upper_pipes[0]["x"] < -IMAGES["pipe"][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES["background"], (0, 0))

        for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES["pipe"][0], (u_pipe["x"], u_pipe["y"]))
            SCREEN.blit(IMAGES["pipe"][1], (l_pipe["x"], l_pipe["y"]))

        SCREEN.blit(IMAGES["base"], (base_x, BASE_Y))
        # print score so player overlaps the score
        show_score(score)

        # Player rotation has a threshold
        visible_rot = player_rot_thr
        if player_rot <= player_rot_thr:
            visible_rot = player_rot

        player_surface = pygame.transform.rotate(
            IMAGES["player"][player_index], visible_rot
        )
        SCREEN.blit(player_surface, (player_x, player_y))

        pygame.display.update()
        FPS_CLOCK.tick(FPS)

        # what we need for the model #
        print(score)
        print(player_y)

        if lower_pipes[0]["x"] > 0:
            print(lower_pipes[0]["x"], lower_pipes[0]["y"])
        else:
            print(lower_pipes[1]["x"], lower_pipes[1]["y"])

        # test to see if the keys are working
        if player_y > lower_pipes[0]["x"]:
            new_event = pygame.event.Event(
                pygame.constants.KEYDOWN, {"key": K_SPACE}
            )
            pygame.event.post(new_event)


def show_game_over_screen(crash_info):
    """crashes the player down ans shows game over image"""
    score = crash_info["score"]
    player_x = SCREEN_WIDTH * 0.2
    player_y = crash_info["y"]
    player_height = IMAGES["player"][0].get_height()
    player_vel_y = crash_info["player_vel_y"]
    player_acc_y = 2
    player_rot = crash_info["player_rot"]
    player_vel_rot = 7

    base_x = crash_info["base_x"]

    upper_pipes, lower_pipes = (
        crash_info["upper_pipes"],
        crash_info["lower_pipes"],
    )

    # play hit and die sounds
    SOUNDS["hit"].play()
    if not crash_info["groundCrash"]:
        SOUNDS["die"].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (
                event.type == KEYDOWN and event.key == K_ESCAPE
            ):
                pygame.quit()
                sys.exit()
            if (
                event.type == KEYDOWN
                and (event.key == K_SPACE or event.key == K_UP)
                and player_y + player_height >= BASE_Y - 1
            ):
                return

        # player y shift
        if player_y + player_height < BASE_Y - 1:
            player_y += min(player_vel_y, BASE_Y - player_y - player_height)

        # player velocity change
        if player_vel_y < 15:
            player_vel_y += player_acc_y

        # rotate only when it's a pipe crash
        if not crash_info["groundCrash"] and player_rot > -90:
            player_rot -= player_vel_rot

        # draw sprites
        SCREEN.blit(IMAGES["background"], (0, 0))

        for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(IMAGES["pipe"][0], (u_pipe["x"], u_pipe["y"]))
            SCREEN.blit(IMAGES["pipe"][1], (l_pipe["x"], l_pipe["y"]))

        SCREEN.blit(IMAGES["base"], (base_x, BASE_Y))
        show_score(score)

        player_surface = pygame.transform.rotate(
            IMAGES["player"][1], player_rot
        )
        SCREEN.blit(player_surface, (player_x, player_y))
        SCREEN.blit(IMAGES["game_over"], (50, 180))

        FPS_CLOCK.tick(FPS)
        pygame.display.update()


def player_shm(player_shm):
    """oscillates the value of player_shm['val'] between 8 and -8"""
    if abs(player_shm["val"]) == 8:
        player_shm["dir"] *= -1

    if player_shm["dir"] == 1:
        player_shm["val"] += 1
    else:
        player_shm["val"] -= 1


def get_random_pipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gap_y = random.randrange(0, int(BASE_Y * 0.6 - PIPE_GAP_SIZE))
    gap_y += int(BASE_Y * 0.2)
    pipe_height = IMAGES["pipe"][0].get_height()
    pipe_x = SCREEN_WIDTH + 10

    return [
        {"x": pipe_x, "y": gap_y - pipe_height},  # upper pipe
        {"x": pipe_x, "y": gap_y + PIPE_GAP_SIZE},  # lower pipe
    ]


def show_score(score):
    """displays score in center of screen"""
    score_digits = [int(x) for x in list(str(score))]
    total_width = 0  # total width of all numbers to be printed

    for digit in score_digits:
        total_width += IMAGES["numbers"][digit].get_width()

    x_offset = (SCREEN_WIDTH - total_width) / 2

    for digit in score_digits:
        SCREEN.blit(IMAGES["numbers"][digit], (x_offset, SCREEN_HEIGHT * 0.1))
        x_offset += IMAGES["numbers"][digit].get_width()


def check_crash(player, upper_pipes, lower_pipes):
    """returns True if player collides with base or pipes."""
    pi = player["index"]
    player["w"] = IMAGES["player"][0].get_width()
    player["h"] = IMAGES["player"][0].get_height()

    # if player crashes into ground
    if player["y"] + player["h"] >= BASE_Y - 1:
        return [True, True]
    else:

        player_rect = pygame.Rect(
            player["x"], player["y"], player["w"], player["h"]
        )
        pipe_w = IMAGES["pipe"][0].get_width()
        pipe_h = IMAGES["pipe"][0].get_height()

        for u_pipe, l_pipe in zip(upper_pipes, lower_pipes):
            # upper and lower pipe rects
            u_pipe_rect = pygame.Rect(u_pipe["x"], u_pipe["y"], pipe_w, pipe_h)
            l_pipe_rect = pygame.Rect(l_pipe["x"], l_pipe["y"], pipe_w, pipe_h)

            # player and upper/lower pipe hit masks
            p_hit_mask = HIT_MASKS["player"][pi]
            u_hit_mask = HIT_MASKS["pipe"][0]
            l_hit_mask = HIT_MASKS["pipe"][1]

            # if bird collided with u_pipe or l_pipe
            u_collide = pixel_collision(
                player_rect, u_pipe_rect, p_hit_mask, u_hit_mask
            )
            l_collide = pixel_collision(
                player_rect, l_pipe_rect, p_hit_mask, l_hit_mask
            )

            if u_collide or l_collide:
                return [True, False]

    return [False, False]


def pixel_collision(rect1, rect2, hit_mask1, hit_mask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hit_mask1[x1 + x][y1 + y] and hit_mask2[x2 + x][y2 + y]:
                return True
    return False


def get_hit_mask(image):
    """returns a hit mask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == "__main__":
    main()
