#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import datetime
from django.db import connection
import os
import zipfile
from django.db import transaction
from psycopg2 import IntegrityError,ProgrammingError
from django.contrib.auth.decorators import login_required
import settings
from django.contrib import auth
from django.http import Http404
from djpoll.models import *

def redirec(request):
    return HttpResponseRedirect("/inicio/")

def index(request):
    return render_to_response('cuestionario/index.html',{}, context_instance=RequestContext(request))

def error_404(request):
    return render_to_response('cuestionario/404.html')

@login_required()
def inicio(request,djpoll_id):
    inicio = True
    if '|' in djpoll_id:
        split_djpoll_id = djpoll_id.split('|')
        if request.method == 'GET':
            id_proyecto = split_djpoll_id[0]
            grupo_salto = split_djpoll_id[1]

            if grupo_salto != "simulador":
                raise Http404
        else:
            id_proyecto = split_djpoll_id[0]
            grupo_salto = split_djpoll_id[1]
            inicio = False
    elif djpoll_id.isdigit():
        request.session['inicio'] = str(datetime.now())
        id_proyecto = djpoll_id
        grupo_salto = ""

    try:
        if request.POST.has_key('simulador_files') or grupo_salto == "simulador" :
            id_cuestionario = id_proyecto
        else:
            objProyecto = Proyecto.objects.get(pk=int(id_proyecto),activo=True)
            id_cuestionario = objProyecto.cuestionario.id

    except Exception ,ty:
        return render_to_response('cuestionario/404.html',{'error':ty},
            context_instance=RequestContext(request))
    
    resp_cuestionario = Cuestionario.objects.filter(pk=id_cuestionario)

    hiddens = ""

    nomProyecto = ""
    nomCuestionario = ""
    if request.POST.has_key('simulador_files') or grupo_salto == "simulador" :
        hiddens += "<input type='hidden' name='simulador_files' value='True' >\n\r"
        nomProyecto = "Simulador"
    else:
        hiddens += "<input type='hidden' name='strProyecto_id_numero' value='"+ str(objProyecto.id) +"' >\n\r"
        nomProyecto = str(objProyecto.nombre)
    hiddens += "<input type='hidden' name='strCuestionario_id_numero' value='"+ str(id_cuestionario) +"' >\n\r"
    nomCuestionario = str(resp_cuestionario[0].nombre)

    if resp_cuestionario.count() == 0:
        return HttpResponse("No existe cuestionario")
    else:
        grupos = GrupoCuestionario.objects.filter(cuestionario=resp_cuestionario[0],activo=True).order_by('numero')
            
        if inicio == True:
            grupo = grupos[0]
            grupo_sig = grupos[1]
            grupo_sig_numero = grupo_sig.numero
            next_group = str(id_proyecto) + '|' + str(grupo_sig_numero)
            
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
                        next_group = str(id_proyecto) + '|' + str(grupo_sig_numero)
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
            html_form += "<div id=div_'" + str(q.id) + "'>\n\r"

            html_form += "<table class=\"table table-striped\">" 

            html_form += "<thead>"
            html_form += "<tr>"
            html_form += "<th></th>"
            html_form += "<th>"
            html_form += q.nombre
            html_form += "</th>"
            html_form += "</tr>"
            html_form += "</thead>"
            
            if q.tipopregunta.codigo == "etiqueta":
                pass

            elif q.tipopregunta.codigo == "unica":

                html_form += "<tbody>"
                html_form += "<div id ='div_ou_"+ str(q.id) +"_error'> </div>\n\r"

                ou_radio = Opcion.objects.filter(pregunta=q,activo=True).order_by('id')

                if ou_radio.count() == 0:
                    return HttpResponse("No hay opciones")
                else:
                    for ou in ou_radio:
                        html_form += "<tr>"
                        html_form += "<td>"
                        html_form += "<input type='radio' id='ou_"+ str(q.id) + "_"+ str(ou.id) +"' data-salto='"+ str(ou.grupo_siguiente.numero) +"' name='ou_" + str(q.id) + "' value='" + str(ou.id) + "'> "
                        html_form += "</td>"
                        html_form += "<td>"
                        html_form += ou.nombre
                        html_form += "</td>"
                        html_form += "</tr>"

                html_form += "</tbody>"

                
                        
            elif q.tipopregunta.codigo == "multiple":
                html_form += "<tbody>"
                html_form += "<div id ='div_om_"+ str(q.id) +"_error'> </div>\n\r"

                om_check = Opcion.objects.filter(pregunta=q,activo=True).order_by('id')

                if om_check.count() == 0:
                    return HttpResponse("No hay opciones")
                else:
                    for om in om_check:
                        html_form += "<tr>"
                        html_form += "<td>"
                        html_form += "<input type='checkbox' id='om_"+ str(q.id) + "_"+ str(om.id) +"' data-salto='"+ str(om.grupo_siguiente.numero) +"' name='om_" + str(q.id) + "' value='" + str(om.id) + "'> "
                        html_form += "</td>"
                        html_form += "<td>"
                        html_form += om.nombre
                        html_form += "</td>"
                        html_form += "</tr>"
                html_form += "</tbody>"

            elif q.tipopregunta.codigo == "lista":
                html_form += "<tbody>"
                html_form += "<div id ='div_ou_"+ str(q.id) +"_error'> </div>\n\r"

                ou_lista = Opcion.objects.filter(pregunta=q,activo=True).order_by('id')

                if ou_lista.count() == 0:
                    return HttpResponse("No hay opciones")
                else:
                    html_form += "<tr><td></td>"
                    html_form += "<td>"
                    html_form += "<select name='ou_" + str(q.id) + "'>"
                    html_form += "<option value=''>Seleccione</option>"
                    for ou in ou_lista:
                        html_form += "<option id='ou_"+ str(q.id) + "_"+ str(ou.id) +"' data-salto='"+ str(ou.grupo_siguiente.numero) +"' value='" + str(ou.id) + "'> "+ou.nombre  +" </option>\n\r"
                    html_form += "</select>"
                    html_form += "</td>"
                    html_form += "</tr>"
                html_form += "</tbody>"
    
            elif q.tipopregunta.codigo == "textoc":
                html_form += "<tbody>"
                list_class = []
                for v_class in q.validaciontexto.values_list('codigo'):
                    list_class.append(v_class[0])

                list_class = ' '.join(list_class)
                
                html_form += "<div id ='div_txtc_"+ str(q.id) +"_error'> </div>"
                html_form += "<tr><td></td>"
                html_form += "<td>"
                html_form += "<input type='text' autocomplete='off' name='txtc_"+ str(q.id) +"' class= '"+ list_class +"' />"
                html_form += "</td>"
                html_form += "</tr>"
                html_form += "</tbody>"

            elif q.tipopregunta.codigo == "textoa":
                html_form += "<tbody>"
                list_class = []
                for v_class in q.validaciontexto.values_list('codigo'):
                    list_class.append(v_class[0])

                list_class = ' '.join(list_class)
                html_form += "<div id ='div_txta_"+ str(q.id) +"_error'> </div>"
                html_form += "<tr><td></td>"
                html_form += "<td>"
                html_form += "<textarea name='txta_"+ str(q.id) +"' class='"+ list_class +"' rows='5' cols='30'></textarea>"
                html_form += "</td>"
                html_form += "</tr>"
                html_form += "</tbody>"


            elif q.tipopregunta.codigo == "matrizexcluyente":

                html_form +="</table>"

                my = MatrizY.objects.filter(pregunta=q,activo=True).order_by('id')
                mx = MatrizX.objects.filter(pregunta=q,activo=True).order_by('id')

                header = "<thead>"
                header += "<tr>"
                header += "<th></th>"
                for xm in mx:
                    header += "<th>"
                    header += xm.nombre
                    header += "</th>"
                header += "</tr>"
                header += "</thead>"
                
                tabla_matriz = "<table class='table table-striped '>\n\r"
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
                

                html_form += tabla_matriz

            elif q.tipopregunta.codigo == "matrizincluyente":
                html_form +="</table>"
                my = MatrizY.objects.filter(pregunta=q,activo=True).order_by('id')
                mx = MatrizX.objects.filter(pregunta=q,activo=True).order_by('id')

                header = "<thead>"
                header += "<tr>"
                header += "<th></th>"
                for xm in mx:
                    header += "<th>"
                    header += xm.nombre
                    header += "</th>"
                header += "</tr>"
                header += "</thead>"
                
                tabla_matriz = "<table class='table table-striped'>\n\r"
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
                

                html_form += tabla_matriz

            html_form += "</table>"
            html_form += "</div>"
    return render_to_response('cuestionario/inicio.html', {
        'nomProyecto':nomProyecto,'nomCuestionario':nomCuestionario,
        'html': html_form,'hiddens':hiddens,'next_group':next_group
        }, context_instance=RequestContext(request))


