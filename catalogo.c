#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TamNome 50

typedef struct livros {
    char nome[TamNome];
    float preco;
} livros;

// Remove um livro por indice deslocando os elementos subsequentes a esquerda
// Retorna o novo tamanho do vetor (tamanho - 1)
int removerLivro(livros p0[], int tamanho, int indice) {
    if (indice < 0 || indice >= tamanho) {
        return tamanho; // Indice invalido, nao altera o tamanho
    }

    for (int i = indice; i < tamanho - 1; ++i) {
        p0[i] = p0[i + 1];
    }

    return tamanho - 1;
}

// Ordena pelo preco: menor para maior
void ordenarLivrosCrescente(livros p0[], int tamanho) {
    for (int i = 1; i < tamanho; ++i) {
        livros key = p0[i];
        int j = i - 1;

        while (j >= 0 && p0[j].preco > key.preco) {
            p0[j + 1] = p0[j];
            j = j - 1;
        }

        p0[j + 1] = key;
    }
}

// Ordena pelo preco: maior para menor
void ordenarLivrosDecrescente(livros p0[], int tamanho) {
    for (int i = 1; i < tamanho; ++i) {
        livros key = p0[i];
        int j = i - 1;

        while (j >= 0 && p0[j].preco < key.preco) {
            p0[j + 1] = p0[j];
            j = j - 1;
        }

        p0[j + 1] = key;
    }
}

// Ordena pelo nome: A-Z
void ordenarNomeCrescente(livros p0[], int tamanho) {
    for (int i = 1; i < tamanho; ++i) {
        livros key = p0[i];
        int j = i - 1;

        while (j >= 0 && strcmp(p0[j].nome, key.nome) > 0) {
            p0[j + 1] = p0[j];
            j = j - 1;
        }

        p0[j + 1] = key;
    }
}

// Ordena pelo nome: Z-A
void ordenarNomeDecrescente(livros p0[], int tamanho) {
    for (int i = 1; i < tamanho; ++i) {
        livros key = p0[i];
        int j = i - 1;

        while (j >= 0 && strcmp(p0[j].nome, key.nome) < 0) {
            p0[j + 1] = p0[j];
            j = j - 1;
        }

        p0[j + 1] = key;
    }
}