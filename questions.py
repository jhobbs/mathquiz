import random
from abc import (
    ABCMeta,
    abstractmethod,
    )

class Question(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def explain(self):
        """Return a string explaining the question to the user."""
        pass

    @abstractmethod
    def question_string(self):
        """Return the question string itself."""
        pass

    @abstractmethod
    def check_answer(self, answer):
        """Check an answer. Return True if correct, False otherwise."""
        pass

    def ask(self):
        print(self.explain())
        answer = raw_input(self.question_string())
        if not self.check_answer(answer):
            print "Wrong!"
            return 0
        
        print "Correct"
        return 1


class ComparisonQuestion(Question):
    """Compare two integers using <, > and =."""
    def __init__(self):
        self.question = self._generate()

    def _generate(self):
        a = random.randint(0, 100000)

        if random.randint(0, 4) == 0:
            return (a, a, '=')

        b = random.randint(0, 100000)
        while b == a:
            b = random.randint(0, 100000)
        
        if a > b:
            return (a, b, '>')

        return (a, b, '<')

    def explain(self):
        return "Fill in the blank with '<', '>' or ="

    def question_string(self):
        return "%d _ %d  " % (self.question[0], self.question[1])

    def check_answer(self, answer):
        return answer == self.question[2]


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
    def __init__(self):
        self.question = self._generate()

    def _generate(self):
        self.number = random.randint(0, 100000)
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
    ]


def run_quiz(num_questions):
    num_correct = sum([
        random.choice(questions)().ask()
        for _ in xrange(num_questions)])
    
    print("You got %d out of %d questions right!" % (num_correct, num_questions))

def main():
    run_quiz(10)

if __name__ == '__main__':
    main()