@login_required()
def guardar(request):
    if 'inicio' in request.session :

        if request.method == 'GET':
            return HttpResponse('error')
        else:
            if not request.POST.has_key('simulador_files'):
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

                        if len(request.POST[datos].split(",")) > 1:
                            arrayOpcion = request.POST[datos].split(",")
                        else:
                            arrayOpcion = request.POST.getlist(datos)

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

                        strPregunta = datos.split("me_")[1].split("_")[0]
                        strMatrizY = datos.split("me_")[1].split("_")[1]
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

                        if len(request.POST[datos].split(",")) > 1:
                            strMatrizX = request.POST[datos].split(",")
                        else:
                            strMatrizX = request.POST.getlist(datos)

                        objPregunta = Pregunta.objects.get(pk=int(strPregunta))
                        objMatrizY = MatrizY.objects.get(pk=int(strMatrizY))

                        for dat in strMatrizX:
                            objMatrizX = MatrizX.objects.get(pk=int(dat))
                            rmi = RespuestaMatrizIncluyente(pregunta = objPregunta, matrizx= objMatrizX, matrizy=objMatrizY, identificador = objCompletos)
                            rmi.save()

                mensaje = "Encuesta guardada correctamente"
            else:
                proyecto = "Simulador"
                mensaje = "Simulador terminado correcto"

            del request.session['inicio']
            

    else:
        mensaje = 'La encuesta ya fue guardada'

    name = ""
    hidden= ""
    strCuestionatio = request.POST['strCuestionario_id_numero']
    if request.POST.has_key('simulador_files'):
        liga = "/djpoll/simular/1/"
        hidden = "<input type='hidden' name='strcuestionario' value = '"+ strCuestionatio +"'>"
        name = "Volver a simular"
    else:
        strProyecto = request.POST['strProyecto_id_numero']
        liga = "/djpoll/" + strProyecto + "/"
        name = "Otra encuesta"

    return render_to_response('cuestionario/guardar.html', {'liga':liga,
        'mensaje':mensaje,'name':name,
        'hidden':hidden
        },
         context_instance=RequestContext(request))

