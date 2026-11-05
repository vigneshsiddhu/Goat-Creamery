import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from business.models import Business, Location
from inventory.models import Item, Vehicle


# ============================================================
# CUSTOMER
# ============================================================
class Customer(models.Model):
    GENDER_CHOICES = [ ("male", "Male"), ("female", "Female"), ("other", "Other"), ("prefer_not_to_say", "Prefer not to say"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=150)
    number = models.CharField(max_length=20)
    gender = models.CharField(max_length=30,choices=GENDER_CHOICES,null=True,blank=True)
    age = models.PositiveIntegerField(null=True,blank=True)
    address = models.TextField(blank=True,null=True)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="customers")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_customers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return f"{self.name} - {self.number}"
    
# ============================================================
# INVOICE
# ============================================================
class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [("pending", "Pending"),("paid", "Paid"),("partial", "Partially Paid"),("cancelled", "Cancelled"),]
    PAYMENT_METHOD_CHOICES = [("cash", "Cash"),("upi", "UPI"),("card", "Card"),("bank_transfer", "Bank Transfer"),("credit", "Credit"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    number = models.CharField(max_length=50,blank=True,)
    date = models.DateField()
    time = models.TimeField(null=True,blank=True,)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT,related_name="invoices",null=True,blank=True,help_text="Optional. Leave empty for walk-in sales.",)
    payment_status = models.CharField(max_length=100,choices=PAYMENT_STATUS_CHOICES,blank=True,default="",)
    payment_method = models.CharField(max_length=100,choices=PAYMENT_METHOD_CHOICES,blank=True,default="",)
    sub_total = models.DecimalField(max_digits=14,decimal_places=2,default=0,)
    discount = models.DecimalField(max_digits=14,decimal_places=2,default=0,)
    gst = models.DecimalField(max_digits=14,decimal_places=2,default=0,)
    grand_total = models.DecimalField(max_digits=14,decimal_places=2,default=0,)
    notes = models.TextField(blank=True,null=True,)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="invoices",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_invoices",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        ordering = ["-date", "-created_at"]
        constraints = [models.UniqueConstraint(fields=["business", "number"],name="unique_invoice_number_per_business",)]
    def __str__(self):
        return self.number

    @classmethod
    def generate_number(cls, business):
        last_number = (
            cls.objects.select_for_update()
            .filter(business=business, number__startswith="INV-")
            .order_by("-number")
            .values_list("number", flat=True)
            .first()
        )
        sequence = 1
        if last_number:
            try:
                sequence = int(last_number.rsplit("-", 1)[-1]) + 1
            except ValueError:
                sequence = cls.objects.filter(business=business).count() + 1
        return f"INV-{sequence:05d}"

    def assign_now(self):
        now = timezone.localtime()
        self.date = now.date()
        self.time = now.time().replace(microsecond=0)
    
# ============================================================
# INVOICE ITEM
# ============================================================
class InvoiceItem(models.Model):
    STATUS_CHOICES = [("active", "Active"),("cancelled", "Cancelled"),("returned", "Returned"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE,related_name="items",)
    item = models.ForeignKey(Item,on_delete=models.PROTECT,related_name="invoice_items",)
    unit = models.CharField( max_length=20)
    quantity = models.DecimalField(max_digits=12,decimal_places=3,)
    price = models.DecimalField(max_digits=12,decimal_places=2,)
    discount = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    gst = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    total = models.DecimalField(max_digits=14,decimal_places=2,default=0,)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="active",)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="invoice_items",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_invoice_items",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    def __str__(self):
        return f"{self.invoice.number} - {self.item}"
    
# ============================================================
# INVOICE LOCATION
# ============================================================
class InvoiceLocation(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE,related_name="locations",)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.PROTECT,related_name="invoice_vehicles",null=True,blank=True,)
    location = models.ForeignKey(Location,on_delete=models.PROTECT,related_name="invoice_locations",null=True,blank=True,)
    latitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True,)
    longitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True,)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="invoice_locations",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_invoice_locations",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    def __str__(self):
        if self.location_id:
            return f"{self.invoice.number} - {self.location}"
        if self.latitude is not None and self.longitude is not None:
            return f"{self.invoice.number} - {self.latitude}, {self.longitude}"
        if self.vehicle_id:
            return f"{self.invoice.number} - {self.vehicle}"
        return f"{self.invoice.number} - location"

