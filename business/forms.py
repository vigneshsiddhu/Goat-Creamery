from django import forms
from django.contrib.auth import get_user_model
from .models import Business,BusinessUser,Location

User = get_user_model()


class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ["name","address","gstn","phone_number","owner","status"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. Goat Creamery"}),
            "address": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Optional address"}),
            "gstn": forms.TextInput(attrs={"class": "form-input", "placeholder": "Optional GSTIN"}),
            "phone_number": forms.TextInput(attrs={"class": "form-input", "placeholder": "Optional phone"}),
            "owner": forms.Select(attrs={"class": "form-input"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["owner"].queryset = User.objects.filter(is_active=True).order_by("username")
        self.fields["owner"].empty_label = "Select owner"
        self.fields["address"].required = False
        self.fields["gstn"].required = False
        self.fields["phone_number"].required = False
        self.fields["status"].required = False


class BusinessUserForm(forms.ModelForm):
    ROLE_CHOICES = [
        ("SUPER_ADMIN", "Super Admin"),
        ("ADMIN", "Admin"),
        ("FARM_MANAGER", "Farm Manager"),
        ("SALES_PERSON", "Sales Person"),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    class Meta:
        model = BusinessUser
        fields = ["user","role","is_active"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["user"].queryset = User.objects.filter(is_active=True).order_by("username")
        self.fields["user"].empty_label = "Select user"
        self.fields["role"].choices = [("", "Select role")] + list(self.ROLE_CHOICES)
        self.fields["is_active"].required = False


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ["name","type","parent","latitude","longitude","status"]
        widgets = {
            "name":forms.TextInput(attrs={"class":"form-input","placeholder":"Enter location name"}),
            "type":forms.Select(attrs={"class":"form-input"}),
            "parent":forms.Select(attrs={"class":"form-input"}),
            "latitude":forms.NumberInput(attrs={"class":"form-input","step":"any","placeholder":"Enter latitude"}),
            "longitude":forms.NumberInput(attrs={"class":"form-input","step":"any","placeholder":"Enter longitude"}),
            "status":forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)

        self.fields["parent"].queryset = Location.objects.none()
        self.fields["parent"].empty_label = "No parent"
        self.fields["parent"].required = False
        self.fields["latitude"].required = False
        self.fields["longitude"].required = False
        self.fields["status"].required = False
        self.fields["type"].choices = [("", "Select type")] + list(Location.LOCATION_TYPES)
        if business:
            parents = Location.objects.filter(business=business, status=True)
            if self.instance and self.instance.pk:
                parents = parents.exclude(pk=self.instance.pk)
            self.fields["parent"].queryset = parents.order_by("name")
    def clean(self):
        cleaned_data = super().clean()
        location_type = cleaned_data.get("type")
        parent = cleaned_data.get("parent")
        if location_type == "state" and parent:
            raise forms.ValidationError("State cannot have a parent location.")
        if location_type == "district":
            if not parent:
                raise forms.ValidationError("District must belong to a State.")
            if parent.type != "state":
                raise forms.ValidationError("District parent must be a State.")
        if location_type == "area":
            if not parent:
                raise forms.ValidationError("Area must belong to a District.")
            if parent.type != "district":
                raise forms.ValidationError("Area parent must be a District.")
        if location_type == "other" and parent and parent.business_id != self.instance.business_id:
            raise forms.ValidationError("Invalid parent location.")

        return cleaned_data