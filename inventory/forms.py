from django import forms
from business.models import Location
from production.models import Product,ProductBatch,ProductPrice
from .models import Item,Vehicle,VehicleLocation,ItemLocation


class ItemForm(forms.ModelForm):
    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        empty_label="Select city",
        label="City",
        widget=forms.Select(attrs={"class": "form-input", "id": "id_location"}),
    )
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(),
        empty_label="Select vehicle",
        label="Vehicle",
        widget=forms.Select(attrs={"class": "form-input", "id": "id_vehicle"}),
    )

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
        from django.utils import timezone
        from .utils import city_locations_for_business, active_vehicles_for_business

        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.business = business

        product_id = None
        if self.data.get("product"):
            product_id = self.data.get("product")
        elif self.instance.pk and self.instance.product_id:
            product_id = str(self.instance.product_id)

        self.fields["product"].queryset = Product.objects.filter(
            business=business,
            status="active",
        ).order_by("type", "variant", "code_sku")
        self.fields["product"].empty_label = "Select product"
        self.fields["product"].label_from_instance = lambda obj: (
            f"{obj.type.title()}{' · ' + obj.variant.title() if obj.variant else ''} ({obj.code_sku})"
        )

        batch_qs = ProductBatch.objects.filter(business=business).select_related("product").order_by("-date", "-created_at")
        price_qs = ProductPrice.objects.filter(business=business, status="active").select_related("product").order_by("-date")
        if product_id:
            batch_qs = batch_qs.filter(product_id=product_id)
            price_qs = price_qs.filter(product_id=product_id)
            self.fields["product_batch"].empty_label = "Select batch"
            self.fields["price"].empty_label = "Select price"
        else:
            batch_qs = batch_qs.none()
            price_qs = price_qs.none()
            self.fields["product_batch"].empty_label = "Select product first"
            self.fields["price"].empty_label = "Select product first"
        self.fields["product_batch"].queryset = batch_qs
        self.fields["price"].queryset = price_qs
        self.fields["product_batch"].label_from_instance = lambda obj: (
            f"{obj.batch_number} · {obj.date.strftime('%d %b %Y')}"
        )
        self.fields["price"].label_from_instance = lambda obj: (
            f"₹{obj.mrp} · {obj.quantity} {obj.unit}"
        )

        self.fields["qr_code"].required = False
        self.fields["product"].required = True
        self.fields["product_batch"].required = True
        self.fields["price"].required = True
        self.fields["description"].required = False
        self.fields["time"].required = False
        self.fields["packed_date"].required = True
        self.fields["exp_date"].required = True
        if business:
            self.fields["location"].queryset = city_locations_for_business(business)
            self.fields["vehicle"].queryset = active_vehicles_for_business(business)
        self.fields["location"].required = False
        self.fields["vehicle"].required = False
        self.fields["location"].empty_label = "Select city (optional)"
        self.fields["vehicle"].empty_label = "Select vehicle (optional)"
        if self.instance.pk and not self.is_bound:
            active = (
                ItemLocation.objects.filter(item=self.instance, status=True)
                .select_related("location", "vehicle")
                .first()
            )
            if active:
                self.fields["location"].initial = active.location_id
                self.fields["vehicle"].initial = active.vehicle_id
        if not getattr(self.instance, "pk", None):
            self.fields.pop("status", None)
            if not self.is_bound:
                self.fields["packed_date"].initial = timezone.localdate()
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
        location = cleaned_data.get("location")
        vehicle = cleaned_data.get("vehicle")
        if location and self.business and location.business_id != self.business.id:
            self.add_error("location", "Invalid city.")
        if vehicle and self.business and vehicle.business_id != self.business.id:
            self.add_error("vehicle", "Invalid vehicle.")
        if vehicle and vehicle.status != "active":
            self.add_error("vehicle", "Selected vehicle is not active.")
        return cleaned_data


