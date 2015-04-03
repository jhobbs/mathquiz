from mathquiz.storage import get_current_user_data


def display_stats(args):
    user = args.user
    print("Stats for %s:" % user)
    user_data = get_current_user_data(user)
    num_quizes = len(user_data['results'])
    print("Quizes completed: %d" % (num_quizes))
    questions = []
    for quiz in user_data['results']:
        questions.extend(quiz.results)
    correct_questions = [
        question for question in questions
        if question.result]
    print("Total questions: %d" % len(questions))
    print("Correctly answered questions: %d" % len(correct_questions))
    print("Overall success rate: %d%%" % (
        int(float(len(correct_questions))/len(questions) * 100)))


def setup_parser(parser):
    parser.set_defaults(func=display_stats)
