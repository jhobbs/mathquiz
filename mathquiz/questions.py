import random
from abc import (
    ABCMeta,
    abstractmethod,
    )


good_names = [
    'genius',
    'whizkid',
    'smarty pants',
    'Doctor',
    'master',
    'winner',
    'your awesomeness',
    ]

bad_names = [
    'doofus',
    'cretin',
    'loser',
    'half-wit',
    'meathead',
    'imbecile',
    'chump',
    ]


def random_digit():
    base = random.randint(0, 4)
    min_val = 10**base
    max_val = 10**(base+1)
    return random.randint(min_val, max_val)


class Question(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.question = self._generate()

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

    def ask(self):
        print(self.explain())
        answer = raw_input(self.question_string())
        if not self.check_answer(answer):
            print "Wrong, %s! The correct answer is: %s" % (
                random.choice(bad_names), self.answer)
            return 0
        
        print "Correct, %s!" % (random.choice(good_names))
        return 1


class ComparisonQuestion(Question):
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
    def _generate(self):
        self.a = random_digit()
        self.b = random_digit()
        self.answer = self.a + self.b

    def explain(self):
        return "Add the two numbers."

    def question_string(self):
        return "%d + %d = " % (self.a, self.b)


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
    
    def check_answer(self, answer):
        try:
            return self.answer == int(answer)
        except ValueError:
            return False


questions = [
    ComparisonQuestion,
    NextMultipleQuestion,
    AdditionQuestion,
    ]