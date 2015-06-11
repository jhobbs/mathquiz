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


