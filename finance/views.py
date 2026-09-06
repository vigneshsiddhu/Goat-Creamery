from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render
from myfarm.permissions import permission_required
from .models import Employee,EmployeeSalary,FarmSpendBook,FarmSpendItem,FarmExpense,BusinessSpendBook,BusinessSpendItem,BusinessExpense
from .forms import EmployeeForm,EmployeeSalaryForm,FarmSpendBookForm,FarmSpendItemForm,FarmExpenseForm,BusinessSpendBookForm,BusinessSpendItemForm,BusinessExpenseForm

@permission_required("employee.view")
def employee_list(request):
    business = request.business
    employees = Employee.objects.filter(business=business).order_by("-created_at")
    return render(request,"employee/employee_list.html",{"objects":employees,"business":business,"business_user":request.business_user})

@permission_required("employee.create")
def employee_create(request):
    business = request.business
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.business = business
            employee.created_by = request.user
            employee.save()
            messages.success(request,f"{employee.name} created successfully.")
            return redirect("finance:employee_list")
    else:
        form = EmployeeForm()
    return render(request,"employee/employee_form.html",{"form":form,"employee":None,"business":business})

@permission_required("employee.update")
def employee_edit(request,pk):
    business = request.business
    employee = get_object_or_404(Employee,pk=pk,business=business)
    if request.method == "POST":
        form = EmployeeForm(request.POST,instance=employee)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.business = business
            updated.created_by = employee.created_by
            updated.save()
            messages.success(request,"Employee updated successfully.")
            return redirect("finance:employee_list")
    else:
        form = EmployeeForm(instance=employee)
    return render(request,"employee/employee_form.html",{"form":form,"employee":employee,"business":business})

@permission_required("employee.delete")
def employee_delete(request,pk):
    business = request.business
    employee = get_object_or_404(Employee,pk=pk,business=business)
    if request.method == "POST":
        employee.delete()
        messages.success(request,"Employee deleted successfully.")
        return redirect("finance:employee_list")
    return render(request,"employee/employee_delete.html",{"employee":employee,"business":business})

@permission_required("employee_salary.view")
def employee_salary_list(request):
    business = request.business
    salaries = EmployeeSalary.objects.filter(employee__business=business).select_related("employee").order_by("-year","-month")
    return render(request,"finance/employee_salary_list.html",{"salaries":salaries,"business":business,"business_user":request.business_user})

@permission_required("employee_salary.create")
def employee_salary_create(request):
    business = request.business
    if request.method == "POST":
        form = EmployeeSalaryForm(request.POST,business=business)
        if form.is_valid():
            salary = form.save(commit=False)
            salary.created_by = request.user
            salary.net_salary = salary.basic_salary + salary.overtime + salary.bonus + salary.allowance - salary.deduction - salary.advance
            salary.save()
            messages.success(request,"Employee salary created successfully.")
            return redirect("finance:employee_salary_list")
    else:
        form = EmployeeSalaryForm(business=business)
    return render(request,"finance/employee_salary_form.html",{"form":form,"salary":None,"business":business})

@permission_required("employee_salary.update")
def employee_salary_edit(request,pk):
    business = request.business
    salary = get_object_or_404(EmployeeSalary,pk=pk,employee__business=business)
    if request.method == "POST":
        form = EmployeeSalaryForm(request.POST,instance=salary,business=business)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.created_by = salary.created_by
            updated.net_salary = updated.basic_salary + updated.overtime + updated.bonus + updated.allowance - updated.deduction - updated.advance
            updated.save()
            messages.success(request,"Employee salary updated successfully.")
            return redirect("finance:employee_salary_list")
    else:
        form = EmployeeSalaryForm(instance=salary,business=business)
    return render(request,"finance/employee_salary_form.html",{"form":form,"salary":salary,"business":business})

