from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# Los modelos se crean acá como clases.
# Luego se importan en admin.py y se registran en el admin de django
# De estos modelos después en el admin de django se pueden crear instancias
# Luego en views se muestran con el nombre del modelo.objects.metodo()
# Luego en los templates se define cómo se muestran en el front

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    #por default los modelos tienen un id generado, empezando en 1
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) #null true es para la base de datos, blank true es para el campo en el form. Esto habilita que tanto en la base como en el formulario pueda estar en blanco el valor.
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']
        #sin el - lo ordena en orden ascendente, con - lo hace en orden descendente
    def __str__(self):
        return self.name
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50]