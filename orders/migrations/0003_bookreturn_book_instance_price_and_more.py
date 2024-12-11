# Generated by Django 5.0.6 on 2024-12-10 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_damagephoto_book_damage'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookreturn',
            name='book_instance_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6, verbose_name='Цена за использование книгу'),
        ),
        migrations.AlterField(
            model_name='damagephoto',
            name='photo',
            field=models.ImageField(upload_to='book_damages/', verbose_name='Фотография'),
        ),
    ]