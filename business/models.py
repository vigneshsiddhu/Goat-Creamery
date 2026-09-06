import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Business(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField( max_length=150)
    address = models.TextField(blank=True)
    gstn = models.CharField( max_length=15, blank=True, null=True)
    phone_number = models.CharField(max_length=15,blank=True)
    created_by = models.ForeignKey( settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='created_businesses')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='owned_businesses')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class BusinessUser(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="business_users")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="business_users")
    role = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "business"],name="unique_user_business")
        ]
    def __str__(self):
        return ( f"{self.user.username} - " f"{self.business.name} - " f"{self.role}")

# business = Business.objects.create(name="Goat Creamery",address="Chennai, Tamil Nadu",gstn="134124",phone_number="9994945543",status=True,created_by=user)
# BusinessUser.objects.create(business=business,user=user,role="SUPER_ADMIN")


class Location(models.Model):
    LOCATION_TYPES = (("state", "State"),("district", "District"),("area", "Area"),("other", "Other"),)
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="locations")
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20,choices=LOCATION_TYPES)
    parent = models.ForeignKey("self",on_delete=models.SET_NULL,null=True,blank=True,related_name="children")
    latitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True)
    longitude = models.DecimalField(max_digits=10,decimal_places=7,null=True,blank=True)
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_locations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["business","name","parent"],name="unique_location_per_parent")]
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name