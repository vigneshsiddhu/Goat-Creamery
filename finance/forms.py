from django import forms
from .models import Employee,EmployeeSalary,FarmSpendBook,FarmSpendItem,FarmExpense,BusinessSpendBook,BusinessSpendItem,BusinessExpense

class EmployeeForm(forms.ModelForm):
    DEPARTMENT_CHOICES = [("farm_operations","Farm Operations"),("animal_care","Animal Care"),("milking","Milking"),("feeding","Feeding"),("fodder","Fodder"),("production","Production"),("quality_control","Quality Control"),("packaging","Packaging"),("sales","Sales"),("delivery","Delivery"),("finance","Finance"),("hr","Human Resources"),("administration","Administration"),("maintenance","Maintenance"),("other","Other"),]
    department = forms.ChoiceField(choices=[("","Select Department")] + DEPARTMENT_CHOICES,required=False,widget=forms.Select(attrs={"class":"form-input",} ) )
    class Meta:
        model = Employee
        fields = ["name","employee_type","department","designation","phone","joining_date","monthly_salary","active","note",]
        widgets = {"name": forms.TextInput(   attrs={"class":"form-input","placeholder":"Enter employee name",      }  ),"employee_type": forms.Select(  attrs={"class":"form-input",      }  ),"designation": forms.TextInput(  attrs={"class":"form-input","placeholder":"Enter designation",      }  ),"phone": forms.TextInput(  attrs={"class":"form-input","placeholder":"Enter phone number",      }  ),"joining_date": forms.DateInput(  attrs={"class":"form-input","type":"date",      }  ),"monthly_salary": forms.NumberInput(  attrs={"class":"form-input","step":"0.01","min":"0","placeholder":"Enter monthly salary",      }  ),"active": forms.CheckboxInput(  attrs={"class":"form-check-input",      }  ),"note": forms.Textarea(  attrs={"class":"form-input","placeholder":"Enter employee notes",          "rows":4,}),}
    def __init__(self,*args,**kwargs):
        business = kwargs.pop("business",None)
        super().__init__(*args,**kwargs)
        self.fields["name"].required = True
        self.fields["employee_type"].required = True
        self.fields["department"].required = True
        self.fields["designation"].required = True
        self.fields["phone"].required = False
        self.fields["joining_date"].required = True
        self.fields["monthly_salary"].required = True
        self.fields["active"].required = True
        self.fields["note"].required = False
    def clean_name(self):
        value = self.cleaned_data.get("name")
        if not value:
            raise forms.ValidationError("Employee name is required.")
        return value.strip()
    def clean_monthly_salary(self):
        value = self.cleaned_data.get("monthly_salary")
        if value is not None and value < 0:
            raise forms.ValidationError("Monthly salary cannot be negative.")
        return value

class EmployeeSalaryForm(forms.ModelForm):
    class Meta:
        model = EmployeeSalary
        fields = ["employee","year","month","basic_salary","overtime","bonus","allowance","deduction","advance","payment_status","payment_date","note"]
        widgets = {
            "employee": forms.Select(attrs={"class":"form-select"}),
            "year": forms.NumberInput(attrs={"class":"form-control"}),
            "month": forms.NumberInput(attrs={"class":"form-control","min":1,"max":12}),
            "basic_salary": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "overtime": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "bonus": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "allowance": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "deduction": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "advance": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "payment_status": forms.Select(attrs={"class":"form-select"}),
            "payment_date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "note": forms.Textarea(attrs={"class":"form-control","rows":3}),
        }

    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business:
            self.fields["employee"].queryset = Employee.objects.filter(business=business,active=True).order_by("name")
        else:
            self.fields["employee"].queryset = Employee.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get("year")
        month = cleaned_data.get("month")
        if year and year < 2000:
            self.add_error("year","Enter a valid year.")
        if month and not 1 <= month <= 12:
            self.add_error("month","Month must be between 1 and 12.")
        return cleaned_data

class FarmSpendBookForm(forms.ModelForm):
    class Meta:
        model = FarmSpendBook
        fields = ["year","month","status"]
        widgets = {
            "year": forms.NumberInput(attrs={"class":"form-control"}),
            "month": forms.NumberInput(attrs={"class":"form-control","min":1,"max":12}),
            "status": forms.Select(attrs={"class":"form-select"}),
        }

