from django.db.models import Count, Q

from scholars.models import Scholar
from scholars.status import active_dropout_status_q, inactive_dropout_status_q, is_active_dropout_status


def retention_rate(queryset=None):
    queryset = queryset or Scholar.objects.all()
    total = queryset.count()
    if not total:
        return 0
    return round((queryset.filter(active_dropout_status_q()).count() / total) * 100, 1)


def kpis():
    qs = Scholar.objects.all()
    return {
        "total_scholars": qs.count(),
        "active_scholars": qs.filter(active_dropout_status_q()).count(),
        "inactive_scholars": qs.filter(inactive_dropout_status_q()).count(),
        "retention_rate": retention_rate(qs),
        "female_scholars": qs.filter(gender="Female").count(),
        "male_scholars": qs.filter(gender="Male").count(),
        "alumni": qs.filter(is_alumni=True).count(),
        "bachelor_scholars": qs.filter(level_of_study="Bachelor").count(),
        "masters_scholars": qs.filter(level_of_study="Masters").count(),
        "stem_scholars": qs.filter(stem_category="STEM").count(),
        "non_stem_scholars": qs.filter(stem_category="Non-STEM").count(),
    }


def labels_values(queryset, field):
    rows = queryset.values(field).annotate(total=Count("id")).order_by(field)
    return {
        "labels": [row[field] or "Unspecified" for row in rows],
        "values": [row["total"] for row in rows],
    }


def charts(queryset=None):
    qs = queryset or Scholar.objects.all()
    cohorts = qs.values("cohort").annotate(enrolled=Count("id"), retained=Count("id", filter=active_dropout_status_q())).order_by("cohort")
    category_gender = qs.values("category").annotate(
        female=Count("id", filter=Q(gender="Female")),
        male=Count("id", filter=Q(gender="Male")),
        other=Count("id", filter=Q(gender="Other")),
    ).order_by("category")
    alumni = qs.filter(is_alumni=True).values("level_of_study").annotate(
        female=Count("id", filter=Q(gender="Female")),
        male=Count("id", filter=Q(gender="Male")),
        other=Count("id", filter=Q(gender="Other")),
    ).order_by("level_of_study")
    return {
        "gender_distribution": labels_values(qs, "gender"),
        "category_by_gender": {
            "labels": [row["category"] for row in category_gender],
            "female": [row["female"] for row in category_gender],
            "male": [row["male"] for row in category_gender],
            "other": [row["other"] for row in category_gender],
        },
        "cohort_enrollment_retention": {
            "labels": [row["cohort"] for row in cohorts],
            "enrolled": [row["enrolled"] for row in cohorts],
            "retained": [row["retained"] for row in cohorts],
        },
        "campus_performance": labels_values(qs, "campus"),
        "college_performance": labels_values(qs, "college"),
        "nationality": labels_values(qs, "nationality"),
        "countries": country_overview(qs),
        "level_of_studies": labels_values(qs, "level_of_study"),
        "stem_non_stem": labels_values(qs, "stem_category"),
        "graduation_year_pipeline": labels_values(qs.exclude(graduation_year__isnull=True), "graduation_year"),
        "alumni_by_gender_level": {
            "labels": [row["level_of_study"] for row in alumni],
            "female": [row["female"] for row in alumni],
            "male": [row["male"] for row in alumni],
            "other": [row["other"] for row in alumni],
        },
    }


def pct(part, whole):
    if not whole:
        return 0
    return round((part / whole) * 100, 1)


COUNTRY_ALIASES = {
    "drc": "DRC",
    "dr congo": "DRC",
    "democratic republic of congo": "DRC",
    "rwandan": "Rwanda",
}

COUNTRY_POSITIONS = {
    "Rwanda": (56, 56),
    "Burundi": (55, 63),
    "DRC": (46, 58),
    "South Sudan": (54, 40),
    "Kenya": (64, 55),
    "Malawi": (59, 76),
    "Sudan": (52, 27),
    "Eritrea": (61, 30),
    "Nigeria": (27, 49),
    "Zimbabwe": (55, 84),
}


def country_label(*values):
    for value in values:
        text = " ".join(str(value or "").strip().split())
        if not text:
            continue
        key = text.lower()
        return COUNTRY_ALIASES.get(key, text.upper() if key == "drc" else text.title())
    return "Unspecified"


