"""
Agenda de Compromissos com Interface Gráfica (Tkinter)
-------------------------------------------------------
Permite:
- Inserir compromissos com data e hora
- Editar texto, data e hora de qualquer compromisso
- Marcar tarefas como concluídas (com ✔)
- Remover tarefas da lista
- Armazenar os dados em um arquivo local
- Ordenar automaticamente por data/hora (ativas primeiro, depois concluídas)

Tecnologias:
- tkinter: interface gráfica
- tkcalendar: calendário para escolha de datas
- datetime: manipulação de datas e horas
- time: pausas temporárias para mensagens
- os: verificação de arquivos
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import DateEntry
from datetime import datetime
import time
import os

# Caminho do arquivo onde as tarefas serão salvas
ARQUIVO_TAREFAS = "tarefas.txt"

# Função que junta a data (YYYY-MM-DD) e hora (HH:MM) em um objeto datetime
def combinar_data_hora(data_str, hora_str):
    try:
        return datetime.strptime(f"{data_str} {hora_str}", "%Y-%m-%d %H:%M")
    except:
        return None  # Retorna None se o formato estiver errado

# Função auxiliar para extrair a data/hora de uma tarefa salva (último campo após "|")
def extrair_data_hora(tarefa):
    try:
        partes = tarefa.rsplit("|", 1)
        return datetime.strptime(partes[1].strip(), "%Y-%m-%d %H:%M")
    except:
        return datetime.min  # Retorna o menor valor possível em caso de erro

# Função para adicionar nova tarefa à lista
def adicionar_tarefa():
    texto = entrada.get().strip()
    data = seletor_data.get_date()
    hora = entrada_hora.get().strip()

    # Valida se os campos estão preenchidos
    if not texto or not hora:
        messagebox.showwarning("Aviso", "Preencha a tarefa e a hora!")
        time.sleep(2)
        return

    dt = combinar_data_hora(str(data), hora)
    if dt:
        tarefa = f"{texto} | {dt.strftime('%Y-%m-%d %H:%M')}"
        lista.insert(tk.END, tarefa)
        entrada.delete(0, tk.END)
        entrada_hora.delete(0, tk.END)
        ordenar_tarefas()
        salvar_tarefas()
    else:
        messagebox.showerror("Erro", "Formato de hora inválido. Use HH:MM.")

# Função para remover a tarefa selecionada
def remover_tarefa():
    try:
        indice = lista.curselection()[0]
        lista.delete(indice)
        salvar_tarefas()
    except:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para remover!")

# Função para marcar uma tarefa como concluída (✔)
def marcar_como_concluida():
    try:
        indice = lista.curselection()[0]
        tarefa = lista.get(indice)

        # Se já não estiver marcada, marca como concluída
        if not tarefa.startswith("[✔]"):
            lista.delete(indice)
            lista.insert(tk.END, f"[✔] {tarefa}")
            ordenar_tarefas()
            salvar_tarefas()
    except:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para concluir!")

# Função para editar tarefa, data e hora
def editar_tarefa():
    try:
        indice = lista.curselection()[0]
        tarefa_antiga = lista.get(indice)

        # Remove o prefixo de tarefa concluída se existir
        concluida = tarefa_antiga.startswith("[✔]")
        texto_completo = tarefa_antiga.replace("[✔] ", "") if concluida else tarefa_antiga

        # Tenta separar texto, data e hora
        try:
            texto, datahora = texto_completo.rsplit("|", 1)
            data_str, hora_str = datahora.strip().split(" ")
        except:
            texto = texto_completo
            data_str = datetime.now().strftime("%Y-%m-%d")
            hora_str = datetime.now().strftime("%H:%M")

        # Solicita novos dados ao usuário
        novo_texto = simpledialog.askstring("Editar Tarefa", "Edite o texto:", initialvalue=texto.strip())
        nova_data = simpledialog.askstring("Editar Data", "Edite a data (AAAA-MM-DD):", initialvalue=data_str)
        nova_hora = simpledialog.askstring("Editar Hora", "Edite a hora (HH:MM):", initialvalue=hora_str)

        # Valida e salva
        if novo_texto and nova_data and nova_hora:
            dt = combinar_data_hora(nova_data.strip(), nova_hora.strip())
            if dt:
                nova_tarefa = f"{novo_texto.strip()} | {dt.strftime('%Y-%m-%d %H:%M')}"
                if concluida:
                    nova_tarefa = "[✔] " + nova_tarefa
                lista.delete(indice)
                lista.insert(tk.END, nova_tarefa)
                ordenar_tarefas()
                salvar_tarefas()
            else:
                messagebox.showerror("Erro", "Data ou hora inválida.")
    except:
        messagebox.showwarning("Aviso", "Selecione uma tarefa para editar!")

# Função que ordena a lista: tarefas ativas primeiro, depois as concluídas
def ordenar_tarefas():
    tarefas = list(lista.get(0, tk.END))
    ativas = sorted([t for t in tarefas if not t.startswith("[✔]")], key=extrair_data_hora)
    concluidas = sorted([t for t in tarefas if t.startswith("[✔]")], key=extrair_data_hora)
    lista.delete(0, tk.END)
    for t in ativas + concluidas:
        lista.insert(tk.END, t)

# Salva todas as tarefas da lista em um arquivo
def salvar_tarefas():
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        for tarefa in lista.get(0, tk.END):
            f.write(tarefa + "\n")

# Carrega as tarefas do arquivo ao iniciar
def carregar_tarefas():
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
            for linha in f:
                lista.insert(tk.END, linha.strip())
        ordenar_tarefas()

# ------------------ INTERFACE GRÁFICA ------------------

janela = tk.Tk()
janela.title("Minha Agenda")
janela.geometry("430x570")

# Campo de entrada de texto da tarefa
entrada = tk.Entry(janela, width=40)
entrada.pack(pady=8)
entrada.bind("<Return>", lambda event: adicionar_tarefa())  # Permite pressionar Enter

# Área com calendário e hora
frame_datahora = tk.Frame(janela)
frame_datahora.pack()

# Seletor de data (usa DateEntry do tkcalendar)
seletor_data = DateEntry(frame_datahora, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
seletor_data.grid(row=0, column=0, padx=5)

# Campo de entrada para hora
entrada_hora = tk.Entry(frame_datahora, width=10)
entrada_hora.insert(0, "HH:MM")
entrada_hora.grid(row=0, column=1, padx=5)

# Botões principais
frame_botoes = tk.Frame(janela)
frame_botoes.pack(pady=5)

btn_adicionar = tk.Button(frame_botoes, text="Adicionar", width=10, command=adicionar_tarefa)
btn_adicionar.grid(row=0, column=0, padx=4)

btn_remover = tk.Button(frame_botoes, text="Remover", width=10, command=remover_tarefa)
btn_remover.grid(row=0, column=1, padx=4)

btn_concluir = tk.Button(frame_botoes, text="Concluir", width=10, command=marcar_como_concluida)
btn_concluir.grid(row=0, column=2, padx=4)

# Botão para editar tarefa
btn_editar = tk.Button(janela, text="Editar Tarefa/Data/Hora", width=35, command=editar_tarefa)
btn_editar.pack(pady=5)

# Lista de tarefas
lista = tk.Listbox(janela, width=60, height=18)
lista.pack(pady=10)

# Carrega as tarefas salvas, se houver
carregar_tarefas()

# Inicia o loop da interface gráfica
janela.mainloop()
