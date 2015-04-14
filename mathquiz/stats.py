from collections import defaultdict
from mathquiz.questions import builtin_question_types
from mathquiz.storage import get_current_user_data

MASTERY_SIZE = 30
MASTERY_PERCENT = 0.90

def questions_from_user_data(user_data):
    questions = []
    for quiz in user_data['results']:
        questions.extend(quiz.results)
    return questions


def question_type_mastered(question_type, question_type_history):
    if len(question_type_history) < MASTERY_SIZE:
        return False

    relevant_history = question_type_history[:-MASTERY_SIZE]
    correct_questions, _ = group_by_correctness(relevant_history)

    return len(correct_questions)/float(MASTERY_SIZE) >= MASTERY_PERCENT


def group_by_mastery(question_types, question_history):
    """Partition a set of question types by mastery.

    Mastery is defined as having answered at least 30 questions of the
    type with at least 90% success rate over the last 30 questions.
    """
    mastered_question_types = set()
    unmastered_question_types = set()
    questions_by_type = group_by_type(question_history)
    for question_type in question_types:
        question_type_history = questions_by_type[question_type]
        if question_type_mastered(question_type, question_type_history):
            mastered_question_types.add(question_type)
        else:
            unmastered_question_types.add(question_type)

    return {
        'mastered': mastered_question_types,
        'unmastered': unmastered_question_types,
        }


def group_by_type(question_results):
    grouped = defaultdict(list)
    for question_result in question_results:
        grouped[question_result.question.name].append(question_result)
    return grouped


def group_by_correctness(question_results):
    correct = []
    incorrect = []
    for question_result in question_results:
        if question_result.result:
            correct.append(question_result)
        else:
            incorrect.append(question_result)

    return correct, incorrect


def display_stats(args):
    user = args.user
    print("Stats for %s:" % user)
    user_data = get_current_user_data(user)
    num_quizes = len(user_data['results'])
    print("Quizes completed: %d" % (num_quizes))
    questions = questions_from_user_data(user_data)

    if len(questions) == 0:
        print("No questions answered yet.")
        return

    correct_questions, incorrect_questions = group_by_correctness(questions)
    print("Total questions: %d" % len(questions))
    print("Correctly answered questions: %d" % len(correct_questions))
    print("Overall success rate: %d%%" % (
        int(float(len(correct_questions))/len(questions) * 100)))
    by_mastery = group_by_mastery(builtin_question_types, questions)

    for mastery, question_types in by_mastery.iteritems():
        strings = [unicode(question_type) for question_type in question_types]
        if len(strings) == 0:
            display = "None"
        else:
            display = " ".join(strings)

        print("%s: %s" % (mastery, display))


def setup_parser(parser):
    parser.set_defaults(func=display_stats)
