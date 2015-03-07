import os
import random
import yaml

from argparse import ArgumentParser
from collections import namedtuple

import boto

from mathquiz.questions import builtin_question_types


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
    def __init__(self, question_types):
        self.question_types = question_types

    def run(self, argv):
        self.parse_args(argv)
        if self.args.include is not None:
            question_types = [
                question_type for question_type
                in self.question_types
                if question_type.name in self.args.include]
        else:
            question_types = self.question_types
        quiz = Quiz(question_types)
        results = self.run_quiz(quiz)
        if self.args.bucket:
            store_quiz_results(args.bucket, args.user, results)
        print_quiz_result(results)

    def run_quiz(self, quiz):
        num_correct = sum([
                self.ask_question(question)
                for question in quiz.questions(self.args)
            ])
        return QuizResult(correct=num_correct, total=self.args.num_questions)

    def parse_args(self, argv):
        parser = ArgumentParser(description="Enjoy a math quiz.")
        parser.add_argument("-n", "--num_questions",
            help="Number of questions in the quiz.", default=10, type=int)
        parser.add_argument("-b", "--bucket",
            help="Name of S3 bucket.", default=os.environ.get('MATHQUIZ_BUCKET'))
        parser.add_argument("-i", "--include",
            nargs="+",
            help="questions to include. by default, all are included, but if this is specified only those specified are included.")
        self.add_question_args(parser)
        parser.add_argument("user", help="Name of user.")
        self.args = parser.parse_args(argv[1:])

    def add_question_args(self, parser):
        for question_type in self.question_types:
            for option_name, option in question_type.options.iteritems():
                option['name'] = option_name
                add_argument_from_option(parser, question_type.name, option)

    def ask_question(self, question):
        print(question.explain())
        answer = raw_input(question.question_string())
        if not question.check_answer(answer):
            print "Wrong, %s! The correct answer is: %s" % (
                random.choice(bad_names), question.answer)
            return 0
        print "Correct, %s!" % (random.choice(good_names))
        return 1


class Quiz(object):
    def __init__(self, question_types):
        self.question_types = question_types

    def questions(self, options):
        for _ in xrange(options.num_questions):
            question_type = random.choice(self.question_types)
            yield self.generate_question(question_type, options)

    def generate_question(self, question, options):
        option_vars = vars(options)
        module_name = "%s_" % (question.name)
        question_options = {
                arg[len(module_name):]: value
                for arg,value in option_vars.iteritems()
                if arg.startswith("%s_" % (question.name))}
        return question(question_options)


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
    runner = ConsoleQuizRunner(builtin_question_types)
    results = runner.run(argv)


def main(argv):
    run_quiz(argv)
