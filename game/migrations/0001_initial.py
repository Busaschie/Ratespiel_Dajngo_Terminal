from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Spieleintrag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playername', models.CharField(max_length=100)),
                ('geheimzahl', models.IntegerField()),
                ('versuche_gesamt', models.IntegerField()),
                ('getippt', models.TextField()),
                ('benoetigt', models.IntegerField()),
                ('abgebrochen', models.BooleanField(default=False)),
                ('erraten', models.BooleanField(default=False)),
                ('datum', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ratedb',
                'ordering': ['-datum'],
            },
        ),
    ]
