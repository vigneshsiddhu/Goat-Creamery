import uuid

from django.conf import settings
from django.db import models

from goats.models import Goat


class Mating(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    male = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="male_matings")
    female = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="female_matings")
    mating_date = models.DateField()
    comment = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_matings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-mating_date"]
    

class ParentMapping(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    child = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="parents")
    parent = models.ForeignKey(Goat,on_delete=models.PROTECT,related_name="children")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_parent_mappings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child", "parent"],
                name="unique_child_parent"
            )
        ]
 