@permission_required("employee_salary.delete")
def employee_salary_delete(request,pk):
    business = request.business
    salary = get_object_or_404(EmployeeSalary,pk=pk,employee__business=business)
    if request.method == "POST":
        salary.delete()
        messages.success(request,"Employee salary deleted successfully.")
        return redirect("finance:employee_salary_list")
    return render(request,"finance/employee_salary_delete.html",{"salary":salary,"business":business})

@permission_required("farm_spend_book.view")
def farm_spend_book_list(request):
    business = request.business
    books = FarmSpendBook.objects.filter(business=business)
    return render(request,"finance/farm_spend_book_list.html",{"books":books,"business":business,"business_user":request.business_user})

@permission_required("farm_spend_book.create")
def farm_spend_book_create(request):
    business = request.business
    if request.method == "POST":
        form = FarmSpendBookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.business = business
            book.created_by = request.user
            book.save()
            messages.success(request,"Farm spend book created successfully.")
            return redirect("finance:farm_spend_book_list")
    else:
        form = FarmSpendBookForm()
    return render(request,"finance/farm_spend_book_form.html",{"form":form,"book":None,"business":business})

@permission_required("farm_spend_book.update")
def farm_spend_book_edit(request,pk):
    business = request.business
    book = get_object_or_404(FarmSpendBook,pk=pk,business=business)
    if request.method == "POST":
        form = FarmSpendBookForm(request.POST,instance=book)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.business = business
            updated.created_by = book.created_by
            updated.save()
            messages.success(request,"Farm spend book updated successfully.")
            return redirect("finance:farm_spend_book_list")
    else:
        form = FarmSpendBookForm(instance=book)
    return render(request,"finance/farm_spend_book_form.html",{"form":form,"book":book,"business":business})

@permission_required("farm_spend_book.delete")
def farm_spend_book_delete(request,pk):
    business = request.business
    book = get_object_or_404(FarmSpendBook,pk=pk,business=business)
    if request.method == "POST":
        book.delete()
        messages.success(request,"Farm spend book deleted successfully.")
        return redirect("finance:farm_spend_book_list")
    return render(request,"finance/farm_spend_book_delete.html",{"book":book,"business":business})

@permission_required("farm_spend_item.view")
def farm_spend_item_list(request):
    business = request.business
    items = FarmSpendItem.objects.filter(spend_book__business=business).select_related("spend_book","employee_salary")
    return render(request,"finance/farm_spend_item_list.html",{"items":items,"business":business,"business_user":request.business_user})

@permission_required("farm_spend_item.create")
def farm_spend_item_create(request):
    business = request.business
    books = FarmSpendBook.objects.filter(business=business)
    if request.method == "POST":
        form = FarmSpendItemForm(request.POST,business=business)
        if form.is_valid():
            item = form.save(commit=False)
            item.spend_book = get_object_or_404(books,pk=request.POST.get("spend_book"))
            item.save()
            messages.success(request,"Farm spend item created successfully.")
            return redirect("finance:farm_spend_item_list")
    else:
        form = FarmSpendItemForm(business=business)
    return render(request,"finance/farm_spend_item_form.html",{"form":form,"item":None,"books":books,"business":business})

@permission_required("farm_spend_item.update")
def farm_spend_item_edit(request,pk):
    business = request.business
    item = get_object_or_404(FarmSpendItem,pk=pk,spend_book__business=business)
    books = FarmSpendBook.objects.filter(business=business)
    if request.method == "POST":
        form = FarmSpendItemForm(request.POST,instance=item,business=business)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.spend_book = get_object_or_404(books,pk=request.POST.get("spend_book"))
            updated.save()
            messages.success(request,"Farm spend item updated successfully.")
            return redirect("finance:farm_spend_item_list")
    else:
        form = FarmSpendItemForm(instance=item,business=business)
    return render(request,"finance/farm_spend_item_form.html",{"form":form,"item":item,"books":books,"business":business})

