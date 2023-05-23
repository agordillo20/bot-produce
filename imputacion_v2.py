import httpx
from bs4 import BeautifulSoup
import datetime
import tkinter as tk
import json
from threading import Thread
from decimal import Decimal

class imputacion:
    url_base="https://produce.viewnext.com/produce"
    url_login = "/do/login"
    url_search = "/do/search/content?searchedContent=?1"
    url_delete = "/JSONTimeEntries"
    url_imputar = "/do/edit/time"
    url_tareas ="/JSONDataTareas?listadoTareasPorCasoUso=true&storyId=?1&status=Todas"
    url_tareas_v2 = "/JSONDataCasosUso?iterationId=?1&status=listarTodos"
    url_horas = "/JSONServletMisHoras"
    proyecto_definido = "320210017E"
    parser = "html.parser"
    year = str(datetime.date.today().year)
    continuar = True

    def __init__(self,proyecto,user,pwd,serv,impresora,root:tk.Frame):
        self.serv = serv
        self.root = root
        self.output = impresora
        self.proyecto_definido = proyecto
        self.login(user,pwd)
        if(self.continuar):
            Thread(target=self.init_triajes).start()
            Thread(target=self.init_sin_remedy).start()
            Thread(target=self.init_pdt_carga).start()
            Thread(target=self.init_indisponibilidad).start()
            self.user_id = BeautifulSoup(self.make_get_request("/do/view/preprincipal").text,self.parser).find(id="oid").attrs['value']
            self.imprimir("carga inicial finalizada")

    def imprimir(self,text):
        self.output.insert("end",text+"\n")
        self.output.see("end")
        self.root.update()
        
    def login(self,user,pwd):
        payload = {"userId":user,"password":pwd,"button":"Acceder","action":"Acceder"}
        request_login = httpx.post(self.url_base+self.url_login,data=payload,verify=False)
        self.cookies = request_login.cookies
        if request_login.status_code==302:
            self.imprimir("login correcto")
        else:
            self.imprimir("Credenciales incorrectos")
            self.continuar = False
        
    def init_indisponibilidad(self):
        url_indisponibilidad = self.search_element('Indisponibilidad Técnica',self.year,"objecttableIter")
        self.url_indisponibilidad = self.search_task(url_indisponibilidad,self.year,True)

    def init_sin_remedy(self):
        result = self.search_element('Actividad sin Remedy '+self.year,['HANDOVER','BUZON','GESTIÓN'])
        self.url_handover = result[0]
        self.url_buzon = result[1]
        self.url_gestion = result[2]

    def init_pdt_carga(self):
        self.url_pdt_carga = self.search_element("REMEDYS PENDIENTES DE CARGAR",None)
    
    def init_triajes(self):
        result = self.search_element('triaje',['NUCLEO','ACTIVO','PASIVO','SERVICIOS BASE','SERVICIOS INTERBANCARIOS','RIESGOS'])
        self.url_triaje_nucleo = result[0]
        self.url_triaje_activo = result[1]
        self.url_triaje_pasivo = result[2]
        self.url_triaje_servicios_base= result[3]
        self.url_triaje_servicios_interbancarios = result[4]
        self.url_triaje_riesgos = result[5]

    def make_get_request(self,url):
        return httpx.get(self.url_base+url,
                        verify=False,
                        follow_redirects=True,
                        headers={"Cookie":"JSESSIONID="+self.cookies['JSESSIONID']},timeout=12)

    def make_post_request(self,url,payload):
        return httpx.post(self.url_base+url,
                        data=payload,
                        verify=False,
                        headers={"Cookie":"JSESSIONID="+self.cookies['JSESSIONID']},timeout=12)
    
    def imputar(self,url:str,fecha:str,tiempo:str,desc:str):
        req = self.make_get_request(url.replace("/produce",""))
        bs = BeautifulSoup(req.text,self.parser)
        form = bs.select_one("form[name='timelog']")
        payload = {"oid":form.select_one("input[name='oid']").attrs['value'],
                "fkey":form.select_one("input[name='fkey']").attrs['value'],
                "taskId":form.select_one("input[name='taskId']").attrs['value'],
                "tipoPresenciaSap":form.select_one("input[name='tipoPresenciaSap']").attrs['value'],
                "motivo":form.select_one("input[name='motivo']").attrs['value'],
                "taskFInicio":form.select_one("input[name='taskFInicio']").attrs['value'],
                "taskFFin":form.select_one("input[name='taskFFin']").attrs['value'],
                "projectId":form.select_one("input[name='projectId']").attrs['value'],
                "returnto":form.select_one("input[name='returnto']").attrs['value'],
                "action":form.select_one("input[name='action']").attrs['value'],
                "reportDate[0]":fecha,
                "reportDateEnd[0]":form.select("#single_cal2")[1].attrs['value'],
                "duration[0]":tiempo,
                "horasDia[0]":"0" if form.select_one(".horasDia").attrs['value']=="" else form.select_one(".horasDia").attrs['value'],
                "remainingHours":form.select_one("input[name='remainingHours']").attrs['value'],
                "person1Id[0]":form.select_one(".personId").attrs['value'],
                "description[0]":desc,
                "entryId[0]":form.select_one(".entryId").attrs['value'],
                "emptyRow[0]":form.select_one(".emptyRow").attrs['value'],
                "version[0]":form.select_one(".version").attrs['value'],
                "rowcount":1,
                "laborables[0]":form.select_one(".laborables").attrs['value'],
                "tipoTrabajo[0]":form.select_one("input[name='tipoPresenciaSap']").attrs['value'][1:4]+"#"+self.proyecto_definido+"#000010"
                }
        self.make_post_request(self.url_imputar,payload)
        self.imprimir("imputado")

    def search_task(self,link:str,hijo:str|list,version:bool):
        oid = link.split("=")[1]
        url = self.url_tareas.replace("?1",oid) if version else self.url_tareas_v2.replace("?1",oid)
        req_tarea = self.make_post_request(url,None)
        response = req_tarea.json()
        if response['recordsTotal']==1:
            try:
                sp = BeautifulSoup(response['data'][0]['acciones'],self.parser)
                return sp.select_one(".incurrir").attrs['href']
            except:
                sp = BeautifulSoup(response['data'][0]['id'],self.parser)
                return sp.find("a").attrs['href']
        else:
            if hijo!=None:
                if type(hijo) == str:
                    try:
                        html = self.filter_json(hijo,"tarea",response['data'])
                        sp = BeautifulSoup(html[0]['acciones'],self.parser)
                        return sp.select_one(".incurrir").attrs['href']
                    except:
                        html = self.filter_json(hijo,"nombre",response['data'])
                        sp = BeautifulSoup(html[0]['id'],self.parser)
                        return sp.select_one("a").attrs['href']
                else:
                    lista = []
                    for iter in hijo:
                        sp = BeautifulSoup(self.filter_json(iter,"tarea",response['data'])[0]['acciones'],self.parser)
                        lista.append(sp.select_one(".incurrir").attrs['href'])
                    return lista
            else:
                self.imprimir("Error no controlado!!!! reportar")
                
    def get_url_triaje(self):
        if(self.serv=="Nucleo"):
            return self.url_triaje_nucleo
        elif(self.serv=="Activo"):
            return self.url_triaje_activo
        elif(self.serv=="Pasivo"):
            return self.url_triaje_pasivo
        elif(self.serv=="Servicios Base"):
            return self.url_triaje_servicios_base
        elif(self.serv=="Servicios Interbancarios"):
            return self.url_triaje_servicios_interbancarios
        elif(self.serv=="Riesgos"):
            return self.url_triaje_riesgos
    
    def search_element(self,search:str,hijo:str|list,id_busqueda:str="objecttableCUso"):
        if search.startswith("0"):
            search = self.transform_remedy(search)
            self.imprimir("buscando remedy... "+search)
        elif search.startswith("IGH"):
            self.imprimir("buscando remedy... "+search)
        elif search == 'H':
            self.imprimir("imputando a Handover")
            return self.url_handover
        elif search == 'B':
            self.imprimir("imputando a buzon")
            return self.url_buzon
        elif search == 'G':
            self.imprimir("imputando a gestion")
            return self.url_gestion
        elif search == 'T':
            self.imprimir("imputando a triaje")
            return self.get_url_triaje()
        elif search == 'I':
            self.imprimir("imputando a indisponibilidad técnica")
            return self.url_indisponibilidad
        
        request = self.make_get_request(self.url_search.replace("?1",search))
        soup = BeautifulSoup(request.text, self.parser)
        parent = soup.find(id=id_busqueda)
        if parent!=None:
            parent = parent.select("tr")
            for p in parent:
                proyecto = str(p.select("td:nth-of-type(2)")).split(":")[1].split(">")[1]
                link = p.select_one("td > a",class_="sorting_1").attrs['href']
                if proyecto==self.proyecto_definido:
                    return self.search_task(link,hijo,id_busqueda=="objecttableCUso")
        
    def transform_remedy(self,remedy:str):
        distint0=False
        index = 0
        for x in remedy:
            if(x!="0"):
                distint0=True
            else:
                if not distint0:
                    index+=1
        return remedy[index:len(remedy)]
    
    def filter_json(self,busqueda,campo,datos):
        return list(filter(lambda x:busqueda in x[campo],datos))
    
    def get_actual_data(self):
        payload_search = {
            "oid":str(self.user_id),
            "verifParteUsuarioDistinto":"false",
            "mes":str(self.fecha[2:4]),
            "anno":str(self.fecha[4:8])
        }
        self.datos = self.make_post_request(self.url_horas,payload_search).json()

    def set_dates(self,fecha,fecha1):
        self.fecha = fecha
        self.fecha1 = fecha1

    def check_pdt_remedy(self):
        fecha_parsed = self.fecha[4:8]+"-"+self.fecha[2:4]+"-"+self.fecha[0:2]
        print(self.url_pdt_carga)
        oid_pdt = self.url_pdt_carga.split("oid=")[1].split("&")[0]
        for iter in json.loads(self.datos['cuerpo']):
            if(fecha_parsed in iter['start']):
                bs = BeautifulSoup(iter['description'],self.parser)
                tareas=bs.select("ul.tarea > li")
                for tarea in tareas:
                    url_task_parent =tarea.select_one("a:not(.delete-timeEntry)").attrs['href']
                    if oid_pdt in url_task_parent:
                        id_task = tarea.attrs['class'][1].split("timeEntry-")[1]
                        payload_delete={
                            "accion":"deleteVarios",
                            "ids[]":id_task
                        }
                        self.make_post_request(self.url_delete,payload_delete)
                        self.imprimir("borrado pdt de carga")
                        break
                break

    def check_remedy_is_imputed(self,remedy):
        fecha_parsed = self.fecha[4:8]+"-"+self.fecha[2:4]+"-"+self.fecha[0:2]
        if remedy == 'H':
            remedy = "HANDOVER"
        elif remedy == 'B':
            remedy = "BUZON"
        elif remedy == 'G':
            remedy = "GESTIÓN"
        elif remedy == 'T':
           remedy = "TRIAJE"
        elif remedy == 'I':
            remedy = "Indisponibilidad Técnica"
        for iter in json.loads(self.datos['cuerpo']):
            if(fecha_parsed in iter['start']):
                bs = BeautifulSoup(iter['description'],self.parser)
                self.imprimir("YA IMPUTADO ? "+str(remedy in bs.text))
                return remedy in bs.text
        
    def check_if_remedy_is_imputable(self,fecha):
        try:
            fecha_parsed = fecha[4:8]+"-"+fecha[2:4]+"-"+fecha[0:2]
            result = self.filter_json(fecha_parsed,"date",self.datos['mapaHorasSuman'])
            return Decimal(result[0]['value'])
        except:
            return Decimal(0)

