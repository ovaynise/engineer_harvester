from datetime import timedelta

from constructions.models import Constructions, ConstructionsCompany
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone


def get_statistics_for_last_week():
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday() + 7)
    end_of_week = start_of_week + timedelta(days=6)
    total_objects_last_week = Constructions.objects.filter(
        date_finish__range=[start_of_week, end_of_week]
    ).count()
    objects_built_last_week = Constructions.objects.filter(
        date_acceptance__range=[start_of_week, end_of_week]
    ).count()
    constructions_in_progress = Constructions.objects.filter(
        date_start__lte=today, date_finish__gte=today
    ).count()
    contractors_count = ConstructionsCompany.objects.count()
    return (
        total_objects_last_week,
        objects_built_last_week,
        constructions_in_progress,
        contractors_count,
    )


def index(request):
    (
        total_objects_last_week,
        objects_built_last_week,
        constructions_in_progress,
        contractors_count,
    ) = get_statistics_for_last_week()
    total_objects = Constructions.objects.count()
    objects_in_progress = Constructions.objects.filter(
        date_finish__isnull=True
    ).count()
    objects_built_this_year = Constructions.objects.filter(
        date_acceptance__year=timezone.now().year
    ).count()
    objects_built_last_year = Constructions.objects.filter(
        date_acceptance__year=timezone.now().year - 1
    ).count()
    today = timezone.now().date()
    end_of_year = today.replace(month=12, day=31)
    days_until_new_year = (end_of_year - today).days
    latest_objects = Constructions.objects.filter(
        date_acceptance__isnull=False
    ).order_by("-date_acceptance")[:5]
    constructions_list = Constructions.objects.order_by(
        "-created_at"
    ).prefetch_related("constructions_company")
    paginator = Paginator(constructions_list, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "total_objects": total_objects,
        "objects_in_progress": objects_in_progress,
        "objects_built_this_year": objects_built_this_year,
        "objects_built_last_year": objects_built_last_year,
        "days_until_new_year": days_until_new_year,
        "latest_objects": latest_objects,
        "page_obj": page_obj,
        "total_objects_last_week": total_objects_last_week,
        "objects_built_last_week": objects_built_last_week,
        "constructions_in_progress": constructions_in_progress,
        "contractors_count": contractors_count,
    }
    return render(request, "homepage/index.html", context)
