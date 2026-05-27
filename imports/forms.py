from django import forms


class ExcelImportForm(forms.Form):
    file = forms.FileField(
        label="Excel file",
        help_text="Upload .xlsx with headers matching Scholar fields.",
        widget=forms.FileInput(attrs={"accept": ".xlsx", "class": "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"}),
    )
