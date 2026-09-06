from django import forms
from farm.models import Land,Water,LandWater,FeedConsumption,FeedStock,FeedStockTransaction
from business.models import Location


class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = ["name","unit","area","soil_type","location"]
        widgets = {
            "name": forms.TextInput(attrs={"class":"form-control","placeholder":"Enter land name"}),
            "unit": forms.TextInput(attrs={"class":"form-control","placeholder":"acre / cent / hectare"}),
            "area": forms.NumberInput(attrs={"class":"form-control","step":"0.01","placeholder":"Enter area"}),
            "soil_type": forms.TextInput(attrs={"class":"form-control","placeholder":"Enter soil type"}),
            "location": forms.Select(attrs={"class":"form-select"}),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business:
            self.fields["location"].queryset = Location.objects.filter(business=business,status=True).order_by("name")
        else:
            self.fields["location"].queryset = Location.objects.none()

class WaterForm(forms.ModelForm):
    class Meta:
        model = Water
        fields = ["source","name"]
        widgets = {
            "source": forms.Select(attrs={"class":"form-select"}),
            "name": forms.TextInput(attrs={"class":"form-control","placeholder":"Enter water source name"}),
        }
        
class LandWaterForm(forms.ModelForm):
    class Meta:
        model = LandWater
        fields = ["land","water","date","status","comment"]
        widgets = {
            "land": forms.Select(attrs={"class":"form-select"}),
            "water": forms.Select(attrs={"class":"form-select"}),
            "date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "status": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "comment": forms.Textarea(attrs={"class":"form-control","rows":3,"placeholder":"Enter comment"}),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business:
            self.fields["land"].queryset = Land.objects.filter(business=business).order_by("name")
            self.fields["water"].queryset = Water.objects.filter(business=business).order_by("name")
        else:
            self.fields["land"].queryset = Land.objects.none()
            self.fields["water"].queryset = Water.objects.none()
        
class FeedStockForm(forms.ModelForm):
    class Meta:
        model = FeedStock
        fields = ["date","fodder_variety","stock_weight","rate"]
        widgets = {
            "date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "fodder_variety": forms.TextInput(attrs={"class":"form-control","placeholder":"Enter fodder variety"}),
            "stock_weight": forms.NumberInput(attrs={"class":"form-control","step":"0.001","placeholder":"Enter stock weight in kg"}),
            "rate": forms.NumberInput(attrs={"class":"form-control","step":"0.01","placeholder":"Enter rate per kg"}),
        }
    def clean(self):
        cleaned_data = super().clean()
        stock_weight = cleaned_data.get("stock_weight")
        rate = cleaned_data.get("rate")

        if stock_weight is not None and stock_weight <= 0:
            self.add_error("stock_weight","Stock weight must be greater than zero.")

        if rate is not None and rate < 0:
            self.add_error("rate","Rate cannot be negative.")
        return cleaned_data


class FeedStockTransactionForm(forms.ModelForm):
    class Meta:
        model = FeedStockTransaction
        fields = ["feed_stock","date","transaction_type","quantity_kg","note"]
        widgets = {
            "feed_stock": forms.Select(attrs={"class":"form-select"}),
            "date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "transaction_type": forms.TextInput(attrs={"class":"form-control","placeholder":"Purchase / Consumption / Adjustment"}),
            "quantity_kg": forms.NumberInput(attrs={"class":"form-control","step":"0.001","placeholder":"Enter quantity in kg"}),
            "note": forms.Textarea(attrs={"class":"form-control","rows":3,"placeholder":"Enter note"}),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
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
        fields = ["date","feed_time","concentrate","dry_fodder","silage","wastage"]
        widgets = {
            "date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "feed_time": forms.Select(attrs={"class":"form-select"}),
            "concentrate": forms.NumberInput(attrs={"class":"form-control","step":"0.01","placeholder":"Kg"}),
            "dry_fodder": forms.NumberInput(attrs={"class":"form-control","step":"0.01","placeholder":"Kg"}),
            "silage": forms.NumberInput(attrs={"class":"form-control","step":"0.01","placeholder":"Kg"}),
            "wastage": forms.NumberInput(attrs={"class":"form-control","step":"0.01","placeholder":"Kg"}),
        }
    def clean(self):
        cleaned_data = super().clean()

        for field in ["concentrate","dry_fodder","silage","wastage"]:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                self.add_error(field,"Value cannot be negative.")

        return cleaned_data