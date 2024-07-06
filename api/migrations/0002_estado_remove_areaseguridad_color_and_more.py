# Generated by Django 4.2.13 on 2024-07-05 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=200)),
                ('color', models.CharField(max_length=50)),
                ('icono', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='areaseguridad',
            name='color',
        ),
        migrations.RemoveField(
            model_name='areaseguridad',
            name='icono',
        ),
        migrations.AlterField(
            model_name='seccionauditoria',
            name='estado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.estado'),
        ),
    ]