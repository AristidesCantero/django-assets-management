# Generated by Django 5.1.7 on 2025-04-03 20:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0003_delete_business_alter_asset_fuel_energy_type_and_more'),
        ('components', '0001_initial'),
        
    ]

    operations = [
        migrations.AlterField(
            model_name='assetsystem',
            name='asset_key',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.asset'),
        ),
    ]
