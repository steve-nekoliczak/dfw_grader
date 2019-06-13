import copy

# criteria
cases = ['Nom', 'Acc', 'Dat', 'Gen']
defs = ['Def', 'Ind']
genders = ['Masc', 'Fem', 'Neut', 'Plur']
verb_forms = ['Fin', 'Part', 'Inf']
tenses = ['Pres', 'Past']
persons = ['1', '2', '3']
numbers = ['Sing', 'Plur']


def gen_pipeline(ex_type, user_id, from_datetime, to_datetime):
    if ex_type == 'adjective':
        return gen_adjective_pipeline(user_id,
                                      from_datetime,
                                      to_datetime)
    elif ex_type == 'article':
        return gen_article_pipeline(user_id,
                                    from_datetime,
                                    to_datetime)
    elif ex_type == 'verb':
        return gen_verb_pipeline(user_id,
                                 from_datetime,
                                 to_datetime)
    else:
        return None


def pipeline_base(ex_type, user_id, from_datetime, to_datetime):
    pipeline = [
        {
            '$match': {
                'user_id': user_id,
                'type': ex_type,
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

    return pipeline


def gen_adjective_pipeline(user_id, from_datetime, to_datetime):

    pipeline = pipeline_base('adjective', user_id, from_datetime, to_datetime)

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

    pipeline = pipeline_base('article', user_id, from_datetime, to_datetime)

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


def gen_verb_pipeline(user_id, from_datetime, to_datetime):

    pipeline = pipeline_base('verb', user_id, from_datetime, to_datetime)

    # only one facet can be used per pipeline, so [0] is safe
    facets = [p['$facet'] for p in pipeline if '$facet' in p][0]

    # populate $facet field in pipeline
    for verb_form in verb_forms:
        for tense in tenses:
            for person in persons:
                for number in numbers:

                    facet_core = [
                        {
                            '$match': {
                                'ex_details.topic_words.feats.VerbForm': verb_form,
                            }
                        },
                        {'$count': 'count'}
                    ]

                    match_index = -1
                    for i, v in enumerate(facet_core):
                        if '$match' in v:
                            match_index = i

                    if verb_form == 'Inf':
                        total_key = verb_form + '_total'
                        correct_key = verb_form + '_correct'
                    else:
                        total_key = verb_form + '_' + tense + '_' + person + '_' + number + '_' + '_total'
                        correct_key = verb_form + '_' + tense + '_' + person + '_' + number + '_' + '_correct'
                        facet_core[match_index]['$match']['ex_details.topic_words.feats.Tense'] = tense
                        facet_core[match_index]['$match']['ex_details.topic_words.feats.Person'] = person
                        facet_core[match_index]['$match']['ex_details.topic_words.feats.Number'] = number

                    facets[total_key] = copy.deepcopy(facet_core)

                    # Customize correct_key's values
                    facet_core[match_index]['$match']['is_correct'] = True
                    facets[correct_key] = copy.deepcopy(facet_core)

    return pipeline
