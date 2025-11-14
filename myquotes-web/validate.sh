echo "🔍 VALIDANDO PROJETO VITE + REACT + TAILWIND"

echo ""
echo "📌 1. Versões de Node e NPM:"
node -v
npm -v

echo ""
echo "📌 2. Validando package.json existe:"
ls -l package.json

echo ""
echo "📌 3. Dependências instaladas:"
npm list vite | sed 's/^/   /'
npm list react | sed 's/^/   /'
npm list tailwindcss | sed 's/^/   /'
npm list postcss | sed 's/^/   /'
npm list autoprefixer | sed 's/^/   /'

echo ""
echo "📌 4. Verificando node_modules:"
if [ -d "node_modules" ]; then
  echo "   ✔ node_modules existe"
else
  echo "   ❌ node_modules NÃO existe"
fi

echo ""
echo "📌 5. Verificando arquivos essenciais:"
files=(
  "index.html"
  "vite.config.js"
  "tailwind.config.js"
  "postcss.config.js"
  "src/index.css"
  "src/main.jsx"
  "src/App.jsx"
)

for f in "${files[@]}"; do
  if [ -f "$f" ]; then
    echo "   ✔ $f encontrado"
  else
    echo "   ❌ $f NÃO ENCONTRADO"
  fi
done

echo ""
echo "📌 6. Conteúdo do tailwind.config.js:"
sed 's/^/   /' tailwind.config.js

echo ""
echo "📌 7. Conteúdo do postcss.config.js:"
sed 's/^/   /' postcss.config.js

echo ""
echo "📌 8. Conteúdo do src/index.css:"
sed 's/^/   /' src/index.css

echo ""
echo "📌 9. Conteúdo do vite.config.js:"
sed 's/^/   /' vite.config.js

echo ""
echo "📌 10. Verificando se Tailwind está preparado:"
grep -q "@tailwind base;" src/index.css && echo "   ✔ Tailwind OK" || echo "   ❌ Tailwind NÃO configurado"

echo ""
echo "🎯 VALIDAÇÃO FINALIZADA"
echo "Se tudo estiver ✔, você pode rodar:"
echo "   npm run dev"

