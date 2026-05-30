from django.db.models import Q


ACTIVE_DROPOUT_STATUS_VALUES = {"active scholar"}


def normalized_status(value):
    return " ".join(str(value or "").strip().lower().split())


def is_active_dropout_status(value):
    return normalized_status(value) in ACTIVE_DROPOUT_STATUS_VALUES


def active_dropout_status_q():
    query = Q()
    for value in ACTIVE_DROPOUT_STATUS_VALUES:
        query |= Q(dropout_active_status__iexact=value)
    return query


def inactive_dropout_status_q():
    return ~active_dropout_status_q()
