import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

# Inicializa a aplicação
def init_app():
    root = tk.Tk()
    root.title("Aplicação de Programação Linear")
    root.geometry("600x400")
    create_method_selection(root)
    root.mainloop()


def load_method_interface(root, method):
    clear_widgets(root)  # Certifique-se de que esta função está bem definida

    if method == "Função Objetiva" or method == "Simplex":
        create_linear_method_interface(root, method)
    elif method == "Método de Transporte":
        create_transport_method_interface(root)
    else:
        raise ValueError(f"Método '{method}' não é válido.")  # Tratamento para valores inesperados

# Interface para seleção de método
def create_method_selection(root):
    clear_widgets(root)
    ttk.Label(root, text="Escolha o Método:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    method = ttk.Combobox(root, values=["Função Objetiva", "Simplex", "Método de Transporte"])
    method.grid(row=0, column=1, padx=10, pady=10)
    method.current(0)  # Define um valor inicial para evitar seleção vazia

    def on_select_method():
        selected_method = method.get().strip()
        if selected_method:
            try:
                load_method_interface(root, selected_method)
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao carregar o método: {str(e)}")
        else:
            messagebox.showwarning("Aviso", "Por favor, selecione um método.")

    ttk.Button(root, text="Selecionar", command=on_select_method).grid(row=1, column=0, columnspan=2, pady=20)

# Limpa os widgets anteriores
def clear_widgets(root):
    for widget in root.winfo_children():
        widget.destroy()

# Interface para métodos lineares (Função Objetiva e Simplex)
def create_linear_method_interface(root, method):
    clear_widgets(root)
    
    # Entradas para os coeficientes e restrições
    obj_entry = create_labeled_entry(root, "Coeficientes da Função Objetiva (ex: 3 5):", 0)
    restrictions_entry = create_labeled_entry(root, "Restrições (ex: 1 1 <= 4; 2 1 <= 6):", 1)
    optimization_type = create_labeled_combobox(root, "Tipo de Otimização:", ["Maximizar", "Minimizar"], 2)

    # Botão Resolver
    ttk.Button(root, text="Resolver", 
               command=lambda: solve_problem(root, obj_entry, restrictions_entry, optimization_type, method)
              ).grid(row=3, column=0, columnspan=2, pady=20)
    
    # Botão Voltar
    ttk.Button(root, text="Voltar", command=lambda: create_method_selection(root)).grid(row=4, column=0, columnspan=2, pady=10)

# Interface para o Método de Transporte
def create_transport_method_interface(root):
    clear_widgets(root)
    
    # Entradas para fornecimento, demanda e custos
    supply_entry = create_labeled_entry(root, "Fornecimento (ex: 20 30 25):", 0)
    demand_entry = create_labeled_entry(root, "Demanda (ex: 30 25 20):", 1)
    costs_entry = create_labeled_entry(root, "Matriz de Custos (ex: 8 6 10; 9 12 13):", 2)

    # Botão Resolver
    ttk.Button(root, text="Resolver", 
               command=lambda: transport_method(root, supply_entry, demand_entry, costs_entry)
              ).grid(row=3, column=0, columnspan=2, pady=20)
    
    # Botão Voltar
    ttk.Button(root, text="Voltar", command=lambda: create_method_selection(root)).grid(row=4, column=0, columnspan=2, pady=10)

# Criação de rótulo e entrada
def create_labeled_entry(root, text, row):
    ttk.Label(root, text=text).grid(row=row, column=0, padx=10, pady=10, sticky="w")
    entry = ttk.Entry(root, width=30)
    entry.grid(row=row, column=1, padx=10, pady=10)
    return entry

# Criação de rótulo e combobox
def create_labeled_combobox(root, text, values, row):
    ttk.Label(root, text=text).grid(row=row, column=0, padx=10, pady=10, sticky="w")
    combobox = ttk.Combobox(root, values=values)
    combobox.grid(row=row, column=1, padx=10, pady=10)
    return combobox

# Solução para problemas lineares

def parse_restrictions(restrictions):
    # Lógica para processar as restrições
    A_ub, b_ub = [], []
    for restriction in restrictions.split(';'):
        parts = restriction.split()
        operator = next(op for op in ["<=", ">=", "="] if op in parts)

        index = parts.index(operator)
        coefficients = list(map(float, parts[:index]))
        limit = float(parts[index + 1])

        if operator == "<=":
            A_ub.append(coefficients)
            b_ub.append(limit)
        elif operator == ">=":
            A_ub.append([-c for c in coefficients])
            b_ub.append(-limit)
        elif operator == "=":
            A_ub += [coefficients, [-c for c in coefficients]]
            b_ub += [limit, -limit]
    return A_ub, b_ub


def solve_problem(root, obj_entry, restrictions_entry, optimization_type, method):
    try:
        obj_func = list(map(float, obj_entry.get().split()))
        A_ub, b_ub = parse_restrictions(restrictions_entry.get())

        if method == "Simplex":
            # Inverte os coeficientes da função objetivo se for uma maximização
            obj_func = [-coef for coef in obj_func] if optimization_type.get() == "Maximizar" else obj_func

            # Executa o método Simplex
            result = linprog(c=obj_func, A_ub=np.array(A_ub), b_ub=np.array(b_ub))

            # Cria a janela de resultado
            result_window = tk.Toplevel(root)
            result_window.title("Resultado do Simplex")

            # Verifica se houve sucesso na resolução
            if result.success:
                # Se for uma maximização, reverte o valor da função objetivo
                if optimization_type.get() == "Maximizar":
                    result.fun = -result.fun

                # Exibe os resultados
                ttk.Label(result_window, text="Solução Ótima Encontrada").pack()
                ttk.Label(result_window, text=f"Valor da Função Objetiva: {result.fun:.4f}").pack()
                for i, val in enumerate(result.x):
                    ttk.Label(result_window, text=f"x{i + 1} = {val:.4f}").pack()
            else:
                # Exibe mensagem de erro caso a solução não tenha sido encontrada
                ttk.Label(result_window, text="Não foi possível encontrar uma solução.").pack()
                ttk.Label(result_window, text=f"Motivo: {result.message}").pack()

        elif method == "Função Objetiva":
            plot_objective_function(obj_func, A_ub, b_ub, optimization_type.get())

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

# Método de Transporte (Canto Noroeste)
def transport_method(root, supply_entry, demand_entry, costs_entry):
    try:
        supply = list(map(int, supply_entry.get().split()))
        demand = list(map(int, demand_entry.get().split()))
        costs = [list(map(int, row.split())) for row in costs_entry.get().split(';')]

        if sum(supply) != sum(demand):
            messagebox.showerror("Erro", "A oferta e a demanda não são iguais.")
            return

        allocation, total_cost = northwest_corner_method(supply, demand, costs)

        result_window = tk.Toplevel(root)
        result_window.title("Resultado do Método de Transporte")
        ttk.Label(result_window, text=f"Alocação: {allocation}").pack()
        ttk.Label(result_window, text=f"Custo Total: {total_cost}").pack()
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

def northwest_corner_method(supply, demand, costs):
    rows, cols = len(supply), len(demand)
    allocation = [[0] * cols for _ in range(rows)]
    total_cost = 0

    i, j = 0, 0
    while i < rows and j < cols:
        amount = min(supply[i], demand[j])
        allocation[i][j] = amount
        total_cost += amount * costs[i][j]

        supply[i] -= amount
        demand[j] -= amount

        if supply[i] == 0:
            i += 1
        elif demand[j] == 0:
            j += 1

    return allocation, total_cost

# Plotagem da função objetivo (versão melhorada)
def plot_objective_function(obj_func, A_ub, b_ub, opt_type):
    if len(obj_func) != 2:
        messagebox.showwarning("Aviso", "Plotagem gráfica disponível apenas para problemas com duas variáveis.")
        return

    x = np.linspace(0, 10, 100)
    fig, ax = plt.subplots()

    for i, (coeffs, limit) in enumerate(zip(A_ub, b_ub)):
        y = (limit - coeffs[0] * x) / coeffs[1]
        ax.plot(x, y, label=f'Restrição {i + 1}')

    y_obj = (-obj_func[0] * x) / obj_func[1] if opt_type == "Minimizar" else (obj_func[0] * x) / obj_func[1]
    ax.plot(x, y_obj, '--', label='Função Objetiva')

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.legend()
    plt.show()

# Inicializa a aplicação
if __name__ == "__main__":
    init_app()
