from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import inlineformset_factory
from .models import GoatWeight,GoatMilk,GoatMilkBatch,GoatMilkTest,Product,ProductPrice,Ingredient,IngredientPrice,Recipe,RecipeItem,ProductBatch,Goat

class GoatWeightForm(forms.ModelForm):
    class Meta:
        model = GoatWeight
        fields = ["goat","weight","date","note"]
        widgets = {
            "goat": forms.Select(attrs={"class": "form-input"}),
            "weight": forms.NumberInput(attrs={"class": "form-input", "placeholder": "Weight in kg", "step": "0.01", "min": "0"}),
            "date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "note": forms.Textarea(attrs={"class": "form-input", "placeholder": "Optional note", "rows": 3}),
        }
        labels = {"goat": "Token ID"}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["goat"].empty_label = "Select Token ID"
        self.fields["goat"].label_from_instance = lambda obj: obj.token_no

class GoatWeightVoiceForm(forms.ModelForm):
    goat = forms.ModelChoiceField(
        queryset=Goat.objects.none(),
        empty_label="Select Token ID",
        label="Token ID",
        widget=forms.Select(attrs={"class": "form-input", "id": "id_goat"}),
    )
    weight = forms.DecimalField(
        min_value=Decimal("0.1"),
        max_value=Decimal("80.0"),
        decimal_places=1,
        max_digits=4,
        label="Goat Weight",
        widget=forms.HiddenInput(attrs={"id": "id_weight"}),
    )
    class Meta:
        model = GoatWeight
        fields = ["goat", "weight"]
    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["goat"].queryset = Goat.objects.none()
        self.fields["goat"].label_from_instance = lambda obj: obj.token_no
        if business:
            self.fields["goat"].queryset = Goat.objects.filter(business=business, live=True).order_by("token_no")
    def clean_weight(self):
        value = self.cleaned_data["weight"].quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        if value < Decimal("0.1") or value > Decimal("80.0"):
            raise ValidationError("Weight must be between 0.1 and 80.0 kg.")
        return value

