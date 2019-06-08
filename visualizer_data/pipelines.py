
# article criteria
cases = ['Nom', 'Acc', 'Dat', 'Gen']
defs = ['Def', 'Ind']
genders = ['Masc', 'Fem', 'Neut', 'Plur']


def article_pipeline(user_id, from_datetime, to_datetime):
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
                    facets_local = {
                        total_key: [
                            {
                                '$match': {
                                    'ex_details.topic_words.feats.Case': case,
                                    'ex_details.topic_words.feats.Definite': def_,
                                    'ex_details.topic_words.feats.Number': 'Plur',
                                }
                            },
                            {'$count': 'count'}
                        ],
                        correct_key: [
                            {
                                '$match': {
                                    'is_correct': True,
                                    'ex_details.topic_words.feats.Case': case,
                                    'ex_details.topic_words.feats.Definite': def_,
                                    'ex_details.topic_words.feats.Number': 'Plur',
                                }
                            },
                            {'$count': 'count'}
                        ],
                    }
                else:
                    facets_local = {
                        total_key: [
                            {
                                '$match': {
                                    'ex_details.topic_words.feats.Case': case,
                                    'ex_details.topic_words.feats.Definite': def_,
                                    'ex_details.topic_words.feats.Gender': gender,
                                    'ex_details.topic_words.feats.Number': 'Sing',
                                }
                            },
                            {'$count': 'count'}
                        ],
                        correct_key: [
                            {
                                '$match': {
                                    'is_correct': True,
                                    'ex_details.topic_words.feats.Case': case,
                                    'ex_details.topic_words.feats.Definite': def_,
                                    'ex_details.topic_words.feats.Gender': gender,
                                    'ex_details.topic_words.feats.Number': 'Sing',
                                }
                            },
                            {'$count': 'count'}
                        ],
                    }
                facets[total_key] = facets_local[total_key]
                facets[correct_key] = facets_local[correct_key]

    return pipeline

