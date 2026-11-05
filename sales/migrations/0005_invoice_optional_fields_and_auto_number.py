from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0004_remove_customer_comment_remove_customer_ratings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoice",
            name="number",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="invoices",
                to="sales.customer",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="payment_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("pending", "Pending"),
                    ("paid", "Paid"),
                    ("partial", "Partially Paid"),
                    ("cancelled", "Cancelled"),
                ],
                default="",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="payment_method",
            field=models.CharField(
                blank=True,
                choices=[
                    ("cash", "Cash"),
                    ("upi", "UPI"),
                    ("card", "Card"),
                    ("bank_transfer", "Bank Transfer"),
                    ("credit", "Credit"),
                ],
                default="",
                max_length=100,
            ),
        ),
    ]
