#!/bin/bash

echo "Veja todos os meus arquivos que trabalhei nessa tarefa, e corrija se algum estiver errado."

# Lista arquivos modificados ou não monitorados
files=$(git status --porcelain | awk '{print $2}')

# Itera sobre cada arquivo encontrado
for f in $files; do
    if [ -f "$f" ]; then
        echo ">>> cat $f"
        cat "$f"
        echo -e "\n----------------------------------------\n"
    fi
done