def country_distribution(qs, limit=None):
    countries = {}
    for row in qs.values("home_country", "nationality_country", "nationality", "dropout_active_status"):
        label = country_label(row["home_country"], row["nationality_country"], row["nationality"])
        item = countries.setdefault(label, {"label": label, "total": 0, "active": 0})
        item["total"] += 1
        if is_active_dropout_status(row["dropout_active_status"]):
            item["active"] += 1
    rows = sorted(countries.values(), key=lambda item: (-item["total"], item["label"]))
    for row in rows:
        row["inactive"] = row["total"] - row["active"]
        row["retention"] = pct(row["active"], row["total"])
    return rows[:limit] if limit else rows


def country_overview(qs):
    rows = country_distribution(qs)
    max_total = max((row["total"] for row in rows), default=1)
    bubbles = []
    fallback_positions = [(22, 28), (76, 34), (74, 68), (32, 74), (42, 20)]
    for index, row in enumerate(rows[:10]):
        x, y = COUNTRY_POSITIONS.get(row["label"], fallback_positions[index % len(fallback_positions)])
        bubbles.append({
            **row,
            "x": x,
            "y": y,
            "size": round(18 + (row["total"] / max_total) * 46, 1),
        })
    return {
        "rows": rows,
        "top": rows[0] if rows else None,
        "country_count": len([row for row in rows if row["label"] != "Unspecified"]),
        "bubbles": bubbles,
        "labels": [row["label"] for row in rows],
        "totals": [row["total"] for row in rows],
        "active": [row["active"] for row in rows],
    }


def analysis_queryset(params):
    qs = Scholar.objects.all()
    exact_filters = {
        "cohort": "cohort",
        "category": "category",
        "gender": "gender",
        "level": "level_of_study",
        "campus": "campus",
        "college": "college",
    }
    for param, field in exact_filters.items():
        value = params.get(param)
        if value and value != "all":
            qs = qs.filter(**{field: value})
    status = params.get("status")
    if status == "active":
        qs = qs.filter(active_dropout_status_q())
    elif status == "inactive":
        qs = qs.filter(inactive_dropout_status_q())
    alumni = params.get("alumni")
    if alumni == "yes":
        qs = qs.filter(is_alumni=True)
    elif alumni == "no":
        qs = qs.filter(is_alumni=False)
    return qs


def filter_options():
    fields = [
        ("cohort", "cohort"),
        ("category", "category"),
        ("gender", "gender"),
        ("level", "level_of_study"),
        ("campus", "campus"),
        ("college", "college"),
    ]
    options = {}
    for key, field in fields:
        options[key] = list(
            Scholar.objects.exclude(**{f"{field}__exact": ""})
            .values_list(field, flat=True)
            .distinct()
            .order_by(field)
        )
    return options


def group_stats(qs, field):
    rows = qs.values(field).annotate(
        total=Count("id"),
        active=Count("id", filter=active_dropout_status_q()),
        inactive=Count("id", filter=inactive_dropout_status_q()),
        female=Count("id", filter=Q(gender="Female")),
        male=Count("id", filter=Q(gender="Male")),
        alumni=Count("id", filter=Q(is_alumni=True)),
    ).order_by(field)
    data = []
    for row in rows:
        total = row["total"]
        data.append({
            "label": row[field] or "Unspecified",
            "total": total,
            "active": row["active"],
            "inactive": row["inactive"],
            "female": row["female"],
            "male": row["male"],
            "alumni": row["alumni"],
            "retention": pct(row["active"], total),
        })
    return data


def gender_summary(qs):
    total = qs.count()
    female = qs.filter(gender="Female").count()
    male = qs.filter(gender="Male").count()
    other = qs.exclude(gender__in=["Female", "Male"]).count()
    return {
        "total": total,
        "female": female,
        "male": male,
        "other": other,
        "female_pct": pct(female, total),
        "male_pct": pct(male, total),
        "active_female": qs.filter(gender="Female").filter(active_dropout_status_q()).count(),
        "active_male": qs.filter(gender="Male").filter(active_dropout_status_q()).count(),
        "alumni_female": qs.filter(gender="Female", is_alumni=True).count(),
        "alumni_male": qs.filter(gender="Male", is_alumni=True).count(),
    }


