#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import datetime

from djpoll.models import *

def inicio(request,djpoll_id):
    inicio = True
    if '|' in djpoll_id:
        if request.method == 'GET':
            return HttpResponse('Error')
        split_djpoll_id = djpoll_id.split('|')
        id_proyecto = split_djpoll_id[0]
        grupo_salto = split_djpoll_id[1]
        inicio = False
    elif djpoll_id.isdigit():
        request.session['inicio'] = str(datetime.now())
        id_proyecto = djpoll_id

    try:
        objProyecto = Proyecto.objects.get(pk=int(id_proyecto),activo=True)
        id_cuestionario = objProyecto.cuestionario.id

    except:
        return HttpResponse('El proyecto no existe')
    
    resp_cuestionario = Cuestionario.objects.filter(pk=id_cuestionario)

    hiddens = ""

    hiddens += "<input type='hidden' name='strProyecto_id_numero' value='"+ str(objProyecto.id) +"' >\n\r"
    hiddens += "<input type='hidden' name='strCuestionario_id_numero' value='"+ str(id_cuestionario) +"' >\n\r"

    if resp_cuestionario.count() == 0:
        return HttpResponse("No existe cuestionario")
    else:
        grupos = GrupoCuestionario.objects.filter(cuestionario=resp_cuestionario[0],activo=True).order_by('numero')
            
        if inicio == True:
            grupo = grupos[0]
            grupo_sig = grupos[1]
            grupo_sig_numero = grupo_sig.numero
            next_group = str(id_cuestionario) + '|' + str(grupo_sig_numero)
            
        else:
            for h in request.POST:
                if str(h) == "strProyecto_id_numero":
                    pass
                elif str(h) == "strCuestionario_id_numero":
                    pass
                else:
                    if h[0:2] == "om":
                        hiddens += "<input type='hidden' name='"+ h +"' value = '"+ ','.join(request.POST.getlist(h)) + "'> \n\r "
                    elif h[0:2] == "mi":
                        hiddens += "<input type='hidden' name='"+ h +"' value = '"+ ','.join(request.POST.getlist(h)) + "'> \n\r "
                    else:
                        hiddens += "<input type='hidden' name='"+ h +"' value = '"+ request.POST[h] + "'> \n\r "
                
            for i in range(len(grupos)):
                if str(grupos[i].numero) == str(grupo_salto):
                    try:
                        grupo_sig_numero = str(grupos[i+1].numero)
                        next_group = str(id_cuestionario) + '|' + str(grupo_sig_numero)
                    except IndexError:
                        grupo_sig_numero = "guardar"
                        next_group = str(grupo_sig_numero) + '/1'
                    
            grupo = GrupoCuestionario.objects.get(cuestionario=resp_cuestionario[0],activo=True,numero=grupo_salto)
            
    preguntas = Pregunta.objects.filter(grupocuestionario=grupo,activo=True)

    if preguntas.count() == 0:
        return HttpResponse("No hay preguntas")
    else:
        html_form = ""
        preguntas = preguntas.order_by('id')
        for q in preguntas:
            html_form += "<div id=div_'" + str(q.id) + "'>"

            html_form += "<label>"
            html_form += q.nombre
            html_form += "</label>"
            
            if q.tipopregunta.codigo == "etiqueta":
                pass

            elif q.tipopregunta.codigo == "unica":
                html_form += "<div id ='div_ou_"+ str(q.id) +"_error'> </div>"

                ou_radio = Opcion.objects.filter(pregunta=q,activo=True).order_by('id')

                if ou_radio.count() == 0:
                    return HttpResponse("No hay opciones")
                else:
                    for ou in ou_radio:
                        html_form += "<label>"
                        html_form += "<input type='radio' data-salto='"+ str(ou.grupo_siguiente.numero) +"' name='ou_" + str(q.id) + "' value='" + ou.codigo + "'> "
                        html_form += ou.nombre
                        html_form += "</label> <br/>"
                        
            elif q.tipopregunta.codigo == "multiple":
                html_form += "<div id ='div_om_"+ str(q.id) +"_error'> </div>"

                om_check = Opcion.objects.filter(pregunta=q,activo=True).order_by('id')

                if om_check.count() == 0:
                    return HttpResponse("No hay opciones")
                else:
                    for om in om_check:
                        html_form += "<label>"
                        html_form += "<input type='checkbox' data-salto='"+ str(om.grupo_siguiente.numero) +"' name='om_" + str(q.id) + "' value='" + om.codigo + "'> "
                        html_form += om.nombre
                        html_form += "</label> <br/>"

            elif q.tipopregunta.codigo == "lista":
                html_form += "<div id ='div_ou_"+ str(q.id) +"_error'> </div>"

                ou_lista = Opcion.objects.filter(pregunta=q,activo=True).order_by('id')

                if ou_lista.count() == 0:
                    return HttpResponse("No hay opciones")
                else:
                    html_form += "<select name='ou_" + str(q.id) + "'>"
                    html_form += "<option value=''>Seleccione</option>"
                    for ou in ou_lista:
                        html_form += "<option data-salto='"+ str(ou.grupo_siguiente.numero) +"' value='" + ou.codigo + "'> "+ou.nombre  +" </option>"
                    html_form += "</select>"
    
            elif q.tipopregunta.codigo == "textoc":
                list_class = []
                for v_class in q.validaciontexto.values_list('codigo'):
                    list_class.append(v_class[0])

                list_class = ' '.join(list_class)
                
                html_form += "<div id ='div_txtc_"+ str(q.id) +"_error'> </div>"
                html_form += "<input type='text' autocomplete='off' name='txtc_"+ str(q.id) +"' class= '"+ list_class +"' />"

            elif q.tipopregunta.codigo == "textoa":
                list_class = []
                for v_class in q.validaciontexto.values_list('codigo'):
                    list_class.append(v_class[0])

                list_class = ' '.join(list_class)
                html_form += "<div id ='div_txta_"+ str(q.id) +"_error'> </div>"
                html_form += "<textarea name='txta_"+ str(q.id) +"' class='"+ list_class +"' rows='5' cols='30'></textarea>"

            elif q.tipopregunta.codigo == "matrizexcluyente":
                my = MatrizY.objects.filter(pregunta=q,activo=True).order_by('id')
                mx = MatrizX.objects.filter(pregunta=q,activo=True).order_by('id')

                header = "<thead>"
                header += "<tr>"
                header += "<td></td>"
                for xm in mx:
                    header += "<td>"
                    header += "<center>" + xm.nombre + "</center>"
                    header += "</td>"
                header += "</tr>"
                header += "</thead>"
                
                tabla_matriz = "<table border=0>\n\r"
                tabla_matriz += header
                for y in my:
                    tabla_matriz += "<tr>\n\r"
                    tabla_matriz += "<td>\n\r"
                    tabla_matriz += y.nombre
                    tabla_matriz += "</td>\n\r"
                    for x in mx:
                        tabla_matriz += "<td>\n\r"
                        tabla_matriz += "<input type='radio' name='me_" + str(q.id) + "_" + str(y.id) + "' value='" + str(x.id) + "'> "
                        tabla_matriz += "</td> \n\r"
                    tabla_matriz += "<td>\n\r"
                    tabla_matriz += "<div id ='div_me_"+ str(q.id)+ "_" + str(y.id) +"_error'> </div>\n\r"
                    tabla_matriz += "</td>\n\r"
                    tabla_matriz += "</tr>\n\r"
                tabla_matriz += "</table>\n\r"

                html_form += tabla_matriz

            elif q.tipopregunta.codigo == "matrizincluyente":
                my = MatrizY.objects.filter(pregunta=q,activo=True).order_by('id')
                mx = MatrizX.objects.filter(pregunta=q,activo=True).order_by('id')

                header = "<thead>"
                header += "<tr>"
                header += "<td></td>"
                for xm in mx:
                    header += "<td>"
                    header += "<center>" + xm.nombre + "</center>"
                    header += "</td>"
                header += "</tr>"
                header += "</thead>"
                
                tabla_matriz = "<table border=0>\n\r"
                tabla_matriz += header
                for y in my:
                    tabla_matriz += "<tr>\n\r"
                    tabla_matriz += "<td>\n\r"
                    tabla_matriz += y.nombre
                    tabla_matriz += "</td>\n\r"
                    for x in mx:
                        tabla_matriz += "<td>\n\r"
                        tabla_matriz += "<input type='checkbox' name='mi_" + str(q.id) + "_" + str(y.id) + "' value='" + str(x.id) + "'> "
                        tabla_matriz += "</td> \n\r"
                    tabla_matriz += "<td>\n\r"
                    tabla_matriz += "<div id ='div_mi_"+ str(q.id)+ "_" + str(y.id) +"_error'> </div>\n\r"
                    tabla_matriz += "</td>\n\r"
                    tabla_matriz += "</tr>\n\r"
                tabla_matriz += "</table>\n\r"

                html_form += tabla_matriz

                
            html_form += "</div>"
    return render_to_response('cuestionario/index.html', {'html': html_form,'hiddens':hiddens,'next_group':next_group}, context_instance=RequestContext(request))



