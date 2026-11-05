import uuid

import django.db.models.deletion
from django.db import migrations, models


def copy_existing_milk_links(apps, schema_editor):
    ProductBatch = apps.get_model("production", "ProductBatch")
    ProductBatchMilk = apps.get_model("production", "ProductBatchMilk")
    links = []
    for batch in ProductBatch.objects.exclude(goat_milk_batch_id=None).iterator():
        links.append(
            ProductBatchMilk(
                product_batch_id=batch.pk,
                goat_milk_batch_id=batch.goat_milk_batch_id,
            )
        )
    if links:
        ProductBatchMilk.objects.bulk_create(links, ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0011_recipe_cost"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductBatchMilk",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "goat_milk_batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="product_batch_links",
                        to="production.goatmilkbatch",
                    ),
                ),
                (
                    "product_batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="milk_links",
                        to="production.productbatch",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="productbatchmilk",
            constraint=models.UniqueConstraint(
                fields=("product_batch", "goat_milk_batch"),
                name="unique_milk_batch_per_product_batch",
            ),
        ),
        migrations.RunPython(copy_existing_milk_links, migrations.RunPython.noop),
    ]