class GoatMilkForm(forms.ModelForm):
    class Meta:
        model = GoatMilk
        fields = ["goat", "milk_weight", "date", "time", "note"]
        widgets = {
            "goat": forms.Select(attrs={"class": "form-input"}),
            "milk_weight": forms.NumberInput(attrs={"class": "form-input", "placeholder": "Milk in litres", "step": "0.1", "min": "0.1"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "time": forms.Select(attrs={"class": "form-input"}),
            "note": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Optional note"}),
        }
        labels = {"goat": "Token ID", "milk_weight": "Milk Quantity (L)", "time": "Milking Time"}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["goat"].empty_label = "Select Token ID"
        self.fields["goat"].label_from_instance = lambda obj: obj.token_no

class GoatMilkVoiceForm(forms.Form):
    goat = forms.ModelChoiceField(
        queryset=Goat.objects.none(),
        empty_label="Select Token ID",
        label="Token ID",
        widget=forms.Select(attrs={"class": "form-input", "id": "id_goat"}),
    )
    milk_weight = forms.DecimalField(
        min_value=Decimal("0.1"),
        max_value=Decimal("5.0"),
        decimal_places=1,
        max_digits=3,
        label="Milk Quantity",
        widget=forms.HiddenInput(attrs={"id": "id_milk_weight"}),
    )
    def __init__(self, *args, business=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["goat"].queryset = Goat.objects.none()
        self.fields["goat"].label_from_instance = lambda obj: obj.token_no
        if business:
            self.fields["goat"].queryset = Goat.objects.filter(
                business=business, gender="FEMALE", live=True
            ).order_by("token_no")
    def clean_milk_weight(self):
        value = self.cleaned_data["milk_weight"].quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        if value < Decimal("0.1") or value > Decimal("5.0"):
            raise ValidationError("Milk quantity must be between 0.1 and 5.0 L.")
        return value

class GoatMilkBatchForm(forms.ModelForm):
    STATUS_CHOICES = [
        ("collected", "Collected"),
        ("pasteurized", "Pasteurized"),
        ("processing", "Processing"),
        ("closed", "Closed"),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    class Meta:
        model = GoatMilkBatch
        fields = ["date", "qr_code", "milk_time", "milk_quantity", "wastage", "status", "packed_date", "exp_date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "qr_code": forms.TextInput(attrs={"class": "form-input", "placeholder": "Scan or enter later"}),
            "milk_time": forms.Select(attrs={"class": "form-input"}),
            "milk_quantity": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "Litres collected"}),
            "wastage": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0"}),
            "packed_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "exp_date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        from django.utils import timezone

        super().__init__(*args, **kwargs)
        self.fields["qr_code"].required = False
        self.fields["wastage"].required = False
        if not self.is_bound and not getattr(self.instance, "pk", None):
            today = timezone.localdate()
            self.fields["date"].initial = today
            self.fields["milk_time"].initial = "morning"
            self.fields["status"].initial = "collected"
            self.fields["wastage"].initial = 0

    def clean_milk_quantity(self):
        value = self.cleaned_data["milk_quantity"]
        if value <= 0:
            raise ValidationError("Milk quantity must be greater than zero.")
        return value

    def clean_wastage(self):
        value = self.cleaned_data.get("wastage")
        if value in (None, ""):
            return 0
        if value < 0:
            raise ValidationError("Wastage cannot be negative.")
        return value

    def clean_qr_code(self):
        value = self.cleaned_data.get("qr_code")
        if not value:
            return None
        return value.strip()

class GoatMilkBatchFarmForm(forms.Form):
    milk_quantity = forms.DecimalField(
        min_value=Decimal("0.01"),
        decimal_places=2,
        max_digits=12,
        label="Milk Quantity (L)",
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0.01", "placeholder": "Litres collected"}),
    )
    qr_code = forms.CharField(
        required=False,
        max_length=255,
        label="QR Code",
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Scan or enter QR code"}),
    )

    def clean_qr_code(self):
        value = self.cleaned_data.get("qr_code")
        if not value:
            return None
        return value.strip()

class GoatMilkTestForm(forms.ModelForm):
    class Meta:
        model = GoatMilkTest
        fields = ["goat_milk_batch","ph","fat","snf","moisture","notes"]
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["goat_milk_batch"].queryset = GoatMilkBatch.objects.filter(business=business).order_by("-date","-created_at")
    def clean(self):
        cleaned = super().clean()
        ph = cleaned.get("ph")
        fat = cleaned.get("fat")
        snf = cleaned.get("snf")
        moisture = cleaned.get("moisture")
        if ph is not None and (ph < 0 or ph > 14):
            self.add_error("ph","pH must be between 0 and 14.")
        if fat is not None and (fat < 0 or fat > 100):
            self.add_error("fat","Fat percentage must be between 0 and 100.")
        if snf is not None and (snf < 0 or snf > 100):
            self.add_error("snf","SNF percentage must be between 0 and 100.")
        if moisture is not None and (moisture < 0 or moisture > 100):
            self.add_error("moisture","Moisture percentage must be between 0 and 100.")
        return cleaned

class ProductForm(forms.ModelForm):
    PRODUCT_TYPE_CHOICES = [("goat milk","Goat Milk"),("cheese","Cheese"),("gelato","Gelato"),("yogurt","Yogurt"),("kefir","Kefir"),("milkshake","Milkshake"),("ghee","Ghee"),]
    VARIANT_CHOICES = [
        ("plain", "Plain"),
        ("vanilla", "Vanilla"),
        ("peach", "Peach"),
        ("chocolate", "Chocolate"),
        ("premium_tiramisu", "Premium Tiramisu"),
        ("premium_pistachio", "Premium Pistachio"),
        ("premium_caramel", "Premium Caramel"),
        ("premium_chocolate_hazelnut", "Premium Chocolate Hazelnut"),
        ("strawberry", "Strawberry"),
        ("mango", "Mango"),
        ("pistachio", "Pistachio"),
        ("coffee", "Coffee"),
        ("tender_coconut", "Tender Coconut"),
        ("blueberry", "Blueberry"),
        ("mixed_berry", "Mixed Berry"),
        ("rose", "Rose"),
        ("kulfi", "Kulfi"),
        ("butterscotch", "Butterscotch"),
        ("caramel", "Caramel"),
        ("salted_caramel", "Salted Caramel"),
        ("banana", "Banana"),
        ("natural", "Natural"),
        ("other", "Other"),
    ]
    STORAGE_TYPE_CHOICES = [("refrigerated","Refrigerated"),("ambient","Ambient"),("frozen","Frozen"),("deep_frozen","Deep Frozen"),("dry_storage","Dry Storage"),("cool_storage","Cool Storage"),]
    LIFE_SPAN_UNIT_CHOICES = [("days","Days"),("week","Week"),("month","Month"),]
    type = forms.ChoiceField(choices=PRODUCT_TYPE_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    variant = forms.ChoiceField(choices=VARIANT_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    life_span_unit = forms.ChoiceField(choices=LIFE_SPAN_UNIT_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    storage_type = forms.ChoiceField(choices=STORAGE_TYPE_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    class Meta:
        model = Product
        fields = ["type","variant","storage_type","storage_temp_min","storage_temp_max","status","description","life_span_value","life_span_unit",]
        widgets = {
            "type": forms.Select(attrs={"class":"form-input"}),
            "variant": forms.Select(attrs={"class":"form-input"}),
            "storage_type": forms.Select(attrs={"class":"form-input"}),
            "storage_temp_min": forms.NumberInput(attrs={"class":"form-input","step":"0.01","placeholder":"Minimum temperature"}),
            "storage_temp_max": forms.NumberInput(attrs={"class":"form-input","step":"0.01","placeholder":"Maximum temperature"}),
            "status": forms.Select(attrs={"class":"form-input"}),
            "description": forms.Textarea(attrs={"class":"form-input","placeholder":"Enter product description","rows":4}),
            "life_span_value": forms.NumberInput(attrs={"class":"form-input","min":"1","placeholder":"Enter shelf life"}),
            "life_span_unit": forms.TextInput(attrs={"class":"form-input","placeholder":"day, week, month"}),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.business = business
        self.fields["life_span_value"].required = True
        if not getattr(self.instance, "pk", None):
            self.fields.pop("status", None)
    def clean(self):
        cleaned = super().clean()
        min_temp = cleaned.get("storage_temp_min")
        max_temp = cleaned.get("storage_temp_max")
        life_value = cleaned.get("life_span_value")
        life_unit = cleaned.get("life_span_unit")
        product_type = cleaned.get("type")
        variant = cleaned.get("variant")
        if min_temp is not None and max_temp is not None and min_temp > max_temp:
            self.add_error("storage_temp_max","Maximum temperature must be greater than or equal to minimum temperature.")
        if life_value is not None and life_value <= 0:
            self.add_error("life_span_value","Life span must be greater than zero.")
        if life_value and not life_unit:
            self.add_error("life_span_unit","Life span unit is required.")
        if self.business and product_type and variant:
            qs = Product.objects.filter(
                business=self.business,
                type=product_type,
                variant=variant,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                type_label = product_type.replace("_", " ").title()
                variant_label = variant.replace("_", " ").title()
                raise ValidationError(
                    f"A product with type “{type_label}” and flavour “{variant_label}” already exists."
                )
        return cleaned

class ProductPriceForm(forms.ModelForm):
    UNIT_CHOICES = [("kg","Kg"),("gram","Gram"),("litre","Litre"),("ml","Ml"),("piece","Piece"),("pack","Pack"),("pocket","Pocket"),("box","Box"),("bottle","Bottle"),("cup","Cup"),("container","Container"),]
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class":"form-input",})
    )
    class Meta:
        model = ProductPrice
        fields = ["product","mrp","gst","date","quantity","unit","status"]
        widgets = {
            "product": forms.Select(attrs={"class":"form-input",}),
            "mrp": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"Enter MRP",}),
            "gst": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","max":"100","placeholder":"Enter GST percentage",}),
            "date": forms.DateInput(attrs={"type":"date","class":"form-input",}),
            "quantity": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"Enter quantity",}),
            "status": forms.Select(attrs={"class":"form-input",}),
        }
    def __init__(self,*args,**kwargs):
        from django.utils import timezone

        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["product"].queryset = Product.objects.filter(
            business=business,
            status="active",
        ).order_by("type", "variant", "code_sku")
        self.fields["product"].empty_label = "Select product"
        if not getattr(self.instance, "pk", None):
            self.fields.pop("status", None)
            if not self.is_bound:
                self.fields["date"].initial = timezone.localdate()
                self.fields["gst"].initial = Decimal("0")
                self.fields["quantity"].initial = Decimal("1")
    def clean(self):
        cleaned = super().clean()
        mrp = cleaned.get("mrp")
        gst = cleaned.get("gst")
        quantity = cleaned.get("quantity")
        if mrp is not None and mrp < 0:
            self.add_error("mrp","MRP cannot be negative.")
        if gst is not None and (gst < 0 or gst > 100):
            self.add_error("gst","GST must be between 0 and 100.")
        if quantity is not None and quantity <= 0:
            self.add_error("quantity","Quantity must be greater than zero.")
        return cleaned

class IngredientWithPriceForm(forms.Form):
    UNIT_CHOICES = [
        ("kg", "Kg"), ("gram", "Gram"), ("litre", "Litre"), ("ml", "Ml"),
        ("piece", "Piece"), ("pack", "Pack"), ("pocket", "Pocket"), ("box", "Box"),
        ("bottle", "Bottle"), ("cup", "Cup"), ("container", "Container"),
    ]
    INPUT_PRICE_FIELDS = ("quantity", "unit", "mrp", "gst", "date", "status")

    name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Enter ingredient name"}),
    )
    details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-input", "placeholder": "Enter ingredient details", "rows": 3}),
    )
    quantity = forms.DecimalField(
        required=True,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={
            "class": "form-input qty-unit-qty",
            "step": "0.001",
            "min": "0",
            "placeholder": "Quantity",
            "aria-label": "Quantity",
        }),
    )
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-input qty-unit-select", "aria-label": "Unit"}),
    )
    mrp = forms.DecimalField(
        required=True,
        min_value=Decimal("0"),
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "Enter MRP"}),
    )
    gst = forms.DecimalField(
        required=True,
        min_value=Decimal("0"),
        max_value=Decimal("100"),
        widget=forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0", "max": "100", "placeholder": "GST %"}),
    )
    date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-input"}),
    )
    status = forms.ChoiceField(
        choices=IngredientPrice.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    def __init__(self, *args, business=None, ingredient=None, **kwargs):
        from django.utils import timezone

        super().__init__(*args, **kwargs)
        self.business = business
        self.ingredient = ingredient
        self.latest_price = None
        self.is_edit = ingredient is not None

        if ingredient:
            self.fields["name"].initial = ingredient.name
            self.fields["details"].initial = ingredient.details
            self.latest_price = (
                ingredient.prices.filter(business=business)
                .order_by("-date", "-created_at")
                .first()
            )
            self.fields["quantity"].required = False
            if self.latest_price:
                self.fields["unit"].initial = self.latest_price.unit
                self.fields["gst"].initial = self.latest_price.gst
                self.fields["status"].initial = self.latest_price.status
            self.fields["status"].required = True
            if not self.is_bound:
                self.fields["date"].initial = timezone.localdate()
        else:
            self.fields.pop("status", None)
            self.fields["quantity"].min_value = Decimal("0.001")
            if not self.is_bound:
                today = timezone.localdate()
                self.fields["date"].initial = today
                self.fields["gst"].initial = Decimal("0")

    def clean_name(self):
        value = self.cleaned_data.get("name")
        if not value:
            raise ValidationError("Ingredient name is required.")
        name = " ".join(value.strip().split()).title()
        if not self.business:
            return name
        qs = Ingredient.objects.filter(business=self.business, name__iexact=name)
        if self.ingredient:
            qs = qs.exclude(pk=self.ingredient.pk)
        if qs.exists():
            raise ValidationError("An ingredient with this name already exists.")
        return name

    def clean_quantity(self):
        value = self.cleaned_data.get("quantity")
        if value in (None, ""):
            value = Decimal("0")
        if not self.is_edit and value <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if value < 0:
            raise ValidationError("Quantity cannot be negative.")
        return value

    def _quantize(self, value, places="0.01"):
        return Decimal(value).quantize(Decimal(places), rounding=ROUND_HALF_UP)

    def compute_stock_and_stock_price(self):
        quantity = self.cleaned_data["quantity"]
        mrp = self.cleaned_data["mrp"]

        if self.latest_price:
            stock = self.latest_price.stock + quantity
            stock_price = (self.latest_price.stock_price + mrp) / Decimal("2")
        else:
            stock = quantity
            stock_price = mrp

        return self._quantize(stock, "0.001"), self._quantize(stock_price, "0.01")

    def get_price_data(self):
        stock, stock_price = self.compute_stock_and_stock_price()
        return {
            "quantity": self.cleaned_data["quantity"],
            "unit": self.cleaned_data["unit"],
            "mrp": self.cleaned_data["mrp"],
            "gst": self.cleaned_data["gst"],
            "date": self.cleaned_data["date"],
            "status": self.cleaned_data.get("status", "active"),
            "stock": stock,
            "stock_price": stock_price,
        }

    def price_changed_from_latest(self):
        if not self.latest_price:
            return True
        quantity = self.cleaned_data.get("quantity") or Decimal("0")
        if quantity > 0:
            return True
        latest = self.latest_price
        compare_fields = ("unit", "mrp", "gst", "date", "status")
        for field_name in compare_fields:
            if field_name == "status" and field_name not in self.cleaned_data:
                continue
            if self.cleaned_data[field_name] != getattr(latest, field_name):
                return True
        return False


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name","details"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class":"form-input",
                    "placeholder":"Enter ingredient name",
                }
            ),
            "details": forms.Textarea(
                attrs={
                    "class":"form-input",
                    "placeholder":"Enter ingredient details",
                    "rows":4,
                }
            ),
        }
    def clean_name(self):
        value = self.cleaned_data.get("name")
        if not value:
            raise ValidationError("Ingredient name is required.")
        return value.strip()
