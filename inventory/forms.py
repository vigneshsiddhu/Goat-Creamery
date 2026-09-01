from django import forms

from .models import FeedStock


FODDER_VARIETY_CHOICES = [
    ("Alfalfa", "Alfalfa"),
    ("Moringa", "Moringa"),
    ("Indigofera", "Indigofera"),
    ("Gliricidia", "Gliricidia"),
    ("Napier", "Napier"),
    ("Hay", "Hay"),
    ("Silage", "Silage"),
    ("Other", "Other"),
]


class FeedStockForm(forms.ModelForm):

    fodder_variety = forms.ChoiceField(
        choices=FODDER_VARIETY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "inventory-form-input"
            }
        )
    )

    class Meta:
        model = FeedStock

        fields = [
            "date",
            "fodder_variety",
            "stock_weight",
            "rate",
            "total_amount",
            "current_stock_kg",
        ]

        widgets = {

            "date": forms.DateInput(
                attrs={
                    "class": "inventory-form-input",
                    "type": "date",
                }
            ),

            "stock_weight": forms.NumberInput(
                attrs={
                    "class": "inventory-form-input",
                    "placeholder": "Enter stock weight",
                    "step": "0.001",
                    "min": "0",
                }
            ),

            "rate": forms.NumberInput(
                attrs={
                    "class": "inventory-form-input",
                    "placeholder": "Enter rate per kg",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "total_amount": forms.NumberInput(
                attrs={
                    "class": "inventory-form-input",
                    "placeholder": "Enter total amount",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "current_stock_kg": forms.NumberInput(
                attrs={
                    "class": "inventory-form-input",
                    "placeholder": "Enter current stock",
                    "step": "0.001",
                    "min": "0",
                }
            ),
        }