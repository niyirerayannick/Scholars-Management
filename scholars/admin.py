from django.contrib import admin

from .models import Scholar


@admin.register(Scholar)
class ScholarAdmin(admin.ModelAdmin):
    list_display = ("student_no", "full_name", "gender", "type_of_scholarship", "category", "cohort", "level_of_study", "campus", "active_status_label", "replacement", "is_alumni")
    list_filter = ("gender", "category", "type_of_scholarship", "cohort", "level_of_study", "campus", "college", "nationality", "replacement", "is_alumni")
    search_fields = ("student_no", "first_name", "last_name", "email", "phone")
    date_hierarchy = "created_at"