def archivos(fetchall,cabecera,path):
    completo = []
    for c in cabecera:
        completo.append(c[0])
    completo = (tuple(completo),)
    flagc = True
    flago = True
    completo += tuple(fetchall)

    finc = open(path + '_tmpc.csv','r')
    foutc = open(path + '_codigos.csv','w')
    
    for line in finc:
        if flagc:
            unicid =completo[0][2]
            linae = line.rstrip('\n').decode('utf-8')
            filac = linae + unicode(unicid).replace('\n',' ').replace('\r','') + '|\n'
            flagc = False
        else:
            id = line.split('|')[0]
            filac = ''
            for id_fect in completo:
                if str(id) == str(id_fect[0]):
                    unicid =id_fect[2]
                    linae = line.rstrip('\n').decode('utf-8')
                    filac = linae + unicode(unicid).replace('\n',' ').replace('\r','') + '|\n'
                    break
                
        if filac != '':
            foutc.write(filac.encode('utf-8'))
        else:
            var = line.rstrip('\n')+ '|\n'
            foutc.write(var)
            
    finc.close()
    foutc.close()
    
    fino = open(path + '_tmpo.csv','r')
    fouto = open(path + '_opciones.csv','w')
    
    for line in fino:
        if flago:
            unicid =completo[0][1]
            linae = line.rstrip('\n').decode('utf-8')
            filao = linae + unicid.replace('\n',' ').replace('\r','') + '|\n'
            flago = False
        else:
            id = line.split('|')[0]
            filao = u''
            for id_fect in completo:
                if str(id) == str(id_fect[0]):
                    unicid =id_fect[1]
                    linae = line.rstrip('\n').decode('utf-8')
                    filao = linae + unicid.replace('\n',' ').replace('\r','') + '|\n'
                    break
                
        if filao != '':
            fouto.write(filao.encode('utf-8'))
        else:
            var = line.rstrip('\n')+ '|\n'
            fouto.write(var)
            
    fino.close()
    fouto.close()
    
    os.remove(path + '_tmpc.csv')
    os.rename(path + '_codigos.csv', path + '_tmpc.csv')
    os.remove(path + '_tmpo.csv')
    os.rename(path + '_opciones.csv', path + '_tmpo.csv')

