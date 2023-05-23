from pathlib import Path

class Utils:
    
    def loadCredentials():
        if Path('./credentials.txt').is_file():
            file = open("credentials.txt","r")
            result = file.read().split("#separador#")
            file.close()
            return result if len(result)>1 else None 
        else:
            return None
    
    def setCredentials(user:str,pwd:str):
        file = open("credentials.txt","w+")
        file.write(user+"#separador#"+pwd)
        file.close()
