# Generated by Django 5.2.3 on 2025-06-14 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_category_product_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