@login_required()
def simular(request):
    if request.method == "GET":
        objCuestionario = Cuestionario.objects.filter(activo = True).order_by("-id")
    else:
        strcuestionario = request.POST['strcuestionario']
        return HttpResponseRedirect("/djpoll/"+ strcuestionario + "|simulador/")
    return render_to_response('cuestionario/simular.html', {'objCuestionario': objCuestionario}, context_instance=RequestContext(request))

@login_required()
def reportes(request):
    boolean = request.POST.has_key('strproyecto')
    if boolean:
        intProyecto = request.POST['strproyecto']

        try:
            c = int(intProyecto)            
        except:
            boolean = False

    if request.method == "GET" or boolean == False:
        objProyectos = Proyecto.objects.filter(activo = True).order_by("-id")
        return render_to_response('cuestionario/reporte.html', {'objProyectos': objProyectos}, context_instance=RequestContext(request))

    intProyecto = request.POST['strproyecto']

    objProyecto = Proyecto.objects.get(pk=int(intProyecto))
    objCuestionario = objProyecto.cuestionario

    nombre = objProyecto.nombre.replace(" ","").replace("\"","").replace("'","") + "_" + objCuestionario.nombre.replace(" ","").replace("\"","").replace("'","")

    separador = "\\"
    if settings.HEROKU:
        separador = "/"

    path = os.path.join(os.path.dirname(__file__),'..'+ separador +'media'+ separador +'archivos'+ separador + nombre.encode('utf-8'))

    arrayPreguntas = Pregunta.objects.filter(cuestionario=objCuestionario).order_by("id")

    arrayCompletos = Completos.objects.filter(cuestionario=objCuestionario,proyecto=objProyecto).order_by("id")

    if arrayCompletos.count() == 0:
        message = "No hay encuestas guardadas"
        objProyectos = Proyecto.objects.filter(activo = True).order_by("-id")
        return render_to_response('cuestionario/reporte.html', {'message':message,'objProyectos': objProyectos}, context_instance=RequestContext(request))

    id_completos = []

    fc = open(path+'_tmpc.csv', 'w')
    fo = open(path+'_tmpo.csv', 'w')

    fc.write('identificador|')
    fo.write('identificador|')
    fc.write('\n')
    fo.write('\n')
    for com in arrayCompletos:
        id_completos.append(com.id)
        fc.write(str(com.id)+'|')
        fo.write(str(com.id)+'|')
        fc.write('\n')
        fo.write('\n')
        
    fc.close()
    fo.close()

    query_aux = ' WHERE a.identificador_id in ('+(id_completos.__str__().strip('[]')) +') AND '
    query_order = ' ORDER BY a.identificador_id '

    cur = connection.cursor()

    for objPregunta in arrayPreguntas:
        if  objPregunta.tipopregunta.id == 2 or objPregunta.tipopregunta.id == 4:
            query = 'SELECT a.identificador_id, b.nombre as '+ str(objPregunta.codigo) +' , b.codigo '+ str(objPregunta.codigo) + ' '
            query +='FROM djpoll_respuestaopcionunica AS a, djpoll_opcion AS b '
            query += query_aux
            query += 'a.opcion_id = b.id AND a.pregunta_id =' + str(objPregunta.id)
            query += query_order
            cur.execute(query)
            archivos(cur.fetchall(),cur.description,path)

        elif objPregunta.tipopregunta.id == 3:
            """CheckBox"""
            respid = Opcion.objects.filter(pregunta = objPregunta).order_by('id')
            for i in respid:
                query = 'SELECT a.identificador_id, b.nombre as '+ str(objPregunta.codigo)  + '_' + str(i.codigo) + ', b.codigo as '+ str(objPregunta.codigo) + '_' + str(i.codigo) + ' '
                query += 'FROM djpoll_respuestaopcionmultiple AS a, djpoll_opcion AS b '
                query += query_aux
                query += 'a.opcion_id =\'' + str(i.id) + '\' '
                query += 'AND b.pregunta_id =\'' + str(objPregunta.id) + '\' '
                query += 'AND a.opcion_id = b.id '
                query += query_order
                cur.execute(query)
                archivos(cur.fetchall(),cur.description,path)

        elif objPregunta.tipopregunta.id == 5:
            """TextBox"""
            query = 'SELECT a.identificador_id, a.opcion as '+ str(objPregunta.codigo) +' , a.opcion as ' + str(objPregunta.codigo) + ' '
            query += 'FROM djpoll_respuestatextoc as a'
            query += query_aux
            query += 'a.pregunta_id = '+ str(objPregunta.id)
            query += query_order
            cur.execute(query)
            archivos(cur.fetchall(),cur.description,path)
            
        elif objPregunta.tipopregunta.id == 6:
            """TextArea"""
            query = 'SELECT a.identificador_id, a.opcion as '+ str(objPregunta.codigo) +' , a.opcion as ' + str(objPregunta.codigo) + ' '
            query += 'FROM djpoll_respuestatextoa as a'
            query += query_aux
            query += 'a.pregunta_id = ' + str(objPregunta.id)
            query += query_order
            cur.execute(query)
            archivos(cur.fetchall(),cur.description,path)

        elif objPregunta.tipopregunta.id == 7:
            """Matriz Excluyente"""
            pme = []
            pme_ids = MatrizY.objects.filter(pregunta=objPregunta).order_by('id')
            for i in pme_ids:
                pme.append([i.id,i.codigo])
            for i in pme:
                query = 'SELECT a.identificador_id, b.nombre as '+ str(objPregunta.codigo) + '_' + i[1] + ', b.codigo as '+ str(objPregunta.codigo) + '_' + i[1] + ' '
                query += 'FROM djpoll_respuestamatrizexcluyente AS a, djpoll_matrizx AS b '
                query += query_aux
                query += 'a.matrizy_id =\'' + str(i[0]) + '\' '
                query += 'AND b.pregunta_id =\'' + str(objPregunta.id) + '\' '
                query += 'AND a.matrizx_id = b.id '
                query += query_order
                cur.execute(query)
                archivos(cur.fetchall(),cur.description,path)

        elif objPregunta.tipopregunta.id == 8:
            """Matriz Incluyente"""
            pm = []
            ppm = []
            rm = []
            rrm = []
            pm_ids = MatrizY.objects.filter(pregunta=objPregunta).order_by('id')
            for i in pm_ids:
                pm.append([i.id,i.codigo])
            
            rm_ids = MatrizX.objects.filter(pregunta=objPregunta).order_by('id')
            for i in rm_ids:
                rm.append([i.id,i.codigo])

            for p in pm:
                for r in rm:
                    query = 'SELECT a.identificador_id, b.nombre as '+ str(objPregunta.codigo) + '_' + p[1] + '_' + r[1] +' , b.codigo as '+ str(objPregunta.codigo) + '_' + p[1] + '_' + r[1] + ' '
                    query += 'FROM djpoll_respuestamatrizincluyente AS a, djpoll_matrizx AS b '
                    query += query_aux
                    query += 'b.pregunta_id =  \'' + str(objPregunta.id) + '\' AND a.matrizy_id = \'' + str(p[0])+ '\' '
                    query += 'and b.id =  \'' + str(r[0]) + '\'  AND a.matrizx_id = b.id '
                    query += query_order
                    cur.execute(query)
                    archivos(cur.fetchall(),cur.description,path)
    os.rename(path + '_tmpc.csv', path + '_codigos.csv')
    os.rename(path + '_tmpo.csv', path + '_opciones.csv')

    archive_list = []
    archive_list.append(path + '_codigos.csv')
    archive_list.append(path + '_opciones.csv')
    zout = zipfile.ZipFile(path+ ".zip", "w")

    for fname in archive_list:
        zout.write(fname, fname.rsplit(separador,1)[1])
    zout.close()

    os.remove(path + '_codigos.csv')
    os.remove(path + '_opciones.csv')

    name_zip = path.rsplit(separador,1)[1]
    return HttpResponseRedirect('media/archivos/' +nombre + '.zip')

