from django import forms
from .models import Goat
from .models import Disease
from .models import DeathGoat


class GoatForm(forms.ModelForm):

    class Meta:
        model = Goat

        fields = [
            "token_no",
            "rfid",
            "breed_variety",
            "dob",
            "gender",
            "maturity",
            "live",
        ]

        widgets = {
            "token_no": forms.TextInput(
                attrs={
                    "class": "goat-form-input",
                    "placeholder": "Enter token number",
                }
            ),

            "rfid": forms.TextInput(
                attrs={
                    "class": "goat-form-input",
                    "placeholder": "Enter RFID number",
                }
            ),

            "dob": forms.DateInput(
                attrs={
                    "class": "goat-form-input",
                    "type": "date",
                }
            ),
            "maturity": forms.DateInput(
                attrs={
                    "class": "goat-form-input",
                    "type": "maturity",
                }
            ),
            "live": forms.CheckboxInput(
                attrs={
                    "class": "goat-form-checkbox",
                }
            ),
        }

class DiseaseForm(forms.ModelForm):

    class Meta:
        model = Disease

        fields = [
            "name",
            "symptoms",
            "impact_goat",
            "treatment",
        ]

        widgets = {

            "name": forms.TextInput(
                attrs={
                    "class": "goat-form-input",
                    "placeholder": "Enter disease name",
                }
            ),

            "symptoms": forms.Textarea(
                attrs={
                    "class": "goat-form-input",
                    "placeholder": "Enter disease symptoms",
                    "rows": 4,
                }
            ),

            "impact_goat": forms.Textarea(
                attrs={
                    "class": "goat-form-input",
                    "placeholder": "Enter impact on goat",
                    "rows": 4,
                }
            ),

            "treatment": forms.Textarea(
                attrs={
                    "class": "goat-form-input",
                    "placeholder": "Enter treatment details",
                    "rows": 4,
                }
            ),
        }

class DeathGoatForm(forms.ModelForm):

    class Meta:
        model = DeathGoat

        fields = [
            "goat",
            "disease",
            "died_date",
            "comment",
        ]

        widgets = {
            "goat": forms.Select(
                attrs={
                    "class": "death-goat-form-input",
                }
            ),

            "disease": forms.Select(
                attrs={
                    "class": "death-goat-form-input",
                }
            ),

            "died_date": forms.DateInput(
                attrs={
                    "class": "death-goat-form-input",
                    "type": "date",
                }
            ),

            "comment": forms.Textarea(
                attrs={
                    "class": "death-goat-form-input",
                    "placeholder": "Enter comment",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        business = kwargs.pop("business", None)

        super().__init__(*args, **kwargs)

        if business:

            self.fields["goat"].queryset = Goat.objects.filter(
                business=business,
                live=True
            ).order_by("token_no")

            self.fields["disease"].queryset = Disease.objects.filter(
                business=business
            ).order_by("name")

        self.fields["disease"].required = False