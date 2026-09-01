from django import forms

from .models import FarmExpense


EXPENSE_CATEGORY_CHOICES = [
    ("Feed", "Feed"),
    ("Fodder", "Fodder"),
    ("Medicine", "Medicine"),
    ("Labour", "Labour"),
    ("Electricity", "Electricity"),
    ("Water", "Water"),
    ("Transportation", "Transportation"),
    ("Maintenance", "Maintenance"),
    ("Equipment", "Equipment"),
    ("Veterinary", "Veterinary"),
    ("Other", "Other"),
]


class FarmExpenseForm(forms.ModelForm):

    category = forms.ChoiceField(
        choices=EXPENSE_CATEGORY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "farm-expense-form-input"
            }
        )
    )

    class Meta:
        model = FarmExpense

        fields = [
            "date",
            "category",
            "amount",
            "comment",
        ]

        widgets = {

            "date": forms.DateInput(
                attrs={
                    "class": "farm-expense-form-input",
                    "type": "date",
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "farm-expense-form-input",
                    "placeholder": "Enter amount",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "class": "farm-expense-form-input",
                    "placeholder": "Enter note",
                    "rows": 4,
                }
            ),
        }