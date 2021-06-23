from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Treeview, Scrollbar, Notebook, Style
import os
import pandas as pd
import h5py
from utils import SUBS, print_attrs, SUBS_fast5
import time
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


class root:
    '''
    Classe applicazione principale ROOT.
    '''
    def __init__(self):
        # Variabili principali usate dal programma.
        self.path=""                # path della folder selezionata per il treeview di sx
        self.full_path = None       # path completo del file selezionato e ricavato dal treeview di sx
        self.h5_file = None         # istanza h5py del file selezionato dal treeview di sx
        self.full_path_dx = None    # path completo del file Fast5 selezionato relativo all'item in focus nel treeview di dx
        self.dataset = pd.DataFrame()         # dataset pandas recuperato dall item
        
        # GUI
        self.finestra = Tk()
        self.finestra.title("fast5surfer")
        self.finestra.state("zoomed")
        self.finestra.iconbitmap("logo.ico")
        self.quadro_sx = Frame(self.finestra)
        self.quadro_sx.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=10, pady=10)
        self.quadro_dx = Frame(self.finestra)
        self.quadro_dx.pack(side=RIGHT, fill=BOTH, expand=TRUE, padx=10, pady=10)
        self.file_browser_labelframe = LabelFrame(self.quadro_sx, text="File Browser")
        self.file_browser_labelframe.pack(fill=BOTH, expand=TRUE)
        self.quadro1 = Frame(self.file_browser_labelframe)
        self.quadro1.pack(side=TOP, fill=BOTH, expand=TRUE, padx=10, pady=(20, 0))
        self.quadro2 = Frame(self.file_browser_labelframe)
        self.quadro2.pack(side=BOTTOM, fill=X, pady=20, padx=15)

        self.fast5_file_labelframe = LabelFrame(self.quadro_dx, text="Fast5 File")
        self.fast5_file_labelframe.pack(fill=BOTH, expand=TRUE)
        
        self.quadro3 = Frame(self.fast5_file_labelframe)
        self.quadro3.pack(side=TOP, fill=BOTH, expand=TRUE, padx=10, pady=(20,0))

        self.tree = Treeview(self.quadro1, show="tree")
        self.vsb = Scrollbar(self.quadro1, orient="vertical",command=self.tree.yview)
        self.vsb.pack(side=RIGHT, fill=Y)
        self.hsb = Scrollbar(self.quadro1, orient="horizontal",command=self.tree.xview)
        self.hsb.pack(side=BOTTOM, fill=X)
        self.tree.pack(side=TOP, fill=BOTH, expand=TRUE)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.tree.bind("<<TreeviewSelect>>", self.selectItem)
        self.browse_button = Button(self.quadro2, text="Select a folder to explore", command=self.browse_button_function)
        self.browse_button.pack()
        self.status_labelframe = LabelFrame(self.quadro2, text="STATUS")
        self.status_labelframe.pack(pady=(20,0), fill=BOTH)
        self.status = Label(self.status_labelframe, text="IDLE", relief=GROOVE, fg="#fff", bg="#97ba28")
        self.status.pack(pady=(0,10), side=BOTTOM, ipadx=25, ipady=5)
        
        # Albero per visualizzare la struttura del file fast5 selezionato sull'albero di sx.
        self.tree_dx = Treeview(self.quadro3, show="tree")
        self.vsb_dx = Scrollbar(self.quadro3, orient="vertical",command=self.tree_dx.yview)
        self.vsb_dx.pack(side=RIGHT, fill=Y)
        self.hsb_dx = Scrollbar(self.quadro3, orient="horizontal",command=self.tree_dx.xview)
        self.hsb_dx.pack(side=BOTTOM, fill=X)
        self.tree_dx.pack(fill=BOTH, expand=True)
        self.tree_dx.configure(yscrollcommand=self.vsb_dx.set, xscrollcommand=self.hsb_dx.set)
        self.tree_dx.bind("<<TreeviewSelect>>", self.selectItem_dx)
        
        # creazione riquadro per visualizzazione dati e attributi
        self.quadro4 = Frame(self.fast5_file_labelframe)
        self.quadro4.pack(side=BOTTOM, fill=BOTH, expand=True, padx=10, pady=20)
        self.info = Notebook(self.quadro4)
        self.info.pack(fill= BOTH, expand=True)
        self.attributes_frame = Frame(self.info)
        self.attributes_frame.pack(fill=BOTH, expand=True)
        self.dataset_frame = Frame(self.info)
        self.dataset_frame.pack(fill=BOTH, expand=True)
        #self.plot_canvas = Canvas(self.info)
        self.frame_canvas = Frame(self.info)
        self.frame_canvas.pack(fill=BOTH, expand=True)
        
        
        # ATTRIBUTE TABLE
        self.attribute_table = Treeview(self.attributes_frame, style="")
        self.vsb_attr_tab = Scrollbar(self.attributes_frame, orient="vertical",command=self.attribute_table.yview)
        self.vsb_attr_tab.pack(side=RIGHT, fill=Y)
        self.hsb_attr_tab = Scrollbar(self.attributes_frame, orient="horizontal",command=self.attribute_table.xview)
        self.hsb_attr_tab.pack(side=BOTTOM, fill=X)
        self.attribute_table.pack(fill=BOTH, expand=True)
        self.attribute_table.configure(yscrollcommand=self.vsb_attr_tab.set, xscrollcommand=self.hsb_attr_tab.set)
        self.attribute_table["columns"]=("Key", "Value")
        self.attribute_table.column("#0", width=0, anchor=CENTER, stretch=NO)
        self.attribute_table.column("Key", anchor=CENTER, stretch=YES)
        self.attribute_table.column("Value", anchor=CENTER, stretch=YES)
        self.attribute_table.heading("Key", text="Key")
        self.attribute_table.heading("Value", text="Value")

        # DATA TABLE
        self.dataset_table = Treeview(self.dataset_frame, style="mystyle.Treeview")
        self.vsb_dataset_tab = Scrollbar(self.dataset_frame, orient="vertical",command=self.dataset_table.yview)
        self.vsb_dataset_tab.pack(side=RIGHT, fill=Y)
        self.hsb_dataset_tab = Scrollbar(self.dataset_frame, orient="horizontal",command=self.dataset_table.xview)
        self.hsb_dataset_tab.pack(side=BOTTOM, fill=X)
        self.dataset_table.pack(fill=BOTH, expand=True)
        self.dataset_table.configure(yscrollcommand=self.vsb_dataset_tab.set, xscrollcommand=self.hsb_dataset_tab.set)

        # aggiunta dei frames creati al notebook
        self.info.add(self.attributes_frame, text="Attributes")
        self.info.add(self.dataset_frame, text="Data")
        self.info.add(self.frame_canvas, text="Plot")

        # bind evento click
        self.info.bind("<ButtonRelease-1>", self.select_plot_tab)
        
        # creazione barra menu superiore
        self.menu = main_menu(self.finestra)

        # Aggiunta di stile ai widget ttk
        style = Style()
        style.configure("Treeview.Heading", font=("Arial", 8, 'bold')) # Modify the font of the headings
        

    def browse_button_function(self):
        '''
        Metodo per apertura di un path nel file sistem da scansionare, 
        analizzare e visualizzare nel file browser della GUI del programma 
        nel treeview widget di sx.
        '''
        self.path=""
        self.h5_file = None
        self.dataset = pd.DataFrame()
        self.full_path = None
        self.full_path_dx = None
        self.tree.delete(*self.tree.get_children())
        self.tree_dx.delete(*self.tree_dx.get_children())
        self.dataset_table.delete(*self.dataset_table.get_children())
        self.attribute_table.delete(*self.attribute_table.get_children())
        self.status.config(text="Loading: please wait...", fg="#fff", bg="#fe5741")
        self.dataset_table["columns"] = [""]
        for child in self.frame_canvas.winfo_children(): # distruggo il canvas al suo interno
            child.destroy()
        try:
            self.path = filedialog.askdirectory()
            self.root = self.tree.insert('', 'end', text=self.path, open=True)
            SUBS(self.path, self.root, self.tree)
            self.status.config(text="IDLE", fg="#fff", bg="#97ba28")
            self.tree.column("#0", minwidth=1500, stretch=YES)
        except:
            print("ERROR! Something get wrong during the folder selection! Try again.")
            self.status.config(text="IDLE", fg="#fff", bg="#97ba28")
    
    def selectItem(self, item):
        # azzeramento tabelle e treeviews di sx e variabili
        self.h5_file = None
        self.full_path = None
        self.full_path_dx = None
        self.dataset = pd.DataFrame()
        self.dataset_table["columns"] = [""]
        self.info.select(0)
        self.dataset_table.delete(*self.dataset_table.get_children())
        self.attribute_table.delete(*self.attribute_table.get_children())
        self.tree_dx.delete(*self.tree_dx.get_children())
        for child in self.frame_canvas.winfo_children(): # distruggo il canvas al suo interno
            child.destroy()
        
        full_path_list = [] # lista informazione per la computazione del full path dell'item selezionato con focus del treview
        iid_focus = self.tree.focus()
        name_iid_focus = self.tree.item(iid_focus)["text"]
        full_path_list.append(name_iid_focus) # appendo alla lista l'ultimo sotto indirizzo.
        
        while name_iid_focus != '':            
            parent_iid_focus = self.tree.parent(iid_focus)
            name_parent_iid_focus = self.tree.item(parent_iid_focus)["text"]
            iid_focus = parent_iid_focus
            name_iid_focus = self.tree.item(iid_focus)["text"]
            full_path_list.append(name_iid_focus)
        
        full_path_list = full_path_list[:-1]
        full_path_list.reverse()
        self.full_path = os.path.join(*full_path_list)

        # se è un file .fast5 inserisci il nodo root nel treeview di destra
        if os.path.isfile(self.full_path) and os.path.split(self.full_path)[-1][-6:] == ".fast5":
            self.root_dx = self.tree_dx.insert("", "end", text=os.path.split(self.full_path)[-1], open=True)
            self.tree_dx.column("#0", width=1000, stretch=YES)
            self.h5_file = h5py.File(self.full_path)
            SUBS_fast5(self.h5_file, self.root_dx, self.tree_dx)
        
    def selectItem_dx(self, item):
        '''Metodo analogo a quello di sopra (senza _dx) per ottenere info del dataset selezionato'''
        # azzeramento tabelle e treeviews
        self.info.select(0)
        self.dataset_table.delete(*self.dataset_table.get_children())
        self.dataset_table["columns"] = [""]
        self.attribute_table.delete(*self.attribute_table.get_children())
        self.dataset = pd.DataFrame()
        for child in self.frame_canvas.winfo_children(): # distruggo il canvas al suo interno
            child.destroy()
        print(self.h5_file)
        full_path_list = []
        iid_focus = self.tree_dx.focus()
        name_iid_focus = self.tree_dx.item(iid_focus)["text"]
        full_path_list.append(name_iid_focus) # appendo alla lista l'ultimo sotto indirizzo.
        
        while name_iid_focus != '':            
            parent_iid_focus = self.tree_dx.parent(iid_focus)
            name_parent_iid_focus = self.tree_dx.item(parent_iid_focus)["text"]
            iid_focus = parent_iid_focus
            name_iid_focus = self.tree_dx.item(iid_focus)["text"]
            full_path_list.append(name_iid_focus)
        
        full_path_list = full_path_list[:-2]
        full_path_list.reverse()
        
        self.full_path_dx = "/".join(full_path_list)

        # visualizzazione degli attributi dell'item selezionato del fast5 in selezione (se presenti)
        # nella tabella attribute_table
        if self.h5_file[self.full_path_dx].attrs.items():
            for key, val in self.h5_file[self.full_path_dx].attrs.items():
                self.attribute_table.insert("", "end", values=(key, val))
        
        # visualizzazione del dataset dell'item selezionato del file fast5 in selezione (se questo è un dataset ed ha dati 
        # presenti al suo interno)
        if type(self.h5_file[self.full_path_dx]) == h5py._hl.dataset.Dataset: # verifica che sia un dataset
            if self.h5_file[self.full_path_dx].shape: # verifica che il dataset sia pieno con almeno un elemento al suo interno
                self.dataset = pd.DataFrame(self.h5_file[self.full_path_dx][:]) # ricava dati e inseriscili all'interno di un Pandas.DataFrame
                shape = self.dataset.shape
                # crea e setta colonne dataset usando le colonne del Pandas.DataFrame
                self.dataset_table.column("#0", width=0, anchor=CENTER, stretch="NO")
                columns = ["Index"] + list(self.dataset.columns)
                self.dataset_table["columns"]=columns
                for column in columns:
                    self.dataset_table.column(column, anchor=CENTER, stretch=NO)
                    self.dataset_table.heading(column, text=column)
                for row in self.dataset.itertuples():
                    self.dataset_table.insert("", "end", values=list(row))
                self.info.select(1) # visualizza il tab del dataset appena visualizzato

    def select_plot_tab(self, event):
        '''
        Metodo per la gestione degli eventi legati ai click sui tab del notebook self.info.
        '''
        if event.widget.identify(event.x, event.y) == "label":
                index = event.widget.index("@%d,%d" % (event.x, event.y))
                title = event.widget.tab(index, "text")
                if title == "Plot":
                    if self.dataset.empty != True:
                        if 0 in self.dataset.columns:
                            fig = Figure(figsize=(5, 4), dpi=100)
                            fig.add_subplot(111).plot(self.dataset)
                            plot_canvas = FigureCanvasTkAgg(fig, master = self.frame_canvas)
                            plot_canvas.draw()
                            plot_canvas.get_tk_widget().pack(fill=BOTH, expand=TRUE)
                            toolbar = NavigationToolbar2Tk(plot_canvas, self.frame_canvas)
                            toolbar.update()

                            def on_key_press(event):
                                key_press_handler(event, plot_canvas, toolbar)
                            plot_canvas.mpl_connect("key_press_event", on_key_press)
                    else:
                        print("Select a dataset item form the fast5 file in analysis")


