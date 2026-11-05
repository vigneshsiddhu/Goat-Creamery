from django import forms
from farm.models import Land,Water,LandWater,FeedConsumption,FeedStock,FeedStockTransaction
from business.models import Location


class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = ["name","location","area","unit","soil_type"]
        widgets = {
            "name": forms.TextInput(attrs={"class":"form-input","placeholder":"e.g. North paddock"}),
            "location": forms.Select(attrs={"class":"form-input"}),
            "area": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"0.00"}),
            "unit": forms.Select(attrs={"class":"form-input"}),
            "soil_type": forms.Select(attrs={"class":"form-input"}),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["name"].label = "Land name"
        self.fields["unit"].choices = [("", "Select unit")] + list(Land.UNIT_CHOICES)
        self.fields["soil_type"].choices = [("", "Select soil / sand type")] + list(Land.SOIL_TYPE_CHOICES)
        self.fields["soil_type"].required = False
        self.fields["location"].required = False
        self.fields["location"].empty_label = "Select location"
        if business:
            self.fields["location"].queryset = Location.objects.filter(business=business,status=True).order_by("name")
        else:
            self.fields["location"].queryset = Location.objects.none()

class WaterForm(forms.ModelForm):
    class Meta:
        model = Water
        fields = ["name", "source"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. Front borewell"}),
            "source": forms.Select(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["source"].choices = [("", "Select source type")] + list(Water.SOURCE_CHOICES)


class LandWaterForm(forms.ModelForm):
    class Meta:
        model = LandWater
        fields = ["land", "water", "date", "status", "comment"]
        widgets = {
            "land": forms.Select(attrs={"class": "form-input"}),
            "water": forms.Select(attrs={"class": "form-input"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comment": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Optional note"}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["land"].empty_label = "Select land"
        self.fields["water"].empty_label = "Select water source"
        self.fields["status"].required = False
        self.fields["comment"].required = False
        if business:
            self.fields["land"].queryset = Land.objects.filter(business=business).order_by("name")
            self.fields["water"].queryset = Water.objects.filter(business=business).order_by("name")
        else:
            self.fields["land"].queryset = Land.objects.none()
            self.fields["water"].queryset = Water.objects.none()
        
class FeedStockForm(forms.ModelForm):
    class Meta:
        model = FeedStock
        fields = ["date", "fodder_variety", "stock_weight", "rate"]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "fodder_variety": forms.Select(attrs={"class": "form-input"}),
            "stock_weight": forms.NumberInput(attrs={"class": "form-input", "step": "0.001", "min": "0", "placeholder": "0.000"}),
            "rate": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fodder_variety"].choices = [("", "Select feed variety")] + list(FeedStock.FODDER_VARIETY_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        stock_weight = cleaned_data.get("stock_weight")
        rate = cleaned_data.get("rate")
        if stock_weight is not None and stock_weight <= 0:
            self.add_error("stock_weight", "Stock weight must be greater than zero.")
        if rate is not None and rate < 0:
            self.add_error("rate", "Rate cannot be negative.")
        return cleaned_data


class FeedStockTransactionForm(forms.ModelForm):
    class Meta:
        model = FeedStockTransaction
        fields = ["feed_stock", "date", "transaction_type", "quantity_kg", "note"]
        widgets = {
            "feed_stock": forms.Select(attrs={"class": "form-input"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "transaction_type": forms.Select(attrs={"class": "form-input"}),
            "quantity_kg": forms.NumberInput(attrs={"class": "form-input", "step": "0.001", "min": "0", "placeholder": "0.000"}),
            "note": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Optional note"}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["feed_stock"].empty_label = "Select feed stock"
        self.fields["transaction_type"].choices = [("", "Select type")] + list(FeedStockTransaction.TRANSACTION_TYPE_CHOICES)
        self.fields["note"].required = False
        if business:
            self.fields["feed_stock"].queryset = FeedStock.objects.filter(business=business).order_by("-date")
        else:
            self.fields["feed_stock"].queryset = FeedStock.objects.none()

    def clean_quantity_kg(self):
        quantity = self.cleaned_data.get("quantity_kg")
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity


class FeedConsumptionForm(forms.ModelForm):
    class Meta:
        model = FeedConsumption
        fields = ["date", "feed_time", "concentrate", "dry_fodder", "silage", "wastage"]
        widgets = {
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "feed_time": forms.Select(attrs={"class": "form-input"}),
            "concentrate": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}),
            "dry_fodder": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}),
            "silage": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}),
            "wastage": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["feed_time"].choices = [("", "Select feed time")] + list(FeedConsumption.FEED_TIME_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        for field in ["concentrate", "dry_fodder", "silage", "wastage"]:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                self.add_error(field, "Value cannot be negative.")
        return cleaned_data