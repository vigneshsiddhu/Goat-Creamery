from django import forms
from django.core.exceptions import ValidationError
from business.models import Location
from .models import GoatWeight,GoatMilk,GoatMilkBatch,GoatMilkTest,Product,ProductPrice,Ingredient,IngredientPrice,Recipe,RecipeItem,ProductBatch,Goat

class GoatWeightForm(forms.ModelForm):
    class Meta:
        model = GoatWeight
        fields = ["goat","weight","date","note"]
        widgets = {
            "goat": forms.Select(attrs={"class":"production-form-input"}),
            "weight": forms.NumberInput(attrs={"class":"production-form-input","placeholder":"Enter weight in kg","step":"0.01","min":"0"}),
            "date": forms.DateInput(attrs={"class":"production-form-input","type":"date"}),
            "note": forms.Textarea(attrs={"class":"production-form-input","placeholder":"Enter note","rows":4}),
        }

class GoatWeightVoiceForm(forms.ModelForm):
    goat = forms.ModelChoiceField(queryset=Goat.objects.none(),empty_label="Select Goat Tag",label="Goat Tag",widget=forms.Select(attrs={"class":"production-form-input"}))
    WEIGHT_CHOICES = [(str(round(i/10,1)),f"{round(i/10,1)} kg") for i in range(10,801)]
    weight = forms.ChoiceField(choices=WEIGHT_CHOICES,required=True,label="Goat Weight",widget=forms.RadioSelect(attrs={"class":"milk-quantity-radio"}))
    class Meta:
        model = GoatWeight
        fields = ["goat","weight"]
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["goat"].queryset = Goat.objects.none()
        if business:
            self.fields["goat"].queryset = Goat.objects.filter(business=business,live=True).order_by("token_no")

class GoatMilkForm(forms.ModelForm):
    QUANTITY_CHOICES = [("0.1","0.1 L"),("0.2","0.2 L"),("0.3","0.3 L"),("0.4","0.4 L"),("0.5","0.5 L"),("0.6","0.6 L"),("0.7","0.7 L"),("0.8","0.8 L"),("0.9","0.9 L"),("1.0","1.0 L"),("1.1","1.1 L"),("1.2","1.2 L"),("1.3","1.3 L"),("1.4","1.4 L"),("1.5","1.5 L"),("1.6","1.6 L"),("1.7","1.7 L"),("1.8","1.8 L"),("1.9","1.9 L"),("2.0","2.0 L")]
    milk_weight = forms.ChoiceField(choices=QUANTITY_CHOICES,required=True,widget=forms.RadioSelect(attrs={"class":"milk-quantity-radio"}))
    class Meta:
        model = GoatMilk
        fields = ["goat","milk_weight","date","time","note"]
        widgets = {
            "date": forms.DateInput(attrs={"type":"date","class":"production-form-input"}),
            "time": forms.Select(attrs={"class":"production-form-input"}),
            "note": forms.Textarea(attrs={"class":"production-form-input","rows":3,"placeholder":"Optional note..."}),
        }
    def __init__(self,*args,business=None,voice=False,**kwargs):
        super().__init__(*args,**kwargs)
        if voice:
            self.fields["date"].required = False
            self.fields["time"].required = False
            self.fields["note"].required = False
            self.fields.pop("date")
            self.fields.pop("time")
            self.fields.pop("note")

class GoatMilkVoiceForm(forms.Form):
    goat = forms.ModelChoiceField(queryset=Goat.objects.none(),empty_label="Select Goat Tag",label="Goat Tag",widget=forms.Select(attrs={"class":"production-form-input"}))
    QUANTITY_CHOICES = [("0.1","0.1 L"),("0.2","0.2 L"),("0.3","0.3 L"),("0.4","0.4 L"),("0.5","0.5 L"),("0.6","0.6 L"),("0.7","0.7 L"),("0.8","0.8 L"),("0.9","0.9 L"),("1.0","1.0 L"),("1.1","1.1 L"),("1.2","1.2 L"),("1.3","1.3 L"),("1.4","1.4 L"),("1.5","1.5 L"),("1.6","1.6 L"),("1.7","1.7 L"),("1.8","1.8 L"),("1.9","1.9 L"),("2.0","2.0 L")]
    milk_weight = forms.ChoiceField(choices=QUANTITY_CHOICES,required=True,widget=forms.RadioSelect(attrs={"class":"milk-quantity-radio"}))
    class Meta:
        model = GoatMilk
        fields = ["goat","milk_weight"]
    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business:
            self.fields["goat"].queryset = Goat.objects.filter(business=business,gender="FEMALE",live=True).order_by("token_no")

