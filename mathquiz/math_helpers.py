import math
import random


def random_digit(min_val=0, max_val=100000):
    """Returns a random digit less than max_val.

    log10(val) should be uniformly distributed between 0 and
    ceil(log10(max_val))."""

    if max_val < min_val:
        raise ValueError(
            "max (%d) is less than min (%d)" % (max_val, min_val))

    if min_val < 0:
        raise ValueError(
            "negative values not supported.")

    if min_val == max_val:
        return min_val

    if max_val == 0:
        return 0

    if max_val == 1:
        return random.choice([0, 1])

    if min_val == 0:
        min_exp = 0
    else:
        min_exp = int(math.ceil(math.log10(min_val)))
    max_exp = int(math.ceil(math.log10(max_val)))

    # only pick 0 as an exponent a tenth as often as other exponents.
    choices = []
    for i in range(min_exp, max_exp + 1):
        if i == 0:
            choices.append(i)
        else:
            choices.extend([i] * 10)

    base = random.choice(choices)

    if base > 0:
        min_int = max(min_val, 10**(base-1))
    else:
        min_int = min_val

    max_int = min(10**base, max_val)

    return random.randint(min_int, max_int)


def find_next_multiple(number, factor, direction):
    if direction == 'down':
        if number % factor == 0:
            return number - factor

        return (number / factor) * factor
    elif direction == 'up':
        if number % factor == 0:
            return number + factor

        return ((number / factor) + 1) * factor
    else:
        raise Exception('Bad direction: %s' % direction)
