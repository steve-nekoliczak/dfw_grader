from bson import ObjectId
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from json import loads

from models import ExAttempt


def post_ex_attempt(ex_id, user_id, topic_word_index, guess, timestamp=None):
    from config import mongo

    ea = ExAttempt(ex_id=ex_id,
                   user_id=user_id,
                   topic_word_index=topic_word_index,
                   guess=guess,
                   timestamp=timestamp)

    result = mongo.db.exercise.find_one(
        {'_id': ObjectId(ex_id)}
    )

    if not result:
        return 'exercise id not found', 404

    answer = [tw['text'] for tw in result['topic_words'] if tw['index'] == topic_word_index][0]
    if answer:
        ea.grade(answer)
    else:
        return 'topic word index not found', 404

    ea_dict = ea.to_dict()
    mongo.db.ex_attempt.insert(ea_dict)

    json_result = loads(dumps(ea_dict, json_options=RELAXED_JSON_OPTIONS))
    return json_result