def guardar(request):
    if 'inicio' in request.session :

        if request.method == 'GET':
            return HttpResponse('error')
        else:
            strCuestionatio = request.POST['strCuestionario_id_numero']
            strUser = request.user
            strProyecto = request.POST['strProyecto_id_numero']

            objCuestionario = Cuestionario.objects.get(pk=int(strCuestionatio))
            objProyecto = Proyecto.objects.get(pk=int(strProyecto))

            objCompletos = Completos(cuestionario=objCuestionario,proyecto=objProyecto,username=strUser)
            objCompletos.save()

            for datos in request.POST:
                if datos.startswith('ou_'):
                    strPregunta = datos.split("ou_")[1]
                    strOpcion = request.POST[datos]

                    objPregunta = Pregunta.objects.get(pk=int(strPregunta))
                    objOpcion = Opcion.objects.get(pk=int(strOpcion))

                    rou = RespuestaOpcionUnica(pregunta = objPregunta, opcion = objOpcion,identificador = objCompletos)
                    rou.save()

                elif datos.startswith('om_'):
                    strPregunta = datos.split("om_")[1]
                    
                    arrayOpcion = request.POST[datos].split('_')

                    for strOpcion in arrayOpcion:
                        objPregunta = Pregunta.objects.get(pk=int(strPregunta))
                        objOpcion = Opcion.objects.get(pk=int(strOpcion))

                        rom = RespuestaOpcionMultiple(pregunta = objPregunta, opcion = objOpcion,identificador = objCompletos)
                        rom.save()

                elif datos.startswith('txtc_'):
                    strPregunta = datos.split("txtc_")[1]
                    strOpcion = request.POST[datos]

                    objPregunta = Pregunta.objects.get(pk=int(strPregunta))

                    rtc = RespuestaTextoC(pregunta = objPregunta, opcion = strOpcion,identificador = objCompletos)
                    rtc.save()

                elif datos.startswith('txta_'):
                    strPregunta = datos.split("txta_")[1]
                    strOpcion = request.POST[datos]

                    objPregunta = Pregunta.objects.get(pk=int(strPregunta))

                    rta = RespuestaTextoA(pregunta = objPregunta, opcion = strOpcion,identificador = objCompletos)
                    rta.save()

                elif datos.startswith('me_'):

                    strPregunta = datos.split("me_")[1]
                    strMatrizY = datos.split("me_")[2]
                    strMatrizX = request.POST[datos]

                    objPregunta = Pregunta.objects.get(pk=int(strPregunta))
                    objMatrizY = MatrizY.objects.get(pk=int(strMatrizY))
                    objMatrizX = MatrizX.objects.get(pk=int(strMatrizX))

                    rme = RespuestaMatrizExcluyente(pregunta = objPregunta, matrizx= objMatrizX, matrizy=objMatrizY, identificador = objCompletos)
                    rme.save()


                elif datos.startswith('mi_'):
                    datosResp = datos.split("mi_")[1]
                    strPregunta = datosResp.split("_")[0]
                    strMatrizY = datosResp.split("_")[1]
                    strMatrizX = request.POST[datos].split(",")

                    objPregunta = Pregunta.objects.get(pk=int(strPregunta))
                    objMatrizY = MatrizY.objects.get(pk=int(strMatrizY))

                    for dat in strMatrizX:
                        objMatrizX = MatrizX.objects.get(pk=int(dat))
                        rmi = RespuestaMatrizIncluyente(pregunta = objPregunta, matrizx= objMatrizX, matrizy=objMatrizY, identificador = objCompletos)
                        rmi.save()

            del request.session['inicio']

    else:
        return HttpResponse('La encuesta ya fue guardada')        

    return HttpResponse('guardando...')


#ISC. Miguel Soltero <figo10mexico@gmail.com>