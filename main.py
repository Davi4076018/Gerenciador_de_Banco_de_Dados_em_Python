from tkinter import *
from tkinter.ttk import *
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror
from tkinter import filedialog as fd
from datetime import datetime
from sqlalchemy.dialects.firebird.base import FBDialect
import re
import sqlalchemy
import fdb
import pyodbc
import firebirdsql
#import sqlalchemy_firebird
from threading import *
from sqlalchemy import create_engine
import urllib
import pandas as pd
from sqlalchemy import text
import openpyxl
import sqlalchemy.dialects
import os

fdb.load_api(r'assets/dll/fbclient.dll')

engineAtual = ''

antigo = ""

ThreadON = False

SQLAtual = ''
sqlserver_uri_Atual = ''
firebird_uri_Atual = ''
PostGre_uri_Atual = ''

palavrasReservadas = []

dictableshow = {}

TipoPesquisa = "tabela"

querybackup = ""

t1 = ""
Stop = False

tela2 = ''

dfquery = pd.DataFrame()


def GetQueryBackup():
    global querybackup
    with open('assets/querybackup.txt', "r") as f:
        querybackup = f.read()
        f.close()
    textAdd(querybackup)

def SetQueryBackup():
    global querybackup
    querybackup = textQuery.get("1.0","end-1c")
    with open('assets/querybackup.txt', "w") as f:
        f.write(querybackup)
        f.close()

def GetReservadas():
    global palavrasReservadas
    with open('assets/reservadas.txt', "r") as f:
        palavrasReservadas = [s.replace('\n', '') for s in f.readlines()]
        f.close()
def GetParametros():
    global SQLAtual, sqlserver_uri_Atual, firebird_uri_Atual, PostGre_uri_Atual
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
        elif (linha.find('postgre_uri=')) != -1:
            PostGre_uri_Atual = linha[len("postgre_uri="):].replace("\n", "")
    print(SQLAtual)
    print(sqlserver_uri_Atual)
    print(firebird_uri_Atual)
    print(PostGre_uri_Atual)
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
def rClickerQuery(e):
    try:
        def tornarAtualR(tipo=1):
            if tipo == 1:
                SetParametros("atual", "SqlServer")
                GetParametros()
                IconSQLAtual.config(image=sqlserverIcon)
            elif tipo == 2:
                SetParametros("atual", "Firebird")
                GetParametros()
                IconSQLAtual.config(image=firebirdIcon)
            elif tipo == 3:
                SetParametros("atual", "PostgreSQL")
                GetParametros()
                IconSQLAtual.config(image=postgreeIcon)

            tables_show()

        e.widget.focus()
        rmenu = Menu(None, tearoff=0, takefocus=0)
        rmenu.config(bg="white")
        rmenu.add_command(label=' Consultar', image=runIcon, compound='left', command=lambda: trendStart(1))
        rmenu.add_command(label=' SqlServer', image=sqlserverIcon, compound='left', command=lambda: tornarAtualR(1))
        rmenu.add_command(label=' FireBird', image=firebirdIcon, compound='left', command=lambda: tornarAtualR(2))
        rmenu.add_command(label=' PostGree', image=postgreeIcon, compound='left', command=lambda: tornarAtualR(3))
        rmenu.add_command(label=' Limpar', image=clearIcon, compound='left', command=clear)
        rmenu.add_command(label=' Configurações', image=configIcon, compound='left', command=config)
        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except Exception as e3:
        print(e3)

    return "break"
def rClickerTabela(e):
    try:

        e.widget.focus()
        rmenu = Menu(None, tearoff=0, takefocus=0)
        rmenu.config(bg="white")
        rmenu.add_command(label=' Gerar Excel', image=excelIcon, compound='left', command=df_to_excel)
        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except Exception as e3:
        print(e3)

    return "break"
