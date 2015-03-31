from argparse import ArgumentParser
from mathquiz.questions import builtin_question_types
from mathquiz.quizrunner import ConsoleQuizRunner


def get_args(argv, runner):
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    runner.setup_parser(subparsers.add_parser('run'))
    args = parser.parse_args(argv[1:])

    return args


def run_quiz(argv):
    runner = ConsoleQuizRunner(builtin_question_types)
    args = get_args(argv, runner)
    runner.run(args)


def main(argv):
    run_quiz(argv)
