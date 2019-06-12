import datetime
from bson.json_util import dumps, RELAXED_JSON_OPTIONS
from json import loads

from visualizer_data import pipelines


def sanitize_facet_result(result):
    result = result[0]
    for key, value in result.items():
        if len(value) == 0:
            result[key] = 0
        else:
            result[key] = value[0]['count']
    return result


def sanitize_from_datetime_input(datetime_str):
    if not datetime_str:
        return datetime.datetime(1970, 1, 1)
    else:
        return datetime.datetime.fromisoformat(datetime_str)


def sanitize_to_datetime_input(datetime_str):
    if not datetime_str:
        return datetime.datetime.utcnow()
    else:
        return datetime.datetime.fromisoformat(datetime_str)


def get_stats(user_id, ex_type, from_datetime=None, to_datetime=None):
    from config import mongo

    from_datetime = sanitize_from_datetime_input(from_datetime)
    to_datetime = sanitize_to_datetime_input(to_datetime)

    pipeline = pipelines.gen_pipeline(ex_type,
                                      user_id,
                                      from_datetime,
                                      to_datetime)
    if pipeline is None:
        return 'exercise type not found', 404

    result = mongo.db.ex_attempt.aggregate(pipeline)
    if not result:
        return 'exercise id not found', 404

    json_result = loads(dumps(result, json_options=RELAXED_JSON_OPTIONS))

    return sanitize_facet_result(json_result)

