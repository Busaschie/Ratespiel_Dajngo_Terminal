from django.db import models


class Spieleintrag(models.Model):
    playername     = models.CharField(max_length=100)
    geheimzahl     = models.IntegerField()
    versuche_gesamt = models.IntegerField()
    getippt        = models.TextField()
    benoetigt      = models.IntegerField()
    abgebrochen    = models.BooleanField(default=False)
    erraten        = models.BooleanField(default=False)
    datum          = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ratedb'
        ordering = ['-datum']

    def __str__(self):
        return f"{self.playername} – {self.datum:%d.%m.%Y}"
