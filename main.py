from tkinter import *
from tkinter.ttk import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror
from datetime import datetime
import re
import sqlalchemy
import fdb
import pyodbc
from threading import *
from sqlalchemy import create_engine
import urllib
import pandas as pd
import openpyxl

engineAtual = ''

antigo = ""

ThreadON = False

SQLAtual = ''
sqlserver_uri_Atual = ''
firebird_uri_Atual = ''

palavrasReservadas = []

t1 = ""
Stop = False

tela2 = ''

dfquery = pd.DataFrame()
def GetReservadas():
    global palavrasReservadas
    with open('assets/reservadas.txt', "r") as f:
        palavrasReservadas = [s.replace('\n', '') for s in f.readlines()]
        f.close()
def GetParametros():
    global SQLAtual, sqlserver_uri_Atual, firebird_uri_Atual
    with open('assets/parametros.txt', "r") as f:
        conteudo = f.readlines()
        f.close()
    for linha in conteudo:
        if (linha.find("atual=")) != -1:
            SQLAtual = linha[len("atual="):].replace("\n", "")
        elif (linha.find('sqlserver_uri=')) != -1:
            sqlserver_uri_Atual = linha[len("sqlserver_uri="):].replace("\n", "")
        elif (linha.find('firebird_uri=')) != -1:
            firebird_uri_Atual = linha[len("firebird_uri="):].replace("\n", "")
    print(SQLAtual)
    print(sqlserver_uri_Atual)
    print(firebird_uri_Atual)
def SetParametros(parametro, valor):
    with open('assets/parametros.txt', "r") as f:
        conteudo = f.readlines()
        f.close()
    for n in range(len(conteudo)):
        if (conteudo[n].find(parametro)) != -1:
            conteudo[n] = str(parametro) + "=" + str(valor) + "\n"
            break
    with open('assets/parametros.txt', "w+") as f:
        f.write("".join(conteudo))
def rClicker(e):
    try:
        def rClick_Copy(e, apnd=0):
            e.widget.event_generate('<Control-c>')

        def rClick_Cut(e):
            e.widget.event_generate('<Control-x>')

        def rClick_Paste(e):
            e.widget.event_generate('<Control-v>')

        e.widget.focus()

        nclst=[
               (' Recortar', lambda: rClick_Cut(e)),
               (' Copiar', lambda: rClick_Copy(e)),
               (' Colar', lambda: rClick_Paste(e)),
               ]

        rmenu = Menu(None, tearoff=0, takefocus=0)

        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except TclError:
        print (' - rClick menu, something wrong')
        pass

    return "break"
def check_input(event=''):
    conteudo = textQuery.get("1.0", "end-1c")
    mod = False
    listaBlue = palavrasReservadas.copy()
    conteudoLower = conteudo.lower()
    for palavra in listaBlue:
        palavrasLoc = [m.start() for m in re.finditer(palavra + " ", conteudoLower)]
        breaklineLoc = [m.start() for m in re.finditer("\n", conteudoLower)]
        dois = sorted(palavrasLoc + breaklineLoc)
        linha = 1
        ultimobreak = 0
        for loc in dois:
            if loc in breaklineLoc:
                linha += 1
                ultimobreak = loc + 1
            else:
                textQuery.tag_add("blue",  str(linha) + "." + str(loc - ultimobreak), str(linha) + "." + str(int(loc - ultimobreak) + len(palavra)))