def rClickertreeTabelas(e):
    try:

        def consultasProntas(tipo):
            tabela = str(tree_tables.focus())
            colunas = ''
            if SQLAtual == "Firebird":
                db_uri = firebird_uri_Atual
                engineAtual = create_engine(db_uri)
                colunas = pd.read_sql_query("SELECT first 0 * FROM " + tabela, con=engineAtual).columns.values.tolist()
            elif SQLAtual == "SqlServer":
                params = urllib.parse.quote_plus(
                    'DRIVER={ODBC Driver 17 for SQL Server}; server=srvaudax01\SQLEXPRESS;database=SGO;uid=thiago.maximinio;pwd=Sarinha1611')  # CONFIGURAÇÕES DO SQLSERVER
                engineAtual = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
                colunas = pd.read_sql_query("SELECT TOP 0 * FROM " + tabela, con=engineAtual).columns.values.tolist()
            print(colunas)
            colunasjoin = ", ".join(colunas)
            print(colunasjoin)
            if tipo == 1:
                texto = "\n\nSELECT \n\t" + colunasjoin + " ,COUNT(*) \nFROM " + tabela + " \nGROUP BY \n\t" + colunasjoin + " \nHAVING \n\t" + " COUNT(*) > 1 "
                print(texto)
                textAdd(Text=texto)
            if tipo == 2:
                texto = """\n\n WITH cte AS ( 
    SELECT 
        """ + colunasjoin + """ 
        ,ROW_NUMBER() OVER ( 
            PARTITION BY  
                """ + colunasjoin + """ 
            ORDER BY  
                """ + colunasjoin + """ 
        ) row_num 
     FROM  
        """ + tabela + """  
) 
DELETE FROM cte 
WHERE row_num > 1;
 """
                print(texto)
                textAdd(Text=texto)
            if tipo == 3:
                texto = """\n\n WITH CTE AS 
(SELECT *,R=RANK() OVER (ORDER BY """ + colunasjoin + """ ) 
FROM """ + tabela + """  ) 
DELETE CTE 
WHERE R IN (SELECT R FROM CTE GROUP BY R HAVING COUNT(*)>1) 
 """
                print(texto)
                textAdd(Text=texto)
        e.widget.focus()
        rmenu = Menu(None, tearoff=0, takefocus=0)
        rmenu.config(bg="white")
        ConsultasP = Menu(None, tearoff=0, takefocus=0)
        ConsultasP.config(bg="white")
        rmenu.add_command(label=' SELECT', image=excelIcon, compound='left', command=lambda: textAdd(Text="\n\nSELECT * FROM " + str(tree_tables.focus())))
        rmenu.add_cascade(label=' Consultas Prontas', image=excelIcon, compound='left', menu=ConsultasP)
        ConsultasP.add_command(label=' Confere caso exista Duplicatas', image=excelIcon, compound='left', command=lambda: consultasProntas(tipo=1))
        ConsultasP.add_command(label=' Remove Duplicatas (mantendo 1)', image=excelIcon, compound='left', command=lambda: consultasProntas(tipo=2))
        ConsultasP.add_command(label=' Remove Duplicatas (todas)', image=excelIcon, compound='left', command=lambda: consultasProntas(tipo=3))
        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except Exception as e3:
        print(e3)

    return "break"
