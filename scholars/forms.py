from django import forms
from django.db.models import Q

from .models import Scholar


class TailwindFormMixin:
    base_class = "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100"

    def _style_fields(self):
        for field in self.fields.values():
            classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{classes} {self.base_class}".strip()


class ScholarForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Scholar
        fields = [
            "student_no",
            "first_name",
            "last_name",
            "gender",
            "dob",
            "marital_status",
            "phone",
            "email",
            "level_of_study",
            "college",
            "program",
            "program_of_studies",
            "campus",
            "stem_category",
            "program_type",
            "joining_year",
            "class_year",
            "intake",
            "cohort",
            "batch",
            "type_of_scholarship",
            "category",
            "region_category",
            "home_country",
            "nationality",
            "nationality_country",
            "province",
            "district",
            "sector",
            "cell",
            "village",
            "length_of_program",
            "expected_graduation_year",
            "graduation_year",
            "home_district",
            "promotion",
            "accepted_offer_status",
            "dropout_active_status",
            "active_status_reason",
            "replacement",
            "by_enrollment",
            "is_active",
            "is_alumni",
            "alumni_status",
            "consider_alumni_as_active",
            "date_of_leaving_program",
            "where_is_going",
            "family_parent_1",
            "family_parent_2",
            "family_parent_3",
            "family_parent_relation_1",
            "family_parent_relation_2",
            "family_parent_relation_3",
            "family_parent_phone_1",
            "family_parent_phone_2",
            "family_parent_phone_3",
            "life_status",
            "remarks",
        ]
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
            "date_of_leaving_program": forms.DateInput(attrs={"type": "date"}),
            "remarks": forms.Textarea(attrs={"rows": 4}),
            "active_status_reason": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ScholarFilterForm(TailwindFormMixin, forms.Form):
    cohort = forms.CharField(required=False)
    category = forms.CharField(required=False)
    gender = forms.ChoiceField(required=False, choices=[("", "All genders")] + Scholar.GENDER_CHOICES)
    status = forms.ChoiceField(required=False, choices=[("", "All statuses"), ("active", "Active"), ("inactive", "Inactive")])
    level_of_study = forms.ChoiceField(required=False, choices=[("", "All levels")] + Scholar.LEVEL_CHOICES)
    campus = forms.CharField(required=False)
    college = forms.CharField(required=False)
    nationality = forms.CharField(required=False)
    alumni_status = forms.ChoiceField(required=False, choices=[("", "All alumni statuses"), ("yes", "Alumni"), ("no", "Not alumni")])
    graduation_year = forms.IntegerField(required=False)
    type_of_scholarship = forms.CharField(required=False)
    q = forms.CharField(required=False, label="Search")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


def filter_scholars(queryset, data):
    form = ScholarFilterForm(data)
    if not form.is_valid():
        return queryset, form
    cleaned = form.cleaned_data
    for field in ["cohort", "category", "gender", "level_of_study", "campus", "college", "nationality", "type_of_scholarship"]:
        value = cleaned.get(field)
        if value:
            lookup = field if field in ["gender", "level_of_study"] else f"{field}__icontains"
            queryset = queryset.filter(**{lookup: value})
    if cleaned.get("status") == "active":
        queryset = queryset.filter(is_active=True)
    elif cleaned.get("status") == "inactive":
        queryset = queryset.filter(is_active=False)
    if cleaned.get("alumni_status") == "yes":
        queryset = queryset.filter(is_alumni=True)
    elif cleaned.get("alumni_status") == "no":
        queryset = queryset.filter(is_alumni=False)
    if cleaned.get("graduation_year"):
        queryset = queryset.filter(graduation_year=cleaned["graduation_year"])
    if cleaned.get("q"):
        q = cleaned["q"]
        queryset = queryset.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(student_no__icontains=q)
            | Q(email__icontains=q)
        )
    return queryset, form