def Consulta():
    global df_tree, treeXScroll, treeYScroll, ThreadON, Stop, textError, engineAtual, dfquery
    if SQLAtual == "Firebird":
        db_uri = firebird_uri_Atual
        engineAtual = create_engine(db_uri)
    elif SQLAtual == "SqlServer":
        params = urllib.parse.quote_plus(
            'DRIVER={ODBC Driver 17 for SQL Server}; server=srvaudax01\SQLEXPRESS;database=SGO;uid=thiago.maximinio;pwd=Sarinha1611')  # CONFIGURAÇÕES DO SQLSERVER
        engineAtual = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    ThreadON = True
    try:
        try:
            consulta = textQuery.get('sel.first', 'sel.last').replace("\n", "")
        except:
            consulta = textQuery.get("1.0","end-1c")
        DataConsulta = datetime.now()
        dfquery = pd.read_sql_query(consulta, con=engineAtual)  # INSERT DO SQLSERVER
        if Stop:
            raise Exception('Consulta Cancelada')
        try:
            df_tree.destroy()
        except:
            pass

        try:
            treeXScroll.destroy()
        except:
            pass

        try:
            treeYScroll.destroy()
        except:
            pass

        try:
            textError.destroy()
        except:
            pass

        df_list = dfquery.columns.values.tolist()
        df_tree = ttk.Treeview(Bottomframe, columns=df_list)
        tam = int(int(screen_width)/len(df_list))
        if tam < 150:
            tam = 150
        for i in df_list:
            df_tree.column(i, width=tam, anchor='c')
            df_tree.heading(i, text=i)
        widthID = int(str(len(str(len(dfquery)))) + "0") + 10
        df_tree.column('#0', width = widthID, anchor="w")
        df_tree.tag_configure(tagname="gray", background="#f2f2f2")
        df_tree.tag_configure(tagname="white", background="#ffffff")
        cont = 0
        for index, row in dfquery.iterrows():
            if (cont % 2) == 0:
                df_tree.insert("", 'end', tags="gray",text=index, values=list(row))
            else:
                df_tree.insert("", 'end', tags="white", text=index, values=list(row))
            cont += 1
            if Stop:
                raise Exception('Consulta Cancelada')

        VarLinhas.set("Linhas: " + str(len(dfquery)) + "  |")
        VarColunas.set("|  Colunas: " + str(len(dfquery.columns)) + "  |")
        VarTempoConsulta.set(" | Tempo da Consulta: " + str(datetime.now() - DataConsulta))
        # attach a Horizontal (x) scrollbar to the frame
        treeXScroll = ttk.Scrollbar(Midframe, orient=HORIZONTAL)
        treeXScroll.configure(command=df_tree.xview)
        treeYScroll = ttk.Scrollbar(Bottomframe, orient=VERTICAL)
        treeYScroll.configure(command=df_tree.yview)
        df_tree.configure(xscrollcommand=treeXScroll.set)
        df_tree.configure(yscrollcommand=treeYScroll.set)
        treeXScroll.pack(fill=X)
        treeYScroll.pack(side='left', expand=True, fill=Y)
        df_tree.pack(expand=True, fill=BOTH)
    except Exception as e2:
        try:
            df_tree.destroy()
        except:
            pass
        try:
            treeXScroll.destroy()
        except:
            pass
        try:
            treeYScroll.destroy()
        except:
            pass
        try:
            textError.destroy()
        except:
            pass
        print(e2)
        ThreadON = False
        Stop = False
        treeXScroll = ttk.Scrollbar(Midframe, orient=HORIZONTAL)
        treeYScroll = ttk.Scrollbar(Bottomframe, orient=VERTICAL)
        treeXScroll.pack(fill=X)
        treeYScroll.pack(side='left', expand=False, fill=Y)
        textError = tk.Text(Bottomframe, undo=True)
        textError.pack(expand = True, fill = BOTH)
        textError.insert('0.0', str(e2))
        textError.config(state='disabled')
    ThreadON = False
    Stop = False
    buttonConsulta.config(image=runIcon)
def trendStart():
    global ThreadON, Stop
    # caso a execução paralela esteja online, ele não é iniciado
    if not(ThreadON):
        buttonConsulta.config(image=stopIcon)
        t1 = Thread(target=Consulta)
        t1.start()
    else:
        Stop = True
        buttonConsulta.config(image=cancelIcon)
def textAdd(Text):
    Conteudo = textQuery.get("1.0", "end-1c")
    textQuery.delete("1.0", "end-1c")
    textQuery.insert('0.0',  Conteudo + Text)
    check_input()
def clear():
    textQuery.delete("1.0", "end-1c")

def df_to_excel():
    global dfquery
    if not(dfquery.empty):
        dfquery.to_excel("gerados/test.xlsx")
