# Generated migration for warning system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_alter_vendorprofile_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='warning_count',
            field=models.IntegerField(default=0, help_text='Number of warnings received'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_suspended',
            field=models.BooleanField(default=False, help_text='Account suspended after 2 warnings'),
        ),
    ]
