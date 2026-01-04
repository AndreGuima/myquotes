#!/bin/bash

echo "Vamos fazer um checkpoint."
echo "Ignora a documetação.txt e foque apenas nos arquivos de código."
echo "Veja todos os arquivos que trabalhamos nessa tarefa."

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

echo "Revise e corrija caso seja necessário ou me diga os próximos passos"
