import ctypes
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# 1. Definicao da struct identica ao C
TAM_NOME = 50

class LivroC(ctypes.Structure):
    _fields_ = [
        ("nome", ctypes.c_char * TAM_NOME),
        ("preco", ctypes.c_float)
    ]

# 2. Carregamento da DLL
caminho_dll = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogo.dll")
if not os.path.exists(caminho_dll):
    caminho_dll = os.path.abspath("catalogo.dll")

if not os.path.exists(caminho_dll):
    print(f"Erro: 'catalogo.dll' nao encontrada em {caminho_dll}.")
    sys.exit(1)

lib = ctypes.CDLL(caminho_dll)

# Configurar tipos das funcoes de ordenacao
for func in [
    lib.ordenarNomeCrescente,
    lib.ordenarNomeDecrescente,
    lib.ordenarLivrosCrescente,
    lib.ordenarLivrosDecrescente,
]:
    func.argtypes = [ctypes.POINTER(LivroC), ctypes.c_int]
    func.restype = None

# Configurar tipo da nova funcao de exclusao: int removerLivro(livros[], int tamanho, int indice)
lib.removerLivro.argtypes = [ctypes.POINTER(LivroC), ctypes.c_int, ctypes.c_int]
lib.removerLivro.restype = ctypes.c_int


class AppCatalogo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Catálogo de Livros - Backend C & Interface Python")
        self.geometry("700x560")
        self.minsize(640, 480)

        self.catalogo = [
            {"nome": "Estruturas de Dados e Algoritmos", "preco": 115.90},
            {"nome": "Linguagem C Completa e Descomplicada", "preco": 79.50},
            {"nome": "Clean Code", "preco": 94.00},
            {"nome": "Arquitetura e Organizacao de Computadores", "preco": 142.30},
            {"nome": "Entendendo Algoritmos", "preco": 62.00},
        ]

        self.configurar_estilo()
        self.criar_componentes()
        self.atualizar_tabela()

    def configurar_estilo(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=4)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=24)

    def criar_componentes(self):
        # --- Formulario de Cadastro ---
        frame_cad = ttk.LabelFrame(self, text=" Cadastrar Novo Livro ", padding=10)
        frame_cad.pack(fill="x", padx=15, pady=(10, 5))

        ttk.Label(frame_cad, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_nome = ttk.Entry(frame_cad, width=32)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_cad, text="Preço (R$):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_preco = ttk.Entry(frame_cad, width=12)
        self.entry_preco.grid(row=0, column=3, padx=5, pady=5)

        btn_add = ttk.Button(frame_cad, text="Adicionar", command=self.adicionar_livro)
        btn_add.grid(row=0, column=4, padx=10, pady=5)

        # --- Painel de Ordenacao e Acoes ---
        frame_opcoes = ttk.LabelFrame(self, text=" Operações de Catálogo (Executadas em C) ", padding=10)
        frame_opcoes.pack(fill="x", padx=15, pady=5)

        ttk.Label(frame_opcoes, text="Critério:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_criterio = ttk.Combobox(
            frame_opcoes, values=["Nome", "Preço"], state="readonly", width=10
        )
        self.combo_criterio.current(0)
        self.combo_criterio.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_opcoes, text="Ordem:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_ordem = ttk.Combobox(
            frame_opcoes, values=["Crescente", "Decrescente"], state="readonly", width=12
        )
        self.combo_ordem.current(0)
        self.combo_ordem.grid(row=0, column=3, padx=5, pady=5)

        btn_ord = ttk.Button(frame_opcoes, text="Ordenar Catálogo", command=self.executar_ordenacao_c)
        btn_ord.grid(row=0, column=4, padx=10, pady=5)

        btn_del = ttk.Button(frame_opcoes, text="Excluir Selecionado", command=self.excluir_livro_c)
        btn_del.grid(row=0, column=5, padx=10, pady=5)

        # --- Tabela de Livros ---
        frame_tab = ttk.Frame(self, padding=10)
        frame_tab.pack(fill="both", expand=True, padx=5)

        colunas = ("nome", "preco")
        self.tree = ttk.Treeview(frame_tab, columns=colunas, show="headings", selectmode="browse")
        self.tree.heading("nome", text="Título / Nome do Livro")
        self.tree.heading("preco", text="Preço")

        self.tree.column("nome", width=460, anchor="w")
        self.tree.column("preco", width=140, anchor="e")

        scroll = ttk.Scrollbar(frame_tab, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def adicionar_livro(self):
        nome = self.entry_nome.get().strip()
        preco_str = self.entry_preco.get().strip().replace(",", ".")

        if not nome:
            messagebox.showwarning("Campo Vazio", "Por favor, informe o título do livro.")
            return

        try:
            preco = float(preco_str)
            if preco < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Preço Inválido", "Digite um valor numérico válido para o preço.")
            return

        self.catalogo.append({"nome": nome, "preco": preco})
        self.entry_nome.delete(0, tk.END)
        self.entry_preco.delete(0, tk.END)
        self.atualizar_tabela()

    def excluir_livro_c(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Seleção Necessária", "Selecione um livro na tabela para excluir.")
            return

        # Pega o indice da linha selecionada na Treeview
        indice = self.tree.index(selecionado[0])
        livro_nome = self.catalogo[indice]["nome"]

        confirmar = messagebox.askyesno(
            "Confirmação", f"Deseja realmente remover o livro:\n\n'{livro_nome}'?"
        )
        if not confirmar:
            return

        n = len(self.catalogo)
        VetorLivrosC = LivroC * n
        buffer_c = VetorLivrosC()

        for i, item in enumerate(self.catalogo):
            buffer_c[i].nome = item["nome"].encode("utf-8")[: TAM_NOME - 1]
            buffer_c[i].preco = item["preco"]

        # Chama a funcao em C que remove o elemento e desloca os dados
        novo_tam = lib.removerLivro(buffer_c, n, indice)

        # Atualiza a lista no Python com o novo tamanho retornado pelo C
        self.catalogo = [
            {
                "nome": buffer_c[i].nome.decode("utf-8", errors="ignore"),
                "preco": buffer_c[i].preco,
            }
            for i in range(novo_tam)
        ]

        self.atualizar_tabela()

    def atualizar_tabela(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for livro in self.catalogo:
            self.tree.insert("", "end", values=(livro["nome"], f"R$ {livro['preco']:.2f}"))

    def executar_ordenacao_c(self):
        n = len(self.catalogo)
        if n <= 1:
            return

        VetorLivrosC = LivroC * n
        buffer_c = VetorLivrosC()

        for i, item in enumerate(self.catalogo):
            buffer_c[i].nome = item["nome"].encode("utf-8")[: TAM_NOME - 1]
            buffer_c[i].preco = item["preco"]

        criterio = self.combo_criterio.get()
        ordem = self.combo_ordem.get()

        if criterio == "Nome":
            if ordem == "Crescente":
                lib.ordenarNomeCrescente(buffer_c, n)
            else:
                lib.ordenarNomeDecrescente(buffer_c, n)
        elif criterio == "Preço":
            if ordem == "Crescente":
                lib.ordenarLivrosCrescente(buffer_c, n)
            else:
                lib.ordenarLivrosDecrescente(buffer_c, n)

        self.catalogo = [
            {
                "nome": buffer_c[i].nome.decode("utf-8", errors="ignore"),
                "preco": buffer_c[i].preco,
            }
            for i in range(n)
        ]

        self.atualizar_tabela()


if __name__ == "__main__":
    app = AppCatalogo()
    app.mainloop()