def tipoPregunta(nombre):
    if nombre == 'etiqueta':
        objTipo = TipoPregunta.objects.get(pk=1)
    elif nombre =='unica':
        objTipo = TipoPregunta.objects.get(pk=2)
    elif nombre == 'multiple':
        objTipo = TipoPregunta.objects.get(pk=3)
    elif nombre == 'lista':
        objTipo = TipoPregunta.objects.get(pk=4)
    elif nombre == 'textoc':
        objTipo = TipoPregunta.objects.get(pk=5)
    elif nombre == 'textoa':
        objTipo = TipoPregunta.objects.get(pk=6)
    elif nombre == 'matrizexcluyente':
        objTipo = TipoPregunta.objects.get(pk=7)
    elif nombre == 'matrizincluyente':
        objTipo = TipoPregunta.objects.get(pk=8)
    return objTipo


def validacionTexto(nombre):
    if nombre == 'required':
        objValidacion = ValidacionTexto.objects.get(pk=1)
    elif nombre =='numeric':
        objValidacion = ValidacionTexto.objects.get(pk=2)
    elif nombre == 'numericspace':
        objValidacion = ValidacionTexto.objects.get(pk=3)
    elif nombre == 'letters':
        objValidacion = ValidacionTexto.objects.get(pk=4)
    elif nombre == 'lettersspace':
        objValidacion = ValidacionTexto.objects.get(pk=5)
    elif nombre == 'numericletters':
        objValidacion = ValidacionTexto.objects.get(pk=6)
    elif nombre == 'numericlettersspace':
        objValidacion = ValidacionTexto.objects.get(pk=7)
    elif nombre == 'upper':
        objValidacion = ValidacionTexto.objects.get(pk=8)
    return objValidacion    


