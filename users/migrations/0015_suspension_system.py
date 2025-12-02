# Generated migration file

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_add_warning_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='suspension_count',
            field=models.IntegerField(default=0, help_text='Number of times suspended (max 3)'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='suspension_end_date',
            field=models.DateTimeField(blank=True, help_text='When suspension will be lifted', null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_permanently_banned',
            field=models.BooleanField(default=False, help_text='Permanently banned (3rd suspension)'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_suspended',
            field=models.BooleanField(default=False, help_text='Currently suspended'),
        ),
    ]