class IngredientPriceForm(forms.ModelForm):
    UNIT_CHOICES = [("kg","Kg"),("gram","Gram"),("litre","Litre"),("ml","Ml"),("piece","Piece"),("pack","Pack"),("pocket","Pocket"),("box","Box"),("bottle","Bottle"),("cup","Cup"),("container","Container"),]
    unit = forms.ChoiceField(choices=UNIT_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    class Meta:
        model = IngredientPrice
        fields = ["ingredient","quantity","unit","mrp","gst","date","status","stock","stock_price"]
        widgets = {
            "ingredient": forms.Select(attrs={"class":"form-input",}),
            "quantity": forms.NumberInput(attrs={"class":"form-input","step":"0.001","min":"0","placeholder":"Enter quantity",}),
            "mrp": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"Enter MRP",}),
            "gst": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","max":"100","placeholder":"Enter GST percentage",}),
            "date": forms.DateInput(attrs={"type":"date","class":"form-input",}),
            "status": forms.Select(attrs={"class":"form-input",}),
            "stock": forms.NumberInput(attrs={"class":"form-input","step":"0.001","min":"0","placeholder":"Enter stock quantity",}),
            "stock_price": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"Enter stock price",}),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["ingredient"].queryset = Ingredient.objects.filter(
            business=business
        ).order_by("name")
        self.fields["ingredient"].required = True
        self.fields["quantity"].required = True
        self.fields["unit"].required = True
        self.fields["mrp"].required = True
        self.fields["gst"].required = True
        self.fields["date"].required = True
        self.fields["status"].required = True
        self.fields["stock"].required = True
        self.fields["stock_price"].required = True
    def clean(self):
        cleaned = super().clean()
        quantity = cleaned.get("quantity")
        mrp = cleaned.get("mrp")
        gst = cleaned.get("gst")
        stock = cleaned.get("stock")
        stock_price = cleaned.get("stock_price")
        if quantity is not None and quantity <= 0:
            self.add_error("quantity","Quantity must be greater than zero.")
        if mrp is not None and mrp < 0:
            self.add_error("mrp","MRP cannot be negative.")
        if gst is not None and (gst < 0 or gst > 100):
            self.add_error("gst","GST must be between 0 and 100.")
        if stock is not None and stock < 0:
            self.add_error("stock","Stock cannot be negative.")
        if stock_price is not None and stock_price < 0:
            self.add_error("stock_price","Stock price cannot be negative.")
        return cleaned
    
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["date","product","procedure","status"]
        widgets = {
            "date": forms.DateInput(attrs={"type":"date","class":"form-input",}),
            "product": forms.Select(attrs={"class":"form-input","id":"id_recipe_product",}),
            "procedure": forms.Textarea(attrs={"class":"form-input","placeholder":"Enter recipe preparation procedure","rows":4,}),
            "status": forms.Select(attrs={"class":"form-input",}),
        }
    def __init__(self,*args,**kwargs):
        from django.utils import timezone

        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.business = business
        used_product_ids = set(
            Recipe.objects.filter(business=business).exclude(pk=self.instance.pk).values_list("product_id", flat=True)
            if self.instance.pk
            else Recipe.objects.filter(business=business).values_list("product_id", flat=True)
        )
        product_qs = Product.objects.filter(
            business=business,
            status="active",
        )
        if used_product_ids:
            if self.instance.pk and self.instance.product_id:
                product_qs = product_qs.filter(Q(pk=self.instance.product_id) | ~Q(pk__in=used_product_ids))
            else:
                product_qs = product_qs.exclude(pk__in=used_product_ids)
        self.fields["product"].queryset = product_qs.order_by("type", "variant", "code_sku")
        self.fields["product"].empty_label = "Select product"
        self.fields["date"].required = True
        self.fields["product"].required = True
        self.fields["procedure"].required = False
        if not getattr(self.instance, "pk", None):
            self.fields.pop("status", None)
            if not self.is_bound:
                self.fields["date"].initial = timezone.localdate()

    def clean_product(self):
        product = self.cleaned_data.get("product")
        if not product or not self.business:
            return product
        qs = Recipe.objects.filter(business=self.business, product=product)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("A recipe already exists for this product.")
        return product

