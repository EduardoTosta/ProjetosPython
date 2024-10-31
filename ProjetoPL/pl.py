import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from scipy.optimize import linprog

# Função que será chamada ao clicar em "Calcular"
def calcular():
    maximizacao = max_min_var.get() == "Maximização"
    
    # Obter os coeficientes da função objetivo
    try:
        c = list(map(float, objetivo_entry.get().split(',')))
        if maximizacao:
            c = [-coef for coef in c]  # Para maximizar, invertendo os sinais
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira valores válidos para a função objetivo.")
        return
    
    # Obter restrições
    restricoes = []
    for entry in restricoes_entries:
        try:
            restricoes.append(list(map(float, entry.get().split(','))))
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos para as restrições.")
            return

    # Separar as restrições em coeficientes e limites
    A = [r[:-1] for r in restricoes]
    b = [r[-1] for r in restricoes]

    if len(c) == 2:
        # Usa o método gráfico para problemas com duas variáveis
        metodo_grafico(c, A, b, maximizacao)
    else:
        # Usa o Simplex para problemas com mais de duas variáveis
        metodo_simplex(c, A, b, maximizacao)

# Função para resolver problemas pelo método gráfico
def metodo_grafico(c, A, b, maximizacao):
    try:
        vertices = encontrar_vertices(A, b)
        if not vertices.size:
            messagebox.showerror("Erro", "Não foi possível encontrar uma região viável.")
            return
        solucao, valor_objetivo = encontrar_solucao_otima(vertices, c)
        solucao = [-x for x in solucao] if maximizacao else solucao  # Ajuste para maximização
        messagebox.showinfo("Resultado", f"Solução ótima: {solucao}\nValor da função objetivo: {valor_objetivo}")
        plotar_grafico(A, b, c, vertices, solucao, maximizacao)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao resolver o problema: {e}")

# Função para resolver problemas pelo método Simplex
def metodo_simplex(c, A, b, maximizacao):
    try:
        resultado = linprog(c, A_ub=A, b_ub=b, method="simplex")
        if resultado.success:
            solucao = [-x for x in resultado.x] if maximizacao else resultado.x  # Ajuste para maximização
            messagebox.showinfo("Resultado", f"Solução ótima: {solucao}\nValor da função objetivo: {resultado.fun}")
        else:
            messagebox.showerror("Erro", "Não foi possível encontrar uma solução ótima.")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao resolver o problema com o método Simplex: {e}")

# Função para encontrar os vértices da região viável
def encontrar_vertices(A, b):
    vertices = []
    for (a1, b1), (a2, b2) in combinations(zip(A, b), 2):
        # Resolver sistema linear para cada par de restrições
        try:
            ponto = np.linalg.solve([a1, a2], [b1, b2])
            if np.all(np.dot(A, ponto) <= b):  # Verificar se o ponto satisfaz todas as restrições
                vertices.append(ponto)
        except np.linalg.LinAlgError:
            continue  # Linhas paralelas ou coincidentes (sem interseção)
    
    # Adicionar interseções com os eixos (para x1, x2 >= 0)
    for i, (a, b_lim) in enumerate(zip(A, b)):
        try:
            if a[1] != 0:  # Interseção com o eixo x1 (x2 = 0)
                x1_intercept = b_lim / a[0]
                if x1_intercept >= 0:
                    vertices.append([x1_intercept, 0])
            if a[0] != 0:  # Interseção com o eixo x2 (x1 = 0)
                x2_intercept = b_lim / a[1]
                if x2_intercept >= 0:
                    vertices.append([0, x2_intercept])
        except ZeroDivisionError:
            continue
    
    return np.array(vertices)

# Função para encontrar a solução ótima
def encontrar_solucao_otima(vertices, c):
    valores_objetivo = np.dot(vertices, c)
    idx_otimo = np.argmin(valores_objetivo)
    return vertices[idx_otimo], valores_objetivo[idx_otimo]

# Função para plotar o gráfico
def plotar_grafico(A, b, c, vertices, x_sol, maximizacao):
    plt.figure()
    x = np.linspace(0, 10, 100)
    
    # Plotar as restrições
    for i, (a, b_lim) in enumerate(zip(A, b)):
        plt.plot(x, (b_lim - a[0]*x) / a[1], label=f"Restrição {i+1}")

    # Plotar a região viável (vértices)
    if len(vertices) > 0:
        plt.fill(vertices[:, 0], vertices[:, 1], color='grey', alpha=0.3, label="Região Viável")

    # Plotar função objetivo
    plt.plot(x, (b[0] - c[0]*x) / c[1], linestyle='--', color='purple', label="Função Objetivo")

    # Plotar a solução ótima
    plt.scatter(x_sol[0], x_sol[1], color='red', label="Solução Ótima")
    
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.legend()
    plt.grid()
    plt.show()

# Configurando a janela principal do Tkinter
root = tk.Tk()
root.title("Programação Linear - Escolha de Método")
root.geometry("400x500")

# Menu para selecionar maximização ou minimização
max_min_var = tk.StringVar(value="Minimização")
max_min_label = tk.Label(root, text="Objetivo:")
max_min_label.pack()
max_min_menu = ttk.Combobox(root, textvariable=max_min_var)
max_min_menu['values'] = ("Minimização", "Maximização")
max_min_menu.pack()

# Entrada para a função objetivo
objetivo_label = tk.Label(root, text="Função Objetivo (separe os coeficientes por vírgula):")
objetivo_label.pack()
objetivo_entry = tk.Entry(root)
objetivo_entry.pack()

# Entradas para as restrições
restricoes_entries = []
restricoes_frame = tk.Frame(root)
restricoes_frame.pack()

restricoes_label = tk.Label(restricoes_frame, text="Restrição (separe coeficientes e limite por vírgula):")
restricoes_label.grid(row=0, column=0, columnspan=2)

# Função para adicionar uma nova linha de restrição
def adicionar_restricao():
    entry = tk.Entry(restricoes_frame)
    entry.grid(row=len(restricoes_entries)+1, column=0)
    restricoes_entries.append(entry)

adicionar_restricao_btn = tk.Button(root, text="Adicionar Restrição", command=adicionar_restricao)
adicionar_restricao_btn.pack()

# Botão para calcular
calcular_btn = tk.Button(root, text="Calcular", command=calcular)
calcular_btn.pack()

# Iniciar a interface
root.mainloop()