def rClickertreePesquisa(e):
    global TipoPesquisa
    try:
        def MudarTipoPesquisa(tipo):
            global TipoPesquisa
            if tipo == 1:
                TipoPesquisa = "tabela"
            elif tipo == 2:
                TipoPesquisa = "coluna"
            elif tipo == 3:
                TipoPesquisa = "valor em coluna"
            print(TipoPesquisa)

        e.widget.focus()
        rmenu = Menu(None, tearoff=0, takefocus=0)
        rmenu.config(bg="white")
        rmenu.add_command(label=' tabela (rapido)', image=excelIcon, compound='left', command=lambda: MudarTipoPesquisa(1))
        rmenu.add_command(label=' coluna (demorado)', image=excelIcon, compound='left', command=lambda: MudarTipoPesquisa(2))
        rmenu.add_command(label=' valor em coluna (muito demorado)', image=excelIcon, compound='left', command=lambda: MudarTipoPesquisa(3))
        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except Exception as e3:
        print(e3)

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
    ThreadON = True
    ConsultaSemRetorno = False
    try:
        if SQLAtual == "Firebird":
            db_uri = firebird_uri_Atual
            engineAtual = create_engine(db_uri)
        elif SQLAtual == "SqlServer":
            params = urllib.parse.quote_plus(
                'DRIVER={ODBC Driver 17 for SQL Server}; server=srvaudax01\SQLEXPRESS;database=SGO;uid=thiago.maximinio;pwd=Sarinha1611')  # CONFIGURAÇÕES DO SQLSERVER
            engineAtual = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
        elif SQLAtual == "PostgreSQL":
            db_uri = PostGre_uri_Atual
            engineAtual = create_engine(db_uri)
        try:
            consulta = textQuery.get('sel.first', 'sel.last').replace("\n", "")
        except:
            consulta = textQuery.get("1.0","end-1c")
        DataConsulta = datetime.now()
        try:
            dfquery = pd.read_sql_query(consulta, con=engineAtual)
        except:
            ConsultaSemRetorno = True
        if not(ConsultaSemRetorno):
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

            tam = 0
            soma = 0
            for i in df_list:
                try:
                    tam = int(dfquery[i].astype(str).map(len).max()) * 10
                    if tam < (len(i) * 10):
                        tam = len(i) * 10
                except Exception as e1:
                    tam = 300
                soma += tam

            if soma < int(screen_width):
                tam = int(int(screen_width) / len(df_list))
                if tam < 150:
                    tam = 150

            for i in df_list:
                df_tree.column(i, width=tam, anchor='c', stretch = False)
                df_tree.heading(i, text=i)
            widthID = int(str(len(str(len(dfquery)))) + "0") + 10
            df_tree.column('#0', width = widthID, anchor="w", stretch = False)
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
            df_tree.bind('<Button-3>', rClickerTabela, add='')
        else:
            sucesso = False
            mensagem = ''
            try:
                new = engineAtual.connect()
                com = new.begin()
                new.execute(text(consulta))
                com.commit()
                sucesso = True
            except Exception as e3:
                mensagem = e3
            if (sucesso):
                raise Exception('A Query foi executada com sucesso')
            else:
                raise Exception(mensagem)

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
def trendStart(tipo):
    global ThreadON, Stop
    # caso a execução paralela esteja online, ele não é iniciado
    if not(ThreadON):
        buttonConsulta.config(image=stopIcon)
        if tipo == 1:
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
        filename = fd.asksaveasfilename(initialdir="/",
                                        defaultextension="*.xlsx*",
                                        filetypes=(("Excel file", "¨*.xlsx"),))
        if not filename:
            return
        dfquery.to_excel(filename)
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
        elif tipo == 3:
            db_uri = str(dbSavePostGre.get())
            enginePostgre = create_engine(db_uri)
            try:
                dftest = pd.read_sql_query('SELECT 1', con=enginePostgre)
                showinfo(
                    title='Mensagem Informativa',
                    message='O PostgreSQL está conectado com sucesso'
                )
            except:
                showerror(
                    title='Mensagem de Erro',
                    message='O PostgreSQL não está conectado, verifique a url de conexão')

    def fechar():
        tela2.destroy()

    def salvar(tipo):
        if tipo == 1:
            if dbUserSQLSERVER.get() != "":
                SetParametros("sqlserver_uri", dbUserSQLSERVER.get())
                dbSaveSQLSERVER.config(state=NORMAL)
                dbSaveSQLSERVER.delete(0, 'end')
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
                dbSaveFirebird.delete(0, 'end')
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
        elif tipo == 3:
            if dbUserPostGre.get() != "":
                SetParametros("postgre_uri", dbUserPostGre.get())
                dbSavePostGre.config(state=NORMAL)
                dbSavePostGre.delete(0, 'end')
                dbSavePostGre.insert(0, str(dbUserPostGre.get()))
                dbSavePostGre.config(state=DISABLED)
                showinfo(
                    title='Mensagem Informativa',
                    message='Novo url do PostgreSQL salva com sucesso'
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
        elif tipo == 3:
            SetParametros("atual", "PostgreSQL")
            GetParametros()
            IconSQLAtual.config(image=postgreeIcon)
            showinfo(
                title='Mensagem Informativa',
                message='o Banco de dados atual foi definido como: PostgreSQL'
            )

     # Caso já tenha uma tela ativa identica a essa, ela é destruida para evitar duplicatas

    try:
        tela2.destroy()
    except:
        pass
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
    tab3 = ttk.Frame(tabControl)

    tabControl.add(tab1, text='SQL SERVER')
    tabControl.add(tab2, text='FireBird')
    tabControl.add(tab3, text='Postgresql')
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

    # tab3
    LabelFundoTab3 = tk.Label(tab3, image=tab3Fundo)
    LabelFundoTab3.place(x=0, y=0)

    dbUserPostGre = tk.Entry(tab3,
                              font=("Helvetica", 10),
                              highlightthickness=2,
                              fg="black")

    dbUserPostGre.place(x=135, y=190,
                         width=480,
                         height=30)

    labelurlUserTab3 = Label(tab3, text="Url Nova:", font=("Helvetica", 13), background="white", foreground="gray")
    labelurlUserTab3.place(x=60, y=195)

    dbSavePostGre = tk.Entry(tab3,
                              font=("Helvetica", 10),
                              highlightthickness=2,
                              fg="black")

    dbSavePostGre.place(x=135, y=260,
                         width=480,
                         height=30)

    labelurlSaveTab3 = Label(tab3, text="Url Atual:", font=("Helvetica", 13), background="white", foreground="gray")
    labelurlSaveTab3.place(x=60, y=265)

    dbSavePostGre.insert(0, PostGre_uri_Atual)
    dbSavePostGre.config(state=DISABLED)

    btTestarConecTab3 = tk.Button(tab3, text="Testar Conexão", command=lambda: testarconec(tipo=3),
                                  font=("Helvetica", 13),
                                  highlightthickness=2,
                                  fg="grey"
                                  )

    btTestarConecTab3.place(x=25, y=350,
                            width=175,
                            height=30)

    btSalvarTab3 = tk.Button(tab3, text="Salvar", command=lambda: salvar(tipo=3),
                             font=("Helvetica", 13),
                             highlightthickness=2,
                             fg="grey"
                             )

    btSalvarTab3.place(x=455, y=350,
                       width=100,
                       height=30)

    btCancelarTab3 = tk.Button(tab3, text="Fechar", command=fechar,
                               font=("Helvetica", 13),
                               highlightthickness=2,
                               fg="grey"
                               )

    btCancelarTab3.place(x=575, y=350,
                         width=100,
                         height=30)

    btSetAtualTab3 = tk.Button(tab3, text="Tornar Atual", command=lambda: tornarAtual(tipo=3),
                               font=("Helvetica", 13),
                               highlightthickness=2,
                               fg="grey"
                               )

    btSetAtualTab3.place(x=300, y=350,
                         width=135,
                         height=30)
def tables_show():
    global tree_tables, treetableYScroll, treetableXScroll, inertopframe, dictableshow
    dictableshow = {}
    try:
        tree_tables.destroy()
    except Exception as e3:
        print(e3)

    try:
        treetableYScroll.destroy()
    except Exception as e3:
        print(e3)

    try:
        treetableXScroll.destroy()
    except Exception as e3:
        print(e3)

    try:
        inertopframe.destroy()
    except Exception as e3:
        print(e3)

    inertopframe = Frame(topframe)
    tree_tables = ttk.Treeview(inertopframe, columns=[])
    if SQLAtual == "Firebird":
        dictableshow['firebird'] = []
        tree_tables.column("#0", width=250, stretch = False, anchor="w")
        tree_tables.heading("#0", text="Tabelas do FireBird", anchor="w")
        tree_tables.tag_configure(tagname="gray", background="#f2f2f2")
        tree_tables.tag_configure(tagname="white", background="#ffffff")
        db_uri = firebird_uri_Atual
        engineAtual = create_engine(db_uri)
        dfDatabases = pd.read_sql_query(""" SELECT RDB$RELATION_NAME as "Tables" FROM RDB$RELATIONS
                                                WHERE (RDB$SYSTEM_FLAG <> 1 OR RDB$SYSTEM_FLAG IS NULL) AND RDB$VIEW_BLR IS NULL
                                                ORDER BY RDB$RELATION_NAME;""", con=engineAtual)
        tam = len(max(dfDatabases['Tables'].values.tolist(), key=len)) * 7
        tree_tables.column("#0", width=tam, stretch=False, anchor="w")
        PesquisaTabela.config(width=int(tam/10))
        for table in dfDatabases['Tables'].values.tolist():
            tree_tables.insert("", 'end', iid=str(table), tags="white", text=str(table), values=(''))
            dictableshow['firebird'].append(table)
        tree_tables.bind('<Button-3>', rClickertreeTabelas, add='')

        treetableYScroll = ttk.Scrollbar(topframe, orient=VERTICAL)
        treetableYScroll.configure(command=tree_tables.yview)
        tree_tables.configure(yscrollcommand=treetableYScroll.set)
        treetableYScroll.pack(side=LEFT, fill=Y)


        inertopframe.pack(side=LEFT, expand = False, fill='both')

        treetableXScroll = ttk.Scrollbar(inertopframe, orient=HORIZONTAL)
        treetableXScroll.configure(command=tree_tables.xview)
        tree_tables.configure(xscrollcommand=treetableXScroll.set)
        treetableXScroll.pack(side=TOP, fill=X)



        tree_tables.bind('<Button-3>', rClickertreeTabelas, add='')

    elif SQLAtual == "SqlServer":
        listMaior = []
        dictableshow["database"] = []
        dictableshow["table"] = []
        tree_tables.column("#0", width=250, stretch = False, anchor="w")
        tree_tables.heading("#0", text="Tabelas do SQLSERVER", anchor="w")
        tree_tables.tag_configure(tagname="gray", background="#f2f2f2")
        tree_tables.tag_configure(tagname="white", background="#ffffff")
        params = urllib.parse.quote_plus(
            'DRIVER={ODBC Driver 17 for SQL Server}; server=srvaudax01\SQLEXPRESS;database=SGO;uid=thiago.maximinio;pwd=Sarinha1611')  # CONFIGURAÇÕES DO SQLSERVER
        engineAtual = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
        dfDatabases = pd.read_sql_query("EXEC sp_databases", con=engineAtual)  # INSERT DO SQLSERVER
        for database in dfDatabases['DATABASE_NAME'].values.tolist():
            tree_tables.insert("", 'end', iid=str(database), tags="white", open=False, text=str(database), values=(''))
            dfTables = pd.read_sql_query("SELECT SCHEMA_NAME() as 'SCHEMA', TABLE_NAME FROM  " + str(database) + ".INFORMATION_SCHEMA.TABLES", con=engineAtual)
            dfTables['TABLE_NAME'] = dfTables['SCHEMA'] + "." + dfTables['TABLE_NAME']
            try:
                listMaior.append(len(max(dfTables['TABLE_NAME'].values.tolist(), key=len)))
            except:
                pass
            for row in range(len(dfTables)):
                table = str(dfTables.iloc[row]['TABLE_NAME'])
                t = table.split(".")
                idformat = "[" + database + "].[" + t[0] + "].[" + t[1] + "]"
                tree_tables.insert(str(database), 'end', tags="gray",iid=idformat, text=table, values=(''))
                dictableshow['database'].append(database)
                dictableshow['table'].append(table)

        tam = max(listMaior) * 7
        tree_tables.column("#0", width=tam, stretch=False, anchor="w")
        PesquisaTabela.config(width=int(tam/9))
        treetableYScroll = ttk.Scrollbar(topframe, orient=VERTICAL)
        treetableYScroll.configure(command=tree_tables.yview)
        tree_tables.configure(yscrollcommand=treetableYScroll.set)
        treetableYScroll.pack(side=LEFT, fill=Y)

        inertopframe.pack(side=LEFT, expand = False, fill='both')

        treetableXScroll = ttk.Scrollbar(inertopframe, orient=HORIZONTAL)
        treetableXScroll.configure(command=tree_tables.xview)
        tree_tables.configure(xscrollcommand=treetableXScroll.set)
        treetableXScroll.pack(side=TOP, fill=X)

        tree_tables.bind('<Button-3>', rClickertreeTabelas, add='')
    elif SQLAtual == "PostgreSQL":
        db_uri = PostGre_uri_Atual
        engineAtual = create_engine(db_uri)
        tree_tables.bind('<Button-3>', rClickertreeTabelas, add='')
    # width of columns and alignment

    tree_tables.pack(side=LEFT, fill=Y)
def buscaTabelas():
    tree_tables.delete(*tree_tables.get_children())
    tempdf = pd.DataFrame.from_dict(dictableshow)
    #print(tempdf)
    print(SQLAtual)
    if SQLAtual == "SqlServer":
        tempdf = tempdf[tempdf["table"].str.contains(PesquisaTabela.get(), case=False)].reset_index(drop=True)
        for row in range(len(tempdf)):
            table = str(tempdf.iloc[row]['table'])
            t = table.split(".")
            idformat = "[" + str(tempdf.iloc[row]['database']) + "].[" + t[0] + "].[" + t[1] + "]"
            tree_tables.insert("", 'end', iid=idformat, tags="white",
                               text=idformat, values=(''))
    elif SQLAtual == "Firebird":
        tempdf = tempdf[tempdf["firebird"].str.contains(PesquisaTabela.get(), case=False)].reset_index(drop=True)
        for row in range(len(tempdf)):
            tree_tables.insert("", 'end', iid=str(tempdf.iloc[row]['firebird']), tags="white", text=str(tempdf.iloc[row]['firebird']), values=(''))

def buscaColuna():
    tree_tables.delete(*tree_tables.get_children())
    tempdf = pd.DataFrame.from_dict(dictableshow)
    # print(tempdf)
    print(SQLAtual)
    achou = []
    pesquisa = PesquisaTabela.get()
    if SQLAtual == "SqlServer":
        print("aqui")
        params = urllib.parse.quote_plus(
            'DRIVER={ODBC Driver 17 for SQL Server}; server=srvaudax01\SQLEXPRESS;database=SGO;uid=thiago.maximinio;pwd=Sarinha1611')  # CONFIGURAÇÕES DO SQLSERVER
        engineAtual = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
        for row in range(len(tempdf)):
            table = str(tempdf.iloc[row]['table'])
            t = table.split(".")
            idformat = "[" + str(tempdf.iloc[row]['database']) + "].[" + t[0] + "].[" + t[1] + "]"
            try:
                colunas = pd.read_sql_query("SELECT TOP 0 * FROM " + idformat, con=engineAtual).columns.values.tolist()
                if pesquisa.lower() in '\t'.join(colunas).lower():
                    achou.append(idformat)
            except Exception as e3:
                print(e3)
        for tabela in achou:
            tree_tables.insert("", 'end', iid=tabela, tags="white",
                               text=tabela, values=(''))
    elif SQLAtual == "Firebird":
        db_uri = firebird_uri_Atual
        engineAtual = create_engine(db_uri)
        dfDatabases = pd.read_sql_query(""" SELECT RDB$RELATION_NAME as "Tables" FROM RDB$RELATIONS
                                                        WHERE (RDB$SYSTEM_FLAG <> 1 OR RDB$SYSTEM_FLAG IS NULL) AND RDB$VIEW_BLR IS NULL
                                                        ORDER BY RDB$RELATION_NAME;""", con=engineAtual)
        for row in range(len(tempdf)):
            table = str(tempdf.iloc[row]['firebird'])
            try:
                colunas = pd.read_sql_query("SELECT first 0 * FROM " + table, con=engineAtual).columns.values.tolist()
                if pesquisa.lower() in '\t'.join(colunas).lower():
                    achou.append(table)
            except Exception as e3:
                print(e3)
        for tabela in achou:
            tree_tables.insert("", 'end', iid=tabela, tags="white",
                               text=tabela, values=(''))


def buscas():
    if TipoPesquisa == "tabela":
        buscaTabelas()
    elif TipoPesquisa == "coluna":
        buscaColuna()
    elif TipoPesquisa == "valor em coluna":
        pass

def fechamento():
    SetQueryBackup()
    root.destroy()

root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry("1000x800")  # Tamanho fixo da janela
root.state('zoomed')

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
pesquisaIcon = PhotoImage(file="assets/icons/pesquisa_icon.png")
refreshIcon = PhotoImage(file="assets/icons/refresh_icon.png")
configIcon = PhotoImage(file="assets/icons/config_icon.png")
firebirdIcon = PhotoImage(file="assets/icons/firebird_icon.png")
sqlserverIcon = PhotoImage(file="assets/icons/sqlserver_icon.png")
excelIcon = PhotoImage(file="assets/icons/excel_icon.png")
postgreeIcon = PhotoImage(file="assets/icons/postgre_icon.png")

tab1Fundo = PhotoImage(file="assets/fundos/tab1_fundo.png")
tab2Fundo = PhotoImage(file="assets/fundos/tab2_fundo.png")
tab3Fundo = PhotoImage(file="assets/fundos/tab3_fundo.png")

s = Style()
s.configure('My.TFrame', background='#F7F7F7')

GetParametros()
GetReservadas()

sqlAtualIcon = ""

if SQLAtual == "Firebird":
    sqlAtualIcon = firebirdIcon
elif SQLAtual == "SqlServer":
    sqlAtualIcon = sqlserverIcon
elif SQLAtual == "PostgreSQL":
    sqlAtualIcon = postgreeIcon

#root.resizable(False, False)
frame = Frame(root)
frame.pack()

Headerframe = Frame(root, style='My.TFrame')
Headerframe.pack(side=TOP, expand = False, fill='both')

topframe = Frame(root)
topframe.pack(side=TOP, expand = False, fill='both')

inertopframe = Frame(topframe)


Midframe = Frame(root)
Midframe.pack(expand = False, fill='x')

Bottomframe = Frame(root)
Bottomframe.pack(expand = True, fill='both')

Downframe = Frame(root)
Downframe.pack(side=BOTTOM, expand = False, fill='x')

buttonRefresh = tk.Button(Headerframe, image=refreshIcon, command=tables_show, bg='white')
buttonRefresh.pack(side='left')

PesquisaTabela = tk.Entry(Headerframe, width= 35, font=("Calibri 12"))
PesquisaTabela.pack(side='left', ipady=3, padx=4)

PesquisaTabela.bind('<Button-3>',rClickertreePesquisa, add='')

buttonPesqTable = tk.Button(Headerframe, image=pesquisaIcon, command=buscas, bg='white')
buttonPesqTable.pack(side='left')

buttonConsulta = tk.Button(Headerframe, image=runIcon, command=lambda: trendStart(1), bg='white')
buttonConsulta.pack(side='left', padx=20, anchor="n")

buttonSelect = tk.Button(Headerframe, image=selectIcon, command=lambda: textAdd(Text="\n\nSELECT * FROM tabela"), bg='white')
buttonSelect.pack(side='left')

buttonWhere = tk.Button(Headerframe, image=whereIcon, command=lambda: textAdd(Text=" WHERE coluna = ''"), bg='white')
buttonWhere.pack(side='left')

buttonOrderBy = tk.Button(Headerframe, image=orderByIcon, command=lambda: textAdd(Text=" ORDER BY coluna1, coluna2"), bg='white')
buttonOrderBy.pack(side='left')

buttonUpdate = tk.Button(Headerframe, image=updateIcon, command=lambda: textAdd(Text="\n\nUPDATE tabela\nSET coluna1 = 'valor', coluna2 = 'valor'\nWHERE coluna = 'valor'"), bg='white')
buttonUpdate.pack(side='left')

buttonDelete = tk.Button(Headerframe, image=deleteIcon, command=lambda: textAdd(Text="\n\nDELETE FROM tabela WHERE coluna = ''"), bg='white')
buttonDelete.pack(side='left')

buttonTruncate = tk.Button(Headerframe, image=truncateIcon, command=lambda: textAdd(Text="\n\nTRUNCATE TABLE tabela"), bg='white')
buttonTruncate.pack(side='left')

buttonCreate = tk.Button(Headerframe, image=createIcon, command=lambda: textAdd(Text="\n\nCREATE TABLE tabela (\n    coluna1 varchar(255),\n    coluna2 datatipo,\n    coluna3 datatipo,\n   ....);"), bg='white')
buttonCreate.pack(side='left')

buttonExcel = tk.Button(Headerframe, image=excelIcon, command=df_to_excel, bg='white')
buttonExcel.pack(side='left')

buttonConfig = tk.Button(Headerframe, image=configIcon, command=config, bg='white')
buttonConfig.pack(side='right')

buttonClear = tk.Button(Headerframe, image=clearIcon, command=clear, bg='white')
buttonClear.pack(side='right')

IconSQLAtual = tk.Label(Headerframe, image=sqlAtualIcon, bg='white')
IconSQLAtual.pack(side='right')

tree_tables = ttk.Treeview(inertopframe, columns=[])
tree_tables.column("#0", width=250, anchor='w')
tree_tables.heading("#0", text="")

tree_tables.pack(side=LEFT, fill=Y)
treetableYScroll = ttk.Scrollbar(topframe, orient=VERTICAL)
treetableXScroll = ttk.Scrollbar(inertopframe, orient=HORIZONTAL)
inertopframe.pack(side=LEFT, expand = True, fill='both')



textQuery = tk.Text(topframe, undo = True)
textQuery.pack(side=RIGHT, expand = True, fill = tk.BOTH)

textQuery.tag_configure("blue", foreground="blue")
textQuery.bind('<KeyRelease>', check_input)
textQuery.bind('<Button-3>',rClickerQuery, add='')
textQueryYScroll = ttk.Scrollbar(topframe, orient=VERTICAL, command=textQuery.yview)
textQueryYScroll.pack(side=RIGHT, fill=Y)
textQuery['yscrollcommand'] = textQueryYScroll.set


df_tree = ttk.Treeview(Bottomframe, columns=[])
df_tree.pack(expand = True, fill=BOTH)
df_tree.bind('<Button-3>',rClickerTabela, add='')
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

GetQueryBackup()

tables_show()

root.title("Gerenciador de banco de dados em Python")
root.protocol("WM_DELETE_WINDOW", fechamento)
root.mainloop()
