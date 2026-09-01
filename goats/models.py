import uuid

from django.conf import settings
from django.db import models

from business.models import Business


# =========================================================
# GOAT
# =========================================================
class Goat(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    token_no = models.CharField(max_length=50,unique=True)
    rfid = models.CharField(max_length=100,unique=True,null=True,blank=True)
    breed_variety = models.CharField(max_length=100)
    dob = models.DateField(null=True,blank=True)
    age = models.PositiveIntegerField(null=True,blank=True)
    live = models.BooleanField(default=True)
    gender = models.CharField(max_length=20)
    maturity = models.CharField(max_length=20)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_goats")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="goats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:ordering = ["-created_at"]
    def __str__(self):
        return self.token_no


# =========================================================
# DISEASE
# =========================================================
class Disease(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=150)
    symptoms = models.TextField(blank=True)
    impact_goat = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_diseases")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="diseases")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name


# =========================================================
# GOAT DISEASE RECORD
# =========================================================
class DiseaseGoat(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    goat = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="disease_records")
    disease = models.ForeignKey(Disease,on_delete=models.PROTECT,related_name="goat_records",null=True,blank=True)
    disease_date = models.DateField()
    comment = models.TextField(blank=True)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_disease_goat_records")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="disease_goats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-disease_date"]


# =========================================================
# DEATH GOAT
# =========================================================
class DeathGoat(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    goat = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="death_records")
    disease = models.ForeignKey(Disease,on_delete=models.PROTECT,related_name="death_goat_records",null=True,blank=True)
    died_date = models.DateField()
    comment = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_death_goats")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="death_goats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-died_date"]
    


# =========================================================
# RACK
# =========================================================
class Rack(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_racks")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="racks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:ordering = ["name"]
    def __str__(self):
        return self.name


# =========================================================
# RACK GOAT ALLOCATION
# =========================================================
class RackGoat(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    goat = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="rack_allocations")
    rack = models.ForeignKey(Rack,on_delete=models.PROTECT,related_name="goat_allocations")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_rack_allocations")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="rack_goats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.goat.token_no} - {self.rack.name}"