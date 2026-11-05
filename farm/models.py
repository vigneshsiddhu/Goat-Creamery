# myfarm/models.py
import uuid
from django.conf import settings
from django.db import models
from business.models import Business, Location


# ============================================================
# LAND
# ============================================================
class Land(models.Model):
    UNIT_CHOICES = [
        ("acre", "Acre"),
        ("hectare", "Hectare"),
        ("cent", "Cent"),
        ("guntha", "Guntha"),
        ("bigha", "Bigha"),
        ("katha", "Katha"),
        ("ground", "Ground"),
        ("sq_m", "Square metre"),
        ("sq_ft", "Square feet"),
        ("sq_yard", "Square yard"),
    ]
    SOIL_TYPE_CHOICES = [
        ("alluvial", "Alluvial soil"),
        ("black_regur", "Black soil (Regur)"),
        ("black_cotton", "Black cotton soil"),
        ("red_soil", "Red soil"),
        ("red_yellow", "Red and yellow soil"),
        ("laterite", "Laterite soil"),
        ("desert_arid", "Desert / arid soil"),
        ("forest_mountain", "Forest / mountain soil"),
        ("saline_alkaline", "Saline / alkaline soil"),
        ("peaty_marshy", "Peaty / marshy soil"),
        ("sandy_loam", "Sandy loam"),
        ("loamy_sand", "Loamy sand"),
        ("silty_loam", "Silty loam"),
        ("clay_loam", "Clay loam"),
        ("clay", "Clay"),
        ("river_sand", "River sand"),
        ("red_sand", "Red sand"),
        ("coastal_sand", "Coastal sand"),
        ("desert_sand", "Desert sand"),
        ("laterite_sand", "Laterite sand"),
    ]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=150)
    unit = models.CharField(max_length=30, choices=UNIT_CHOICES)
    area = models.DecimalField(max_digits=12,decimal_places=2)
    soil_type = models.CharField(max_length=100, choices=SOIL_TYPE_CHOICES, blank=True, null=True)
    location = models.ForeignKey(Location,on_delete=models.PROTECT,related_name="land",null=True,blank=True)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="lands")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_lands")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return self.name
    
# ============================================================
# WATER
# ============================================================
class Water(models.Model):
    SOURCE_CHOICES = [("borewell", "Borewell"),("open_well", "Open Well"),("pond", "Pond"),("rain", "Rain Water"),("river", "River"),("canal", "Canal"),("other", "Other"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    source = models.CharField(max_length=50,choices=SOURCE_CHOICES)
    name = models.CharField(max_length=150)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="water_sources")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_water_sources")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
    def __str__(self):
        return f"{self.name} - {self.get_source_display()}"


# ============================================================
# LAND WATER
# ============================================================
class LandWater(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    land = models.ForeignKey(Land,on_delete=models.CASCADE,related_name="water_usage")
    water = models.ForeignKey(Water,on_delete=models.CASCADE,related_name="land_usage")
    date = models.DateField()
    status = models.BooleanField(default=True)
    comment = models.TextField(blank=True,null=True)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="land_water_records")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_land_water_records")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date"]
    def __str__(self):
        return f"{self.land.name} - {self.water.name} - {self.date}"

# ============================================================
# FEED CONSUMPTION
# ============================================================
class FeedStock(models.Model):
    FODDER_VARIETY_CHOICES = [
        ("silage", "Silage"),
        ("kadalai_kodi", "Kadalai kodi fodder"),
        ("thovarai", "Thovarai"),
        ("sanapai", "Sanapai"),
        ("ulutham_kodi", "Ulutham kodi"),
        ("solla_thatai", "Solla thatai"),
        ("kuthirai_masal", "Kuthirai masal"),
        ("khejiri", "Khejiri"),
        ("concentrate", "Concentrate feed"),
        ("maize", "Maize"),
        ("paruthi_punnaku", "Paruthi punnaku"),
        ("kadalai_punnaku", "Kadalai punnaku"),
        ("thavudu", "Thavudu"),
    ]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    date = models.DateField()
    fodder_variety = models.CharField(max_length=100, choices=FODDER_VARIETY_CHOICES)
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
    def __str__(self):
        return f"{self.get_fodder_variety_display()} · {self.date}"

class FeedStockTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ("purchase", "Purchase"),
        ("consumption", "Consumption"),
        ("adjustment", "Adjustment"),
        ("wastage", "Wastage"),
        ("return", "Return"),
    ]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    feed_stock = models.ForeignKey(FeedStock,on_delete=models.PROTECT,related_name="transactions")
    date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity_kg = models.DecimalField(max_digits=12,decimal_places=3)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="created_feed_stock_transactions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date", "-created_at"]
    def __str__(self):
        return f"{self.get_transaction_type_display()} · {self.quantity_kg} kg"

class FeedConsumption(models.Model):
    FEED_TIME_CHOICES = [("morning", "Morning"),("afternoon", "Afternoon"),("evening", "Evening"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    date = models.DateField()
    feed_time = models.CharField(max_length=20,choices=FEED_TIME_CHOICES)
    concentrate = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    dry_fodder = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    silage = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    wastage = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="feed_consumptions")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_feed_consumptions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date", "-created_at"]
    def __str__(self):
        return f"Feed - {self.date} - {self.get_feed_time_display()}"