import os

class Utils:

    def loadCredentials():#repasar la carga
        user_produce:str
        pass_produce:str
        user_zs:str = None
        pass_zs:str = None
        try:
            file = open("credentials.txt", "x")
            return None
        except:
            file = open("credentials.txt", "r")
            lineas = file.readlines()
            total = len(lineas)
            if total >= 1:
                linea_produce = lineas[0].split("#separador#")
                user_produce = linea_produce[0]
                pass_produce = linea_produce[1].replace("\n","")
            if total==2:
                linea_zs = lineas[1].split("#separador#")
                user_zs = linea_zs[0]
                pass_zs = linea_zs[1]
            else:
                return None
            return [user_produce,pass_produce,user_zs,pass_zs]

    def setCredentials(user_produce:str,pass_produce:str,user_zs:str = None,pass_zs:str = None):
        file = open("credentials.txt", "w")
        if user_zs!=None and pass_zs!=None:
            file.write('{}\n{}'.format(user_produce+"#separador#"+pass_produce,user_zs+"#separador#"+pass_zs))
        else:
            file.write('{}\n'.format(user_produce+"#separador#"+pass_produce))
        file.close()