class RecipeItemInlineForm(forms.ModelForm):
    UNIT_CHOICES = [
        ("kg","Kg"),("gram","Gram"),("litre","Litre"),("ml","Ml"),
        ("piece","Piece"),("pack","Pack"),("pocket","Pocket"),("box","Box"),
        ("bottle","Bottle"),("cup","Cup"),("container","Container"),
    ]
    unit = forms.ChoiceField(
        choices=[("", "Select unit")] + UNIT_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class":"form-input recipe-item-unit",}),
    )
    class Meta:
        model = RecipeItem
        fields = ["ingredient","unit","quantity"]
        widgets = {
            "ingredient": forms.Select(attrs={"class":"form-input recipe-item-ingredient",}),
            "quantity": forms.NumberInput(attrs={"class":"form-input recipe-item-quantity","step":"0.001","min":"0","placeholder":"Qty",}),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.business = business
        self.empty_permitted = True
        self.fields["ingredient"].queryset = Ingredient.objects.filter(
            business=business,
        ).order_by("name")
        self.fields["ingredient"].required = False
        self.fields["unit"].required = False
        self.fields["quantity"].required = False

    def _is_marked_for_delete(self):
        if not self.data:
            return False
        delete_key = self.add_prefix("DELETE")
        return self.data.get(delete_key) in ("on", "true", "True", "1")

    def full_clean(self):
        if self._is_marked_for_delete():
            self._errors = {}
            self.cleaned_data = {"DELETE": True}
            return
        super().full_clean()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        ingredient = cleaned.get("ingredient")
        quantity = cleaned.get("quantity")
        unit = cleaned.get("unit")
        if not ingredient and not quantity and not unit:
            return cleaned
        if not ingredient:
            self.add_error("ingredient", "Select an ingredient.")
            return cleaned
        if quantity in (None, ""):
            self.add_error("quantity", "Quantity is required.")
            return cleaned
        if quantity is not None and quantity <= 0:
            self.add_error("quantity", "Quantity must be greater than zero.")
        if not unit:
            self.add_error("unit", "Select a unit.")
        if self.business and ingredient.business_id != self.business.id:
            self.add_error("ingredient", "Invalid ingredient.")
        return cleaned

class BaseRecipeItemFormSet(forms.BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields.pop("recipe", None)

    def clean(self):
        super().clean()
        active_items = []
        seen_ingredients = set()
        for form in self.forms:
            if form.errors:
                continue
            cleaned = getattr(form, "cleaned_data", None)
            if not cleaned or cleaned.get("DELETE"):
                continue
            ingredient = cleaned.get("ingredient")
            if not ingredient:
                continue
            if ingredient.pk in seen_ingredients:
                raise ValidationError("Each ingredient can only appear once in a recipe.")
            seen_ingredients.add(ingredient.pk)
            active_items.append(cleaned)
        if self.data and not active_items:
            raise ValidationError("Add at least one recipe item.")

RecipeItemFormSet = inlineformset_factory(
    Recipe,
    RecipeItem,
    form=RecipeItemInlineForm,
    formset=BaseRecipeItemFormSet,
    extra=1,
    can_delete=True,
)

class RecipeItemForm(forms.ModelForm):
    UNIT_CHOICES = [
        ("kg","Kg"),
        ("gram","Gram"),
        ("litre","Litre"),
        ("ml","Ml"),
        ("piece","Piece"),
        ("pack","Pack"),
        ("pocket","Pocket"),
        ("box","Box"),
        ("bottle","Bottle"),
        ("cup","Cup"),
        ("container","Container"),
    ]
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        required=True,
        widget=forms.Select(
            attrs={
                "class":"form-input",
            }
        )
    )
    class Meta:
        model = RecipeItem
        fields = ["recipe","ingredient","unit","quantity"]
        widgets = {
            "recipe": forms.Select(attrs={"class":"form-input",}),
            "ingredient": forms.Select(attrs={"class":"form-input",}),
            "quantity": forms.NumberInput(attrs={    "class":"form-input",    "step":"0.001",    "min":"0",    "placeholder":"Enter quantity",}),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["recipe"].queryset = Recipe.objects.filter(
            business=business
        ).select_related(
            "product"
        ).order_by(
            "-date",
            "-created_at"
        )
        self.fields["ingredient"].queryset = Ingredient.objects.filter(
            business=business
        ).order_by("name")
        self.fields["recipe"].required = True
        self.fields["ingredient"].required = True
        self.fields["unit"].required = True
        self.fields["quantity"].required = True
    def clean(self):
        cleaned = super().clean()
        recipe = cleaned.get("recipe")
        ingredient = cleaned.get("ingredient")
        quantity = cleaned.get("quantity")
        if recipe and ingredient and recipe.business_id != ingredient.business_id:
            raise ValidationError(
                "Recipe and ingredient must belong to the same business."
            )
        if quantity is not None and quantity <= 0:
            self.add_error(
                "quantity",
                "Quantity must be greater than zero."
            )
        return cleaned

class ProductBatchForm(forms.ModelForm):
    UNIT_CHOICES = [("kg","Kg"),("gram","Gram"),("litre","Litre"),("ml","Ml"),("piece","Piece"),("pack","Pack"),("pocket","Pocket"),("box","Box"),("bottle","Bottle"),("cup","Cup"),("container","Container"),]
    unit = forms.ChoiceField(choices=[("","Select Unit")] + UNIT_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    STATUS_CHOICES = [("active","Active"),("inactive","Inactive"),]
    status = forms.ChoiceField(choices=STATUS_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    close_milk_batch = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    class Meta:
        model = ProductBatch
        fields = ["product","recipe","quantity","unit","date","time","cost","qr_code","notes","qc_status","status","wastage",]
        widgets = {
            "product": forms.Select(attrs={"class":"form-input","id":"id_product"}),
            "recipe": forms.Select(attrs={"class":"form-input","id":"id_recipe"}),
            "quantity": forms.NumberInput(attrs={"class":"form-input","step":"0.001","min":"0","placeholder":"Enter quantity"}),
            "date": forms.DateInput(attrs={"type":"date","class":"form-input"}),
            "time": forms.TimeInput(attrs={"type":"time","class":"form-input"}),
            "cost": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"Enter production cost"}),
            "qr_code": forms.TextInput(attrs={"class":"form-input","placeholder":"Optional — scan or enter later"}),
            "notes": forms.Textarea(attrs={"class":"form-input","placeholder":"Optional notes","rows":3}),
            "qc_status": forms.Select(attrs={"class":"form-input"}),
            "wastage": forms.NumberInput(attrs={"class":"form-input","step":"0.001","min":"0","placeholder":"0"}),
        }
    def __init__(self,*args,**kwargs):
        from django.utils import timezone

        business = kwargs.pop("business",None)
        hide_checkout = kwargs.pop("hide_checkout", False)
        kwargs.pop("locked_milk_batch", None)
        super().__init__(*args,**kwargs)
        self.business = business

        product_id = None
        if self.data.get("product"):
            product_id = self.data.get("product")
        elif self.instance.pk and self.instance.product_id:
            product_id = str(self.instance.product_id)

        self.fields["product"].queryset = Product.objects.filter(
            business=business,
            status="active",
        ).order_by("type","code_sku")
        self.fields["product"].empty_label = "Select product"

        recipe_qs = Recipe.objects.filter(business=business).order_by("-date", "-created_at")
        if product_id:
            product = Product.objects.filter(pk=product_id, business=business).first()
            if product:
                recipe_qs = Recipe.objects.filter(business=business).filter(
                    Q(product=product) | Q(type=product.type)
                ).order_by("-date", "-created_at")
            else:
                recipe_qs = recipe_qs.none()
            self.fields["recipe"].empty_label = "No recipe (optional)"
        else:
            recipe_qs = recipe_qs.none()
            self.fields["recipe"].empty_label = "Select product first"
        self.fields["recipe"].queryset = recipe_qs

        self.fields["product"].required = True
        self.fields["recipe"].required = False
        self.fields["quantity"].required = True
        self.fields["date"].required = True
        self.fields["time"].required = False
        self.fields["cost"].required = False
        self.fields["qr_code"].required = False
        self.fields["notes"].required = False
        self.fields["qc_status"].required = True
        self.fields["status"].required = True
        self.fields["wastage"].required = False

        if self.instance._state.adding:
            today = timezone.localdate()
            self.fields["date"].initial = today
            self.fields["cost"].initial = 0
            self.fields["wastage"].initial = 0
            self.fields["qc_status"].initial = "pending"
            self.fields["status"].initial = "active"
            self.fields.pop("status", None)
        else:
            self.fields.pop("close_milk_batch", None)
        if hide_checkout:
            self.fields.pop("close_milk_batch", None)

    def clean_cost(self):
        value = self.cleaned_data.get("cost")
        if value in (None, ""):
            return 0
        if value < 0:
            raise ValidationError("Cost cannot be negative.")
        return value

    def clean_wastage(self):
        value = self.cleaned_data.get("wastage")
        if value in (None, ""):
            return 0
        if value < 0:
            raise ValidationError("Wastage cannot be negative.")
        return value

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        recipe = cleaned.get("recipe")
        quantity = cleaned.get("quantity")
        if recipe and product and recipe.type != product.type:
            self.add_error(
                "recipe",
                "Selected recipe does not match the selected product type."
            )
        if quantity is not None and quantity <= 0:
            self.add_error(
                "quantity",
                "Quantity must be greater than zero."
            )
        return cleaned


class ProductBatchVoiceForm(forms.Form):
    UNIT_CHOICES = [
        ("kg", "Kg"),
        ("gram", "Gram"),
        ("litre", "Litre"),
        ("ml", "Ml"),
        ("piece", "Piece"),
        ("pack", "Pack"),
        ("pocket", "Pocket"),
        ("box", "Box"),
        ("bottle", "Bottle"),
        ("cup", "Cup"),
        ("container", "Container"),
    ]
    unit = forms.ChoiceField(
        choices=UNIT_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-input qty-unit-select", "aria-label": "Unit"}),
    )
    close_milk_batch = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        required=True,
        empty_label="Select product",
        widget=forms.Select(attrs={"class": "form-input", "id": "id_product"}),
    )
    quantity = forms.DecimalField(
        required=True,
        min_value=Decimal("0.001"),
        widget=forms.NumberInput(attrs={
            "class": "form-input qty-unit-qty",
            "step": "0.001",
            "min": "0.001",
            "placeholder": "Quantity",
            "aria-label": "Quantity",
        }),
    )

    def __init__(self, *args, **kwargs):
        business = kwargs.pop("business", None)
        hide_checkout = kwargs.pop("hide_checkout", False)
        kwargs.pop("locked_milk_batch", None)
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(
            business=business,
            status="active",
        ).order_by("type", "code_sku")
        self.fields["product"].empty_label = "Select product"
        self.fields["product"].required = True
        self.fields["quantity"].required = True
        self.fields["unit"].required = True
        if hide_checkout:
            self.fields.pop("close_milk_batch", None)

    def clean_quantity(self):
        value = self.cleaned_data.get("quantity")
        if value is None or value <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return value
