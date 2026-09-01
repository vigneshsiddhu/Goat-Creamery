from django import forms

from .models import GoatWeight, GoatMilk, Goat


class GoatWeightForm(forms.ModelForm):

    class Meta:
        model = GoatWeight
        fields = ["goat","weight","date","note",]
        widgets = {
            "goat": forms.Select(
                attrs={
                    "class": "production-form-input"
                }
            ),
            "weight": forms.NumberInput(
                attrs={
                    "class": "production-form-input",
                    "placeholder": "Enter weight in kg",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "production-form-input",
                    "type": "date",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "production-form-input",
                    "placeholder": "Enter note",
                    "rows": 4,
                }
            ),
        }

class GoatWeightVoiceForm(forms.ModelForm):
    goat = forms.ModelChoiceField(
            queryset=Goat.objects.none(),
            empty_label="Select Goat Tag",
            label="Goat Tag",
            widget=forms.Select(
            attrs={
                "class": "production-form-input"
            }
        )
    )
    # WEIGHT_CHOICES = [("0.1", "0.1 L"),("0.2", "0.2 L"),("0.3", "0.3 L"),("0.4", "0.4 L"),("0.5", "0.5 L"),("0.6", "0.6 L"),("0.7", "0.7 L"),("0.8", "0.8 L"),("0.9", "0.9 L"),("1.0", "1.0 L"),("1.1", "1.1 L"),("1.2", "1.2 L"),("1.3", "1.3 L"),("1.4", "1.4 L"),("1.5", "1.5 L"),("1.6", "1.6 L"),("1.7", "1.7 L"),("1.8", "1.8 L"),("1.9", "1.9 L"),("2.0", "2.0 L"),]
    WEIGHT_CHOICES = [(str(round(i / 10, 1)), f"{round(i / 10, 1)} kg") for i in range(10, 801)]
    weight = forms.ChoiceField(choices=WEIGHT_CHOICES,required=True,label="Goat Weight",
            widget=forms.RadioSelect(
                attrs={
                    "class": "milk-quantity-radio"
                }
            )
    )
    class Meta:
        model = GoatWeight
        fields = [
            "goat",
            "weight",
        ]
    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Initially no goats
        self.fields["goat"].queryset = Goat.objects.none()
        # Load goats belonging to current business
        if business:
            self.fields["goat"].queryset = (
                Goat.objects
                .filter(
                    business=business,
                    live=True
                )
                .order_by("token_no")
            )


class GoatMilkForm(forms.ModelForm):
    QUANTITY_CHOICES = [("0.1", "0.1 L"),("0.2", "0.2 L"),("0.3", "0.3 L"),("0.4", "0.4 L"),("0.5", "0.5 L"),("0.6", "0.6 L"),("0.7", "0.7 L"),("0.8", "0.8 L"),("0.9", "0.9 L"),("1.0", "1.0 L"),("1.1", "1.1 L"),("1.2", "1.2 L"),("1.3", "1.3 L"),("1.4", "1.4 L"),("1.5", "1.5 L"),("1.6", "1.6 L"),("1.7", "1.7 L"),("1.8", "1.8 L"),("1.9", "1.9 L"),("2.0", "2.0 L"),]
    # goat = forms.ModelChoiceField(
    #     queryset=Goat.objects.none(),
    #     empty_label="Select Goat Tag",
    #     label="Goat Tag",
    #     widget=forms.Select(
    #         attrs={
    #             "class": "production-form-input"
    #         }
    #     )
    # )
    milk_weight = forms.ChoiceField(
        choices=QUANTITY_CHOICES,
        required=True,
        widget=forms.RadioSelect(
            attrs={
                "class": "milk-quantity-radio"
            }
        )
    )
    class Meta:
        model = GoatMilk
        fields = [
        "goat",
        "milk_weight",
        "date",
        "time",
        "note",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "production-form-input",
                }
            ),
            "time": forms.Select(
                attrs={
                    "class": "production-form-input",
                }
            ),
            "note": forms.Textarea(
                attrs={
                    "class": "production-form-input",
                    "rows": 3,
                    "placeholder": "Optional note...",
                }
            ),
        }
    def __init__(self,*args,business=None,voice=False,**kwargs):
        super().__init__(*args, **kwargs)
        # self.fields["goat"].queryset = Goat.objects.none()
        # if business:
        #     self.fields["goat"].queryset = (
        #         Goat.objects
        #         .filter(
        #             business=business,
        #             gender="FEMALE",
        #             live=True,
        #         )
        #         .order_by("token_no")
        #     )
        if voice:
            self.fields["date"].required = False
            self.fields["time"].required = False
            self.fields["note"].required = False
            self.fields.pop("date")
            self.fields.pop("time")
            self.fields.pop("note")


class GoatMilkVoiceForm(forms.Form):
    goat = forms.ModelChoiceField(
    queryset=Goat.objects.none(),
    empty_label="Select Goat Tag",
    label="Goat Tag",
    widget=forms.Select(
            attrs={
                "class": "production-form-input"
            }
        )
    )
    QUANTITY_CHOICES = [("0.1", "0.1 L"),("0.2", "0.2 L"),("0.3", "0.3 L"),("0.4", "0.4 L"),("0.5", "0.5 L"),("0.6", "0.6 L"),("0.7", "0.7 L"),("0.8", "0.8 L"),("0.9", "0.9 L"),("1.0", "1.0 L"),("1.1", "1.1 L"),("1.2", "1.2 L"),("1.3", "1.3 L"),("1.4", "1.4 L"),("1.5", "1.5 L"),("1.6", "1.6 L"),("1.7", "1.7 L"),("1.8", "1.8 L"),("1.9", "1.9 L"),("2.0", "2.0 L"),]
    milk_weight = forms.ChoiceField(
        choices=QUANTITY_CHOICES,
        required=True,
        widget=forms.RadioSelect(
            attrs={
                "class": "milk-quantity-radio"
            }
        )
    )
    class Meta:
        model = GoatMilk
        fields = [
            "goat",
            "milk_weight",
        ]
    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        if business:
            self.fields["goat"].queryset = (
                Goat.objects
                .filter(
                    business=business,
                    gender="FEMALE",
                    live=True
                )
                .order_by("token_no")
            )
    