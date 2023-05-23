from decimal import Decimal
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement 
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import Select
import imputacion_v2 as imp

class Imputacion:

    browser:webdriver.Chrome=None 
    tiempo_base=None
    project = ""

    def __init__(self,browser,tiempo_base,project):
        self.browser=browser
        self.tiempo_base=tiempo_base
        self.project = project

    def completarHasta8H(self,fecha):#OK
        total = self.obtenerTotalHorasImputadas(fecha[4:8]+"-"+fecha[2:4]+"-"+fecha[0:2])
        imputarHorasRestante = Decimal(8.0)-Decimal(total)
        if imputarHorasRestante!=0:
            ano=fecha[4:8]
            self.browser.execute_script("window.scrollTo(0, 0)")
            self.browser.find_element(By.LINK_TEXT,"Cajamar-ZEUS").click()
            self.waitPage(self.browser.find_element(By.ID,"loading"))
            self.browser.find_elements(By.CLASS_NAME,"sorting_1")[0].click()
            self.waitPage(self.browser.find_element(By.ID,"loading"))
            sleep(0.3)
            self.browser.find_elements(By.CLASS_NAME,"sorting_1")[1].find_element(By.TAG_NAME,"a").click()
            self.waitPage(self.browser.find_element(By.ID,"datatable_processing"))
            Select(self.browser.find_element(By.NAME,"datatable_length")).select_by_value("-1")
            lista = self.browser.find_elements(By.CLASS_NAME,"storyName")
            for l in lista:
                if l.get_attribute('innerHTML')=="Actividad sin Remedy "+ano:
                    self.browser.execute_script("window.scrollTo(0,"+str(l.rect.get("y"))+")")
                    l.click()
                    break
            self.waitPage(self.browser.find_element(By.ID,"datatable_processing"))
            self.browser.execute_script("window.scrollTo(0, 120)")
            id = self.browser.find_element(By.XPATH,"//span[text()='OTROS']/parent::*/parent::*/parent::*").get_attribute("id")
            self.browser.find_element(By.ID,id).find_element(By.CLASS_NAME,"incurrir").click()
            self.waitPage(self.browser.find_element(By.ID,"loading"))
            fecha_impu = fecha[0:2]+"-"+fecha[2:4]+"-"+fecha[4:8]
            self.imputarRemedy(fecha_impu,imputarHorasRestante,descripcion="Otras tareas")

    def posicionarMes(self,fecha):#OK
        result = self.browser.find_element(By.CLASS_NAME,"fc-center").text
        meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        sp = result.split(" ")
        if fecha[4:8]==sp[1] or int(fecha[4:8])<int(sp[1]):
            if int(fecha[2:4]) - meses.index(sp[0])+1==1 or int(sp[1])-int(fecha[4:8])==1:
                self.browser.find_element(By.CLASS_NAME,"fc-button-group").find_element(By.CLASS_NAME,"fc-corner-left").click()
                self.waitPage(self.browser.find_element(By.ID,"loading"))
        else:
            print("No debe de aplicar el fichero, no se puede imputar a futuro")

    def transformRemedy(self,remedy:str):#ok
        distint0=False
        index = 0
        for x in remedy:
            if(x!="0"):
                distint0=True
            else:
                if not distint0:
                    index+=1
        return remedy[index:len(remedy)]

    def obtenerTotalHorasImputadas(self,fecha)->WebElement|int:#OK
        firsts = self.browser.find_elements(By.CLASS_NAME,"fc-content-skeleton")
        for f in firsts:
            try:
                element=f.find_element(By.CSS_SELECTOR,"td[data-date='"+fecha+"']")
                try:
                    x = element.find_element(By.CLASS_NAME,"incurred-day-total").find_element(By.CLASS_NAME,"number").get_attribute('innerHTML')
                    element.click()
                    return x
                except:
                    return 0
            except:
                pass

    def imputadoEsPendiente(self):#OK
        tarea = self.browser.find_element(By.CLASS_NAME,"evento").find_element(By.CLASS_NAME,"tarea")
        try:
            a = tarea.find_element(By.LINK_TEXT,"REMEDYS PENDIENTES DE CARGAR")
            scriptString = "sId=function(e, i){e.id = i;};sId(arguments[0], arguments[1]);"
            self.browser.execute_script(scriptString,a,"pdt")
            self.browser.execute_script("document.getElementById('pdt').parentNode.getElementsByClassName('delete-timeEntry')[0].click()")
            sleep(0.5*self.tiempo_base)
            modal = self.browser.find_element(By.ID,"borradoConfirmacionModal")
            modal.find_element(By.CLASS_NAME,"aceptar").click()
            sleep(0.5*self.tiempo_base)
            return True
        except NoSuchElementException:
            return False
            
    def controlTotalHoras(self,fecha):#OK
        total = self.obtenerTotalHorasImputadas(fecha)
        if(float(total)>=8.0):
            return self.imputadoEsPendiente()
        else:
            return True

    def manageRemedy(self,remedy:str,tiempo:float,descripcion:str,fecha):#OK
        #search remedy
        if remedy.startswith("0"):
            remedy = self.transformRemedy(remedy)
        self.browser.execute_script("window.scrollTo(0, 0)") 
        self.browser.find_element(By.CLASS_NAME,"fa-search").click()
        search_padre = self.browser.find_element(By.CLASS_NAME,"idsearch_dos")
        search_padre.find_element(By.CLASS_NAME,"form-control").send_keys(remedy)
        sleep(0.5*self.tiempo_base)
        iconos = search_padre.find_element(By.CLASS_NAME,"float_rigth")
        iconos.find_element(By.TAG_NAME,"input").click()
        sleep(0.5*self.tiempo_base)
        #list of found remedys
        try:
            tabla = self.browser.find_element(By.ID,"objecttableCUso")
            lista = tabla.find_elements(By.TAG_NAME,"tr")
            for iter in lista:
                try:
                    if iter.find_elements(By.TAG_NAME,"td")[1].get_attribute('innerHTML').__contains__(self.project):
                        iter.find_element(By.LINK_TEXT,remedy).click()
                        break
                except:
                    pass
            self.waitPage(self.browser.find_element(By.ID,"loading"))
            sleep(1)
            self.browser.find_element(By.CLASS_NAME,"incurrir").click()
            self.imputarRemedy(fecha[0:2]+"-"+fecha[2:4]+"-"+fecha[4:8],tiempo,descripcion=descripcion)
            print(remedy+" imputado")
        except:
            return " - "+remedy

    def controlRemedyYaImputado(self,fecha,remedy:str):#OK
        if remedy.startswith("0"):
            remedy = self.transformRemedy(remedy)
        print("remedy a controlar "+remedy)
        firsts = self.browser.find_elements(By.CLASS_NAME,"fc-content-skeleton")
        for f in firsts:
            try:
                element=f.find_element(By.CSS_SELECTOR,"td[data-date='"+fecha+"']")
                self.browser.execute_script("window.scrollTo(0,"+str(element.rect.get("y"))+")")
                element.click()
                break
            except:
                pass
        try:
            ventana = self.browser.find_element(By.CLASS_NAME,"ventanaIncurridos")
            iteraciones = ventana.find_elements(By.CLASS_NAME,"iteracion")
            encontrado=False
            for iter in iteraciones:
                if encontrado:
                    break
                padre = iter.find_elements(By.CLASS_NAME,"casoUso")
                for p in padre:
                    try:
                        ps = p.find_element(By.CLASS_NAME,"casoUso")
                        ps.find_element(By.TAG_NAME,"span").find_element(By.LINK_TEXT,remedy)
                        encontrado=True
                        break
                    except:
                        encontrado=False
            return encontrado
        except:
            return False

    def remedysNoDisponible(self,fecha,remedysNoDisponiblesAun):#OK
        total = self.obtenerTotalHorasImputadas(fecha[4:8]+"-"+fecha[2:4]+"-"+fecha[0:2])
        self.waitPage(self.browser.find_element(By.ID,"loading"))
        al = self.browser.find_element(By.LINK_TEXT,"Cajamar-ZEUS")
        self.browser.execute_script("window.scrollTo(0, "+str(al.rect.get("y"))+")")
        al.click()
        sleep(0.5*self.tiempo_base)
        self.browser.find_elements(By.CLASS_NAME,"sorting_1")[0].click()
        sleep(0.7*self.tiempo_base)
        self.browser.find_elements(By.CLASS_NAME,"sorting_1")[1].find_element(By.TAG_NAME,"a").click()
        self.waitPage(self.browser.find_element(By.ID,"datatable_processing"))
        el = self.browser.find_element(By.ID,"tr_879190").find_element(By.CLASS_NAME,"storyId")
        self.browser.execute_script("window.scrollTo(0, "+str(el.rect.get("y"))+")")
        el.click()
        sleep(0.7*self.tiempo_base)
        self.browser.find_element(By.ID,"tr_2729886").find_element(By.CLASS_NAME,"incurrir").click()
        sleep(0.5*self.tiempo_base)
        self.imputarRemedy(fecha[0:2]+"-"+fecha[2:4]+"-"+fecha[4:8],8-float(total),remedysNoDisponiblesAun)
        
    def waitPage(self,load:WebElement):#OK
        while(True):
            sleep(0.3)
            if load.get_attribute("style").split(" ")[1].split(";")[0]!="block":
                break
                
    def imputarRemedy(self,fecha,tiempo,remedyNoImputados=None,descripcion=None):#OK
        tiempo = float(str(tiempo).replace(",","."))
        inputFecha = self.browser.find_element(By.ID,"single_cal2")
        self.browser.execute_script("arguments[0].removeAttribute('readonly')", inputFecha)
        sleep(0.6*self.tiempo_base)
        self.browser.execute_script("arguments[0].value=arguments[1]", inputFecha,"")
        sleep(0.8*self.tiempo_base)
        inputFecha.send_keys(fecha)
        sleep(0.4*self.tiempo_base)
        #seteo tiempo
        self.browser.find_element(By.CLASS_NAME,"hrs").send_keys(tiempo)
        #descripcion
        if remedyNoImputados!=None:
            self.browser.find_element(By.CLASS_NAME,"descripcion").send_keys("Pendientes"+remedyNoImputados)
        if descripcion!=None:
            self.browser.find_element(By.CLASS_NAME,"descripcion").send_keys(descripcion)
        #Añadir imputación
        #ocultar calendario para que deje darle al boton
        calendar = self.browser.find_element(By.CLASS_NAME,"daterangepicker")
        self.browser.execute_script("arguments[0].setAttribute('style', 'display: none;')", calendar)
        self.browser.find_element(By.CLASS_NAME,"Modificar").click()