

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
from .models import Invoice, InvoiceItem, Customer, Item

class InvoiceForm(forms.ModelForm):
    PAYMENT_STATUS_CHOICES = [("pending", "Pending"),("paid", "Paid"),("partial", "Partially Paid"),("cancelled", "Cancelled"),]
    payment_status = forms.ChoiceField(choices=PAYMENT_STATUS_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    PAYMENT_METHOD_CHOICES = [ ("cash", "Cash"),("upi", "UPI"),("card", "Card"),("bank_transfer", "Bank Transfer"),("credit", "Credit"),]
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    class Meta:
        model = Invoice
        fields = ["number","date","time","customer","payment_status","payment_method","discount","gst","notes",]
        widgets = { 
            "number": forms.TextInput(attrs={"class": "form-input", "placeholder": "Invoice number", }),
            "date": forms.DateInput(attrs={ "class": "form-input", "type": "date", }), 
            "time": forms.TimeInput(attrs={ "class": "form-input", "type": "time", }), 
            "customer": forms.Select(attrs={ "class": "form-input", }),
            "discount": forms.NumberInput(attrs={ "class": "form-input", "placeholder": "0.00", "step": "0.01", "min": "0", }), 
            "gst": forms.NumberInput(attrs={ "class": "form-input", "placeholder": "0.00", "step": "0.01", "min": "0", }),
            "notes": forms.Textarea(attrs={ "class": "form-input", "placeholder": "Invoice notes", "rows": 3, }),
        }

    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.filter(
            business=business
        )
        self.fields["payment_status"].choices = [("pending", "Pending"),("paid", "Paid"),("partial", "Partially Paid"),("cancelled", "Cancelled"),]
        self.fields["payment_method"].choices = [("cash", "Cash"),("upi", "UPI"),("card", "Card"),("bank_transfer", "Bank Transfer"),("credit", "Credit"),]
    def clean_discount(self):
        value = self.cleaned_data.get("discount") or 0
        if value < 0:
            raise forms.ValidationError("Discount cannot be negative.")
        return value
    def clean_gst(self):
        value = self.cleaned_data.get("gst") or 0
        if value < 0:
            raise forms.ValidationError("GST cannot be negative.")
        return value

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["item","unit","quantity","price","discount","gst",]
        widgets = {
            "item": forms.Select(attrs={"class": "form-input invoice-item-product", }),
            "unit": forms.TextInput(attrs={"class": "form-input invoice-item-unit","placeholder": "Unit", }),
            "quantity": forms.NumberInput(attrs={"class": "form-input invoice-item-quantity","placeholder": "Quantity","step": "0.001","min": "0.001", }),
            "price": forms.NumberInput(attrs={"class": "form-input invoice-item-price","placeholder": "Price","step": "0.01","min": "0", }),
            "discount": forms.NumberInput(attrs={"class": "form-input invoice-item-discount","placeholder": "0.00","step": "0.01","min": "0", }),
            "gst": forms.NumberInput(attrs={"class": "form-input invoice-item-gst","placeholder": "0.00","step": "0.01","min": "0", }),
        }
    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = Item.objects.filter(business=business,status=True).select_related("product","product_batch","price")
    def clean_quantity(self):
        value = self.cleaned_data.get("quantity")
        if value is None or value <= 0:
            raise forms.ValidationError("Quantity must be greater than 0.")
        return value
    def clean_price(self):
        value = self.cleaned_data.get("price")
        if value is None or value < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return value
    def clean_discount(self):
        value = self.cleaned_data.get("discount") or 0
        if value < 0:
            raise forms.ValidationError("Discount cannot be negative.")
        return value
    def clean_gst(self):
        value = self.cleaned_data.get("gst") or 0
        if value < 0:
            raise forms.ValidationError("GST cannot be negative.")
        return value

InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
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

            self.fields["location"].queryset = Location.objects.filter(
                business=business,
                status=True
            )

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