def category_totals(qs):
    rows = qs.values("category").annotate(
        total=Count("id"),
        active=Count("id", filter=active_dropout_status_q()),
        female=Count("id", filter=Q(gender="Female")),
        male=Count("id", filter=Q(gender="Male")),
    ).order_by("category")
    return list(rows)


def class_year_intake(qs):
    class_years = list(qs.exclude(class_year="").values_list("class_year", flat=True).distinct().order_by("class_year"))
    intakes = list(qs.exclude(intake="").values_list("intake", flat=True).distinct().order_by("intake"))
    datasets = []
    for intake in intakes:
        datasets.append({
            "label": intake,
            "values": [qs.filter(class_year=year, intake=intake).count() for year in class_years],
        })
    return {"labels": class_years, "datasets": datasets}


def chart_payload(qs):
    cohorts = group_stats(qs, "cohort")
    campuses = group_stats(qs, "campus")
    colleges = group_stats(qs, "college")
    categories = category_totals(qs)
    graduation = group_stats(qs.exclude(graduation_year__isnull=True), "graduation_year")
    alumni_gender = group_stats(qs.filter(is_alumni=True), "gender")
    alumni_level = group_stats(qs.filter(is_alumni=True), "level_of_study")
    levels = group_stats(qs, "level_of_study")
    return {
        "gender": gender_summary(qs),
        "countries": country_overview(qs),
        "categories": categories,
        "cohorts": cohorts,
        "campuses": campuses,
        "colleges": colleges,
        "nationality": group_stats(qs, "nationality"),
        "levels": levels,
        "stem": group_stats(qs, "stem_category"),
        "graduation": graduation,
        "class_year_intake": class_year_intake(qs),
        "alumni_gender": alumni_gender,
        "alumni_level": alumni_level,
    }


def top_bottom(rows):
    if not rows:
        return None, None
    ranked = sorted(rows, key=lambda item: item["retention"], reverse=True)
    return ranked[0], ranked[-1]


def analysis_context(params):
    qs = analysis_queryset(params)
    total = qs.count()
    active = qs.filter(active_dropout_status_q()).count()
    inactive = qs.filter(inactive_dropout_status_q()).count()
    female = qs.filter(gender="Female").count()
    alumni = qs.filter(is_alumni=True).count()
    payload = chart_payload(qs)
    campus_best, campus_low = top_bottom(payload["campuses"])
    cohort_best, cohort_low = top_bottom(payload["cohorts"])
    level_low = min(payload["levels"], key=lambda item: item["retention"], default=None)
    kpi_cards = [
        {"label": "Total Scholars", "value": total, "sub": "Current filtered population", "tone": "teal"},
        {"label": "Active Scholars", "value": active, "sub": f"{pct(active, total)}% retention", "tone": "teal"},
        {"label": "Dropout / Inactive", "value": inactive, "sub": f"{pct(inactive, total)}% attrition", "tone": "gold"},
        {"label": "Female Scholars", "value": female, "sub": f"{pct(female, total)}% of filtered group", "tone": "slate"},
        {"label": "Alumni", "value": alumni, "sub": f"{payload['gender']['alumni_female']}F / {payload['gender']['alumni_male']}M", "tone": "plum"},
    ]
    funnel = [
        {"label": "Total Scholars", "count": total, "pct": 100},
        {"label": "Active", "count": active, "pct": pct(active, total)},
        {"label": "Alumni", "count": alumni, "pct": pct(alumni, total)},
        {"label": "Inactive", "count": inactive, "pct": pct(inactive, total)},
    ]
    insights = [
        f"{cohort_best['label']} leads cohort retention at {cohort_best['retention']}%." if cohort_best else "No cohort data is available yet.",
        f"{campus_low['label']} has the lowest campus retention at {campus_low['retention']}%." if campus_low else "No campus retention data is available yet.",
        f"{level_low['label']} retention is {level_low['retention']}%, the lowest level-of-study rate." if level_low else "No level-of-study data is available yet.",
        f"Female representation is {pct(female, total)}% across the current filtered scholar set.",
    ]
    return {
        "options": filter_options(),
        "selected": {key: params.get(key, "all") for key in ["cohort", "category", "gender", "status", "level", "campus", "alumni", "college"]},
        "kpi_cards": kpi_cards,
        "payload": payload,
        "campuses": payload["campuses"],
        "colleges": payload["colleges"],
        "cohorts": payload["cohorts"],
        "funnel": funnel,
        "insights": insights,
        "filtered_total": total,
    }
