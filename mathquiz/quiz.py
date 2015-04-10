import random


class Quiz(object):
    def __init__(self, question_types, user_data):
        self.question_types = question_types
        self.user_data = user_data

    def questions(self, options):
        for _ in xrange(options.num_questions):
            question_type = random.choice(self.question_types)
            yield self.generate_question(question_type, options)

    def generate_question(self, question, options):
        option_vars = vars(options)
        module_name = "%s_" % (question.name)
        question_options = {
            arg[len(module_name):]: value
            for arg, value in option_vars.iteritems()
            if arg.startswith("%s_" % (question.name))}
        return question(question_options)
