from django import forms
from django.contrib.auth import get_user_model

from .models import Business, BusinessUser


User = get_user_model()


# =========================================================
# BUSINESS FORM
# =========================================================

class BusinessForm(forms.ModelForm):

    class Meta:

        model = Business

        fields = [
            "name",
            "address",
            "gstn",
            "phone_number",
            "owner",
            "status",
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # -------------------------------------------------
        # OWNER
        # -------------------------------------------------

        self.fields["owner"].queryset = (
            User.objects
            .filter(is_active=True)
            .order_by("username")
        )

        self.fields["owner"].widget.attrs.update({
            "class": "form-select"
        })

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        self.fields["name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter business name",
        })

        # -------------------------------------------------
        # ADDRESS
        # -------------------------------------------------

        self.fields["address"].widget.attrs.update({
            "class": "form-control",
            "rows": 3,
            "placeholder": "Enter business address",
        })

        # -------------------------------------------------
        # GSTN
        # -------------------------------------------------

        self.fields["gstn"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter GSTIN",
        })

        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------

        self.fields["phone_number"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter phone number",
        })

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.fields["status"].widget.attrs.update({
            "class": "form-select"
        })


# =========================================================
# BUSINESS USER FORM
# =========================================================

class BusinessUserForm(forms.ModelForm):

    class Meta:

        model = BusinessUser

        fields = [
            "user",
            "business",
            "role",
            "is_active",
        ]

        widgets = {

            # -------------------------------------------------
            # USER
            # -------------------------------------------------

            "user": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            # -------------------------------------------------
            # BUSINESS
            # -------------------------------------------------

            "business": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            # -------------------------------------------------
            # ROLE
            # -------------------------------------------------

            "role": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            # -------------------------------------------------
            # ACTIVE STATUS
            # -------------------------------------------------

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }

    def __init__(
        self,
        *args,
        business=None,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        # -------------------------------------------------
        # ACTIVE USERS ONLY
        # -------------------------------------------------

        self.fields["user"].queryset = (
            User.objects
            .filter(is_active=True)
            .order_by("username")
        )

        # -------------------------------------------------
        # BUSINESS
        # -------------------------------------------------

        if business:

            # Only the logged-in user's business
            self.fields["business"].queryset = (
                Business.objects.filter(
                    pk=business.pk
                )
            )

            # Automatically select current business
            self.fields["business"].initial = business

            # Do not allow changing business
            self.fields["business"].disabled = True

        else:

            self.fields["business"].queryset = (
                Business.objects
                .all()
                .order_by("name")
            )

        # -------------------------------------------------
        # ROLE
        # -------------------------------------------------

        self.fields["role"].choices = [
            ("", "Select Business Role"),
            ("ADMIN", "Admin"),
            ("FARM_MANAGER", "Farm Manager"),
            ("SALES_PERSON", "Sales Person"),
        ]