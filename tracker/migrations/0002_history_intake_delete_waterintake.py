# Generated by Django 4.2.3 on 2023-07-31 02:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goal', models.DecimalField(decimal_places=2, help_text='Meta do dia em ML', max_digits=6, verbose_name='Meta')),
                ('date', models.DateField(auto_now_add=True, help_text='Data', verbose_name='Data')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='tracker.user', verbose_name='Usuário')),
            ],
            options={
                'unique_together': {('user_id', 'date')},
            },
        ),
        migrations.CreateModel(
            name='Intake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, help_text='Quantidade em ML', max_digits=6, verbose_name='Quantidade')),
                ('history_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='intake', to='tracker.history', verbose_name='Histórico')),
            ],
        ),
        migrations.DeleteModel(
            name='WaterIntake',
        ),
    ]
