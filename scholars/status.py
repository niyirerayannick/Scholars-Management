from django.db.models import Q


ACTIVE_REPLACEMENT_VALUES = {"active scholar"}


def normalized_replacement(value):
    return " ".join(str(value or "").strip().lower().split())


def is_active_replacement(value):
    return normalized_replacement(value) in ACTIVE_REPLACEMENT_VALUES


def active_replacement_q():
    query = Q()
    for value in ACTIVE_REPLACEMENT_VALUES:
        query |= Q(replacement__iexact=value)
    return query


def inactive_replacement_q():
    return ~active_replacement_q()