class VehicleForm(forms.ModelForm):
    UNIT_CHOICES = [
        ("kg", "Kg"),
        ("gram", "Gram"),
        ("litre", "Litre"),
        ("ml", "Ml"),
        ("piece", "Piece"),
        ("box", "Box"),
    ]
    VEHICLE_TYPE_CHOICES = [
        ("", "Select type"),
        ("van", "Van"),
        ("truck", "Truck"),
        ("bike", "Bike / Scooter"),
        ("auto", "Auto"),
        ("car", "Car"),
        ("other", "Other"),
    ]
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    vehicle_type = forms.ChoiceField(
        choices=VEHICLE_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    status = forms.ChoiceField(
        choices=Vehicle.STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    class Meta:
        model = Vehicle
        fields = ["number", "name", "vehicle_type", "unit", "capacity", "status"]
        widgets = {
            "number": forms.TextInput(attrs={"class": "form-input", "placeholder": "e.g. TN 09 AB 1234"}),
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Optional display name"}),
            "capacity": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "Max load"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = False
        self.fields["capacity"].required = False
        if not getattr(self.instance, "pk", None):
            self.fields.pop("status", None)
            if not self.is_bound:
                self.fields["unit"].initial = "kg"
        if self.instance.pk and self.instance.vehicle_type:
            current_type = self.instance.vehicle_type
            type_values = {choice[0] for choice in self.VEHICLE_TYPE_CHOICES}
            if current_type not in type_values:
                self.fields["vehicle_type"].choices = self.VEHICLE_TYPE_CHOICES + [(current_type, current_type.title())]

    def clean_number(self):
        number = self.cleaned_data["number"].strip()
        if not number:
            raise forms.ValidationError("Vehicle number is required.")
        return number

    def clean_capacity(self):
        capacity = self.cleaned_data.get("capacity")
        if capacity is not None and capacity < 0:
            raise forms.ValidationError("Capacity cannot be negative.")
        return capacity


class VehicleLocationForm(forms.ModelForm):
    class Meta:
        model = VehicleLocation
        fields = ["vehicle","location","date","time","status","comment"]
        widgets = {
            "vehicle": forms.Select(attrs={"class": "form-input"}),
            "location": forms.Select(attrs={"class": "form-input"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "form-input", "type": "time"}),
            "status": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comment": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Optional note"}),
        }
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.business = business
        self.fields["vehicle"].queryset = Vehicle.objects.none()
        self.fields["location"].queryset = Location.objects.none()
        self.fields["vehicle"].empty_label = "Select vehicle"
        self.fields["location"].empty_label = "Select location"
        self.fields["time"].required = False
        self.fields["comment"].required = False
        self.fields["status"].required = False
        if business:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(business=business).order_by("number")
            self.fields["location"].queryset = Location.objects.filter(business=business, status=True).order_by("name")
    def clean(self):
        cleaned_data = super().clean()
        vehicle = cleaned_data.get("vehicle")
        location = cleaned_data.get("location")
        if vehicle and self.business and vehicle.business_id != self.business.id:
            raise forms.ValidationError("Invalid vehicle.")
        if location and self.business and location.business_id != self.business.id:
            raise forms.ValidationError("Invalid location.")
        return cleaned_data


class ItemLocationCreateForm(forms.ModelForm):
    class Meta:
        model = ItemLocation
        fields = ["item", "location", "vehicle"]
        widgets = {
            "item": forms.Select(attrs={"class": "form-input", "id": "id_item"}),
            "location": forms.Select(attrs={"class": "form-input", "id": "id_location"}),
            "vehicle": forms.Select(attrs={"class": "form-input", "id": "id_vehicle"}),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business
        if business:
            from .utils import city_locations_for_business, active_vehicles_for_business, items_for_location

            self.fields["item"].queryset = items_for_location(business)
            self.fields["item"].empty_label = "Select item"
            self.fields["item"].label_from_instance = lambda obj: obj.billing_label
            self.fields["location"].queryset = city_locations_for_business(business)
            self.fields["location"].empty_label = "Select city (optional)"
            self.fields["location"].label = "City"
            self.fields["vehicle"].queryset = active_vehicles_for_business(business)
            self.fields["vehicle"].empty_label = "Select vehicle (optional)"
        self.fields["location"].required = False
        self.fields["vehicle"].required = False

    def clean_item(self):
        item = self.cleaned_data.get("item")
        if not item:
            raise forms.ValidationError("Item is required.")
        if item and self.business and item.business_id != self.business.id:
            raise forms.ValidationError("Invalid item.")
        return item

    def clean_location(self):
        location = self.cleaned_data.get("location")
        if location and self.business and location.business_id != self.business.id:
            raise forms.ValidationError("Invalid city.")
        return location

    def clean_vehicle(self):
        vehicle = self.cleaned_data.get("vehicle")
        if vehicle and self.business and vehicle.business_id != self.business.id:
            raise forms.ValidationError("Invalid vehicle.")
        if vehicle and vehicle.status != "active":
            raise forms.ValidationError("Selected vehicle is not active.")
        return vehicle

