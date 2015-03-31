from argparse import ArgumentParser
from mathquiz.questions import builtin_question_types
from mathquiz.quizrunner import ConsoleQuizRunner

def display_stats(args):
    user = args.user

    print("Stats for %s:" % user)


def setup_stats_display(parser):
    parser.set_defaults(func=display_stats)


def get_args(argv, runner):
    parser = ArgumentParser()
    parser.add_argument(
            "-u", "--user",
            default="default", help="Name of user.")
    subparsers = parser.add_subparsers()
    runner.setup_parser(subparsers.add_parser('run'))
    setup_stats_display(subparsers.add_parser('stats'))
    args = parser.parse_args(argv[1:])
    return args


def run_quiz(argv):
    runner = ConsoleQuizRunner(builtin_question_types)
    args = get_args(argv, runner)
    args.func(args)


def main(argv):
    run_quiz(argv)
