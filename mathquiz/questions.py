import random
import string
import uuid

from fractions import (
    gcd,
    Fraction,
    )

from abc import (
    ABCMeta,
    abstractmethod,
    abstractproperty,
    )

from mathquiz.math_helpers import (
    find_next_multiple,
    greatest_factor,
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

    def __init__(self, options, properties=None):
        self.provided_options = options
        self.uuid = unicode(uuid.uuid4())
        if properties is None:
            self._generate()
        else:
            for key, value in properties.iteritems():
                setattr(self, key, value)

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

    def check_answer(self, given_answer):
        normalized_answer = " ".join(str(given_answer).split())
        return str(normalized_answer) == str(self.answer)

    @property
    def graphic_cue(self):
        return {}

    def fancy_name(self):
        return string.capwords(self.name.replace('-', ' ').replace('_', ' '))

    def option_get(self, option_name):
        if option_name in self.provided_options:
            return self.provided_options(option_name)
        return self.options[option_name]['default']


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
        max_val = self.option_get('max_val')
        self.a = random_digit(max_val=max_val)
        self.b = random_digit(max_val=4)
        self.answer = self.a ** self.b

    def explain(self):
        return "Exponent: raise a number to the given power."

    def question_string(self):
        return "%d^%d = " % (self.a, self.b)


class Addition(Question):
    name = "addition"
    max_val = 100000

    def _generate(self):
        max_val = self.option_get('max_val')
        self.a = random_digit(max_val=max_val)
        self.b = random_digit(max_val=max_val)
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
        self.count_by = random.randint(1, 9)
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
        max_val = self.option_get('max_val')
        self.a = self._generator(max_val=max_val)
        self.b = self._generator(max_val=max_val)
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
        try:
            fraction_answer = Fraction(answer)
        except ValueError:
            return False

        return self.answer == fraction_answer


class Subtraction(Question):
    name = "subtraction"
    max_val = 100000

    def _generate(self):
        max_val = self.option_get('max_val')
        self.a = random_digit(max_val=max_val)
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
        max_val = self.option_get('max_val')
        self.divisor = random_digit(
            min_val=1, max_val=max_val)
        self.answer = random_digit(
            max_val=max_val)
        self.dividend = self.divisor * self.answer

    def explain(self):
        return "Divide one number by the other"

    def question_string(self):
        return "%d / %d = " % (
            self.dividend,
            self.divisor
            )


class Modulo(Question):
    name = "modulo"
    max_val = 24

    def _generate(self):
        max_val = self.option_get('max_val')
        if max_val is None:
            max_val = self.max_val
        self.divisor = random_digit(
            min_val=1,
            max_val=max_val)
        self.dividend = random_digit(
            min_val=self.divisor,
            max_val=max_val)
        self.answer = self.dividend % self.divisor

    def explain(self):
        return "Find the remainder"

    def question_string(self):
        return "%d mod %d = " % (
            self.dividend,
            self.divisor
            )


class Gcd(Question):
    name = "gcd"
    max_val = 20

    def _generate(self):
        max_val = self.option_get('max_val')
        if max_val is None:
            max_val = self.max_val
        self.a = random_digit(max_val=max_val)
        self.b = random_digit(max_val=max_val)
        self.answer = gcd(self.a, self.b)

    def explain(self):
        return "Find the greatest common denominator"

    def question_string(self):
        return "gcd(%d, %d) = " % (
            self.a,
            self.b,
            )


class GreatestFactor(Question):
    name = "greatest-factor"
    max_val = 20

    def _generate(self):
        max_val = self.option_get('max_val')
        if max_val is None:
            max_val = self.max_val
        self.a = random_digit(min_val=1, max_val=max_val)
        self.answer = greatest_factor(self.a)

    def explain(self):
        return "Find the greatest factor of the number."

    def question_string(self):
        return "gf(%d) = " % (
            self.a,
            )


class RectangleQuestion(Question):
    def _generate(self):
        self.height = random_digit(min_val=1, max_val=12)
        self.width = random_digit(min_val=1, max_val=12)

    @property
    def graphic_cue(self):
        return {'rectangle': {'width': self.width, 'height': self.height}}


class RectangularArea(RectangleQuestion):
    name = "rectangular-area"
    max_val = 12

    def _generate(self):
        super(RectangularArea, self)._generate()
        self.answer = self.height * self.width

    def explain(self):
        return "Find the area of the rectangle."

    def question_string(self):
        return "Find the area of a %d by %d rectangle: " % (
            self.width,
            self.height,
            )

    @property
    def graphic_cue(self):
        graphic_cue = super(RectangularArea, self).graphic_cue
        graphic_cue['rectangle']['solid'] = True
        return graphic_cue


class RectangularPerimeter(RectangleQuestion):
    name = "rectangular-perimeter"
    max_val = 12

    def _generate(self):
        super(RectangularPerimeter, self)._generate()
        self.answer =  2 * (self.height + self.width)

    def explain(self):
        return "Find the perimeter of the rectangle."

    def question_string(self):
        return "Find the perimeter of a %d by %d rectangle: " % (
            self.width,
            self.height,
            )

def question_name_to_class_name(question_name):
    return question_name.title().replace('-','').replace('_', '')

builtin_question_types = [
    IntegerComparison,
    FractionComparison,
    NextMultiple,
    Addition,
    CountBy,
    IntegerMultiplication,
    FractionMultiplication,
    Subtraction,
    Rounding,
    Division,
    Modulo,
    Exponent,
    RectangularArea,
    RectangularPerimeter,
    Gcd,
    GreatestFactor,
    ]
