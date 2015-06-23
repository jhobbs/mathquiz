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

    relevant_history = question_type_history[-MASTERY_SIZE:]
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
        question_type_history = questions_by_type[question_type.name]
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


def generate_stats(user):
    results = {
        'quizes': {},
        'questions': {},
        'question_types': {},
    }

    user_data = get_current_user_data(user)
    num_quizes = len(user_data['results'])
    results['quizes']['completed'] = num_quizes

    questions = questions_from_user_data(user_data)

    results['questions']['total'] = len(questions)

    if len(questions) == 0:
        results['questions']['correct'] = 0
        results['questions']['success_rate'] = 0
        return results

    correct_questions, _ = group_by_correctness(questions)
    results['questions']['correct'] = len(correct_questions)
    results['questions']['success_rate'] = \
        int(float(len(correct_questions))/len(questions) * 100)
    by_mastery = group_by_mastery(builtin_question_types, questions)

    for question_type in builtin_question_types:
        results['question_types'][question_type] = dict()

    for mastery, question_types in by_mastery.iteritems():
        for question_type in question_types:
            results['question_types'][question_type]['mastery'] = mastery

    results['mastery_size'] = MASTERY_SIZE

    for question_type in builtin_question_types:
        questions_of_type = filter(
            lambda x: x.question.name == question_type.name, questions)
        relevant_questions = questions_of_type[-MASTERY_SIZE:]
        results['question_types'][question_type]['total'] = \
            len(relevant_questions)
        correct_of_type, _ = group_by_correctness(relevant_questions)
        results['question_types'][question_type]['correct'] = \
            len(correct_of_type)

    return results


def display_stats(args):
    user = args.user
    print("Stats for %s:" % user)
    stats = generate_stats(user)
    print("Quizes completed: %d" % stats['quizes']['completed'])

    if stats['questions']['total'] == 0:
        print("No questions answered yet.")
        return

    print("Total questions: %d" % stats['questions']['total'])
    print("Correctly answered questions: %d" % stats['questions']['correct'])
    print("Overall success rate: %d%%" % stats['questions']['success_rate'])

    print('Per question history for last %d of each type' % (
        stats['mastery_size']))

    for question_type, history in stats['question_types'].iteritems():
        print('%s: %s, %s/%s' % (
            question_type,
            history['mastery'],
            history['correct'],
            history['total'],
        ))


def setup_parser(parser):
    parser.set_defaults(func=display_stats)