class GoatMilkBatchForm(forms.ModelForm):
    STATUS_CHOICES = [("pasteurized","Pasteurized"),("processing","Processing"),("packed","Packed"),("sold","Sold")]
    status = forms.ChoiceField(choices=STATUS_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    class Meta:
        model = GoatMilkBatch
        fields = ["date","qr_code","milk_time","milk_quantity","wastage","status","packed_date","exp_date",]
        widgets = {"date": forms.DateInput(attrs={"type":"date","class":"form-input",}),"qr_code": forms.TextInput(attrs={"class":"form-input","placeholder":"Enter or scan QR code","required":True,}),"milk_time": forms.Select(attrs={"class":"form-input",}),"milk_quantity": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"Enter milk quantity",}),"wastage": forms.NumberInput(attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"Enter wastage",}),"status": forms.TextInput(attrs={"class":"form-input","placeholder":"Enter status",}),"packed_date": forms.DateTimeInput(attrs={"type":"datetime-local","class":"form-input",}),"exp_date": forms.DateTimeInput(attrs={"type":"datetime-local","class":"form-input",}),}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields["qr_code"].required = True
    def clean_milk_quantity(self):
        value = self.cleaned_data["milk_quantity"]
        if value <= 0: raise ValidationError("Milk quantity must be greater than zero.")
        return value
    def clean_wastage(self):
        value = self.cleaned_data["wastage"]
        if value < 0: raise ValidationError("Wastage cannot be negative.")
        return value
    def clean_qr_code(self):
        value = self.cleaned_data.get("qr_code")
        if not value: raise ValidationError("QR code is required.")
        return value.strip()
        return value

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
    PRODUCT_TYPE_CHOICES = [("goat_milk","Goat Milk"),("cheese","Cheese"),("gelato","Gelato"),("yogurt","Yogurt"),("kefir","Kefir"),("milkshake","Milkshake"),("ghee","Ghee"),]
    VARIANT_CHOICES = [("plain","Plain"),("vanilla","Vanilla"),("chocolate","Chocolate"),("strawberry","Strawberry"),("mango","Mango"),("pistachio","Pistachio"),("coffee","Coffee"),("tender_coconut","Tender Coconut"),("blueberry","Blueberry"),("mixed_berry","Mixed Berry"),("rose","Rose"),("kulfi","Kulfi"),("butterscotch","Butterscotch"),("caramel","Caramel"),("salted_caramel","Salted Caramel"),("banana","Banana"),("natural","Natural"),("other","Other"),]
    STORAGE_TYPE_CHOICES = [("refrigerated","Refrigerated"),("ambient","Ambient"),("frozen","Frozen"),("deep_frozen","Deep Frozen"),("dry_storage","Dry Storage"),("cool_storage","Cool Storage"),]
    LIFE_SPAN_UNIT_CHOICES = [("days","Days"),("week","Week"),("month","Month"),]
    type = forms.ChoiceField(choices=PRODUCT_TYPE_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    variant = forms.ChoiceField(choices=VARIANT_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    life_span_unit = forms.ChoiceField(choices=LIFE_SPAN_UNIT_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    storage_type = forms.ChoiceField(choices=STORAGE_TYPE_CHOICES,required=True,widget=forms.Select(attrs={"class":"form-input",}))
    class Meta:
        model = Product
        fields = ["goat_milk_batch","type","variant","storage_type","storage_temp_min","storage_temp_max","status","description","life_span_value","life_span_unit",]
        widgets = {
            "goat_milk_batch": forms.Select(attrs={"class":"form-input"}),
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
        self.fields["life_span_value"].required = True 
        self.fields["goat_milk_batch"].queryset = GoatMilkBatch.objects.filter(
            business=business
        ).order_by("-date","-created_at")
    def clean(self):
        cleaned = super().clean()
        min_temp = cleaned.get("storage_temp_min")
        max_temp = cleaned.get("storage_temp_max")
        life_value = cleaned.get("life_span_value")
        life_unit = cleaned.get("life_span_unit")
        if min_temp is not None and max_temp is not None and min_temp > max_temp:
            self.add_error("storage_temp_max","Maximum temperature must be greater than or equal to minimum temperature.")
        if life_value is not None and life_value <= 0:
            self.add_error("life_span_value","Life span must be greater than zero.")
        if life_value and not life_unit:
            self.add_error("life_span_unit","Life span unit is required.")
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
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["product"].queryset = Product.objects.filter(
            business=business
        ).order_by("type","code_sku")
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
            "date": forms.DateInput(attrs={    "type":"date",    "class":"form-input",}),
            "product": forms.Select(attrs={    "class":"form-input",}),
            "procedure": forms.Textarea(attrs={    "class":"form-input",    "placeholder":"Enter recipe preparation procedure",    "rows":6,}),
            "status": forms.Select(attrs={    "class":"form-input",}),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["product"].queryset = Product.objects.filter(
            business=business
        ).order_by("type","code_sku")
        self.fields["date"].required = True
        self.fields["product"].required = True
        self.fields["procedure"].required = True
        self.fields["status"].required = True

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
    class Meta:
        model = ProductBatch
        fields = ["goat_milk_batch","product","recipe","location","quantity","unit","date","time","cost","qr_code","notes","qc_status","status","wastage",]
        widgets = {
            "goat_milk_batch": forms.Select( attrs={     "class":"form-input", }),
            "product": forms.Select( attrs={     "class":"form-input", }),
            "recipe": forms.Select( attrs={     "class":"form-input", }),
            "location": forms.Select( attrs={     "class":"form-input", }),
            "quantity": forms.NumberInput( attrs={     "class":"form-input",     "step":"0.001",     "min":"0",     "placeholder":"Enter quantity", }),
            "date": forms.DateInput( attrs={     "type":"date",     "class":"form-input", }),
            "time": forms.TimeInput( attrs={     "type":"time",     "class":"form-input", }),
            "cost": forms.NumberInput( attrs={     "class":"form-input",     "step":"0.01",     "min":"0",     "placeholder":"Enter production cost", }),
            "qr_code": forms.TextInput( attrs={     "class":"form-input",     "placeholder":"Enter or scan QR code", }),
            "notes": forms.Textarea( attrs={     "class":"form-input",     "placeholder":"Enter notes",     "rows":4, }),
            "qc_status": forms.Select( attrs={     "class":"form-input", }),
            "status": forms.Select( attrs={     "class":"form-input", }),
            "wastage": forms.NumberInput( attrs={     "class":"form-input",     "step":"0.001",     "min":"0",     "placeholder":"Enter wastage", }),
        }
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["goat_milk_batch"].queryset = GoatMilkBatch.objects.filter(business=business).order_by("-date","-created_at")
        self.fields["product"].queryset = Product.objects.filter(business=business).order_by("type","code_sku")
        self.fields["recipe"].queryset = Recipe.objects.filter(business=business).select_related("product").order_by("-date","-created_at")
        self.fields["location"].queryset = Location.objects.filter(business=business).order_by("name")
        self.fields["goat_milk_batch"].required = False
        self.fields["product"].required = True
        self.fields["recipe"].required = False
        self.fields["location"].required = False
        self.fields["quantity"].required = True
        self.fields["unit"].required = True
        self.fields["date"].required = True
        self.fields["time"].required = False
        self.fields["cost"].required = True
        self.fields["qr_code"].required = True
        self.fields["notes"].required = False
        self.fields["qc_status"].required = True
        self.fields["status"].required = True
        self.fields["wastage"].required = True
    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        recipe = cleaned.get("recipe")
        goat_milk_batch = cleaned.get("goat_milk_batch")
        location = cleaned.get("location")
        quantity = cleaned.get("quantity")
        cost = cleaned.get("cost")
        wastage = cleaned.get("wastage")
        if recipe and product and recipe.product_id != product.id:
            self.add_error(
                "recipe",
                "Selected recipe does not belong to the selected product."
            )
        if goat_milk_batch and product and goat_milk_batch.business_id != product.business_id:
            self.add_error(
                "goat_milk_batch",
                "Milk batch and product must belong to the same business."
            )
        if location and location.business_id != product.business_id:
            self.add_error(
                "location",
                "Location must belong to the same business."
            )
        if quantity is not None and quantity <= 0:
            self.add_error(
                "quantity",
                "Quantity must be greater than zero."
            )
        if cost is not None and cost < 0:
            self.add_error(
                "cost",
                "Cost cannot be negative."
            )
        if wastage is not None and wastage < 0:
            self.add_error(
                "wastage",
                "Wastage cannot be negative."
            )
        return cleaned