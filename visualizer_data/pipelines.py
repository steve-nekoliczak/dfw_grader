import copy

# article criteria
cases = ['Nom', 'Acc', 'Dat', 'Gen']
defs = ['Def', 'Ind']
genders = ['Masc', 'Fem', 'Neut', 'Plur']


def gen_pipeline(ex_type, user_id, from_datetime, to_datetime):
    if ex_type == 'adjective':
        return gen_adjective_pipeline(user_id,
                                      from_datetime,
                                      to_datetime)
    elif ex_type == 'article':
        return gen_article_pipeline(user_id,
                                    from_datetime,
                                    to_datetime)
    else:
        return None


def gen_adjective_pipeline(user_id, from_datetime, to_datetime):
    pipeline = [
        {
            '$match': {
                'user_id': user_id,
                'type': 'adjective',
                'timestamp': {'$gt': from_datetime, '$lt': to_datetime}
            }
        },
        {
            '$lookup': {
                'from': 'exercise',
                'localField': "ex_id",
                'foreignField': '_id',
                'as': 'ex_details'
            }
        },
        {'$unwind': '$ex_details'},
        {'$unwind': '$ex_details.topic_words'},
        {
            '$match': {
                '$expr': {
                    '$eq': ['$topic_word_index', '$ex_details.topic_words.index']
                }
            }
        },
        {
            '$facet': {
            }
        }
    ]

    # only one facet can be used per pipeline, so [0] is safe
    facets = [p['$facet'] for p in pipeline if '$facet' in p][0]

    # populate $facet field in pipeline
    for case in cases:
        for gender in genders:
            total_key = case + '_' + gender + '_total'
            correct_key = case + '_' + gender + '_correct'

            if gender == 'Plur':
                number = 'Plur'
            else:
                number = 'Sing'

            facet_core = [
                {
                    '$match': {
                        'ex_details.topic_words.feats.Case': case,
                        'ex_details.topic_words.feats.Number': number,
                    }
                },
                {'$count': 'count'}
            ]

            match_index = -1
            for i, v in enumerate(facet_core):
                if '$match' in v:
                    match_index = i

            if number == 'Sing':
                facet_core[match_index]['$match']['ex_details.topic_words.feats.Gender'] = gender

            facets[total_key] = copy.deepcopy(facet_core)

            # Customize correct_key's values
            facet_core[match_index]['$match']['is_correct'] = True
            facets[correct_key] = copy.deepcopy(facet_core)

    return pipeline


def gen_article_pipeline(user_id, from_datetime, to_datetime):
    pipeline = [
        {
            '$match': {
                'user_id': user_id,
                'type': 'article',
                'timestamp': {'$gt': from_datetime, '$lt': to_datetime}
            }
        },
        {
            '$lookup': {
                'from': 'exercise',
                'localField': "ex_id",
                'foreignField': '_id',
                'as': 'ex_details'
            }
        },
        {'$unwind': '$ex_details'},
        {'$unwind': '$ex_details.topic_words'},
        {
            '$match': {
                '$expr': {
                    '$eq': ['$topic_word_index', '$ex_details.topic_words.index']
                }
            }
        },
        {
            '$facet': {
            }
        }
    ]

    # only one facet can be used per pipeline, so [0] is safe
    facets = [p['$facet'] for p in pipeline if '$facet' in p][0]

    # populate $facet field in pipeline
    for case in cases:
        for def_ in defs:
            for gender in genders:
                total_key = case + '_' + def_ + '_' + gender + '_total'
                correct_key = case + '_' + def_ + '_' + gender + '_correct'

                if gender == 'Plur':
                    number = 'Plur'
                else:
                    number = 'Sing'

                facet_core = [
                    {
                        '$match': {
                            'ex_details.topic_words.feats.Case': case,
                            'ex_details.topic_words.feats.Definite': def_,
                            'ex_details.topic_words.feats.Number': number,
                        }
                    },
                    {'$count': 'count'}
                ]

                match_index = -1
                for i, v in enumerate(facet_core):
                    if '$match' in v:
                        match_index = i

                if number == 'Sing':
                    facet_core[match_index]['$match']['ex_details.topic_words.feats.Gender'] = gender

                facets[total_key] = copy.deepcopy(facet_core)

                # Customize correct_key's values
                facet_core[match_index]['$match']['is_correct'] = True
                facets[correct_key] = copy.deepcopy(facet_core)

    return pipeline

