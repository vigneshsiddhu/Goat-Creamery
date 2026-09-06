from django import forms
from business.models import Location
from production.models import Product,ProductBatch,ProductPrice
from .models import Item,Vehicle,VehicleLocation,ItemLocation


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["qr_code","product","product_batch","price","description","status","time","packed_date","exp_date",]
        widgets = {
            "qr_code": forms.TextInput(attrs={"class":"form-input","placeholder":"Enter or scan QR code",}),
            "product": forms.Select(attrs={"class":"form-input",}),
            "product_batch": forms.Select(attrs={"class":"form-input",}),
            "price": forms.Select(attrs={"class":"form-input",}),
            "description": forms.Textarea(attrs={"class":"form-input","placeholder":"Enter item description","rows":4,}),
            "status": forms.CheckboxInput(attrs={"class":"form-check-input",}),
            "time": forms.TimeInput(attrs={"class":"form-input","type":"time",}),
            "packed_date": forms.DateInput(attrs={"class":"form-input","type":"date",}),
            "exp_date": forms.DateInput(attrs={"class":"form-input","type":"date",}),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["product"].queryset = Product.objects.filter( business=business  ).order_by( "type", "code_sku")
        self.fields["product_batch"].queryset = ProductBatch.objects.filter( business=business  ).select_related( "product"  ).order_by( "-date", "-created_at"  )
        self.fields["price"].queryset = ProductPrice.objects.filter(business=business, status="active"  ).select_related( "product"  ).order_by( "product__type", "product__code_sku", "-date"  )
        self.fields["qr_code"].required = False
        self.fields["product"].required = True
        self.fields["product_batch"].required = True
        self.fields["price"].required = True
        self.fields["description"].required = False
        self.fields["status"].required = True
        self.fields["time"].required = False
        self.fields["packed_date"].required = True
        self.fields["exp_date"].required = True
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        product_batch = cleaned_data.get("product_batch")
        price = cleaned_data.get("price")
        packed_date = cleaned_data.get("packed_date")
        exp_date = cleaned_data.get("exp_date")
        if product and product_batch and product_batch.product_id != product.id:
            self.add_error("product_batch","Selected product batch does not belong to the selected product.")
        if product and price and price.product_id != product.id:
            self.add_error("price",            "Selected item price does not belong to the selected product.")
        if packed_date and exp_date and exp_date < packed_date:
            self.add_error("exp_date","Expiry date cannot be before packed date.")
        return cleaned_data


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["number","name","vehicle_type","unit","capacity","status"]
        widgets = {
            "number": forms.TextInput(attrs={"class":"form-control"}),
            "name": forms.TextInput(attrs={"class":"form-control"}),
            "vehicle_type": forms.TextInput(attrs={"class":"form-control"}),
            "unit": forms.TextInput(attrs={"class":"form-control"}),
            "capacity": forms.NumberInput(attrs={"class":"form-control","step":"0.01","min":"0"}),
            "status": forms.Select(attrs={"class":"form-select"}),
        }
    def clean_number(self):
        number = self.cleaned_data["number"].strip()
        if not number:
            raise forms.ValidationError("Vehicle number is required.")
        return number


class VehicleLocationForm(forms.ModelForm):
    class Meta:
        model = VehicleLocation
        fields = ["vehicle","location","date","time","status","comment"]
        widgets = {
            "vehicle": forms.Select(attrs={"class":"form-select"}),
            "location": forms.Select(attrs={"class":"form-select"}),
            "date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "time": forms.TimeInput(attrs={"class":"form-control","type":"time"}),
            "status": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "comment": forms.Textarea(attrs={"class":"form-control","rows":3}),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.business = business

        if business:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(business=business)
            self.fields["location"].queryset = Location.objects.filter(business=business,status=True)
    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get("vehicle")
        location = cleaned_data.get("location")
        if vehicle and self.business and vehicle.business_id != self.business.id:
            raise forms.ValidationError("Invalid vehicle.")
        if location and self.business and location.business_id != self.business.id:
            raise forms.ValidationError("Invalid location.")
        return cleaned_data


class ItemLocationForm(forms.ModelForm):
    class Meta:
        model = ItemLocation
        fields = [
            "vehicle",
            "location",
            "item",
            "loaded_at",
            "unloaded_at",
            "time",
            "status",
        ]
        widgets = {
            "vehicle": forms.Select(attrs={"class":"form-select"}),
            "location": forms.Select(attrs={"class":"form-select"}),
            "item": forms.Select(attrs={"class":"form-select"}),
            "loaded_at": forms.DateTimeInput(attrs={"class":"form-control","type":"datetime-local"}),
            "unloaded_at": forms.DateTimeInput(attrs={"class":"form-control","type":"datetime-local"}),
            "time": forms.TimeInput(attrs={"class":"form-control","type":"time"}),
            "status": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.business = business
        if business:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(business=business)
            self.fields["location"].queryset = Location.objects.filter(business=business,status=True)
            self.fields["item"].queryset = Item.objects.filter(business=business).select_related("product","product_batch")
    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get("vehicle")
        location = cleaned_data.get("location")
        item = cleaned_data.get("item")
        loaded_at = cleaned_data.get("loaded_at")
        unloaded_at = cleaned_data.get("unloaded_at")
        if not vehicle and not location:
            raise forms.ValidationError("Vehicle or location is required.")
        if vehicle and self.business and vehicle.business_id != self.business.id:
            raise forms.ValidationError("Invalid vehicle.")
        if location and self.business and location.business_id != self.business.id:
            raise forms.ValidationError("Invalid location.")
        if item and self.business and item.business_id != self.business.id:
            raise forms.ValidationError("Invalid item.")
        if loaded_at and unloaded_at and unloaded_at < loaded_at:
            raise forms.ValidationError("Unloaded time cannot be before loaded time.")
        return cleaned_data