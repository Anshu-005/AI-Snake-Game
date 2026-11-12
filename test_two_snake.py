
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

from game.two_snake_game import TwoSnakeGame
from game.snake_game import Direction, Point, BLOCK_SIZE, HEADER_HEIGHT
import pygame


# =============================================================
# TEST 1-6: BASIC TWO-SNAKE MECHANICS
# =============================================================

def run_tests():

    print("=" * 60)
    print("RUNNING TWO-SNAKE ENVIRONMENT MECHANICS TESTS (STAGE 1)")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1: Initialization & Independent States
    # ---------------------------------------------------------

    game = TwoSnakeGame(speed=0)

    assert game.alive1 is True and game.alive2 is True
    assert game.score1 == 0 and game.score2 == 0
    assert game.head1.x < game.head2.x

    distance = abs(game.head1.x - game.head2.x)

    assert distance >= 200
    assert game.food is not None
    assert game.food not in game.snake1
    assert game.food not in game.snake2

    print(" [PASS] Test 1: Initialization & independent state separation")

    # ---------------------------------------------------------
    # TEST 2: Shared Food Mechanics & Respawn
    # ---------------------------------------------------------

    game.reset()

    next_head1 = game._next_head(game.head1, game.direction1)
    game.food = next_head1

    initial_food = game.food

    game.play_step(action1=None, action2=None)

    assert game.score1 == 1
    assert game.score2 == 0
    assert game.food != initial_food
    assert game.food not in game.snake1
    assert game.food not in game.snake2

    print(" [PASS] Test 2: Shared food consumption, score attribution, and respawn")

    # ---------------------------------------------------------
    # TEST 3: Wall Collision & Single Elimination
    # ---------------------------------------------------------

    game.reset()
    game.direction1 = Direction.UP

    # Use a bounded loop to prevent infinite execution.
    for _ in range(50):

        if not game.alive1:
            break

        game.play_step(
            action1=Direction.UP,
            action2=None
        )

    assert not game.alive1, "Snake 1 should hit the header wall."
    assert game.alive2, "Snake 2 must survive."

    print(" [PASS] Test 3: Wall collision eliminates crashing snake, survivor continues")

    # ---------------------------------------------------------
    # TEST 4: Opponent Body Collision
    # ---------------------------------------------------------

    game.reset()

    target_body = game.snake2[1]

    game.head1 = Point(
        target_body.x,
        target_body.y + BLOCK_SIZE
    )

    game.snake1 = [
        game.head1,
        Point(game.head1.x, game.head1.y + BLOCK_SIZE)
    ]

    game.direction1 = Direction.UP

    game.play_step(
        action1=Direction.UP,
        action2=Direction.LEFT
    )

    assert not game.alive1
    assert game.alive2

    print(" [PASS] Test 4: Opponent body collision elimination")

    # ---------------------------------------------------------
    # TEST 5: Head-to-Head Collision
    # ---------------------------------------------------------

    game.reset()

    meet_point = Point(320, 260)

    game.head1 = Point(
        meet_point.x - BLOCK_SIZE,
        meet_point.y
    )

    game.direction1 = Direction.RIGHT

    game.snake1 = [
        game.head1,
        Point(game.head1.x - BLOCK_SIZE, game.head1.y)
    ]

    game.head2 = Point(
        meet_point.x + BLOCK_SIZE,
        meet_point.y
    )

    game.direction2 = Direction.LEFT

    game.snake2 = [
        game.head2,
        Point(game.head2.x + BLOCK_SIZE, game.head2.y)
    ]

    game_over, s1, s2, winner = game.play_step(
        action1=None,
        action2=None
    )

    assert not game.alive1
    assert not game.alive2
    assert game_over

    print(" [PASS] Test 5: Head-to-head collision eliminates both snakes")

    # ---------------------------------------------------------
    # TEST 6: Winner Determination
    # ---------------------------------------------------------

    game.reset()

    game.score1 = 5
    game.score2 = 3

    assert game.get_winner() == "human"

    game.score1 = 2
    game.score2 = 7

    assert game.get_winner() == "ai"

    game.score1 = 4
    game.score2 = 4

    assert game.get_winner() == "draw"

    print(" [PASS] Test 6: Winner and draw determination based on scores")

    # ---------------------------------------------------------
    # TESTS 7-11: ADVANCED MECHANICS
    # ---------------------------------------------------------

    test_7_head_swap_collision()
    test_8_moving_tail_collision()
    test_9_tail_collision_when_opponent_eats()
    test_10_food_placement_validity()
    test_11_full_board_handling()

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    print("=" * 60)
    print("ALL 12 STAGE 1 + STAGE 2 TESTS PASSED!")
    print("=" * 60)


# =============================================================
# TEST 7: HEAD-SWAP COLLISION
# =============================================================

