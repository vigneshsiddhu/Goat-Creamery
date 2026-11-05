from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0012_productbatchmilk"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productbatch",
            name="goat_milk_batch",
        ),
    ]
