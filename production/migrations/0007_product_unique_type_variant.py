from django.db import migrations, models


def dedupe_product_type_variant(apps, schema_editor):
    Product = apps.get_model("production", "Product")
    seen = {}
    delete_ids = []
    for product in Product.objects.order_by("business_id", "type", "variant", "created_at"):
        key = (product.business_id, product.type, product.variant or "")
        if key in seen:
            delete_ids.append(product.pk)
        else:
            seen[key] = product.pk
    if delete_ids:
        Product.objects.filter(pk__in=delete_ids).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("production", "0006_recipe_type_unique_per_business"),
    ]

    operations = [
        migrations.RunPython(dedupe_product_type_variant, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(
                fields=("business", "type", "variant"),
                name="unique_product_type_variant_per_business",
            ),
        ),
    ]