def test_7_head_swap_collision():

    """Both snakes die when they swap head positions."""

    game = TwoSnakeGame(speed=0)

    game.snake1 = [
        Point(200, 200),
        Point(180, 200),
        Point(160, 200)
    ]

    game.snake2 = [
        Point(220, 200),
        Point(240, 200),
        Point(260, 200)
    ]

    game.head1 = game.snake1[0]
    game.head2 = game.snake2[0]

    game.direction1 = Direction.RIGHT
    game.direction2 = Direction.LEFT

    game.food = Point(400, 400)

    game_over, score1, score2, winner = game.play_step(None, None)

    assert not game.alive1, "Snake 1 should be eliminated."
    assert not game.alive2, "Snake 2 should be eliminated."
    assert game_over, "Game should end after both snakes die."

    print(" [PASS] Test 7: Head-swap collision eliminates both snakes")


# =============================================================
# TEST 8: MOVING TAIL COLLISION
# =============================================================

def test_8_moving_tail_collision():

    """Snake 1 can enter Snake 2's tail position if that tail moves away."""

    game = TwoSnakeGame(speed=0)

    game.snake1 = [
        Point(280, 200),
        Point(260, 200),
        Point(240, 200)
    ]

    game.snake2 = [
        Point(340, 220),
        Point(320, 220),
        Point(320, 200),
        Point(300, 200)
    ]

    game.head1 = game.snake1[0]
    game.head2 = game.snake2[0]

    game.direction1 = Direction.RIGHT
    game.direction2 = Direction.RIGHT

    game.food = Point(500, 400)

    game_over, score1, score2, winner = game.play_step(None, None)

    assert game.alive1, "Snake 1 should survive because Snake 2's tail vacates."
    assert game.alive2, "Snake 2 should survive."
    assert game.head1 == Point(300, 200)

    print(" [PASS] Test 8: Moving tail collision handled correctly")


# =============================================================
# TEST 9: TAIL REMAINS WHEN OPPONENT EATS
# =============================================================

def test_9_tail_collision_when_opponent_eats():

    """Snake 1 dies if it enters the tail position while Snake 2 eats."""

    game = TwoSnakeGame(speed=0)

    game.snake1 = [
        Point(280, 200),
        Point(260, 200),
        Point(240, 200)
    ]

    game.snake2 = [
        Point(340, 220),
        Point(320, 220),
        Point(320, 200),
        Point(300, 200)
    ]

    game.head1 = game.snake1[0]
    game.head2 = game.snake2[0]

    game.direction1 = Direction.RIGHT
    game.direction2 = Direction.RIGHT

    # Snake 2's next head position.
    game.food = Point(360, 220)

    game_over, score1, score2, winner = game.play_step(None, None)

    assert not game.alive1, "Snake 1 should collide with Snake 2's retained tail."
    assert game.alive2, "Snake 2 should survive after eating."
    assert game.score2 == 1, "Snake 2 should receive the food score."

    print(" [PASS] Test 9: Tail remains when opponent eats food")


# =============================================================
# TEST 10: FOOD PLACEMENT VALIDITY
# =============================================================

def test_10_food_placement_validity():

    """Food must never spawn inside either snake or outside the play area."""

    game = TwoSnakeGame(speed=0)

    game._place_food()

    assert game.food is not None

    assert game.food not in game.snake1
    assert game.food not in game.snake2

    assert 0 <= game.food.x <= game.width - BLOCK_SIZE
    assert HEADER_HEIGHT <= game.food.y <= game.height - BLOCK_SIZE

    assert game.food.x % BLOCK_SIZE == 0
    assert (game.food.y - HEADER_HEIGHT) % BLOCK_SIZE == 0

    print(" [PASS] Test 10: Food placement validity")


# =============================================================
# TEST 11: FULL BOARD HANDLING
# =============================================================

def test_11_full_board_handling():

    """Food placement should safely return None when the board is full."""

    game = TwoSnakeGame(speed=0)

    all_positions = [
        Point(x, y)
        for x in range(0, game.width, BLOCK_SIZE)
        for y in range(
            HEADER_HEIGHT,
            game.height - BLOCK_SIZE + 1,
            BLOCK_SIZE
        )
    ]

    # Occupy every valid board position.
    game.snake1 = all_positions
    game.snake2 = []

    game.head1 = game.snake1[0]
    game.head2 = None

    game._place_food()

    assert game.food is None, "Food should be None when no free cell exists."

    print(" [PASS] Test 11: Full-board handling")

    test_12_human_keyboard_controls()


# =============================================================
# MAIN EXECUTION
# =============================================================
def test_12_human_keyboard_controls():

    game = TwoSnakeGame(speed=0)

    # Initial direction should be RIGHT.
    assert game.direction1 == Direction.RIGHT

    # RIGHT -> UP
    game.handle_human_input(pygame.K_UP)
    assert game.direction1 == Direction.UP

    # UP -> LEFT
    game.handle_human_input(pygame.K_LEFT)
    assert game.direction1 == Direction.LEFT

    # LEFT -> DOWN
    game.handle_human_input(pygame.K_DOWN)
    assert game.direction1 == Direction.DOWN

    # DOWN -> RIGHT
    game.handle_human_input(pygame.K_RIGHT)
    assert game.direction1 == Direction.RIGHT

    # Direct reversal should be rejected.
    game.handle_human_input(pygame.K_LEFT)
    assert game.direction1 == Direction.RIGHT

    print("[PASS] Test 12: Human keyboard controls and reversal prevention")
    
if __name__ == "__main__":
    run_tests()
