import random
from fractions import Fraction

from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
    )

from mathquiz.math_helpers import (
    find_next_multiple,
    random_digit,
    random_fraction,
    )


def setup_builtin_options(builtin_options, attrs):
    for option, option_config in builtin_options.iteritems():
        if option not in attrs:
            continue

        value = attrs[option]

        if 'options' not in attrs:
            attrs['options'] = dict()

        attrs['options'][option] = {
            'help': option_config['help'],
            'type': option_config['type'],
            'default': option_config['type'](value),
        }


class QuestionMeta(ABCMeta):

    def __new__(cls, name, bases, attrs):
        for base in bases:
            if hasattr(base, 'builtin_options'):
                setup_builtin_options(base.builtin_options, attrs)

        new_class = super(
            QuestionMeta, cls).__new__(cls, name, bases, attrs)

        return new_class

    def __str__(self):
        return self.name


class Question(object):
    __metaclass__ = QuestionMeta

    options = dict()

    builtin_options = {
        'max_val': {
            'help': "Maximum value for operation",
            'type': int,
        }
    }

    def __init__(self, options):
        self.provided_options = options
        self._generate()

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


class BaseComparison(Question):
    """Compare two values using <, > and =."""

    name = "base-comparison"

    def _generator(self):
        return self.generator.__func__()

    def _generate(self):
        self.a = self._generator()

        if random.randint(0, 4) == 0:
            self.b = self.a
            self.answer = '='
            return

        self.b = self._generator()
        while self.b == self.a:
            self.b = self._generator()

        if self.a > self.b:
            self.answer = '>'
            return

        self.answer = '<'

    def explain(self):
        return "Fill in the blank with '<', '>' or ="

    def question_string(self):
        return "%s _ %s  " % (self.a, self.b)


class IntegerComparison(BaseComparison):
    name = "integer-comparison"
    generator = random_digit


class FractionComparison(BaseComparison):
    name = "fraction-comparison"
    generator = random_fraction


class Exponent(Question):
    name = "exponent"
    max_val = 9

    def _generate(self):
        self.a = random_digit(max_val=self.provided_options.get('max_val'))
        self.b = random_digit(max_val=self.provided_options.get('max_val'))
        self.answer = self.a ** self.b

    def explain(self):
        return "Multiple a number by itself the given times"

    def question_string(self):
        return "%d**%d = " % (self.a, self.b)


class Addition(Question):
    name = "addition"
    max_val = 100000

    def _generate(self):
        self.a = random_digit(max_val=self.provided_options.get('max_val'))
        self.b = random_digit(max_val=self.provided_options.get('max_val'))
        self.answer = self.a + self.b

    def explain(self):
        return "Add the two numbers."

    def question_string(self):
        return "%d + %d = " % (self.a, self.b)


class NextMultiple(Question):
    name = "next-multiple"

    def _generate(self):
        self.number = random_digit(min_val=1)
        self.factor = random.choice([10, 100, 10000])
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


class CountBy(Question):
    name = "count-by"

    """Count by an integer"""
    def _generate(self):
        self.offset = random.randint(0, 9)
        self.count_by = random.randint(0, 9)
        iterations = random.randint(1, 9)
        self.answer_list = [
            "%d" % (self.offset + self.count_by * i)
            for i in range(0, iterations)]
        self.answer = " ".join(self.answer_list)

    def explain(self):
        return ("Count by a number from one number to another. For example, "
                "count by 5's starting at 3 up to 23: 3 8 13 18 23")

    def question_string(self):
        return "Count by %d's starting at %d up to %s: " % (
            self.count_by, self.offset, self.answer_list[-1])


class BaseMultiplication(Question):

    def _generator(self, *args, **kwargs):
        return self.generator.__func__(*args, **kwargs)

    def _generate(self):
        max_val = self.provided_options.get('max_val')
        self.a = self._generator(max_val=self.provided_options.get('max_val'))
        self.b = self._generator(max_val=self.provided_options.get('max_val'))
        self.answer = self.a * self.b

    def explain(self):
        return "Multiply the two numbers."

    def question_string(self):
        return "%s * %s = " % (self.a, self.b)


class IntegerMultiplication(BaseMultiplication):
    name = "integer_multiplication"
    generator = random_digit
    max_val = 9


class FractionMultiplication(BaseMultiplication):
    name = "fraction_multiplication"
    generator = random_fraction
    max_val = 9

    def check_answer(self, answer):
        return self.answer == Fraction(answer)

class Subtraction(Question):
    name = "subtraction"
    max_val = 100000

    def _generate(self):
        self.a = random_digit(max_val=self.provided_options.get('max_val'))
        self.b = random_digit(max_val=self.a)
        self.answer = self.a - self.b

    def explain(self):
        return "Find the difference."

    def question_string(self):
        return "%d - %d = " % (self.a, self.b)


class Rounding(Question):
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


class Division(Question):
    name = "division"
    max_val = 12

    def _generate(self):
        self.divisor = random_digit(
            min_val=1, max_val=self.provided_options.get('max_val'))
        self.answer = random_digit(
            max_val=self.provided_options.get('max_val'))
        self.dividend = self.divisor * self.answer

    def explain(self):
        return "Divide one number by the other"

    def question_string(self):
        return "%d %% %d = " % (
            self.dividend,
            self.divisor
            )


class Modulo(Question):
    name = "modulo"
    max_val = 12

    def _generate(self):
        self.divisor = random_digit(
            min_val=1,
            max_val=self.provided_options.get('max_val'))
        self.dividend = random_digit(
            min_val=self.divisor,
            max_val=self.provided_options.get('max_val'))
        self.answer = self.dividend % self.divisor

    def explain(self):
        return "Find the remainder"

    def question_string(self):
        return "%d mod %d = " % (
            self.dividend,
            self.divisor
            )


builtin_question_types = [
    IntegerComparison,
    #FractionComparison,
    NextMultiple,
    Addition,
    CountBy,
    IntegerMultiplication,
    FractionMultiplication,
    Subtraction,
    Rounding,
    Division,
    Modulo,
    Exponent
    ]
