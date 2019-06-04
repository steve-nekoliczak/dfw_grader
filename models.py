import datetime
import time


class ExAttempt(dict):

    def __init__(self, ex_id, user_id, topic_word_index, guess, timestamp=None):
        self.ex_id = ex_id
        self.user_id = user_id
        self.topic_word_index = topic_word_index
        self.guess = guess
        self.answer = None
        self.is_correct = None
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.datetime.fromtimestamp(time.time()).isoformat()

    def grade(self, answer):
        self.answer = answer
        self.is_correct = self.guess == self.answer

    def to_dict(self):
        return self.__dict__


class GradeAggregator:

    def __init__(self):
        self.grades = []

