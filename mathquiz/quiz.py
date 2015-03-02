import random
from mathquiz.questions import questions


def run_quiz(num_questions):
    num_correct = sum([
        random.choice(questions)().ask()
        for _ in xrange(num_questions)])
    
    print("You got %d out of %d questions right!" % (num_correct, num_questions))
