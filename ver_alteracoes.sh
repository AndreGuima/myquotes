#!/bin/bash

# Script para imprimir e mostrar conteúdo de TODOS os arquivos alterados na branch atual

echo "=== TODOS OS ARQUIVOS ALTERADOS NA BRANCH ATUAL ==="
echo ""

# Verifica se estamos em um repositório git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Erro: Este diretório não é um repositório Git!"
    exit 1
fi

# Obtém o nome da branch atual
BRANCH_ATUAL=$(git branch --show-current)
echo "📋 Branch atual: $BRANCH_ATUAL"
echo ""

# Array para armazenar todos os arquivos alterados
ARQUIVOS_TOTAL=()

# 1. Arquivos modificados não commitados (git status)
echo "🔍 Buscando arquivos modificados não commitados..."
while IFS= read -r arquivo; do
    if [ -n "$arquivo" ]; then
        ARQUIVOS_TOTAL+=("$arquivo")
    fi
done < <(git status --porcelain | awk '{print $2}')

# 2. Arquivos commitados na branch atual (comparação com main/master)
echo "🔍 Buscando arquivos commitados na branch..."
if git show-ref --verify --quiet refs/heads/main 2>/dev/null; then
    BRANCH_REFERENCIA="main"
elif git show-ref --verify --quiet refs/heads/master 2>/dev/null; then
    BRANCH_REFERENCIA="master"
else
    echo "⚠️  Não foi encontrar branch main/master, usando HEAD~1 como referência"
    BRANCH_REFERENCIA="HEAD~1"
fi

while IFS= read -r arquivo; do
    if [ -n "$arquivo" ] && [[ ! " ${ARQUIVOS_TOTAL[@]} " =~ " ${arquivo} " ]]; then
        ARQUIVOS_TOTAL+=("$arquivo")
    fi
done < <(git diff --name-only $BRANCH_REFERENCIA...HEAD 2>/dev/null || git diff --name-only HEAD~1 HEAD 2>/dev/null)

# Remove duplicatas (caso haja)
ARQUIVOS_UNICOS=()
for arquivo in "${ARQUIVOS_TOTAL[@]}"; do
    if [[ ! " ${ARQUIVOS_UNICOS[@]} " =~ " ${arquivo} " ]]; then
        ARQUIVOS_UNICOS+=("$arquivo")
    fi
done

# Verifica se há arquivos alterados
if [ ${#ARQUIVOS_UNICOS[@]} -eq 0 ]; then
    echo "✅ Nenhum arquivo foi alterado nesta branch."
    exit 0
fi

echo "🎯 Encontrados ${#ARQUIVOS_UNICOS[@]} arquivo(s) alterado(s) no total:"
printf '%s\n' "${ARQUIVOS_UNICOS[@]}"
echo ""

CONTADOR=1

# Processa cada arquivo
for arquivo in "${ARQUIVOS_UNICOS[@]}"; do
    echo "================================================================================"
    echo "📄 ARQUIVO $CONTADOR/${#ARQUIVOS_UNICOS[@]}: $arquivo"
    echo "================================================================================"
    
    # Verifica status do arquivo
    STATUS=$(git status --porcelain "$arquivo" 2>/dev/null | awk '{print $1}' || echo "")
    
    case "$STATUS" in
        "M") STATUS_DESC="Modificado (não commitado)" ;;
        "A") STATUS_DESC="Adicionado (não commitado)" ;;
        "D") STATUS_DESC="Deletado (não commitado)" ;;
        "??") STATUS_DESC="Novo arquivo (não trackeado)" ;;
        *) STATUS_DESC="Comitado na branch" ;;
    esac
    
    echo "📝 Status: $STATUS_DESC"
    
    if [ -f "$arquivo" ] && [ -r "$arquivo" ]; then
        # Verifica se é arquivo texto antes de mostrar
        if file "$arquivo" | grep -q text; then
            echo "--- CONTEÚDO ---"
            cat -- "$arquivo"
            echo ""
            echo "--- FIM DO ARQUIVO ---"
        else
            echo "⚠️  Arquivo binário ou não-texto - conteúdo não será exibido"
        fi
    else
        echo "❌ Arquivo não encontrado ou sem permissão de leitura (pode ter sido deletado)"
    fi
    
    echo ""
    ((CONTADOR++))
done

echo "================================================================================
🎉 Processamento concluído! Todos os $((CONTADOR-1)) arquivos foram verificados.
================================================================================"

