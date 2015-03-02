import random

from argparse import ArgumentParser

from mathquiz.questions import questions

def main(argv):
    parser = ArgumentParser(description="Enjoy a math quiz.")
    parser.add_argument("--num_questions",
        help="Number of questions in the quiz.", default=10, type=int)
    args = parser.parse_args(argv[1:])
    run_quiz(args.num_questions)


def run_quiz(num_questions):
    num_correct = sum([
        random.choice(questions)().ask()
        for _ in xrange(num_questions)])
    
    print("You got %d out of %d questions right!" % (num_correct, num_questions))
