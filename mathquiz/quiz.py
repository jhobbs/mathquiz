import random

from mathquiz.stats import (
    group_by_mastery,
    questions_from_user_data,
    )


class Quiz(object):
    def __init__(self, question_types, user_data):
        self.question_types = question_types
        self.user_data = user_data
        self.weighted_question_types = self.get_weighted_question_types()

    def get_weighted_question_types(self):
        question_history = questions_from_user_data(self.user_data)
        question_types_by_mastery = group_by_mastery(
            self.question_types, question_history)
        return self.question_types

    def pick_next_question_type(self):
        question_type = random.choice(self.question_types)
        return question_type

    def questions(self, options):
        for _ in xrange(options.num_questions):
            question_type = self.pick_next_question_type()
            yield self.generate_question(question_type, options)

    def generate_question(self, question, options):
        option_vars = vars(options)
        module_name = "%s_" % (question.name)
        question_options = {
            arg[len(module_name):]: value
            for arg, value in option_vars.iteritems()
            if arg.startswith("%s_" % (question.name))}
        return question(question_options)
