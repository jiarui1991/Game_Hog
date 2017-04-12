"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

# Taking turns

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'

    total, pig_out = 0, False 
    while num_rolls != 0:
        single_roll = dice()
        if single_roll == 1:
            pig_out = True
        total,num_rolls = total + single_roll, num_rolls - 1
    if pig_out:
        return 1
    return total

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'

    if num_rolls == 0:
        return free_bacon(opponent_score)
    return roll_dice(num_rolls, dice)

def free_bacon(score):
    return max(score // 10, score % 10) + 1

# Playing a game

def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).
    """

    if (opponent_score + score) % 7 == 0:
        return four_sided
    return six_sided

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first.
    strategy1:  The strategy function for Player 1, who plays second.
    """

    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    score, opponent_score = 0, 0
    while max(score, opponent_score) < goal:
        if who == 0:
            func_strategy = strategy0
        else:
            func_strategy = strategy1

        num_rolls = func_strategy(score, opponent_score)
        dice = select_dice(score, opponent_score)
        score += take_turn(num_rolls, opponent_score, dice)

        if score == 2 * opponent_score or opponent_score == 2 * score:
            score, opponent_score = opponent_score, score
        score, opponent_score = opponent_score, score
        who = other(who)

    if who == 0:
        return score, opponent_score
    return opponent_score, score  # You may wish to change this line.


#######################
# Phase 2: Strategies #
#######################

# Basic Strategy


def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """

    def average(*args):
        i, total = 0, 0
        while i < num_samples:
            total, i = total + fn(*args), i + 1
        return total / num_samples
    return average

def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    1 dice scores 3.0 on average
    2 dice scores 6.0 on average
    3 dice scores 9.0 on average
    4 dice scores 12.0 on average
    5 dice scores 15.0 on average
    6 dice scores 18.0 on average
    7 dice scores 21.0 on average
    8 dice scores 24.0 on average
    9 dice scores 27.0 on average
    10 dice scores 30.0 on average
    10
    """

    roll, ave_value = 1, 0
    max_num_roll, best_value = 0, 0
    averaged_dice = make_averaged(roll_dice)
    while roll <= 10:
        ave_value = averaged_dice(roll, dice)
        print(roll, 'dice scores', ave_value, 'on average')
        if ave_value > best_value:
            max_num_roll, best_value = roll, ave_value
        roll += 1
    return max_num_roll


def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""

    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    if free_bacon(opponent_score) >= margin:
        return 0
    return num_rolls

def swap_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least MARGIN points and rolls
    NUM_ROLLS otherwise.
    """

    bacon_point = free_bacon(opponent_score)
    if (bacon_point + score) * 2 == opponent_score:
        return 0
    elif bacon_point + score == opponent_score * 2:
        return num_rolls
    elif bacon_point >= margin:
        return 0
    return num_rolls

def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.
    First of all, if my score is greater than 90, then I just want to use free 
    bacon to reduce my riks to get Pig out, sicne only 10 ten points to get a 
    win. Then if my losing score greater than 20, then it is worth to use Swin
    Swap to change my score with the opponent's score. Otherwise, I can just
    roll 3 or 4 dice to have more chance to get 20 points. 
    Finally, when our difference is small, I won't take too many risks to roll
    more dices to get Pig Out. But when it is large, I'm willing to take more 
    risks and roll dices as more as I can. 
    """
    
    dice_size = select_dice(score, opponent_score)
    bacon_point = free_bacon(opponent_score)
    losing_score = opponent_score - score
    
    if score > 90:
        return 0
    
    if losing_score > 20:
        if (score + bacon_point) * 2 == opponent_score:
            return 0
        if (score + 1) * 2 == opponent_score:
            return 10
        if (score * 2 + 1) == opponent_score:
            return 10

    if losing_score > 40:
        return 10
    elif losing_score > 20:
        return 8
    elif losing_score > 10:
        return 6
    elif losing_score == 0:
        return 4
    else:
        return swap_strategy(score, opponent_score)
        

##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.

@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()
