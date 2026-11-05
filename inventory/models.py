import uuid
from django.conf import settings
from django.db import models
from business.models import Business,Location
from production.models import Product,ProductBatch ,ProductPrice


class Item(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    qr_code = models.CharField(max_length=255,unique=True,null=True,blank=True)
    # name = models.CharField(max_length=150)
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="items")
    product_batch = models.ForeignKey(ProductBatch,on_delete=models.PROTECT,related_name="items")
    price = models.ForeignKey(ProductPrice,on_delete=models.PROTECT,related_name="items")
    description = models.TextField(blank=True,null=True)
    status = models.BooleanField(default=True)
    time = models.TimeField(null=True,blank=True,)
    packed_date = models.DateField()
    exp_date = models.DateField()
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="items")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return self.billing_label

    @property
    def billing_label(self):
        flavour = self.product.flavour_display
        type_label = (self.product.type or "").replace("_", " ").title()
        qr = self.qr_code or ""
        parts = []
        if flavour:
            parts.append(flavour)
        if type_label:
            parts.append(type_label)
        if qr:
            parts.append(qr)
        return " · ".join(parts) or self.product.code_sku

    @property
    def shelf_days_remaining(self):
        from django.utils import timezone

        return (self.exp_date - timezone.localdate()).days

class Vehicle(models.Model):
    STATUS_CHOICES = [("active", "Active"),("inactive", "Inactive"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    number = models.CharField(max_length=30)
    name = models.CharField(max_length=100,blank=True,null=True)
    vehicle_type = models.CharField(max_length=100)
    unit = models.CharField(max_length=20,default="kg")
    capacity = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="active")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="vehicles")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_vehicles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["number"]
        constraints = [models.UniqueConstraint(fields=["business", "number"],name="unique_vehicle_number_per_business")]
    def __str__(self):
        return self.number


class VehicleLocation(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name="locations")
    location = models.ForeignKey(Location,on_delete=models.PROTECT,related_name="vehicles")
    date = models.DateField()
    time = models.TimeField(null=True,blank=True,)
    status = models.BooleanField(default=True)
    comment = models.TextField(blank=True,null=True)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="vehicle_locations")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_vehicle_locations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date"]
    def __str__(self):
        return f"{self.vehicle.number} - {self.location}"

class ItemLocation(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.PROTECT,related_name="vehicle_items",null=True,blank=True)
    location = models.ForeignKey(Location,on_delete=models.PROTECT,related_name="item_locations",null=True,blank=True)
    item = models.ForeignKey(Item,on_delete=models.PROTECT,related_name="vehicle_assignments")
    loaded_at = models.DateTimeField(null=True,blank=True)
    unloaded_at = models.DateTimeField(null=True,blank=True)
    time = models.TimeField(null=True,blank=True,)
    status = models.BooleanField(default=True)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="vehicle_items")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_vehicle_items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.vehicle} - {self.item}"
   