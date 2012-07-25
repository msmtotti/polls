# -*- coding: utf-8 -*-
from django.contrib import admin

from djpoll.models import *

admin.site.register(Pregunta)

admin.site.register(ValidacionTexto)

admin.site.register(TipoPregunta)

admin.site.register(Cuestionario)

admin.site.register(GrupoCuestionario)

admin.site.register(Opcion)

admin.site.register(MatrizX)

admin.site.register(MatrizY)

admin.site.register(Proyecto)
admin.site.register(Completos)
admin.site.register(RespuestaOpcionUnica)
admin.site.register(RespuestaOpcionMultiple)
admin.site.register(RespuestaTextoC)
admin.site.register(RespuestaTextoA)

admin.site.register(RespuestaMatrizExcluyente)
admin.site.register(RespuestaMatrizIncluyente)


