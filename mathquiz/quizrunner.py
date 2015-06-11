import random
import subprocess

from mathquiz.quiz import Quiz
from mathquiz.results import (
    QuestionResult,
    QuizResult,
    )
from mathquiz.storage import (
    get_current_user_data,
    store_quiz_results_local,
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
        user_data = get_current_user_data(args.user)
        if args.include is not None:
            question_types = [
                question_type for question_type
                in self.question_types
                if question_type.name in args.include]
        else:
            question_types = self.question_types
        quiz = Quiz(question_types, user_data)
        results = self.run_quiz(quiz, args)
        store_quiz_results_local(args.user, results)
        print_quiz_result(results)

    def run_quiz(self, quiz, args):
        results = []
        questions_left = args.num_questions
        while questions_left > 0:
            for question in quiz.questions(questions_left, args):
                answer, result = self.ask_question(question)
                results.append(QuestionResult(question, answer, result))
                if result == 0:
                    print("Adding two more questions for incorrect answer!")
                    questions_left += 1
                else:
                    questions_left -= 1
                print("Only %d questions left!" % (questions_left))
        return QuizResult(results)

    def setup_parser(self, parser):
        parser.help = "Enjoy a math quiz."
        parser.add_argument(
            "-n", "--num_questions",
            help="Number of questions in the quiz.", default=10, type=int)
        parser.add_argument(
            "-i", "--include", nargs="+",
            help="questions to include. by default, all are included.")
        parser.set_defaults(func=self.run)
        self.add_question_args(parser)

    def add_question_args(self, parser):
        for question_type in self.question_types:
            for option_name, option in question_type.options.iteritems():
                option['name'] = option_name
                add_argument_from_option(parser, question_type.name, option)

    def report(self, text):
        print(text)
        subprocess.check_call(['espeak', text])

    def ask_question(self, question):
        print(question.explain())
        answer = raw_input(question.question_string())
        if not question.check_answer(answer):
            self.report("Wrong, %s! The correct answer is: %s" % (
                random.choice(bad_names), question.answer))
            return answer, 0
        self.report("Correct, %s!" % (random.choice(good_names)))
        return answer, 1
