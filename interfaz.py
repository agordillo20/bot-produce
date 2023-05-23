import tkinter as tk
from bot_v2 import Bot
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
            Bot(userProducetext,PassProducetext,project = self.lb_proyect.get(self.lb_proyect.curselection()),serv=self.lb_serv.get(self.lb_serv.curselection()),impresora=self.output,root=root)

    def generateElements(self,result):
        canvas = tk.Canvas()
        tk.Label(self.root,text="Produce",font='Helvetica 16 bold').place(x=240,y=10,height=20)
        tk.Label(self.root,text="Credenciales").place(x=200,y=51,height=20)
        tk.Label(self.root,text="Configuracion proyecto").place(x=140,y=151,height=20)
        canvas.create_rectangle(20,60,280,110,width=1,outline="black")
        canvas.create_rectangle(20,160,280,250,width=1,outline="black")
        canvas.place(x=0,y=0)
         
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
            self.inputUserProduce.insert(0,result[0])
            self.passUserProduce.insert(0,result[1])

        self.inputUserProduce.place(x=40,y=80,width=80,height=20)
        self.passUserProduce.place(x=160,y=80,width=80,height=20)

        #Listbox de los proyectos
        self.lb_proyect = tk.Listbox(self.root,exportselection=False)
        self.lb_proyect.insert(1,"320210017E")
        self.lb_proyect.insert(2,"320210017L")
        self.lb_proyect.insert(3,"320210017G")
        self.lb_proyect.insert(4,"320210017D")
        self.lb_proyect.place(x=180,y=180,height=50,width=80)
        scrollbar = tk.Scrollbar(self.root)
        scrollbar.place(in_=self.lb_proyect,x=80,bordermode="outside")
        self.lb_proyect.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.lb_proyect.yview)
        self.lb_proyect.select_set(0)
        self.lb_proyect.event_generate("<<ListboxSelect>>")

        #Listbox de los grupos de servicios
        self.lb_serv = tk.Listbox(self.root,exportselection=False)
        self.lb_serv.insert(1,"Nucleo")
        self.lb_serv.insert(2,"Activo")
        self.lb_serv.insert(3,"Pasivo")
        self.lb_serv.insert(4,"Servicios Base")
        self.lb_serv.insert(5,"Servicios Interbancarios")
        self.lb_serv.insert(6,"Riesgos")
        self.lb_serv.place(x=30,y=180,height=50,width=120)
        scrollbar_1 = tk.Scrollbar(self.root)
        scrollbar_1.place(in_=self.lb_serv,x=120,bordermode="outside")
        self.lb_serv.config(yscrollcommand=scrollbar_1.set)
        scrollbar_1.config(command=self.lb_serv.yview)
        self.lb_serv.select_set(4)
        self.lb_serv.event_generate("<<ListboxSelect>>")

        self.btRunBot = tk.Button(self.root,text="Lanzar Bot",command=lambda :self.runBot(result))
        self.btRunBot.place(x=250,y=340)

        self.output = tk.Text(self.root,height=18,width=39,background="BLACK",fg="WHITE",font="CONSOLAS 9",padx=2,pady=2)
        self.output.place(x=300,y=60)
        self.output.bind("<Key>", lambda e: "break")

if __name__ == '__main__':
    #root config
    root = tk.Tk()
    root.title("BOT IMPUTACIÓN")
    alignstr = '%dx%d+%d+%d' % (600, 400, (root.winfo_screenwidth() - 600) / 2, ( root.winfo_screenheight() - 400) / 2)
    root.geometry(alignstr)
    root.resizable(width=False, height=False)
    app = Interfaz(master=root)
    app.mainloop()