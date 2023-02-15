import tkinter as tk
from bot import Bot
from utils import Utils

class Interfaz(tk.Frame):

    def __init__(self,master=None) -> None:
        super().__init__(master)
        self.root = master
        self.generateElements(Utils.loadCredentials())
    
    def clearInput(self,event):
        if event.widget.get()=="usuario" or event.widget.get()=="contraseña":
            event.widget.delete(0,len(event.widget.get()))
            event.widget.config(fg="black")

    def runBot(self,result):
        userProducetext = self.inputUserProduce.get()
        PassProducetext = self.passUserProduce.get()
        if userProducetext!="" and PassProducetext!="":
            if result==None or (result[0]!=userProducetext or result[1]!=PassProducetext):
                Utils.setCredentials(userProducetext,PassProducetext)
            Bot(userProduce=userProducetext,passProduce=PassProducetext)

    def generateElements(self,result):
        tk.Label(self.root,text="Produce").place(x=130,y=30,height=20)
        self.btRunBot = tk.Button(self.root,text="Lanzar Bot",command=lambda :self.runBot(result))
        self.btRunBot.place(x=120,y=100) 
        if result==None:
            self.inputUserProduce = tk.Entry(self.root,fg='grey')
            self.inputUserProduce.insert(0,"usuario")
            self.inputUserProduce.bind("<FocusIn>", self.clearInput)
            self.passUserProduce = tk.Entry(self.root,fg='grey',show="*")
            self.passUserProduce.insert(0,"contraseña")
            self.passUserProduce.bind("<FocusIn>", self.clearInput)
        else:
            self.inputUserProduce = tk.Entry(self.root)
            self.passUserProduce = tk.Entry(self.root,show="*")
            self.inputUserProduce.place(x=60,y=60,width=80,height=20)
            self.passUserProduce.place(x=160,y=60,width=80,height=20)
            self.inputUserProduce.insert(0,result[0])
            self.passUserProduce.insert(0,result[1])
             

if __name__ == '__main__':
    #root config
    root = tk.Tk()
    root.title("BOT IMPUTACIÓN")
    alignstr = '%dx%d+%d+%d' % (320, 195, (root.winfo_screenwidth() - 320) / 2, ( root.winfo_screenheight() - 195) / 2)
    root.geometry(alignstr)
    root.resizable(width=False, height=False)
    app = Interfaz(master=root)
    app.mainloop()