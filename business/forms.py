from django import forms
from django.contrib.auth import get_user_model
from .models import Business,BusinessUser,Location

User = get_user_model()


class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ["name","address","gstn","phone_number","owner","status"]
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["owner"].queryset = User.objects.filter(is_active=True).order_by("username")
        self.fields["owner"].widget.attrs.update({"class":"form-select"})
        self.fields["name"].widget.attrs.update({"class":"form-control","placeholder":"Enter business name"})
        self.fields["address"].widget.attrs.update({"class":"form-control","rows":3,"placeholder":"Enter business address"})
        self.fields["gstn"].widget.attrs.update({"class":"form-control","placeholder":"Enter GSTIN"})
        self.fields["phone_number"].widget.attrs.update({"class":"form-control","placeholder":"Enter phone number"})
        self.fields["status"].widget.attrs.update({"class":"form-select"})


class BusinessUserForm(forms.ModelForm):
    class Meta:
        model = BusinessUser
        fields = ["user","business","role","is_active"]
        widgets = {
            "user":forms.Select(attrs={"class":"form-select"}),
            "business":forms.Select(attrs={"class":"form-select"}),
            "role":forms.Select(attrs={"class":"form-select"}),
            "is_active":forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["user"].queryset = User.objects.filter(is_active=True).order_by("username")

        if business:
            self.fields["business"].queryset = Business.objects.filter(pk=business.pk)
            self.fields["business"].initial = business
            self.fields["business"].disabled = True
        else:
            self.fields["business"].queryset = Business.objects.all().order_by("name")

        self.fields["role"].choices = [
            ("","Select Business Role"),
            ("ADMIN","Admin"),
            ("FARM_MANAGER","Farm Manager"),
            ("SALES_PERSON","Sales Person"),
        ]


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

        if business:
            self.fields["parent"].queryset = Location.objects.filter(business=business,status=True).exclude(pk=self.instance.pk)

        self.fields["parent"].required = False
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