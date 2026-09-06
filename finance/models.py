import uuid
from django.conf import settings
from django.db import models
from business.models import Business

# ============================================================
# EMPLOYEE
# ============================================================
class Employee(models.Model):
    EMPLOYEE_TYPE_CHOICES = [("farm", "Farm"),("business", "Business"),]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="employees")
    employee_code = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPE_CHOICES)
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_employees")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
        constraints = [ models.UniqueConstraint(fields=["business","employee_code"],name="unique_employee_code_per_business")]
    def save(self,*args,**kwargs):
        if not self.employee_code:
            prefix = "EMP"
            last_employee = (Employee.objects.filter(business=self.business,employee_code__startswith=f"{prefix}-").order_by("-employee_code").first())
            if last_employee:
                last_number = int(last_employee.employee_code.split("-")[-1])
                next_number = last_number + 1
            else:
                next_number = 1
            self.employee_code = f"{prefix}-{next_number:03d}"
        super().save(*args,**kwargs)
    def __str__(self):
        return f"{self.employee_code} - {self.name}"


# ============================================================
# EMPLOYEE SALARY
# ============================================================

class EmployeeSalary(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="salaries")
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField()
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    advance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="draft")
    payment_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_employee_salaries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "year", "month"],
                name="unique_employee_salary_month"
            )
        ]
    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year} - {self.net_salary}"


# ============================================================
# FARM SPEND BOOK
# ============================================================
class FarmSpendBook(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("closed", "Closed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="farm_spend_books")
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    total_forecast = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_approved = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_actual = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_farm_spend_books")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_farm_spend_books")
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "year", "month"],
                name="unique_farm_spend_book_month"
            )
        ]
    def __str__(self):
        return f"Farm - {self.month}/{self.year}"


# ============================================================
# FARM SPEND ITEM
# ============================================================
class FarmSpendItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spend_book = models.ForeignKey(FarmSpendBook, on_delete=models.CASCADE, related_name="items")
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    employee_salary = models.ForeignKey(EmployeeSalary, on_delete=models.PROTECT, null=True, blank=True, related_name="farm_spend_items")
    forecast_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    approved_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=30)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.category} - {self.description}"
       
# ============================================================
# FARM EXPENSE
# ============================================================
class FarmExpense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    category = models.CharField(max_length=100)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True, related_name="farm_ƒemployee_salary")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_farm_expenses")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="farm_expenses")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date", "-created_at"]


# ============================================================
# BUSINESS SPEND BOOK
# ============================================================
class BusinessSpendBook(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("closed", "Closed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="business_spend_books")
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    total_forecast = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_approved = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_actual = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_business_spend_books")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_business_spend_books")
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "year", "month"],
                name="unique_business_spend_book_month"
            )
        ]
    def __str__(self):
        return f"Business - {self.month}/{self.year}"


# ============================================================
# BUSINESS SPEND ITEM
# ============================================================

class BusinessSpendItem(models.Model):
    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("approved", "Approved"),
        ("partially_spent", "Partially Spent"),
        ("spent", "Spent"),
        ("cancelled", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spend_book = models.ForeignKey(BusinessSpendBook, on_delete=models.CASCADE, related_name="items")
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    employee_salary = models.ForeignKey(EmployeeSalary, on_delete=models.PROTECT, null=True, blank=True, related_name="business_spend_items")
    forecast_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    approved_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="planned")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.category} - {self.description}"


# ============================================================
# BUSINESS EXPENSE
# ============================================================

class BusinessExpense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("upi", "UPI"),
        ("card", "Card"),
        ("credit", "Credit"),
        ("other", "Other"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cash")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True, related_name="business_employee_salary")
    spend_item = models.ForeignKey(BusinessSpendItem, on_delete=models.PROTECT, null=True, blank=True, related_name="actual_expenses")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_business_expenses")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="business_expenses")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-date", "-created_at"]
    def __str__(self):
        return f"{self.date} - {self.category} - {self.amount}"