import uuid

from django.conf import settings
from django.db import models

from business.models import Business
from inventory.models import Item, Vehicle
from farm.models import Location


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
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    number = models.CharField(max_length=50,)
    date = models.DateField()
    time = models.TimeField(null=True,blank=True,)
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT,related_name="invoices",)
    payment_status = models.CharField(max_length=100,)
    payment_method = models.CharField(max_length=100)
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
    location = models.ForeignKey(Location,on_delete=models.PROTECT,related_name="invoice_locations",)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="invoice_locations",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_invoice_locations",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    def __str__(self):
        return f"{self.invoice.number} - {self.location}"

