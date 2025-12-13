#!/bin/bash

echo "Veja todos os meus arquivos que trabalhei nessa tarefa, corrija se algum estiver errado."

# Usa while para ler status e arquivo
git status --porcelain | while read status file; do
    if [ -f "$file" ]; then
        echo ">>> [$status] $file"
        cat "$file"
        echo -e "\n----------------------------------------\n"
    elif [ -d "$file" ]; then
        # Se for diretório, percorre os arquivos dentro
        find "$file" -type f | while read subf; do
            echo ">>> [$status] $subf"
            cat "$subf"
            echo -e "\n----------------------------------------\n"
        done
    fi
done
