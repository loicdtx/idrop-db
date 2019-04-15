import re


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance


def snakify(string):
    """Convert camel case string to snake case

    Examples:
        >>> snakify('speciesId')
        'species_id'
        >>> snakify('studyAreaId')
        'study_area_id'
        >>> snakify('study_area_id')
        'study_area_id'

    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def camelify(string):
    """Convert snake case string to camel case

    Examples:
        >>> camelify('species_id')
        'speciesId'
        >>> camelify('speciesId')
        'speciesId'
        >>> camelify('study_area_id')
        'studyAreaId'
    """
    def _camel(match):
        return match.group(1) + match.group(2).upper()
    return re.sub(r'(.*?)_([a-zA-Z])', _camel, string)
