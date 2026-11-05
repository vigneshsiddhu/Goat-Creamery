from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Goat,Disease,DeathGoat,GoatHealth

class GoatForm(forms.ModelForm):
    class Meta:
        model = Goat
        fields = [
            "token_no",
            "rfid",
            "breed_variety",
            "maturity",
            "gender",
            "dob",
            "live",
        ]
        widgets = {
            "token_no": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. GC-F-001",
            }),
            "rfid": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Optional tag number",
            }),
            "breed_variety": forms.Select(attrs={"class": "form-input"}),
            "maturity": forms.Select(attrs={"class": "form-input"}),
            "gender": forms.Select(attrs={"class": "form-input"}),
            "dob": forms.DateInput(attrs={
                "class": "form-input",
                "type": "date",
            }),
            "live": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rfid"].required = False
        self.fields["dob"].required = False
        self.fields["live"].required = False
        self.fields["breed_variety"].choices = [("", "Select breed")] + list(Goat.BREED_CHOICES)
        self.fields["maturity"].choices = [("", "Select maturity")] + list(Goat.MATURITY_CHOICES)
        self.fields["gender"].choices = [("", "Select gender")] + list(Goat.GENDER_CHOICES)

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
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "e.g. PPR, mastitis",
            }),
            "symptoms": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": "What you observe",
                "rows": 3,
            }),
            "impact_goat": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": "Effect on the animal",
                "rows": 3,
            }),
            "treatment": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": "Treatment or protocol",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["symptoms"].required = False
        self.fields["impact_goat"].required = False
        self.fields["treatment"].required = False

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
            "goat": forms.Select(attrs={"class": "form-input"}),
            "disease": forms.Select(attrs={"class": "form-input"}),
            "died_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "comment": forms.Textarea(attrs={
                "class": "form-input",
                "placeholder": "Optional note",
                "rows": 3,
            }),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["goat"].queryset = Goat.objects.none()
        self.fields["disease"].queryset = Disease.objects.none()
        self.fields["goat"].empty_label = "Select goat"
        self.fields["disease"].empty_label = "Select disease (optional)"
        self.fields["disease"].required = False
        self.fields["comment"].required = False
        if business:
            goats = Goat.objects.filter(business=business, live=True)
            if self.instance and getattr(self.instance, "goat_id", None):
                goats = Goat.objects.filter(business=business).filter(
                    Q(live=True) | Q(pk=self.instance.goat_id)
                )
            self.fields["goat"].queryset = goats.order_by("token_no")
            self.fields["disease"].queryset = Disease.objects.filter(
                business=business
            ).order_by("name")

class GoatHealthForm(forms.ModelForm):
    STATUS_CHOICES = [("under_treatment","Under Treatment"),("recovered","Recovered"),("critical","Critical"),]
    status = forms.ChoiceField(choices=STATUS_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    class Meta:
        model = GoatHealth
        fields = [
            "goat",
            "disease",
            "comment",
            "status",
            "date",
        ]
        widgets = {
            "goat": forms.Select(attrs={
                "class":"form-input",
            }),
            "disease": forms.Select(attrs={
                "class":"form-input",
            }),
            "comment": forms.Textarea(attrs={
                "class":"form-input",
                "placeholder":"Enter health notes",
                "rows":4,
            }),
            "date": forms.DateInput(attrs={
                "class":"form-input",
                "type":"date",
            }),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["goat"].queryset = Goat.objects.none()
        self.fields["disease"].queryset = Disease.objects.none()
        self.fields["goat"].empty_label = "Select goat"
        self.fields["disease"].empty_label = "Select disease"
        self.fields["status"].choices = [("", "Select status")] + list(self.STATUS_CHOICES)
        self.fields["comment"].required = False
        if business:
            self.fields["goat"].queryset = Goat.objects.filter(
                business=business
            ).order_by("token_no")
            self.fields["disease"].queryset = Disease.objects.filter(
                business=business
            ).order_by("name")
    def clean(self):
        cleaned = super().clean()
        goat = cleaned.get("goat")
        disease = cleaned.get("disease")
        if goat and disease and goat.business_id != disease.business_id:
            raise ValidationError(
                "Goat and disease must belong to the same business."
            )
        return cleaned