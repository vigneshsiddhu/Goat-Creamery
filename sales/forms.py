

from django import forms
from business.models import Location
from inventory.models import Item,Vehicle
from .models import Customer,Invoice,InvoiceItem,InvoiceLocation


from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name","number","gender","age","address",]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input","placeholder": "Enter customer name",}),
            "number": forms.TextInput(attrs={"class": "form-input","placeholder": "Enter phone number",}),
            "gender": forms.Select(attrs={"class": "form-input",}),
            "age": forms.NumberInput(attrs={"class": "form-input","placeholder": "Enter age","min": "1",}),
            "address": forms.Textarea(attrs={"class": "form-input","placeholder": "Enter customer address","rows": 3,}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["gender"].required = False
        self.fields["age"].required = False
        self.fields["address"].required = False
        self.fields["gender"].choices = [("", "Select gender")] + list(Customer.GENDER_CHOICES)

    def clean_name(self):
        value = self.cleaned_data.get("name")
        if not value:
            raise forms.ValidationError("Customer name is required.")
        return value.strip()
    def clean_number(self):
        value = self.cleaned_data.get("number")
        if not value:
            raise forms.ValidationError("Customer number is required.")
        return value.strip()
    def clean_age(self):
        value = self.cleaned_data.get("age")
        if value is not None and value <= 0:
            raise forms.ValidationError("Age must be greater than 0.")
        return value


from django import forms
from django.forms import inlineformset_factory
from decimal import Decimal
from .models import Invoice, InvoiceItem, Customer, Item

class InvoiceForm(forms.ModelForm):
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-input billing-vehicle-select"}),
    )
    latitude = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=7,
        widget=forms.HiddenInput(attrs={"id": "invoice_latitude"}),
    )
    longitude = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=7,
        widget=forms.HiddenInput(attrs={"id": "invoice_longitude"}),
    )
    payment_status = forms.ChoiceField(
        choices=[("", "---------")] + Invoice.PAYMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class":"form-input billing-hidden-select","id":"id_payment_status"}),
    )
    payment_method = forms.ChoiceField(
        choices=[("", "---------")] + Invoice.PAYMENT_METHOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class":"form-input billing-hidden-select","id":"id_payment_method"}),
    )
    new_customer_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Customer name", "id": "id_new_customer_name"}),
    )
    new_customer_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Phone number", "id": "id_new_customer_number"}),
    )
    new_customer_gender = forms.ChoiceField(
        choices=[("", "Gender (optional)")] + list(Customer.GENDER_CHOICES),
        required=False,
        widget=forms.Select(attrs={"class": "form-input", "id": "id_new_customer_gender"}),
    )
    new_customer_age = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-input", "placeholder": "Age (optional)", "min": "1", "id": "id_new_customer_age"}),
    )
    new_customer_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-input", "placeholder": "Address (optional)", "rows": 2, "id": "id_new_customer_address"}),
    )
    class Meta:
        model = Invoice
        fields = ["customer","payment_status","payment_method","discount","notes",]
        widgets = {
            "customer": forms.Select(attrs={"class": "form-input billing-customer-select", }),
            "discount": forms.NumberInput(attrs={"class": "form-input", "placeholder": "0.00", "step": "0.01", "min": "0", }),
            "notes": forms.Textarea(attrs={"class": "form-input", "placeholder": "Optional note", "rows": 2, }),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business
        self.fields["customer"].queryset = Customer.objects.filter(business=business)
        self.fields["customer"].required = False
        self.fields["customer"].empty_label = "Walk-in customer (optional)"
        self.fields["notes"].required = False
        if business:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(business=business).order_by("number")
            self.fields["vehicle"].empty_label = "No vehicle (optional)"
        if self.instance and self.instance.pk:
            self.fields.pop("vehicle", None)
            self.fields.pop("latitude", None)
            self.fields.pop("longitude", None)
    def clean_discount(self):
        value = self.cleaned_data.get("discount") or 0
        if value < 0:
            raise forms.ValidationError("Discount cannot be negative.")
        return value

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get("customer")
        name = (cleaned_data.get("new_customer_name") or "").strip()
        number = (cleaned_data.get("new_customer_number") or "").strip()

        if customer and (name or number):
            raise forms.ValidationError(
                "Choose an existing customer or enter new customer details — not both."
            )
        if name or number:
            if not name:
                self.add_error("new_customer_name", "Customer name is required.")
            if not number:
                self.add_error("new_customer_number", "Phone number is required.")
        return cleaned_data

    def resolve_customer(self, business, user):
        customer = self.cleaned_data.get("customer")
        if customer:
            return customer
        name = (self.cleaned_data.get("new_customer_name") or "").strip()
        number = (self.cleaned_data.get("new_customer_number") or "").strip()
        if not name and not number:
            return None
        return Customer.objects.create(
            business=business,
            name=name,
            number=number,
            gender=self.cleaned_data.get("new_customer_gender") or None,
            age=self.cleaned_data.get("new_customer_age"),
            address=(self.cleaned_data.get("new_customer_address") or "").strip() or None,
            created_by=user,
        )

    def clean_vehicle(self):
        vehicle = self.cleaned_data.get("vehicle")
        business = getattr(self, "business", None)
        if vehicle and business and vehicle.business_id != business.id:
            raise forms.ValidationError("Invalid vehicle.")
        return vehicle

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["item","unit","quantity","price","discount","gst",]
        widgets = {
            "item": forms.Select(attrs={"class": "form-input invoice-item-select", }),
            "unit": forms.HiddenInput(attrs={"class": "invoice-item-unit", }),
            "quantity": forms.HiddenInput(attrs={"class": "invoice-item-quantity"}),
            "price": forms.HiddenInput(attrs={"class": "invoice-item-price", }),
            "discount": forms.HiddenInput(attrs={"class": "invoice-item-discount", }),
            "gst": forms.HiddenInput(attrs={"class": "invoice-item-gst", }),
        }
    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = business
        self.empty_permitted = True
        self.fields["item"].queryset = Item.objects.filter(
            business=business,
            status=True,
        ).select_related("product","product_batch","price")
        self.fields["item"].required = False
        self.fields["item"].empty_label = "Select product"
        self.fields["item"].label_from_instance = lambda obj: obj.billing_label
        self.fields["quantity"].required = False
        self.fields["quantity"].initial = Decimal("1")
        for field_name in ["unit","price","discount","gst"]:
            self.fields[field_name].required = False
    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get("item")
        if not item:
            return cleaned_data
        cleaned_data["quantity"] = Decimal("1")
        if self.business and item.business_id != self.business.id:
            self.add_error("item","Invalid item.")
            return cleaned_data
        from .utils import get_item_pricing
        pricing = get_item_pricing(item, cleaned_data["quantity"])
        cleaned_data["unit"] = pricing["unit"]
        cleaned_data["price"] = Decimal(pricing["price"])
        cleaned_data["discount"] = Decimal(pricing["discount"])
        cleaned_data["gst"] = Decimal(pricing["gst"])
        return cleaned_data


class BaseInvoiceItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        active_items = [
            form.cleaned_data
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get("DELETE")
            and form.cleaned_data.get("item")
        ]
        if self.instance.pk or self.data:
            if not active_items:
                raise forms.ValidationError("Add at least one product to complete the bill.")
        seen = set()
        for form in self.forms:
            data = form.cleaned_data
            if not data or data.get("DELETE"):
                continue
            item = data.get("item")
            if not item:
                continue
            if item.pk in seen:
                form.add_error("item", "This product is already on the bill. Add a different product.")
            seen.add(item.pk)


InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    formset=BaseInvoiceItemFormSet,
    extra=0,
    can_delete=True,
)


class InvoiceLocationForm(forms.ModelForm):

    class Meta:
        model = InvoiceLocation
        fields = ["vehicle","location"]
        widgets = {
            "vehicle": forms.Select(attrs={"class":"form-select"}),
            "location": forms.Select(attrs={"class":"form-select"}),
        }

    def __init__(self,*args,business=None,invoice=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.business = business
        self.invoice = invoice

        if business:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(
                business=business
            )
            self.fields["vehicle"].required = False
            self.fields["vehicle"].empty_label = "No vehicle (optional)"
            self.fields["location"].queryset = Location.objects.filter(
                business=business,
                status=True,
            )
            self.fields["location"].required = False
            self.fields["location"].empty_label = "No business location (optional)"

    def clean(self):
        cleaned_data = super().clean()

        vehicle = cleaned_data.get("vehicle")
        location = cleaned_data.get("location")

        if vehicle and self.business:
            if vehicle.business_id != self.business.id:
                raise forms.ValidationError("Invalid vehicle.")

        if location and self.business:
            if location.business_id != self.business.id:
                raise forms.ValidationError("Invalid location.")

        return cleaned_data