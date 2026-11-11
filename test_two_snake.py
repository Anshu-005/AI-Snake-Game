import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

from game.two_snake_game import TwoSnakeGame
from game.snake_game import Direction, Point, BLOCK_SIZE


def run_tests():
    print("=" * 60)
    print("RUNNING TWO-SNAKE ENVIRONMENT MECHANICS TESTS (STAGE 1)")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1: Initialization & Independent States
    # ---------------------------------------------------------
    game = TwoSnakeGame(speed=0)
    assert game.alive1 is True and game.alive2 is True, "Both snakes must start alive."
    assert game.score1 == 0 and game.score2 == 0, "Both scores must start at 0."
    assert game.head1.x < game.head2.x, "Snake 1 must start on left, Snake 2 on right."
    distance = abs(game.head1.x - game.head2.x)
    assert distance >= 200, f"Initial distance must be >= 200px (got {distance}px)."
    assert game.food is not None, "Food must be placed at start."
    assert game.food not in game.snake1 and game.food not in game.snake2, "Food must not spawn on snakes."
    print(" [PASS] Test 1: Initialization & independent state separation")

    # ---------------------------------------------------------
    # TEST 2: Shared Food Mechanics & Respawn
    # ---------------------------------------------------------
    game.reset()
    # Force food right in front of Snake 1
    next_head1 = game._next_head(game.head1, game.direction1)
    game.food = next_head1
    initial_food = game.food

    game.play_step(action1=None, action2=None)
    assert game.score1 == 1, f"Snake 1 score should be 1 after eating food (got {game.score1})."
    assert game.score2 == 0, "Snake 2 score should remain 0."
    assert game.food != initial_food, "Food must respawn at a new location."
    assert game.food not in game.snake1 and game.food not in game.snake2, "Respawned food must not be on snakes."
    print(" [PASS] Test 2: Shared food consumption, score attribution, and respawn")

    # ---------------------------------------------------------
    # TEST 3: Wall Collision & Single Elimination
    # ---------------------------------------------------------
    game.reset()
    # Move Snake 1 up towards the top header wall (y < 60)
    game.direction1 = Direction.UP
    while game.alive1:
        game.play_step(action1=Direction.UP, action2=None)

    assert not game.alive1, "Snake 1 should be eliminated after hitting the header wall."
    assert game.alive2, "Snake 2 must continue playing when Snake 1 is eliminated."
    print(" [PASS] Test 3: Wall collision eliminates crashing snake, survivor continues")

    # ---------------------------------------------------------
    # TEST 4: Opponent Body Collision
    # ---------------------------------------------------------
    game.reset()
    # Snake 2 is at head=(480, 260), body=[(480, 260), (500, 260), (520, 260)] moving LEFT.
    # Place Snake 1 directly below body segment (500, 260) facing UP into it.
    target_body = game.snake2[1]  # (500, 260)
    game.head1 = Point(target_body.x, target_body.y + BLOCK_SIZE)
    game.snake1 = [game.head1, Point(game.head1.x, game.head1.y + BLOCK_SIZE)]
    game.direction1 = Direction.UP

    # Keep Snake 2 moving straight ahead (left) into safe open space
    game.play_step(action1=Direction.UP, action2=Direction.LEFT)
    assert not game.alive1, "Snake 1 must be eliminated upon hitting opponent's body."
    assert game.alive2, "Snake 2 must survive when Snake 1 crashes into its body."
    print(" [PASS] Test 4: Opponent body collision elimination")

    # ---------------------------------------------------------
    # TEST 5: Head-to-Head Collision
    # ---------------------------------------------------------
    game.reset()
    # Position both snakes 2 blocks apart moving towards each other
    meet_point = Point(320, 260)
    game.head1 = Point(meet_point.x - BLOCK_SIZE, meet_point.y)
    game.direction1 = Direction.RIGHT
    game.snake1 = [game.head1, Point(game.head1.x - BLOCK_SIZE, game.head1.y)]

    game.head2 = Point(meet_point.x + BLOCK_SIZE, meet_point.y)
    game.direction2 = Direction.LEFT
    game.snake2 = [game.head2, Point(game.head2.x + BLOCK_SIZE, game.head2.y)]

    # Step: both heads attempt to enter meet_point simultaneously
    game_over, s1, s2, winner = game.play_step(action1=None, action2=None)
    assert not game.alive1 and not game.alive2, "Both snakes must be eliminated in a head-to-head collision."
    assert game_over, "Game must be over when both snakes are eliminated."
    print(" [PASS] Test 5: Head-to-head collision eliminates both snakes")

    # ---------------------------------------------------------
    # TEST 6: Winner Determination
    # ---------------------------------------------------------
    game.reset()
    game.score1 = 5
    game.score2 = 3
    assert game.get_winner() == "human", "Human must win when score1 > score2."

    game.score1 = 2
    game.score2 = 7
    assert game.get_winner() == "ai", "AI must win when score2 > score1."

    game.score1 = 4
    game.score2 = 4
    assert game.get_winner() == "draw", "Must result in a draw when scores are equal."
    print(" [PASS] Test 6: Winner and draw determination based on scores")

    print("=" * 60)
    print("ALL STAGE 1 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
