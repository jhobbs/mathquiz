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


class Quiz(object):
    def __init__(self, questions):
        self.questions = questions

    def run(self, num_questions):
        num_correct = sum([
            random.choice(self.questions)().ask()
            for _ in xrange(num_questions)])

        return QuizResult(correct=num_correct, total=num_questions)


def parse_args(argv):
    parser = ArgumentParser(description="Enjoy a math quiz.")
    parser.add_argument("-n", "--num_questions",
        help="Number of questions in the quiz.", default=10, type=int)
    parser.add_argument("-b", "--bucket",
        help="Name of S3 bucket.", default=os.environ.get('MATHQUIZ_BUCKET'))
    parser.add_argument("user", help="Name of user.")
    return parser.parse_args(argv[1:])


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


def main(argv):
    args = parse_args(argv)
    quiz = Quiz(quests)
    results = quiz.run(args.num_questions)
    print_quiz_result(results)
    if args.bucket:
        store_quiz_results(args.bucket, args.user, results)
