from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render

from myfarm.permissions import permission_required
from django.db import transaction
from .forms import CustomerForm,InvoiceForm,InvoiceItemForm,InvoiceLocationForm,InvoiceItemFormSet
from .models import Customer,Invoice,InvoiceItem,InvoiceLocation
from .utils import save_created_by


# ============================================================
# CUSTOMER
# ============================================================

@permission_required("customer.view")
def customer_list(request):
    business = request.business
    customers = Customer.objects.filter(business=business).order_by("name")
    return render(
        request,"customer/customer_list.html",{"customers": customers,"business": business,"business_user": request.business_user,}, )


@permission_required("customer.create")
def customer_create(request):
    business = request.business

    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save(commit=False)
            customer.business = business
            customer.created_by = request.business_user.user
            customer.save()

            messages.success(request,"Customer created successfully.")
            return redirect("sales:customer_list")
    else:
        form = CustomerForm()

    return render(
        request,
        "customer/customer_form.html",
        {"form":form,"title":"Create Customer"}
    )


@permission_required("customer.update")
def customer_edit(request,pk):
    business = request.business

    customer = get_object_or_404(
        Customer,
        pk=pk,
        business=business
    )

    if request.method == "POST":
        form = CustomerForm(
            request.POST,
            instance=customer
        )

        if form.is_valid():
            form.save()

            messages.success(request,"Customer updated successfully.")
            return redirect("sales:customer_list")
    else:
        form = CustomerForm(instance=customer)

    return render(
        request,
        "customer/customer_form.html",
        {
            "form":form,
            "title":"Edit Customer",
            "customer":customer
        }
    )


@permission_required("customer.delete")
def customer_delete(request,pk):
    business = request.business

    customer = get_object_or_404(
        Customer,
        pk=pk,
        business=business
    )

    if request.method == "POST":
        customer.delete()

        messages.success(request,"Customer deleted successfully.")
        return redirect("sales:customer_list")

    return render(
        request,
        "customer/customer_confirm_delete.html",
        {"customer":customer}
    )


# ============================================================
# INVOICE
# ============================================================

@permission_required("invoice.view")
def invoice_list(request):
    business=request.business
    invoices=Invoice.objects.filter(business=business).select_related("customer").prefetch_related("items").order_by("-date","-created_at")
    return render(request,"invoice/invoice_list.html",{"invoices":invoices,"business":business,"business_user":request.business_user})

@permission_required("invoice.create")
def invoice_create(request):
    business=request.business
    if request.method=="POST":
        form=InvoiceForm(request.POST,business=business)
        formset=InvoiceItemFormSet(request.POST,form_kwargs={"business":business})
      
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice=form.save(commit=False)
                invoice.business=business
                invoice.sub_total=Decimal("0")
                invoice.grand_total=Decimal("0")
                save_created_by(invoice,request)
                invoice.save()
                formset.instance=invoice
                items=formset.save(commit=False)
                sub_total=Decimal("0")
                for item in items:
                    item.invoice=invoice
                    item.business=business
                    item.total=(item.quantity*item.price)-item.discount
                    if item.total<0:
                        item.total=Decimal("0")
                    sub_total+=item.total
                    save_created_by(item,request)
                    item.save()
                invoice.sub_total=sub_total
                invoice.grand_total=sub_total-invoice.discount+invoice.gst
                if invoice.grand_total<0:
                    invoice.grand_total=Decimal("0")
                invoice.save(update_fields=["sub_total","grand_total","updated_at"])
            messages.success(request,"Invoice created successfully.")
            return redirect("sales:invoice_list")
    else:
        form=InvoiceForm(business=business)
        formset=InvoiceItemFormSet(form_kwargs={"business":business})
    return render(request,"invoice/invoice_form.html",{"form":form,"formset":formset,"title":"Create Invoice"})

@permission_required("invoice.update")
def invoice_edit(request,pk):
    business=request.business
    invoice=get_object_or_404(Invoice.objects.prefetch_related("items"),pk=pk,business=business)
    if request.method=="POST":
        form=InvoiceForm(request.POST,instance=invoice,business=business)
        formset=InvoiceItemFormSet(request.POST,instance=invoice,form_kwargs={"business":business})
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice=form.save(commit=False)
                invoice.business=business
                formset.instance=invoice
                items=formset.save(commit=False)
                sub_total=Decimal("0")
                for item in items:
                    item.invoice=invoice
                    item.business=business
                    item.total=(item.quantity*item.price)-item.discount
                    if item.total<0:
                        item.total=Decimal("0")
                    sub_total+=item.total
                    item.save()
                for deleted_item in formset.deleted_objects:
                    deleted_item.delete()
                invoice.sub_total=sub_total
                invoice.grand_total=sub_total-invoice.discount+invoice.gst
                if invoice.grand_total<0:
                    invoice.grand_total=Decimal("0")
                invoice.save()
            messages.success(request,"Invoice updated successfully.")
            return redirect("sales:invoice_list")
    else:
        form=InvoiceForm(instance=invoice,business=business)
        formset=InvoiceItemFormSet(instance=invoice,form_kwargs={"business":business})
    return render(request,"invoice/invoice_form.html",{"form":form,"formset":formset,"title":"Edit Invoice","invoice":invoice})