@permission_required("farm_spend_item.delete")
def farm_spend_item_delete(request,pk):
    business = request.business
    item = get_object_or_404(FarmSpendItem,pk=pk,spend_book__business=business)
    if request.method == "POST":
        item.delete()
        messages.success(request,"Farm spend item deleted successfully.")
        return redirect("finance:farm_spend_item_list")
    return render(request,"finance/farm_spend_item_delete.html",{"item":item,"business":business})

@permission_required("farm_expense.view")
def farm_expense_list(request):
    business = request.business
    expenses = FarmExpense.objects.filter(business=business).select_related("employee","created_by")
    return render(request,"finance/farm_expense_list.html",{"expenses":expenses,"business":business,"business_user":request.business_user})

@permission_required("farm_expense.create")
def farm_expense_create(request):
    business = request.business
    if request.method == "POST":
        form = FarmExpenseForm(request.POST,business=business)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.business = business
            expense.created_by = request.user
            expense.save()
            messages.success(request,"Farm expense created successfully.")
            return redirect("finance:farm_expense_list")
    else:
        form = FarmExpenseForm(business=business)
    return render(request,"finance/farm_expense_form.html",{"form":form,"expense":None,"business":business})

@permission_required("farm_expense.update")
def farm_expense_edit(request,pk):
    business = request.business
    expense = get_object_or_404(FarmExpense,pk=pk,business=business)
    if request.method == "POST":
        form = FarmExpenseForm(request.POST,instance=expense,business=business)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.business = business
            updated.created_by = expense.created_by
            updated.save()
            messages.success(request,"Farm expense updated successfully.")
            return redirect("finance:farm_expense_list")
    else:
        form = FarmExpenseForm(instance=expense,business=business)
    return render(request,"finance/farm_expense_form.html",{"form":form,"expense":expense,"business":business})

@permission_required("farm_expense.delete")
def farm_expense_delete(request,pk):
    business = request.business
    expense = get_object_or_404(FarmExpense,pk=pk,business=business)
    if request.method == "POST":
        expense.delete()
        messages.success(request,"Farm expense deleted successfully.")
        return redirect("finance:farm_expense_list")
    return render(request,"finance/farm_expense_delete.html",{"expense":expense,"business":business})

@permission_required("business_spend_book.view")
def business_spend_book_list(request):
    business = request.business
    books = BusinessSpendBook.objects.filter(business=business)
    return render(request,"finance/business_spend_book_list.html",{"books":books,"business":business,"business_user":request.business_user})

@permission_required("business_spend_book.create")
def business_spend_book_create(request):
    business = request.business
    if request.method == "POST":
        form = BusinessSpendBookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.business = business
            book.created_by = request.user
            book.save()
            messages.success(request,"Business spend book created successfully.")
            return redirect("finance:business_spend_book_list")
    else:
        form = BusinessSpendBookForm()
    return render(request,"finance/business_spend_book_form.html",{"form":form,"book":None,"business":business})

@permission_required("business_spend_book.update")
def business_spend_book_edit(request,pk):
    business = request.business
    book = get_object_or_404(BusinessSpendBook,pk=pk,business=business)
    if request.method == "POST":
        form = BusinessSpendBookForm(request.POST,instance=book)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.business = business
            updated.created_by = book.created_by
            updated.save()
            messages.success(request,"Business spend book updated successfully.")
            return redirect("finance:business_spend_book_list")
    else:
        form = BusinessSpendBookForm(instance=book)
    return render(request,"finance/business_spend_book_form.html",{"form":form,"book":book,"business":business})

@permission_required("business_spend_book.delete")
def business_spend_book_delete(request,pk):
    business = request.business
    book = get_object_or_404(BusinessSpendBook,pk=pk,business=business)
    if request.method == "POST":
        book.delete()
        messages.success(request,"Business spend book deleted successfully.")
        return redirect("finance:business_spend_book_list")
    return render(request,"finance/business_spend_book_delete.html",{"book":book,"business":business})