class main_menu:
    '''
    BARMENU classe per il menu in alto a tendina con varie funzioni.
    '''
    def __init__(self, Windows):
        self.Windows = Windows
        self.menubar = Menu(self.Windows, bg='black')
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.Windows.destroy)
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Info Fast5 and HDF5 formats", command=self.Help_ButtonPress)
        self.helpmenu.add_command(label="Info Software", command=self.about_ButtonPress)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.Windows.config(menu=self.menubar)
    
    def Help_ButtonPress(self):
            os.system('start https://www.google.com/search?q=fast5+nanopore&oq=fast5+nanopore&aqs=chrome.0.69i59j0i22i30j69i60j69i65l3j69i60j69i61.3340j0j7&sourceid=chrome&ie=UTF-8')

    def about_ButtonPress(self):
            list_w = self.Windows.winfo_children()
            print('\n', list_w)
            if '.!toplevel' in str(list_w):
                    print('There is already a Toplevel in the widgets list')
                    print(list_w[-1])
                    list_w[-1].destroy()    
            self.about_win=Toplevel(self.Windows)
            self.about_win.title('fast5surfer | INFO')
            self.about_win.resizable(width=0, height=0)
            self.about_win.iconbitmap('logo.ico')
            self.frame1 = Frame(self.about_win)
            self.frame1.grid(row=1, column=2)
            self.img = Image.open("Logo.jpg")
            self.img = self.img.resize((150, 150))
            self.photo1 = ImageTk.PhotoImage(self.img)
            self.Immagine = Canvas(self.about_win)
            self.Immagine.grid(row=1, column=1)
            self.Immagine.create_image(150, 150, image=self.photo1)
            self.programtitle=Label(self.frame1, text="fast5surfer", font="Times 12 bold", width=30)
            self.programtitle.grid(pady=2)
            self.author=Label(self.frame1, text='Author: Adriano Fonzino\nIstitution: XXX', font="Times 10 bold")
            self.author.grid(pady=5)
            self.description=Label(self.frame1, text='Software for the visualization and exploration of Fast5 file from Oxford Nanopore Technology sequencing.\n\n', font=6)
            self.description.grid()


if __name__ == "__main__":
    app = root()
    app.finestra.mainloop()