@permission_required("invoice.delete")
def invoice_delete(request,pk):
    invoice=get_object_or_404(Invoice,pk=pk,business=request.business)
    if request.method=="POST":
        invoice.delete()
        messages.success(request,"Invoice deleted successfully.")
        return redirect("sales:invoice_list")
    return render(request,"invoice/confirm_delete.html",{"object":invoice})

# ============================================================
# INVOICE LOCATION
# ============================================================
@permission_required("invoice_location.view")
def invoice_location_list(request):
    business = request.business

    invoice_locations = InvoiceLocation.objects.filter(
        business=business
    ).select_related(
        "invoice",
        "vehicle",
        "location"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "sales/invoice_location_list.html",
        {"invoice_locations":invoice_locations}
    )


@permission_required("invoice_location.create")
def invoice_location_create(request):
    business = request.business

    invoice_id = request.GET.get("invoice")

    invoice = None

    if invoice_id:
        invoice = get_object_or_404(
            Invoice,
            pk=invoice_id,
            business=business
        )

    if request.method == "POST":
        invoice_id = request.POST.get("invoice")

        invoice = get_object_or_404(
            Invoice,
            pk=invoice_id,
            business=business
        )

        form = InvoiceLocationForm(
            request.POST,
            business=business,
            invoice=invoice
        )

        if form.is_valid():
            invoice_location = form.save(commit=False)
            invoice_location.invoice = invoice
            invoice_location.business = business
            invoice_location.created_by = request.business_user
            invoice_location.save()

            messages.success(request,"Invoice location created successfully.")
            return redirect("sales:invoice_location_list")
    else:
        form = InvoiceLocationForm(
            business=business,
            invoice=invoice
        )

    return render(
        request,
        "sales/invoice_location_form.html",
        {
            "form":form,
            "title":"Create Invoice Location",
            "invoice":invoice
        }
    )


@permission_required("invoice_location.update")
def invoice_location_edit(request,pk):
    business = request.business

    invoice_location = get_object_or_404(
        InvoiceLocation,
        pk=pk,
        business=business
    )

    invoice = invoice_location.invoice

    if request.method == "POST":
        form = InvoiceLocationForm(
            request.POST,
            instance=invoice_location,
            business=business,
            invoice=invoice
        )

        if form.is_valid():
            form.save()

            messages.success(request,"Invoice location updated successfully.")
            return redirect("sales:invoice_location_list")
    else:
        form = InvoiceLocationForm(
            instance=invoice_location,
            business=business,
            invoice=invoice
        )

    return render(
        request,
        "sales/invoice_location_form.html",
        {
            "form":form,
            "title":"Edit Invoice Location",
            "invoice_location":invoice_location,
            "invoice":invoice
        }
    )


@permission_required("invoice_location.delete")
def invoice_location_delete(request,pk):
    business = request.business

    invoice_location = get_object_or_404(
        InvoiceLocation,
        pk=pk,
        business=business
    )

    if request.method == "POST":
        invoice_location.delete()

        messages.success(request,"Invoice location deleted successfully.")
        return redirect("sales:invoice_location_list")

    return render(
        request,
        "sales/invoice_location_confirm_delete.html",
        {"invoice_location":invoice_location}
    )


# ============================================================
# INVOICE TOTAL CALCULATION
# ============================================================

def update_invoice_totals(invoice):
    items = invoice.items.all()

    sub_total = Decimal("0")
    gst = Decimal("0")

    for item in items:
        quantity = item.quantity or Decimal("0")
        price = item.price or Decimal("0")
        discount = item.discount or Decimal("0")
        item_gst = item.gst or Decimal("0")

        sub_total += (
            quantity * price
        ) - discount

        gst += item_gst

    discount = invoice.discount or Decimal("0")

    grand_total = sub_total - discount + gst

    invoice.sub_total = sub_total
    invoice.gst = gst
    invoice.grand_total = grand_total

    invoice.save(
        update_fields=[
            "sub_total",
            "gst",
            "grand_total",
            "updated_at"
        ]
    )