class FarmSpendItemForm(forms.ModelForm):
    class Meta:
        model = FarmSpendItem
        fields = ["category","description","employee_salary","forecast_amount","approved_amount","actual_amount","status","note"]
        widgets = {
            "category": forms.TextInput(attrs={"class":"form-control","placeholder":"Category"}),
            "description": forms.TextInput(attrs={"class":"form-control","placeholder":"Description"}),
            "employee_salary": forms.Select(attrs={"class":"form-select"}),
            "forecast_amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "approved_amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "actual_amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "status": forms.TextInput(attrs={"class":"form-control","placeholder":"Planned / Approved / Spent"}),
            "note": forms.Textarea(attrs={"class":"form-control","rows":3}),
        }

    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business:
            self.fields["employee_salary"].queryset = EmployeeSalary.objects.filter(employee__business=business).select_related("employee").order_by("-year","-month")
        else:
            self.fields["employee_salary"].queryset = EmployeeSalary.objects.none()

class FarmExpenseForm(forms.ModelForm):
    class Meta:
        model = FarmExpense
        fields = ["date","category","employee","amount","comment"]
        widgets = {
            "date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "category": forms.TextInput(attrs={"class":"form-control","placeholder":"Expense Category"}),
            "employee": forms.Select(attrs={"class":"form-select"}),
            "amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "comment": forms.Textarea(attrs={"class":"form-control","rows":3}),
        }

    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business:
            self.fields["employee"].queryset = Employee.objects.filter(business=business,active=True).order_by("name")
        else:
            self.fields["employee"].queryset = Employee.objects.none()

class BusinessSpendBookForm(forms.ModelForm):
    class Meta:
        model = BusinessSpendBook
        fields = ["year","month","status"]
        widgets = {
            "year": forms.NumberInput(attrs={"class":"form-control"}),
            "month": forms.NumberInput(attrs={"class":"form-control","min":1,"max":12}),
            "status": forms.Select(attrs={"class":"form-select"}),
        }

class BusinessSpendItemForm(forms.ModelForm):
    class Meta:
        model = BusinessSpendItem
        fields = ["category","description","employee_salary","forecast_amount","approved_amount","actual_amount","status","note"]
        widgets = {
            "category": forms.TextInput(attrs={"class":"form-control","placeholder":"Category"}),
            "description": forms.TextInput(attrs={"class":"form-control","placeholder":"Description"}),
            "employee_salary": forms.Select(attrs={"class":"form-select"}),
            "forecast_amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "approved_amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "actual_amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "status": forms.Select(attrs={"class":"form-select"}),
            "note": forms.Textarea(attrs={"class":"form-control","rows":3}),
        }

    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business:
            self.fields["employee_salary"].queryset = EmployeeSalary.objects.filter(employee__business=business).select_related("employee").order_by("-year","-month")
        else:
            self.fields["employee_salary"].queryset = EmployeeSalary.objects.none()

class BusinessExpenseForm(forms.ModelForm):
    class Meta:
        model = BusinessExpense
        fields = ["date","category","amount","comment","payment_method","employee","spend_item"]
        widgets = {
            "date": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "category": forms.TextInput(attrs={"class":"form-control","placeholder":"Expense Category"}),
            "amount": forms.NumberInput(attrs={"class":"form-control","step":"0.01"}),
            "comment": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "payment_method": forms.Select(attrs={"class":"form-select"}),
            "employee": forms.Select(attrs={"class":"form-select"}),
            "spend_item": forms.Select(attrs={"class":"form-select"}),
        }

    def __init__(self,*args,business=None,**kwargs):
        super().__init__(*args,**kwargs)
        if business:
            self.fields["employee"].queryset = Employee.objects.filter(business=business,active=True).order_by("name")
            self.fields["spend_item"].queryset = BusinessSpendItem.objects.filter(spend_book__business=business).select_related("spend_book").order_by("-spend_book__year","-spend_book__month")
        else:
            self.fields["employee"].queryset = Employee.objects.none()
            self.fields["spend_item"].queryset = BusinessSpendItem.objects.none()

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount