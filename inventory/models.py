import uuid
from django.conf import settings
from django.db import models
from business.models import Business


class FeedStock(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    date = models.DateField()
    fodder_variety = models.CharField(max_length=100)
    stock_weight = models.DecimalField(max_digits=12,decimal_places=3)
    rate = models.DecimalField(max_digits=12,decimal_places=2)
    total_amount = models.DecimalField(max_digits=14,decimal_places=2)
    current_stock_kg = models.DecimalField(max_digits=12,decimal_places=3)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_feed_stocks")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="feed_stocks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date", "-created_at"]

class FeedStockTransaction(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    feed_stock = models.ForeignKey(FeedStock,on_delete=models.PROTECT,related_name="transactions")
    date = models.DateField()
    transaction_type = models.CharField(max_length=20)
    quantity_kg = models.DecimalField(max_digits=12,decimal_places=3)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_feed_stock_transactions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date", "-created_at"]