@login_required()
@transaction.commit_manually
def subirArchivo(request):
    err = "Correcto"
    if request.method == 'GET':
        return render_to_response('cuestionario/subirarchivo.html',{'GET':'get'}, context_instance=RequestContext(request))
    else:
        archivo = request.FILES["file_files"]
        nombre = request.POST["name_files"]

        try:

            cuestionario = Cuestionario(nombre=nombre,activo=True)
            cuestionario.save()

            id_cuestionario = cuestionario.id

            arrayTipo = ['etiqueta','unica','multiple','textoc','textoa','lista','matrizexcluyente','matrizincluyente']

            arrayOpciones = ['unica','multiple','lista']
            arrayTexto = ['textoc','textoa']
            arrayMatriz = ['matrizexcluyente','matrizincluyente']
            arrayEtiqueta = ['etiqueta']

            for index,f in enumerate(archivo):
                if index == 0:
                    pass
                else:
                    info = f.split("|")

                    pagina = info[0].replace(" ","").replace("\"","").replace("'","").decode('utf-8')
                    pregunta = info[1].lstrip('\'').lstrip('\"').rstrip('\'').rstrip('\"').decode('utf-8')
                    code = info[2].replace(" ","").replace("\"","").replace("'","").replace(".","").replace("-","").decode('utf-8')

                    tipo = info[3].replace(" ","").replace("\"","").replace("'","").decode('utf-8')

                    opciones_code = info[4].replace(" ","").replace("\"","").replace("'","").replace(".","").replace("-","").decode('utf-8')
                    opciones_name = info[5].lstrip('\'').lstrip('\"').rstrip('\'').rstrip('\"').decode('utf-8')
                    salto_pagina = info[6].replace(" ","").replace("\"","").replace("'","").decode('utf-8')

                    validaciones_texto = info[7]

                    Yopciones_code = info[8].replace(" ","").replace("\"","").replace("'","").replace(".","").replace("-","").decode('utf-8')
                    Yopciones_name = info[9].lstrip('\'').lstrip('\"').rstrip('\'').rstrip('\"').decode('utf-8')

                    Xopciones_code = info[10].replace(" ","").replace("\"","").replace("'","").replace(".","").replace("-","").decode('utf-8')
                    Xopciones_name = info[11].lstrip('\'').lstrip('\"').rstrip('\'').rstrip('\"').decode('utf-8')

                    if tipo in arrayTipo:

                        objGC, created = GrupoCuestionario.objects.get_or_create(cuestionario=cuestionario, numero=pagina,activo=True)
                        objPregunta = Pregunta(
                            cuestionario = cuestionario,
                            grupocuestionario = objGC,
                            tipopregunta = tipoPregunta(tipo),
                            nombre = pregunta,
                            codigo = code,
                            activo = True
                        )
                        objPregunta.save()

                    if len(opciones_code) > 0:
                        objGC, created = GrupoCuestionario.objects.get_or_create(cuestionario=cuestionario, numero=salto_pagina,activo=True)
                        objOpcion = Opcion(pregunta=objPregunta,grupo_siguiente=objGC,nombre=opciones_name,codigo=opciones_code,activo=True)
                        objOpcion.save()

                    if len(validaciones_texto) > 0:
                        validator = validaciones_texto.split(",")
                        for v in validator:
                            objPregunta.validaciontexto.add( validacionTexto(v) )
                            objPregunta.save()
                        

                    if len(Yopciones_code) > 0:
                        
                        objMatrizY = MatrizY(
                            pregunta = objPregunta,
                            nombre = Yopciones_name,
                            codigo = Yopciones_code,
                            activo = True
                        )
                        objMatrizY.save()

                    if len(Xopciones_code) > 0:
                        
                        objMatrizX = MatrizX(
                            pregunta = objPregunta,
                            nombre = Xopciones_name,
                            codigo = Xopciones_code,
                            activo = True
                        )
                        objMatrizX.save()

            transaction.commit()
        except Exception ,error_r:
            err = error_r
            transaction.rollback()

    return render_to_response('cuestionario/subirarchivo.html',{'POST':'post','error_r':err,'sumulador':id_cuestionario}, context_instance=RequestContext(request))

