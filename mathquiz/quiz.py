import os
import random
import yaml

from argparse import ArgumentParser
from collections import namedtuple

import boto

from mathquiz.questions import questions as quests

UserRecord = namedtuple('UserRecord', [
    'name',
    'results',
    ])

QuizResult = namedtuple('QuizResult', [
    'correct',
    'total',
    ])


def print_quiz_result(quiz_result): 
    print("You got %d out of %d questions right!" % (
        quiz_result.correct, quiz_result.total))


def add_argument_from_option(parser, module_name, option):
    parser.add_argument(
        "--%s-%s" % (module_name, option['name']),
        help=option['help'],
        default=option['default'],
        type=option.get('type', str),
        )


class ConsoleQuizRunner(object):
    def __init__(self, questions):
        self.quiz = Quiz(questions)

    def run(self, argv):
        self.parse_args(argv)
        results = self.quiz.run(self.args)
        if self.args.bucket:
            store_quiz_results(args.bucket, args.user, results)
        print_quiz_result(results)

    def parse_args(self, argv):
        parser = ArgumentParser(description="Enjoy a math quiz.")
        parser.add_argument("-n", "--num_questions",
            help="Number of questions in the quiz.", default=10, type=int)
        parser.add_argument("-b", "--bucket",
            help="Name of S3 bucket.", default=os.environ.get('MATHQUIZ_BUCKET'))
        self.add_quiz_args(parser)
        parser.add_argument("user", help="Name of user.")
        self.args = parser.parse_args(argv[1:])

    def add_quiz_args(self, parser):
        for question in self.quiz.questions:
            for option_name, option in question.options.iteritems():
                option['name'] = option_name
                add_argument_from_option(parser, question.name, option)


class Quiz(object):
    def __init__(self, questions):
        self.questions = questions

    def run(self, options):
        num_correct = sum([
            self.ask(random.choice(self.questions), options)
            for _ in xrange(options.num_questions)])

        return QuizResult(
            correct=num_correct, total=options.num_questions)

    def ask(self, question, options):
        option_vars = vars(options)
        module_name = "%s_" % (question.name)
        question_options = {
                arg[len(module_name):]: value
                for arg,value in option_vars.iteritems()
                if arg.startswith("%s_" % (question.name))}
        question = question(question_options)
        return question.ask()


def store_quiz_results(bucket_name, user, results):
    c = boto.connect_s3()
    bucket = c.get_bucket(bucket_name)
    key = bucket.get_key('%s-results' % (user))
    if key is None:
        key = bucket.new_key('%s-results' % (user))
        contents = []
    else:
        contents = yaml.load(key.get_contents_as_string())

    contents.append(results)
    key.set_contents_from_string(yaml.dump(contents))


def run_quiz(argv):
    runner = ConsoleQuizRunner(quests)
    results = runner.run(argv)


def main(argv):
    run_quiz(argv)
