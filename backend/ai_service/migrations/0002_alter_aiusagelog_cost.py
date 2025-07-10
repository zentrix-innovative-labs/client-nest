from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_integration', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aiusagelog',
            name='cost',
            field=models.DecimalField(decimal_places=6, default=0.0, help_text='Cost in USD', max_digits=10),
        ),
    ] 
