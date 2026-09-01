import uuid

from django.conf import settings
from django.db import models

from goats.models import Goat
from business.models import Business


# =========================================================
# GOAT WEIGHT
# =========================================================

class GoatWeight(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    goat = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="weight_records")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="goat_weight_records")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="weight_records")
    weight = models.DecimalField(max_digits=6,decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_goat_weight_records")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = [
            "-date",
            "-created_at"
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "business",
                    "goat",
                    "date"
                ],
                name="unique_goat_weight_per_day"
            )
        ]
        indexes = [
            models.Index(
                fields=[
                    "goat",
                    "date"
                ]
            ),
            models.Index(
                fields=[
                    "user",
                    "date"
                ]
            ),
        ]
    def __str__(self):
        return (
            f"{self.goat} - "
            f"{self.weight} kg - "
            f"{self.date}"
        )


# =========================================================
# GOAT MILK
# =========================================================

class GoatMilk(models.Model):
    class MilkingTime(models.TextChoices):
        MORNING = "morning", "Morning"
        EVENING = "evening", "Evening"

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    goat = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="milk_records")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="goat_milk_records")
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="milk_records")
    milk_weight = models.DecimalField(max_digits=7,decimal_places=3)
    date = models.DateField()
    time = models.CharField(max_length=10,choices=MilkingTime.choices)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_goat_milk_records")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = [
            "-date",
            "-created_at"
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "business",
                    "goat",
                    "date",
                    "time"
                ],
                name="unique_goat_milk_per_session"
            )
        ]
        indexes = [
            models.Index(
                fields=[
                    "goat",
                    "date"
                ]
            ),

            models.Index(
                fields=[
                    "user",
                    "date"
                ]
            ),

            models.Index(
                fields=[
                    "goat",
                    "date",
                    "time"
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.goat} - "
            f"{self.milk_weight} L - "
            f"{self.date} - "
            f"{self.get_time_display()}"
        )