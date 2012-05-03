from django.db import models

class Ladestelle(models.Model):
    name = models.CharField(max_length=200)
    kurzbeschreibung = models.CharField(max_length=200, blank=True)
    detailbeschreibung = models.TextField(blank=True)
    buchungsschluss = models.TimeField()
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Ladestellen"

class Rampe(models.Model):
    ladestelle = models.ForeignKey(Ladestelle)
    name = models.CharField(max_length=200)
    beschreibung = models.CharField(max_length=200, blank=True)
    anzahl_parallele_abarbeitungen = models.IntegerField()
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Rampen"

class Slot(models.Model):
    rampe = models.ForeignKey(Rampe)
    start = models.TimeField()
    ende = models.TimeField()
    dauer = models.IntegerField()
    gueltig_ab = models.DateField()
    def __unicode__(self):
        return "%s (bis %s)" % (self.rampe, self.gueltig_ab.isoformat())

class Pause(models.Model):
    rampe = models.ForeignKey(Rampe)
    gueltig_ab = models.DateField()
    gueltig_bis = models.DateField()
    start = models.TimeField()
    ende = models.TimeField()
    class Meta:
        verbose_name_plural = "Pausen"
    def __unicode__(self):
        return "%s (bis %s)" % (self.rampe, self.gueltig_bis.isoformat())
