from django.db import models

class Prediccion(models.Model):
    accion = models.CharField(max_length=100)
    fecha = models.DateTimeField('fecha')
    precio_real = models.DecimalField(max_digits=20,decimal_places=10)
    precio_estimado = models.DecimalField(max_digits=20,decimal_places=10)
