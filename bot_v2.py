from io import TextIOWrapper
from tkinter.filedialog import askopenfilename
import imputacion_v2 as imp
import os
from decimal import Decimal
import tkinter as tk
from threading import Thread

class Bot():

    imputador:imp.imputacion
    acumulador = 0
    not_avaliable = "remedys: "
    threads = []
    filename = ""

    #ver si pasar el imp.imputacion para evitar hacer el login y la carga de las url iniciales multiples veces
    def __init__(self,user:str,pwd:str,project:str,serv:str,impresora,root:tk.Frame):
        self.root = root
        self.output = impresora
        self.imputador = imp.imputacion(user=user,pwd=pwd,proyecto=project,serv=serv,impresora=impresora,root=root)
        if(self.imputador.continuar):
            self.leer_fichero()

    def leer_fichero(self):
        for filename in askopenfilename(multiple=True,filetypes=[('txt','*.txt')]):
            self.acumulador = 0 #reset contador para que no se trafuque xd
            self.filename = filename
            f = open(self.filename, "r+")
            self.delete_empty_lines(f)
            if self.validity_file(f):#Comprueba que en el fichero no haya mas de 8H 
                self.imprimir("FICHERO VALIDO")
                result = self.is_necesary_transform(f)#Se compruba si es necesario transformar el fichero(Caso triajes)
                if result != None:
                    self.imprimir("TRANSFORMANDO FICHERO")
                    self.transform_file(result,f)#Se transforma el fichero
                    self.delete_empty_lines(f)
                    self.imprimir("FICHERO TRANSFORMADO")
                self.read_file(f)#Se lee y procesa el fichero
            else:
                self.imprimir("el fichero "+self.filename+ " no es valido, revisar")
            f.close()
        self.imprimir("imputacion finalizada")

    def imprimir(self,text):
        self.output.insert("end",text+"\n")
        self.output.see("end")
        self.root.update()

    def read_file(self,f:TextIOWrapper):
        fecha = os.path.basename(self.filename)
        fecha1 = fecha[0:2]+"-"+fecha[2:4]+"-"+fecha[4:8]
        self.imputador.set_dates(fecha,fecha1)
        self.imprimir("leyendo de: "+fecha1)
        self.imputador.get_actual_data()
        self.imputador.check_pdt_remedy()
        self.tiempo_ya_imputado = self.imputador.check_if_remedy_is_imputable(fecha1)
        f.seek(0)
        for linea in f:
           self.process(fecha1,linea)
        if self.acumulador!=0:
            self.imputador.get_actual_data()
            tiempo = self.imputador.check_if_remedy_is_imputable(fecha1)
            if tiempo + self.acumulador<=Decimal(8):
                Thread(target=self.imputador.imputar(self.imputador.url_pdt_carga,fecha1,self.acumulador,self.not_avaliable)).start()
            else:
                self.imprimir("no se puede imputar los pdt de carga porque sobrepasan las 8H.")
    
    def delete_empty_lines(self,file:TextIOWrapper):
        lineas = file.readlines()
        total = len(lineas)
        borradas = 0
        for i in range(total):
            if lineas[i-borradas]=="\n":
                lineas.pop(i-borradas)
                borradas+=1
        ultima = lineas[len(lineas)-1]
        if ultima.endswith("\n"):
            ultima = ultima.removesuffix("\n")
            lineas[len(lineas)-1] = ultima
        file.seek(0)
        file.writelines(lineas)    
        file.truncate()
        file.seek(0)  
      
    def validity_file(self,file:TextIOWrapper):
        acumulador=0
        for linea in file:
            acumulador+=Decimal(linea.split(";")[1])
        file.seek(0) 
        return acumulador<=8.0
    
    def is_necesary_transform(self,file:TextIOWrapper):
        for linea in file:
            sp = linea.split(";")
            if(sp[0]=="T" and len(sp)==3):
                return linea
    
    def transform_file(self,linea:str,file:TextIOWrapper):
        file.seek(0)
        lineas = file.readlines()
        lineas.remove(linea)
        sp = linea.split(";")
        tiempo = Decimal(sp[1])
        remedys = sp[2].split("-")
        if(len(remedys)>0):
            time_for_each = round(tiempo/len(remedys),2)
            for index,remedy in enumerate(remedys):
                if index==0:
                    new_time = time_for_each+tiempo-(time_for_each*len(remedys))
                    new_linea = "\n"+remedy.replace("\n","")+";"+str(new_time)+";triajes"
                else:
                    new_linea = "\n"+remedy.replace("\n","")+";"+str(time_for_each)+";triajes"
                lineas.append(new_linea)
            file.seek(0)
            file.writelines(lineas)
            file.truncate()
        file.seek(0)
            
    def process(self,fecha,linea:str):
        spliteo = linea.split(";")
        longitud = len(spliteo)
        if longitud<2 or longitud >3:
            self.imprimir("no se puede realizar imputación con los datos introducidos !!!")
        else:
            tiempo_remedy = spliteo[1]
            remedy = spliteo[0]
            if self.tiempo_ya_imputado + Decimal(tiempo_remedy)<=Decimal(8):
                if not self.imputador.check_remedy_is_imputed(remedy):
                    url_task = self.imputador.search_element(remedy,None)
                    if url_task!=None:
                        self.tiempo_ya_imputado+=Decimal(tiempo_remedy)
                        Thread(target=self.imputador.imputar(url_task,fecha,tiempo_remedy,"" if longitud == 2 else spliteo[2])).start()
                    else:
                        self.not_avaliable+=" "+remedy
                        self.acumulador+=Decimal(spliteo[1])
                        self.imprimir("remedy aun no cargado, añadido a la lista de pendientes de cargar")
                else:
                    self.imprimir("Remedy ya se encuentra imputado, saltando")
            else:
                self.imprimir("Remedy no imputable, se superan las 8H con su imputación, revisar.")
        
        