def config():
    global tela2

    def testarconec(tipo):
        # dados do SQL SERVER
        if tipo == 1:
            params = urllib.parse.quote_plus(str(dbSaveSQLSERVER.get()))
            engineSQLServer = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
            try:
                dftest = pd.read_sql_query('SELECT 1', con=engineSQLServer)
                showinfo(
                    title='Mensagem Informativa',
                    message='O SQL SERVER está conectado com sucesso'
                )
            except:
                showerror(
                    title='Mensagem de Erro',
                    message='O SQL SERVER não está conectado, verifique a url de conexão')
        elif tipo == 2:
            db_uri = str(dbSaveFirebird.get())
            engineFirebird = create_engine(db_uri)
            try:
                dftest = pd.read_sql_query('SELECT 1 FROM RDB$DATABASE', con=engineFirebird)
                showinfo(
                    title='Mensagem Informativa',
                    message='O FireBird está conectado com sucesso'
                )
            except:
                showerror(
                    title='Mensagem de Erro',
                    message='O FireBird não está conectado, verifique a url de conexão')

    def fechar():
        tela2.destroy()

    # Caso já tenha uma tela ativa identica a essa, ela é destruida para evitar duplicatas
    try:
        tela2.destroy()
    except:
        pass

    def salvar(tipo):
        if tipo == 1:
            if dbUserSQLSERVER.get() != "":
                SetParametros("sqlserver_uri", dbUserSQLSERVER.get())
                dbSaveSQLSERVER.config(state=NORMAL)
                dbSaveSQLSERVER.delete(0)
                dbSaveSQLSERVER.insert(0, str(dbUserSQLSERVER.get()))
                dbSaveSQLSERVER.config(state=DISABLED)
                showinfo(
                    title='Mensagem Informativa',
                    message='Novo url do SQL SERVER salvo com sucesso'
                )
                GetParametros()
            else:
                showerror(
                    title='Mensagem de Erro',
                    message='O valor não pode ser vazio'
                )
        elif tipo == 2:
            if dbUserFirebird.get() != "":
                SetParametros("firebird_uri", dbUserSQLSERVER.get())
                dbSaveFirebird.config(state=NORMAL)
                dbSaveFirebird.delete(0)
                dbSaveFirebird.insert(0, str(dbUserFirebird.get()))
                dbSaveFirebird.config(state=DISABLED)
                showinfo(
                    title='Mensagem Informativa',
                    message='Novo url do Firebird salvo com sucesso'
                )
                GetParametros()
            else:
                showerror(
                    title='Mensagem de Erro',
                    message='O valor não pode ser vazio'
                )

    def tornarAtual(tipo=1):
        if tipo == 1:
            SetParametros("atual", "SqlServer")
            GetParametros()
            IconSQLAtual.config(image=sqlserverIcon)
            showinfo(
                title='Mensagem Informativa',
                message='o Banco de dados atual foi definido como: SQL SERVER'
            )
        elif tipo == 2:
            SetParametros("atual", "Firebird")
            GetParametros()
            IconSQLAtual.config(image=firebirdIcon)
            showinfo(
                title='Mensagem Informativa',
                message='o Banco de dados atual foi definido como: Firebird'
            )

    # cria uma nova janela no nivel acima da normal
    UserWindow = tk.Toplevel()
    # trava as janelas inferiores para não responderem enquanto a superior estiver ativa
    UserWindow.grab_set()
    # coloca a jenale atual na varivel global para ser finalizada futuramente
    tela2 = UserWindow
    # é definido o nome da janela nova
    UserWindow.title("Configuração dos Bancos de Dados")
    # é definida o tamanho da janela nova
    UserWindow.geometry("700x425")  # Tamanho fixo da janela
    # a janela nova é definida como não redimensionada
    UserWindow.resizable(False, False)

    tabControl = ttk.Notebook(tela2)

    tab1 = ttk.Frame(tabControl)
    tab2 = ttk.Frame(tabControl)

    tabControl.add(tab1, text='SQL SERVER')
    tabControl.add(tab2, text='FireBird')
    tabControl.pack(expand=1, fill="both")

    # tab1
    LabelFundoTab1 = tk.Label(tab1, image=tab1Fundo)
    LabelFundoTab1.place(x=0, y=0)

    dbUserSQLSERVER = tk.Entry(tab1,
                              font=("Helvetica", 10),
                              highlightthickness=2,
                              fg="black")

    dbUserSQLSERVER.place(x=135, y=190,
                          width=480,
                          height=30)

    labelurlUserTab1 = Label(tab1, text="Url Nova:", font=("Helvetica", 13), background="white", foreground="gray")
    labelurlUserTab1.place(x=60, y=195)

    dbSaveSQLSERVER = tk.Entry(tab1,
                                font=("Helvetica", 10),
                                highlightthickness=2,
                                fg="black")

    dbSaveSQLSERVER.place(x=135, y=260,
                           width=480,
                           height=30)

    labelurlSaveTab1 = Label(tab1, text="Url Atual:", font=("Helvetica", 13), background="white", foreground="gray")
    labelurlSaveTab1.place(x=60, y=265)

    dbSaveSQLSERVER.insert(0, sqlserver_uri_Atual)
    dbSaveSQLSERVER.config(state=DISABLED)

    btTestarConecTab1 = tk.Button(tab1, text="Testar Conexão", command=lambda: testarconec(tipo=1),
                          font=("Helvetica", 13),
                          highlightthickness=2,
                          fg="grey"
                          )

    btTestarConecTab1.place(x=25, y=350,
                    width=175,
                    height=30)

    btSalvarTab1 = tk.Button(tab1, text="Salvar", command=lambda: salvar(tipo=1),
                          font=("Helvetica", 13),
                          highlightthickness=2,
                          fg="grey"
                          )

    btSalvarTab1.place(x=455, y=350,
                    width=100,
                    height=30)

    btCancelarTab1 = tk.Button(tab1, text="Fechar", command=fechar,
                             font=("Helvetica", 13),
                             highlightthickness=2,
                             fg="grey"
                             )

    btCancelarTab1.place(x=575, y=350,
                       width=100,
                       height=30)

    btSetAtualTab1 = tk.Button(tab1, text="Tornar Atual", command=lambda: tornarAtual(tipo=1),
                               font=("Helvetica", 13),
                               highlightthickness=2,
                               fg="grey"
                               )

    btSetAtualTab1.place(x=300, y=350,
                         width=135,
                         height=30)

    # tab2
    LabelFundoTab2 = tk.Label(tab2, image=tab2Fundo)
    LabelFundoTab2.place(x=0, y=0)

    dbUserFirebird = tk.Entry(tab2,
                               font=("Helvetica", 10),
                               highlightthickness=2,
                               fg="black")

    dbUserFirebird.place(x=135, y=190,
                          width=480,
                          height=30)

    labelurlUserTab2 = Label(tab2, text="Url Nova:", font=("Helvetica", 13), background="white", foreground="gray")
    labelurlUserTab2.place(x=60, y=195)

    dbSaveFirebird = tk.Entry(tab2,
                               font=("Helvetica", 10),
                               highlightthickness=2,
                               fg="black")

    dbSaveFirebird.place(x=135, y=260,
                          width=480,
                          height=30)

    labelurlSaveTab2 = Label(tab2, text="Url Atual:", font=("Helvetica", 13), background="white", foreground="gray")
    labelurlSaveTab2.place(x=60, y=265)

    dbSaveFirebird.insert(0, firebird_uri_Atual)
    dbSaveFirebird.config(state=DISABLED)

    btTestarConecTab2 = tk.Button(tab2, text="Testar Conexão", command=lambda: testarconec(tipo=2),
                                  font=("Helvetica", 13),
                                  highlightthickness=2,
                                  fg="grey"
                                  )

    btTestarConecTab2.place(x=25, y=350,
                            width=175,
                            height=30)

    btSalvarTab2 = tk.Button(tab2, text="Salvar", command=lambda: salvar(tipo=2),
                             font=("Helvetica", 13),
                             highlightthickness=2,
                             fg="grey"
                             )

    btSalvarTab2.place(x=455, y=350,
                       width=100,
                       height=30)

    btCancelarTab2 = tk.Button(tab2, text="Fechar", command=fechar,
                               font=("Helvetica", 13),
                               highlightthickness=2,
                               fg="grey"
                               )

    btCancelarTab2.place(x=575, y=350,
                         width=100,
                         height=30)


    btSetAtualTab2 = tk.Button(tab2, text="Tornar Atual", command=lambda: tornarAtual(tipo=2),
                               font=("Helvetica", 13),
                               highlightthickness=2,
                               fg="grey"
                               )

    btSetAtualTab2.place(x=300, y=350,
                         width=135,
                         height=30)

