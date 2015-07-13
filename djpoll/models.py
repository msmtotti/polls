#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.db import models

# Create your models here.

class ValidacionTexto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100,db_index=True)
    activo = models.BooleanField()

    def __unicode__(self):
        return self.nombre

class TipoPregunta(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100,db_index=True)
    activo = models.BooleanField()

    def __unicode__(self):
        return self.nombre
    

class Cuestionario(models.Model):
    nombre = models.CharField(max_length=100,db_index=True)
    activo = models.BooleanField()

    def __unicode__(self):
        return '%s - %s' % (self.id,self.nombre)

class GrupoCuestionario(models.Model):
    cuestionario = models.ForeignKey('Cuestionario')
    numero = models.DecimalField(max_digits=8, decimal_places=2, db_index=True)
    activo = models.BooleanField()

    def __unicode__(self):
        return  '%s - %s' % (self.cuestionario, self.numero)

class Pregunta(models.Model):
    cuestionario = models.ForeignKey('Cuestionario')
    grupocuestionario = models.ForeignKey(GrupoCuestionario)
    tipopregunta = models.ForeignKey(TipoPregunta)
    validaciontexto = models.ManyToManyField(ValidacionTexto,blank=True,null=True)
    nombre = models.TextField(db_index=True)
    codigo = models.CharField(max_length=250,db_index=True)
    activo = models.BooleanField()

    def __unicode__(self):
        return "%s - %s -%s" % (self.nombre,self.grupocuestionario,self.tipopregunta)
    
class Opcion(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    grupo_siguiente = models.ForeignKey('GrupoCuestionario')
    nombre = models.TextField(db_index=True)
    codigo = models.CharField(max_length=100,db_index=True)
    aleatorio = models.BooleanField()
    activo = models.BooleanField()

    def __unicode__(self):
        return '%s - %s' % (self.pregunta, self.nombre)
    
class MatrizX(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    nombre = models.TextField(db_index=True)
    codigo = models.CharField(max_length=100,db_index=True)
    aleatorio = models.BooleanField()
    activo = models.BooleanField()

    def __unicode__(self):
        return '%s - %s' % (self.pregunta, self.nombre)

class MatrizY(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    grupo_siguiente = models.ForeignKey('GrupoCuestionario',blank=True,null=True)
    nombre = models.TextField(db_index=True)
    codigo = models.CharField(max_length=100,db_index=True)
    aleatorio = models.BooleanField()
    activo = models.BooleanField()

    def __unicode__(self):
        return '%s - %s' % (self.pregunta, self.nombre)

class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    cuestionario = models.ForeignKey('Cuestionario')
    activo = models.BooleanField()

    def __unicode__(self):
        return '%s - %s' % (self.id, self.nombre)

class Completos(models.Model):
    cuestionario = models.ForeignKey('Cuestionario')
    proyecto = models.ForeignKey('Proyecto')
    username = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s' % (self.id)

class RespuestaOpcionUnica(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    opcion = models.ForeignKey('Opcion')
    identificador = models.ForeignKey('Completos')


class RespuestaOpcionMultiple(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    opcion = models.ForeignKey('Opcion')
    identificador = models.ForeignKey('Completos')

class RespuestaTextoC(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    opcion = models.TextField(blank=True,null=True)
    identificador = models.ForeignKey('Completos')

class RespuestaTextoA(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    opcion = models.TextField(blank=True,null=True)
    identificador = models.ForeignKey('Completos')

class RespuestaMatrizExcluyente(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    matrizx = models.ForeignKey('MatrizX')
    matrizy = models.ForeignKey('MatrizY')
    identificador = models.ForeignKey('Completos')

class RespuestaMatrizIncluyente(models.Model):
    pregunta = models.ForeignKey('Pregunta')
    matrizx = models.ForeignKey('MatrizX')
    matrizy = models.ForeignKey('MatrizY')
    identificador = models.ForeignKey('Completos')