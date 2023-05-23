from tkinter.filedialog import askopenfilename
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement 
from selenium.common.exceptions import *
from Imputaciones import Imputacion

import os

class Bot():

    vpn:bool = False
    userProduce:str
    passProduce:str
    userZS:str
    passZS:str

    def __init__(self,userProduce:str,passProduce:str,project:str) -> None:
        self.init(project)
        self.loadProduce(userProduce,passProduce)
        self.leerFichero()

    def init(self,project):
        self.url_produce = "https://produce.viewnext.com/produce/do/login"
        self.url_produce_home = "https://produce.viewnext.com/produce/do/view/preprincipal?aleat=0.08351092456268738"
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(options=self.chrome_options)
        self.browser.maximize_window()
        self.imputacion = Imputacion(self.browser,3,project)
            
    def loadProduce(self,userProduce,passProduce):
        self.browser.get(self.url_produce)
        self.browser.find_element(By.NAME,"userId").send_keys(userProduce)
        self.browser.find_element(By.NAME,"password").send_keys(passProduce)
        self.browser.find_element(By.CLASS_NAME,"submit").click()

    def leerFichero(self):
        filename_list = askopenfilename(multiple=True,filetypes=[('txt','*.txt')])
        for filename in filename_list:
            remedysNoDisponiblesAun = ""
            fecha = os.path.basename(filename)
            fecha1 = fecha[4:8]+"-"+fecha[2:4]+"-"+fecha[0:2]
            print("leyendo de: "+fecha1)
            procesable = self.imputacion.controlTotalHoras(fecha1)
            if procesable:
                file = open(filename, "r")
                for linea in file:
                    spliteo = linea.split(";")
                    longitud = len(spliteo)
                    if longitud<2 or longitud >3:
                        print("no se puede realizar imputación con los datos introducidos")
                    else:
                        self.imputacion.posicionarMes(fecha)
                        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                        if not self.imputacion.controlRemedyYaImputado(fecha1,spliteo[0]):
                            result = self.imputacion.manageRemedy(spliteo[0],spliteo[1],None if longitud == 2 else spliteo[2],fecha)
                            if result!=None:
                                remedysNoDisponiblesAun=remedysNoDisponiblesAun+result
                            self.browser.get(self.url_produce_home)
                            self.imputacion.waitPage(self.browser.find_element(By.ID,"loading"))
                        else:
                            print("remedy "+spliteo[0]+" ya imputado")
                if remedysNoDisponiblesAun=="":
                    self.imputacion.completarHasta8H(fecha)
                else:
                    self.browser.get(self.url_produce_home)
                    self.imputacion.remedysNoDisponible(fecha,remedysNoDisponiblesAun)
                self.browser.get(self.url_produce_home)
                self.imputacion.waitPage(self.browser.find_element(By.ID,"loading"))
            else:
                print("ya se han alcanzado el total de horas y no se puede imputar más")