root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry("1000x800")  # Tamanho fixo da janela

cancelIcon = PhotoImage(file="assets/icons/cancel_icon.png")
runIcon = PhotoImage(file="assets/icons/run_icon.png")
stopIcon = PhotoImage(file="assets/icons/stop_icon.png")
selectIcon = PhotoImage(file="assets/icons/select_icon.png")
whereIcon = PhotoImage(file="assets/icons/where_icon.png")
orderByIcon = PhotoImage(file="assets/icons/order_by_icon.png")
deleteIcon = PhotoImage(file="assets/icons/delete_icon.png")
updateIcon = PhotoImage(file="assets/icons/update_icon.png")
truncateIcon = PhotoImage(file="assets/icons/truncate_icon.png")
createIcon = PhotoImage(file="assets/icons/create_icon.png")
clearIcon = PhotoImage(file="assets/icons/trash_icon.png")
configIcon = PhotoImage(file="assets/icons/config_icon.png")
firebirdIcon = PhotoImage(file="assets/icons/firebird_icon.png")
sqlserverIcon = PhotoImage(file="assets/icons/sqlserver_icon.png")
excelIcon = PhotoImage(file="assets/icons/excel_icon.png")

tab1Fundo = PhotoImage(file="assets/fundos/tab1_fundo.png")
tab2Fundo = PhotoImage(file="assets/fundos/tab2_fundo.png")


