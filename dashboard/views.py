from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import analysis_context, analysis_queryset, charts, kpis


@login_required
def dashboard(request):
    stats = kpis()
    cards = [
        ("Total Scholars", stats["total_scholars"]),
        ("Active Scholars", stats["active_scholars"]),
        ("Inactive Scholars", stats["inactive_scholars"]),
        ("Retention Rate", f'{stats["retention_rate"]}%'),
        ("Female Scholars", stats["female_scholars"]),
        ("Male Scholars", stats["male_scholars"]),
        ("Alumni", stats["alumni"]),
        ("Bachelor Scholars", stats["bachelor_scholars"]),
        ("Masters Scholars", stats["masters_scholars"]),
        ("STEM Scholars", stats["stem_scholars"]),
        ("Non-STEM Scholars", stats["non_stem_scholars"]),
    ]
    context = analysis_context(request.GET)
    context.update({"cards": cards, "charts": charts(analysis_queryset(request.GET)), "month_label": "May 2026"})
    return render(request, "dashboard/dashboard.html", context)


@login_required
def analysis(request):
    return render(request, "dashboard/analysis.html", analysis_context(request.GET))
