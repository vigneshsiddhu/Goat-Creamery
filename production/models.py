import uuid
from django.conf import settings
from django.db import models
from goats.models import Goat
from business.models import Business,Location


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
        ordering = ["-date","-created_at"]
        constraints = [models.UniqueConstraint(fields=["business","goat","date"],name="unique_goat_weight_per_day")]
        indexes = [models.Index(fields=["goat","date"]),models.Index(fields=["user","date"]),]
    def __str__(self):
        return (f"{self.goat} - "f"{self.weight} kg - "f"{self.date}")


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
        ordering = ["-date","-created_at"]
        constraints = [models.UniqueConstraint(fields=["business","goat","date","time"],name="unique_goat_milk_per_session")]
        indexes = [models.Index(fields=["goat","date"]),models.Index(fields=["user","date"]),models.Index(fields=["goat","date","time"]),]
    def __str__(self):
        return (f"{self.goat} - "f"{self.milk_weight} L - "f"{self.date} - "f"{self.get_time_display()}")

# ============================================================
# GOAT MILK BATCH
# ============================================================
class GoatMilkBatch(models.Model):
    MILK_TIME_CHOICES = [("morning", "Morning"),("evening", "Evening"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    batch_number = models.CharField(max_length=50,)
    date = models.DateField()
    qr_code = models.CharField(max_length=255,unique=True,blank=True,null=True,)
    milk_time = models.CharField(max_length=20,choices=MILK_TIME_CHOICES,)
    milk_quantity = models.DecimalField(max_digits=12,decimal_places=2,help_text="Milk quantity in litres",)
    wastage = models.DecimalField(max_digits=12,decimal_places=2,default=0,help_text="Milk wastage in litres",)
    status = models.CharField(max_length=100)
    packed_date = models.DateTimeField(null=True,blank=True,)
    exp_date = models.DateTimeField(null=True,blank=True,)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="goat_milk_batches",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_goat_milk_batches",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        ordering = ["-date","-created_at"]
        constraints = [ models.UniqueConstraint(fields=["business","batch_number"],name="unique_goat_milk_batch_number_per_business",)]
    def save(self,*args,**kwargs):
        if not self.batch_number:
            date_part = self.date.strftime("%Y%m%d")
            prefix = f"MB-{date_part}-"
            last_batch = (GoatMilkBatch.objects.filter(business=self.business,batch_number__startswith=prefix,).order_by("-batch_number").first())
            if last_batch: 
                last_number = int(last_batch.batch_number.split("-")[-1])
                next_number = last_number + 1
            else:
                next_number = 1
            self.batch_number = f"{prefix}{next_number:03d}"
        super().save(*args,**kwargs)
    def __str__(self):
        return self.batch_number


# ============================================================
# GOAT MILK TEST
# ============================================================
class GoatMilkTest(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    goat_milk_batch = models.ForeignKey(GoatMilkBatch,on_delete=models.CASCADE,related_name="tests", )
    ph = models.DecimalField( max_digits=5,decimal_places=2,null=True, blank=True, )
    fat = models.DecimalField(max_digits=6,decimal_places=2,  null=True,blank=True, help_text="Fat percentage", )
    snf = models.DecimalField(max_digits=6,decimal_places=2,  null=True,blank=True, help_text="SNF percentage", )
    moisture = models.DecimalField(max_digits=6,  decimal_places=2, null=True,blank=True,help_text="Moisture percentage",  )
    notes = models.TextField( blank=True,  null=True,)
    date = models.DateTimeField(  auto_now_add=True,)
    business = models.ForeignKey( Business,on_delete=models.CASCADE,related_name="goat_milk_tests",  )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.SET_NULL,null=True,  blank=True,related_name="created_goat_milk_tests",  )
    created_at = models.DateTimeField(auto_now_add=True, )
    updated_at = models.DateTimeField(auto_now=True, )
    def __str__(self):
        return f"{self.goat_milk_batch.batch_number} - Milk Test"


# ============================================================
# PRODUCT
# ============================================================
class Product(models.Model):
    STATUS_CHOICES = [("active","Active"),("inactive","Inactive"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    goat_milk_batch = models.ForeignKey(GoatMilkBatch,on_delete=models.SET_NULL,null=True,blank=True,related_name="products",)
    code_sku = models.CharField(max_length=100,blank=True,editable=False,)
    type = models.CharField(max_length=100)
    variant = models.CharField(max_length=100,blank=True,null=True,)
    storage_type = models.CharField(max_length=100)
    storage_temp_min = models.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True,help_text="Minimum storage temperature in °C",)
    storage_temp_max = models.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True,help_text="Maximum storage temperature in °C",)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="active",)
    description = models.TextField(blank=True,null=True,)
    life_span_value = models.PositiveIntegerField(null=True,blank=True,)
    life_span_unit = models.CharField(max_length=20,null=True,blank=True,help_text="day, week, month",)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="products",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_products",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        ordering = ["type","code_sku"]
        constraints = [models.UniqueConstraint(fields=["business","code_sku"],name="unique_product_sku_per_business")]
    def save(self,*args,**kwargs):
        if not self.code_sku:
            prefix_map = {"goat_milk":"GM","cheese":"CH","gelato":"GEL","yogurt":"YOG","kefir":"KEF","milkshake":"MS","ghee":"GHEE",}
            prefix = prefix_map.get(self.type,"PROD")
            last_product = (Product.objects.filter(business=self.business,code_sku__startswith=f"{prefix}-").order_by("-code_sku").first())
            if last_product:
                last_number = int(last_product.code_sku.split("-")[-1])
                next_number = last_number + 1
            else:
                next_number = 1
            self.code_sku = f"{prefix}-{next_number:03d}"
        super().save(*args,**kwargs)
    def __str__(self):
        if self.variant:
            return f"{self.code_sku} - {self.type} - {self.variant}"
        return self.code_sku


# ============================================================
# PRODUCT PRICE
# ============================================================
class ProductPrice(models.Model):
    STATUS_CHOICES = [("active", "Active"),("inactive", "Inactive"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="prices",)
    mrp = models.DecimalField(max_digits=12,decimal_places=2,)
    gst = models.DecimalField(max_digits=6,decimal_places=2,default=0,help_text="GST percentage",)
    date = models.DateField()
    quantity = models.DecimalField(max_digits=12,decimal_places=2,default=1,)
    unit = models.CharField(max_length=20,default="unit",)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="active",)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="product_prices",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_product_prices",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        ordering = ["-date", "-created_at"]
    def __str__(self):
        return f"{self.product.code_sku} - ₹{self.mrp}"

# ============================================================
# INGREDIENT
# ============================================================
class Ingredient(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    code = models.CharField(max_length=100,)
    name = models.CharField(max_length=150,)
    details = models.TextField(blank=True,null=True,)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="ingredients",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_ingredients",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["business","code"],name="unique_ingredient_code_per_business",)]
    def save(self,*args,**kwargs):
        if not self.code:
            prefix = "ING"
            last_ingredient = (Ingredient.objects.filter(business=self.business,code__startswith=f"{prefix}-").order_by("-code").first())
            if last_ingredient:
                last_number = int(last_ingredient.code.split("-")[-1])
                next_number = last_number + 1
            else:
                next_number = 1
            self.code = f"{prefix}-{next_number:03d}"
        super().save(*args,**kwargs)
    def __str__(self):
        return f"{self.code} - {self.name}"


# ============================================================
# INGREDIENT PRICE
# ============================================================
class IngredientPrice(models.Model):
    STATUS_CHOICES = [("active", "Active"),("inactive", "Inactive"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE,related_name="prices",)
    quantity = models.DecimalField(max_digits=12,decimal_places=3,)
    unit = models.CharField(max_length=20)
    mrp = models.DecimalField(max_digits=12,decimal_places=2,)
    gst = models.DecimalField(max_digits=6,decimal_places=2,default=0,help_text="GST percentage",)
    date = models.DateField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="active",)
    stock = models.DecimalField(max_digits=12,decimal_places=3,default=0,)
    stock_price = models.DecimalField(max_digits=12,decimal_places=2,default=0,)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="ingredient_prices",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_ingredient_prices",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        ordering = ["-date", "-created_at"]
    def __str__(self):
        return f"{self.ingredient.name} - ₹{self.mrp}"


# ============================================================
# RECIPE
# ============================================================
class Recipe(models.Model):
    STATUS_CHOICES = [("active", "Active"),("inactive", "Inactive"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    date = models.DateField()
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="recipes",)
    procedure = models.TextField(blank=True,null=True,)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="draft",)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="recipes",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_recipes",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    def __str__(self):return f"{self.product.code_sku} {self.product.type} - Recipe"

# ============================================================
# RECIPE ITEM
# ============================================================
class RecipeItem(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    recipe = models.ForeignKey(Recipe,on_delete=models.CASCADE,related_name="items",)
    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE,related_name="recipe_items",)
    unit = models.CharField(max_length=20,default="kg",)
    quantity = models.DecimalField(max_digits=12,decimal_places=3,)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="recipe_items",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_recipe_items",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        ordering = ["created_at"]
    def __str__(self):
        return f"{self.recipe} - {self.ingredient.name}"


# ============================================================
# PRODUCT BATCH
# ============================================================
class ProductBatch(models.Model):
    QC_STATUS_CHOICES = [("pending", "Pending"),("passed", "Passed"),("failed", "Failed"),]
    UNIT_CHOICES = [("kg","Kg"),("gram","Gram"),("litre","Litre"),("ml","Ml"),("piece","Piece"),("pack","Pack"),("pocket","Pocket"),("box","Box"),("bottle","Bottle"),("cup","Cup"),("container","Container"),]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    goat_milk_batch = models.ForeignKey(GoatMilkBatch,on_delete=models.SET_NULL,null=True,blank=True,related_name="product_batches",)
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="batches",)
    recipe = models.ForeignKey(Recipe,on_delete=models.SET_NULL,null=True,blank=True,related_name="product_batches",)
    location = models.ForeignKey(Location,on_delete=models.PROTECT,related_name="area", null=True,blank=True)
    batch_number = models.CharField(max_length=50,)
    unit = models.CharField(max_length=20,choices=UNIT_CHOICES,default="kg",)
    quantity = models.DecimalField(max_digits=12,decimal_places=3,)
    date = models.DateField()
    time = models.TimeField(null=True,blank=True,)
    cost = models.DecimalField(max_digits=14,decimal_places=2,default=0,)
    qr_code = models.CharField(max_length=255,unique=True,blank=True,null=True,)
    notes = models.TextField(blank=True,null=True,)
    qc_status = models.CharField(max_length=20,choices=QC_STATUS_CHOICES,default="pending",)
    status = models.CharField(max_length=100)
    wastage = models.DecimalField(max_digits=12,decimal_places=3,default=0,)
    business = models.ForeignKey(Business,on_delete=models.CASCADE,related_name="product_batches",)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="created_product_batches",)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    class Meta:
        ordering = ["-date","-created_at"]
        constraints = [    models.UniqueConstraint(        fields=["business","batch_number"],        name="unique_product_batch_number_per_business",    )]
    def save(self,*args,**kwargs):
        if not self.batch_number:
            date_part = self.date.strftime("%Y%m%d")
            prefix = f"PB-{date_part}-"
            last_batch = (ProductBatch.objects.filter( business=self.business, batch_number__startswith=prefix,).order_by("-batch_number").first())
            if last_batch:
                last_number = int(
                    last_batch.batch_number.split("-")[-1]
                )
                next_number = last_number + 1
            else:
                next_number = 1
            self.batch_number = f"{prefix}{next_number:03d}"
        super().save(*args,**kwargs)
    def __str__(self):

        return self.batch_number