@permission_required("business_spend_item.view")
def business_spend_item_list(request):
    business = request.business
    items = BusinessSpendItem.objects.filter(spend_book__business=business).select_related("spend_book","employee_salary")
    return render(request,"finance/business_spend_item_list.html",{"items":items,"business":business,"business_user":request.business_user})

@permission_required("business_spend_item.create")
def business_spend_item_create(request):
    business = request.business
    books = BusinessSpendBook.objects.filter(business=business)
    if request.method == "POST":
        form = BusinessSpendItemForm(request.POST,business=business)
        if form.is_valid():
            item = form.save(commit=False)
            item.spend_book = get_object_or_404(books,pk=request.POST.get("spend_book"))
            item.save()
            messages.success(request,"Business spend item created successfully.")
            return redirect("finance:business_spend_item_list")
    else:
        form = BusinessSpendItemForm(business=business)
    return render(request,"finance/business_spend_item_form.html",{"form":form,"item":None,"books":books,"business":business})

@permission_required("business_spend_item.update")
def business_spend_item_edit(request,pk):
    business = request.business
    item = get_object_or_404(BusinessSpendItem,pk=pk,spend_book__business=business)
    books = BusinessSpendBook.objects.filter(business=business)
    if request.method == "POST":
        form = BusinessSpendItemForm(request.POST,instance=item,business=business)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.spend_book = get_object_or_404(books,pk=request.POST.get("spend_book"))
            updated.save()
            messages.success(request,"Business spend item updated successfully.")
            return redirect("finance:business_spend_item_list")
    else:
        form = BusinessSpendItemForm(instance=item,business=business)
    return render(request,"finance/business_spend_item_form.html",{"form":form,"item":item,"books":books,"business":business})

@permission_required("business_spend_item.delete")
def business_spend_item_delete(request,pk):
    business = request.business
    item = get_object_or_404(BusinessSpendItem,pk=pk,spend_book__business=business)
    if request.method == "POST":
        item.delete()
        messages.success(request,"Business spend item deleted successfully.")
        return redirect("finance:business_spend_item_list")
    return render(request,"finance/business_spend_item_delete.html",{"item":item,"business":business})

@permission_required("business_expense.view")
def business_expense_list(request):
    business = request.business
    expenses = BusinessExpense.objects.filter(business=business).select_related("employee","spend_item","created_by")
    return render(request,"finance/business_expense_list.html",{"expenses":expenses,"business":business,"business_user":request.business_user})

@permission_required("business_expense.create")
def business_expense_create(request):
    business = request.business
    if request.method == "POST":
        form = BusinessExpenseForm(request.POST,business=business)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.business = business
            expense.created_by = request.user
            expense.save()
            messages.success(request,"Business expense created successfully.")
            return redirect("finance:business_expense_list")
    else:
        form = BusinessExpenseForm(business=business)
    return render(request,"finance/business_expense_form.html",{"form":form,"expense":None,"business":business})

@permission_required("business_expense.update")
def business_expense_edit(request,pk):
    business = request.business
    expense = get_object_or_404(BusinessExpense,pk=pk,business=business)
    if request.method == "POST":
        form = BusinessExpenseForm(request.POST,instance=expense,business=business)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.business = business
            updated.created_by = expense.created_by
            updated.save()
            messages.success(request,"Business expense updated successfully.")
            return redirect("finance:business_expense_list")
    else:
        form = BusinessExpenseForm(instance=expense,business=business)
    return render(request,"finance/business_expense_form.html",{"form":form,"expense":expense,"business":business})

@permission_required("business_expense.delete")
def business_expense_delete(request,pk):
    business = request.business
    expense = get_object_or_404(BusinessExpense,pk=pk,business=business)
    if request.method == "POST":
        expense.delete()
        messages.success(request,"Business expense deleted successfully.")
        return redirect("finance:business_expense_list")
    return render(request,"finance/business_expense_delete.html",{"expense":expense,"business":business})