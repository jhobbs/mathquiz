import random

from argparse import ArgumentParser
from collections import namedtuple

from mathquiz.quiz import Quiz
from mathquiz.storage import store_quiz_results_local


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


class QuestionResult(object):
    def __init__(self, question, answer, result):
        self.question = question
        self.answer = answer
        self.result = result


class QuizResult(object):
    def __init__(self, results=None):
        if results is None:
            self.results = []
        else:
            self.results = results

    @property
    def num_questions(self):
        return len(self.results)

    @property
    def num_correct(self):
        return sum([result.result for result in self.results])


def print_quiz_result(quiz_result): 
    print("You got %d out of %d questions right!" % (
        quiz_result.num_correct, quiz_result.num_questions))


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

    def run(self, args):
        if args.include is not None:
            question_types = [
                question_type for question_type
                in self.question_types
                if question_type.name in args.include]
        else:
            question_types = self.question_types
        quiz = Quiz(question_types)
        results = self.run_quiz(quiz, args)
        store_quiz_results_local(args.user, results)
        print_quiz_result(results)

    def run_quiz(self, quiz, args):
        results = []
        for question in quiz.questions(args):
            answer, result = self.ask_question(question)
            results.append(QuestionResult(question, answer, result))


        return QuizResult(results)

    def setup_parser(self, parser):
        parser.help="Enjoy a math quiz."
        parser.add_argument("-n", "--num_questions",
            help="Number of questions in the quiz.", default=10, type=int)
        parser.add_argument("-i", "--include",
            nargs="+",
            help="questions to include. by default, all are included, but if this is specified only those specified are included.")
        self.add_question_args(parser)
        parser.add_argument("user", help="Name of user.")

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
            return answer, 0
        print "Correct, %s!" % (random.choice(good_names))
        return answer, 1
