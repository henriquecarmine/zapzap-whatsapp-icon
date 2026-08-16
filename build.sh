#!/usr/bin/env bash
# Monta o gancho e o tarball que o .spec espera.
#
# A arte fica em UM lugar só, na raiz. O gancho precisa dela ao lado, então
# ela é copiada na construção em vez de versionada duas vezes — duas cópias
# do mesmo SVG é convite a corrigir uma e esquecer a outra.
set -euo pipefail

AQUI=$(cd "$(dirname "$0")" && pwd)
cd "$AQUI"

NOME=zapzap-whatsapp-icon
VERSAO=$(awk -F': *' '/^Version:/{print $2; exit}' $NOME.spec)

echo "== $NOME $VERSAO =="

# 1. Arte ao lado do gancho, para rodar direto do repositório.
rm -rf hook/arte
mkdir -p hook/arte
cp whatsapp-symbolic.svg whatsapp-symbolic-count.svg hook/arte/

# 2. Confere que o gerador ainda produz SVG válido em cada faixa de dígitos.
#    Barato, e pega o dia em que alguém mexer no modelo e quebrar a
#    substituição de {size} ou {stroke}.
for n in 0 1 9 47; do
	python3 gerar.py "$n" | grep -q "</svg>" \
		|| { echo "gerar.py $n não produziu SVG completo" >&2; exit 1; }
	python3 gerar.py "$n" | grep -q "{" \
		&& { echo "gerar.py $n deixou marcador por substituir" >&2; exit 1; }
done
echo "gerador: ok em 0, 1, 9 e 47"

# 3. Tarball para o rpmbuild.
rm -rf dist
mkdir -p "dist/$NOME-$VERSAO/arte"
cp hook/sitecustomize.py gerar.py README.md LICENSE $NOME "dist/$NOME-$VERSAO/"
cp whatsapp-symbolic.svg whatsapp-symbolic-count.svg "dist/$NOME-$VERSAO/arte/"
( cd dist && tar czf "$NOME-$VERSAO.tar.gz" "$NOME-$VERSAO" && rm -rf "$NOME-$VERSAO" )

echo
echo "dist/$NOME-$VERSAO.tar.gz  -> ~/rpmbuild/SOURCES/ e então:"
echo "                              rpmbuild -ba $NOME.spec"
