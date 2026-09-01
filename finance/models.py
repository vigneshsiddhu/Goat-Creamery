import uuid
from django.conf import settings
from django.db import models
from business.models import Business

class FarmExpense(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    date = models.DateField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12,decimal_places=2)
    comment = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_farm_expenses")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="farm_expenses")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date", "-created_at"]