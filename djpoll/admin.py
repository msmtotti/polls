# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.sites.models import Site

from djpoll.models import *

admin.site.unregister(Site)

class OpcionInline(admin.TabularInline):
    model = Opcion
    fk_name = 'pregunta'
    extra = 3
    fieldsets = ((None, {
            'classes': ('collapse'),
            'fields': ('nombre','codigo','grupo_siguiente')
        }),
    )

class MatrizYInline(admin.TabularInline):
    model = MatrizY
    fk_name = 'pregunta'
    extra = 3
    fieldsets = ((None, {
            'classes': ('collapse'),
            'fields': ('nombre','codigo')
        }),
    )

class MatrizXInline(admin.TabularInline):
    model = MatrizX
    fk_name = 'pregunta'
    extra = 3
    fieldsets = ((None, {
            'classes': ('collapse'),
            'fields': ('nombre','codigo')
        }),
    )

class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('cuestionario','grupocuestionario','nombre','codigo','tipopregunta')
    inlines = [OpcionInline,MatrizYInline,MatrizXInline]
    search_fields = ('cuestionario__nombre','codigo','nombre')
    list_filter =('cuestionario',)
    list_per_page = 30
admin.site.register(Pregunta,PreguntaAdmin)

class CuestionarioAdmin(admin.ModelAdmin):
    list_display = ('nombre','activo')
    search_fields = ('nombre',)
    list_per_page = 30
admin.site.register(Cuestionario,CuestionarioAdmin)

# admin.site.register(ValidacionTexto)

# admin.site.register(TipoPregunta)

# admin.site.register(GrupoCuestionario)

# admin.site.register(Opcion)

# admin.site.register(MatrizX)

# admin.site.register(MatrizY)

# admin.site.register(Proyecto)
# admin.site.register(Completos)
# admin.site.register(RespuestaOpcionUnica)
# admin.site.register(RespuestaOpcionMultiple)
# admin.site.register(RespuestaTextoC)
# admin.site.register(RespuestaTextoA)

# admin.site.register(RespuestaMatrizExcluyente)
# admin.site.register(RespuestaMatrizIncluyente)