def login(request):
    if request.method == 'GET':
        return render_to_response('cuestionario/login.html',context_instance=RequestContext(request))
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)

    if user is not None and user.is_active:
        auth.login(request, user)
        request.POST
        return HttpResponseRedirect("/inicio/")
    else:
        return render_to_response('cuestionario/login.html',{'errors':'errors'},context_instance=RequestContext(request))

@login_required()
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/login/")

@login_required()
def crearProyecto(request):
    objCuestionario = Cuestionario.objects.filter(activo=True).order_by('-id')

    liga = ""
    id_pro= ""

    if request.POST:
        nombreProyecto = request.POST['name_proy']
        strCuestionatio = request.POST['strcuestionario']

        objCues = Cuestionario.objects.get(pk=int(strCuestionatio))
        objGrupo = GrupoCuestionario.objects.filter(cuestionario=objCues).order_by("numero")[0]

        p = Proyecto(nombre=nombreProyecto,cuestionario=objCues,activo=True)
        p.save()

        id_pro = str(p.id)

        liga = "/djpoll/" + str(p.id) + "/"
        
    return render_to_response('cuestionario/proyecto.html', {
        'objCuestionario': objCuestionario,
        'id_pro':id_pro,
        'liga':liga},
         context_instance=RequestContext(request))


#ISC. Miguel Soltero <figo10mexico@gmail.com>