s = Style()
s.configure('My.TFrame', background='#F7F7F7')

GetParametros()
GetReservadas()

sqlAtualIcon = ""

if SQLAtual == "Firebird":
    sqlAtualIcon = firebirdIcon
elif SQLAtual == "SqlServer":
    sqlAtualIcon = sqlserverIcon

#root.resizable(False, False)
frame = Frame(root)
frame.pack()

Headerframe = Frame(root, style='My.TFrame')
Headerframe.pack(side=TOP, expand = False, fill='both')

topframe = Frame(root)
topframe.pack(side=TOP, expand = True, fill='both')

Midframe = Frame(root)
Midframe.pack(expand = False, fill='x')

Bottomframe = Frame(root)
Bottomframe.pack(expand = True, fill='both')

Downframe = Frame(root)
Downframe.pack(side=BOTTOM, expand = False, fill='x')

buttonConsulta = tk.Button(Headerframe, image=runIcon, command=trendStart, bg='white')
buttonConsulta.pack(side='left')

buttonSelect = tk.Button(Headerframe, image=selectIcon, command=lambda: textAdd(Text="\nSELECT * FROM tabela"), bg='white')
buttonSelect.pack(side='left')

buttonWhere = tk.Button(Headerframe, image=whereIcon, command=lambda: textAdd(Text=" WHERE coluna = ''"), bg='white')
buttonWhere.pack(side='left')

buttonOrderBy = tk.Button(Headerframe, image=orderByIcon, command=lambda: textAdd(Text=" ORDER BY coluna1, coluna2"), bg='white')
buttonOrderBy.pack(side='left')

buttonUpdate = tk.Button(Headerframe, image=updateIcon, command=lambda: textAdd(Text="\nUPDATE tabela\nSET coluna1 = 'valor', coluna2 = 'valor'\nWHERE coluna = 'valor'"), bg='white')
buttonUpdate.pack(side='left')

buttonDelete = tk.Button(Headerframe, image=deleteIcon, command=lambda: textAdd(Text="\nDELETE FROM tabela WHERE coluna = ''"), bg='white')
buttonDelete.pack(side='left')

buttonTruncate = tk.Button(Headerframe, image=truncateIcon, command=lambda: textAdd(Text="\nTRUNCATE TABLE tabela"), bg='white')
buttonTruncate.pack(side='left')

buttonCreate = tk.Button(Headerframe, image=createIcon, command=lambda: textAdd(Text="\nCREATE TABLE tabela (\n    coluna1 varchar(255),\n    coluna2 datatipo,\n    coluna3 datatipo,\n   ....);"), bg='white')
buttonCreate.pack(side='left')

IconSQLAtual = tk.Label(Headerframe, image=sqlAtualIcon, bg='white')
IconSQLAtual.pack(side='right')

buttonConfig = tk.Button(Headerframe, image=configIcon, command=config, bg='white')
buttonConfig.pack(side='right')

buttonClear = tk.Button(Headerframe, image=clearIcon, command=clear, bg='white')
buttonClear.pack(side='right')

buttonExcel = tk.Button(Headerframe, image=excelIcon, command=df_to_excel, bg='white')
buttonExcel.pack(side='left')

textQuery = tk.Text(topframe, undo = True)
textQuery.pack(expand = True, fill = tk.BOTH)

textQuery.tag_configure("blue", foreground="blue")
textQuery.bind('<KeyRelease>', check_input)
textQuery.bind('<Button-3>',rClicker, add='')

df_tree = ttk.Treeview(Bottomframe, columns=[])
df_tree.pack(expand = True, fill=BOTH)
treeXScroll = ttk.Scrollbar(Midframe, orient=HORIZONTAL)
treeYScroll = ttk.Scrollbar(Bottomframe, orient=VERTICAL)
#textShow = tk.Text(Bottomframe, undo = True)
#textShow.pack(expand = True, fill = tk.BOTH)

VarLinhas = StringVar()
labelLinhas = Label(Downframe, textvariable=VarLinhas)
labelLinhas.pack(side=RIGHT)
VarLinhas.set("         |")

VarColunas = StringVar()
labelColunas = Label(Downframe, textvariable=VarColunas)
labelColunas.pack(side=RIGHT)
VarColunas.set("|           |")

VarTempoConsulta = StringVar()
labelTempoConsulta = Label(Downframe, textvariable=VarTempoConsulta)
labelTempoConsulta.pack(side=LEFT)
VarTempoConsulta.set(" |           ")

textError = tk.Text(Bottomframe, undo=True)

root.title("Gerenciador de banco de dados em Python")
root.mainloop()
