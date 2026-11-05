from django import forms

from .models import Mating, ParentMapping
from goats.models import Goat


class MatingForm(forms.ModelForm):

    class Meta:
        model = Mating

        fields = [
            "male",
            "female",
            "mating_date",
            "comment",
        ]

        widgets = {
            "male": forms.Select(attrs={"class": "form-input"}),
            "female": forms.Select(attrs={"class": "form-input"}),
            "mating_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "comment": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 3,
                "placeholder": "Optional note",
            }),
        }

    def __init__(self, *args, business=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["male"].queryset = Goat.objects.none()
        self.fields["female"].queryset = Goat.objects.none()
        self.fields["male"].empty_label = "Select male"
        self.fields["female"].empty_label = "Select female"
        self.fields["comment"].required = False

        if business:

            self.fields["male"].queryset = Goat.objects.filter(
                business=business,
                gender="MALE",
                maturity="ADULT",
                live=True,
            ).order_by("token_no")

            self.fields["female"].queryset = Goat.objects.filter(
                business=business,
                gender="FEMALE",
                maturity="ADULT",
                live=True,
            ).order_by("token_no")

    def clean(self):

        cleaned_data = super().clean()

        male = cleaned_data.get("male")
        female = cleaned_data.get("female")

        if male and female and male == female:
            raise forms.ValidationError(
                "Male and female goat cannot be the same goat."
            )

        return cleaned_data


class ParentMappingForm(forms.ModelForm):

    class Meta:
        model = ParentMapping

        fields = [
            "child",
            "parent",
        ]

        widgets = {
            "child": forms.Select(attrs={"class": "form-input"}),
            "parent": forms.Select(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, business=None, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["child"].queryset = Goat.objects.none()
        self.fields["parent"].queryset = Goat.objects.none()
        self.fields["child"].empty_label = "Select kid"
        self.fields["parent"].empty_label = "Select dam"

        if business:
            goats = Goat.objects.filter(
              business=business,
              live=True,
              gender="FEMALE",
              maturity="ADULT",
            ).order_by("token_no")
            mapped_kids = ParentMapping.objects.filter(
                child__business=business
            )
            # When editing, allow the current child
            if self.instance and self.instance.pk:
                mapped_kids = mapped_kids.exclude(
                    pk=self.instance.pk
                )
            mapped_kid_ids = mapped_kids.values_list(
                "child_id",
                flat=True
            )
            kids = Goat.objects.filter(
                business=business,
                live=True,
                maturity="KID",
            ).exclude(
                id__in=mapped_kid_ids
            ).order_by("token_no")

            self.fields["child"].queryset = kids
            self.fields["parent"].queryset = goats
    def clean(self):
        cleaned_data = super().clean()
        child = cleaned_data.get("child")
        parent = cleaned_data.get("parent")

        if child and parent and child == parent:
            raise forms.ValidationError(
                "A goat cannot be its own parent."
            )

        return cleaned_data