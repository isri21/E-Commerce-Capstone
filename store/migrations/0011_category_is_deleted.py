# Generated by Django 4.2.17 on 2025-01-02 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_product_is_deleted_alter_category_creator_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
