# Generated by Django 4.0.2 on 2022-02-16 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testor', '0003_testing_diagram_remove_testing_question_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testing',
            name='question',
        ),
        migrations.AddField(
            model_name='testing',
            name='question',
            field=models.JSONField(default=1, verbose_name='id оставшихся вопросов'),
            preserve_default=False,
        ),
    ]
