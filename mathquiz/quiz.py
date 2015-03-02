import random

from argparse import ArgumentParser
from collections import namedtuple

from mathquiz.questions import questions as quests

UserRecord = namedtuple('UserRecord', [
    'name',
    'results',
    ])


class Quiz(object):
    def __init__(self, questions, user):
        self.questions = questions
        self.user = user

    def run(self, num_questions):
        num_correct = sum([
            random.choice(self.questions)().ask()
            for _ in xrange(num_questions)])
        
        print("You got %d out of %d questions right!" % (
            num_correct, num_questions))


def parse_args(argv):
    parser = ArgumentParser(description="Enjoy a math quiz.")
    parser.add_argument("-n", "--num_questions",
        help="Number of questions in the quiz.", default=10, type=int)
    parser.add_argument("user", help="Name of user.")
    return parser.parse_args(argv[1:])


def main(argv):
    args = parse_args(argv)
    quiz = Quiz(quests, args.user)
    quiz.run(args.num_questions)
