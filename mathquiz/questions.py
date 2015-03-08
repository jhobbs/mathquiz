import math
import random

from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
    )


def random_digit(max_val=100000):
    """Returns a random digit less than max_val.

    log10(val) should be uniformly distributed between 0 and
    ceil(log10(max_val))."""

    if max_val == 0:
        return 0

    if max_val == 1:
        return random.choice([0, 1])

    max_exp = int(math.ceil(math.log10(max_val)))

    # only pick 0 as an exponent a tenth as often as other exponents.
    choices = []
    for i in range(0, max_exp + 1):
        if i == 0:
            choices.append(i)
        else:
            choices.extend([i] * 10)

    base = random.choice(choices)

    if base > 0:
        min_int = 10**(base-1)
    else:
        min_int = 0

    max_int = min(10**base, max_val)

    return random.randint(min_int, max_int)


class Question(object):
    __metaclass__ = ABCMeta

    options = dict()

    def __init__(self, options):
        self.provided_options = options
        self.question = self._generate()

    @abstractproperty
    def name(self):
        """A short name to be used in option generation."""
        pass

    @abstractmethod
    def _generate(self):
        """Generate the question."""
        pass

    @abstractmethod
    def explain(self):
        """Return a string explaining the question to the user."""
        pass

    @abstractmethod
    def question_string(self):
        """Return the question string itself."""
        pass

    def check_answer(self, answer):
        return str(answer) == str(self.answer)


class ComparisonQuestion(Question):
    name = "comparison"

    """Compare two integers using <, > and =."""
    def _generate(self):
        self.a = random_digit()

        if random.randint(0, 4) == 0:
            self.b = self.a
            self.answer = '='
            return

        self.b = random_digit()
        while self.b == self.a:
            self.b = random_digit()
        
        if self.a > self.b:
            self.answer = '>'
            return

        self.answer = '<'

    def explain(self):
        return "Fill in the blank with '<', '>' or ="

    def question_string(self):
        return "%d _ %d  " % (self.a, self.b)


class AdditionQuestion(Question):
    name = "addition"

    def _generate(self):
        self.a = random_digit(max_val=self.provided_options.get('max_val'))
        self.b = random_digit(max_val=self.provided_options.get('max_val'))
        self.answer = self.a + self.b

    def explain(self):
        return "Add the two numbers."

    def question_string(self):
        return "%d + %d = " % (self.a, self.b)

    options = {
        'max_val': {
            'help': 'maximum number used in addition.',
            'default': 100000,
            'type': int,
            }
    }


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


class NextMultipleQuestion(Question):
    name = "next-multiple"

    def _generate(self):
        self.number = random_digit()
        self.factor = random.choice([10,100,10000])
        self.direction = random.choice(['up', 'down'])
        self.answer = find_next_multiple(
            self.number, self.factor, self.direction)

    def explain(self):
        return "Answer the question using the correct multiple."

    def question_string(self):
        return "What is the next multiple of %d going %s from %d? " % (
            self.factor,
            self.direction,
            self.number)


class CountByQuestion(Question):
    name = "count-by"

    """Count by an integer"""
    def _generate(self):
        self.offset = random.randint(0,9)
        self.count_by = random.randint(0,9)
        iterations = random.randint(1,9)
        self.answer_list = [
            "%d" % (self.offset + self.count_by * i)
            for i in range(0,iterations)]
        self.answer = " ".join(self.answer_list)

    def explain(self):
        return ("Count by a number from one number to another. For example, "
                "count by 5's starting at 3 up to 23: 3 8 13 18 23")

    def question_string(self):
        return "Count by %d's starting at %d up to %s: " % (
            self.count_by, self.offset, self.answer_list[-1])


class MultiplicationQuestion(Question):
    name = "multiplication"

    def _generate(self):
        self.a = random_digit(max_val=self.provided_options.get('max_val'))
        self.b = random_digit(max_val=self.provided_options.get('max_val'))
        self.answer = self.a * self.b

    def explain(self):
        return "Multiply the two numbers."

    def question_string(self):
        return "%d * %d = " % (self.a, self.b)

    options = {
        'max_val': {
            'help': 'maximum number used in multiplication.',
            'default': 9,
            'type': int,
            }
    }


class SubtractionQuestion(Question):
    name = "subtraction"

    def _generate(self):
        self.a = random_digit(max_val=self.provided_options.get('max_val'))
        self.b = random_digit(max_val=self.a)
        self.answer = self.a - self.b

    def explain(self):
        return "Find the difference."

    def question_string(self):
        return "%d - %d = " % (self.a, self.b)

    options = {
        'max_val': {
            'help': 'maximum number used in subtraction.',
            'default': 100000,
            'type': int,
            }
    }


class RoundingQuestion(Question):
    name = "rounding"

    def _generate(self):
        self.number = random_digit()
        self.round_to = random.choice(range(-4, -1))
        self.answer = int(round(self.number, self.round_to))

    def explain(self):
        return "Round the number to the given precision."

    def question_string(self):
        return "Round %d to the nearest %d: " % (
            self.number,
            10**(self.round_to * -1),
            )


builtin_question_types = [
    ComparisonQuestion,
    NextMultipleQuestion,
    AdditionQuestion,
    CountByQuestion,
    MultiplicationQuestion,
    SubtractionQuestion,
    RoundingQuestion,
    ]
