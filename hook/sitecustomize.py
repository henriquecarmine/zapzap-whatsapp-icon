"""Substitui o ícone de bandeja do ZapZap sem tocar no pacote dele.

Python importa `sitecustomize` sozinho na partida, se ele estiver no
caminho. O flatpak honra `PYTHONPATH` (conferido), então basta apontar para
esta pasta e o remendo entra — sem escrever nada dentro do flatpak, que é
somente leitura, e sem impedir que ele se atualize pelo Flathub.

O que muda: nos temas SIMBÓLICOS, o glifo passa a ser a marca do WhatsApp e o
contador deixa de ser pílula vermelha, virando um dígito na mesma cor com um
vão aberto atrás. O tema `default` fica intacto — quem escolher o logo verde
do ZapZap continua com ele. Remendo que sequestra a escolha do usuário é
remendo mal-educado.

Se qualquer coisa falhar aqui, o ZapZap segue com o ícone original: toda a
instalação do gancho está sob try/except largo, porque um erro nesta camada
não pode impedir o aplicativo de abrir.
"""
import os
import sys

ALVO = "zapzap.assets.icons.tray_icon"


def _encadear_original():
    """Roda o sitecustomize que o nosso está sombreando.

    Python importa UM `sitecustomize` só — o primeiro do caminho. Como o
    nosso entra pelo PYTHONPATH, ele vem antes do da distribuição, e o
    original nunca roda. No runtime do flatpak isso é fatal: é justamente o
    sitecustomize dele que acrescenta `/app/.../site-packages` ao caminho.
    Sem encadear, o PyQt6 some e o aplicativo não abre.

    Medido: com o gancho ingênuo, `/app/lib/python3.13/site-packages`
    desaparecia de sys.path e o import de PyQt6 estourava.
    """
    import importlib.util

    meu = os.path.dirname(os.path.abspath(__file__))
    for entrada in sys.path:
        if not entrada or os.path.abspath(entrada) == meu:
            continue
        alvo = os.path.join(entrada, "sitecustomize.py")
        if not os.path.isfile(alvo):
            continue
        spec = importlib.util.spec_from_file_location("_sitecustomize_orig", alvo)
        if spec and spec.loader:
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)
        break


def _instalar():
    import importlib.abc
    import importlib.util
    from pathlib import Path

    arte = Path(__file__).resolve().parent / "arte"

    def _ler(nome):
        return (arte / nome).read_text(encoding="utf-8")

    class _Envolve(importlib.abc.Loader):
        """Deixa o módulo original carregar e só então o remenda."""

        def __init__(self, interno):
            self._interno = interno

        def create_module(self, spec):
            return self._interno.create_module(spec)

        def exec_module(self, modulo):
            self._interno.exec_module(modulo)
            try:
                _remendar(modulo)
            except Exception as e:            # noqa: BLE001
                print(f"[zapzap-whatsapp-icon] remendo não aplicado: {e}",
                      file=sys.stderr)

    class _Localizador(importlib.abc.MetaPathFinder):
        _ocupado = False

        def find_spec(self, nome, caminho=None, alvo=None):
            if nome != ALVO or _Localizador._ocupado:
                return None
            # Reentrância: find_spec abaixo dispararia este mesmo localizador.
            _Localizador._ocupado = True
            try:
                spec = importlib.util.find_spec(nome)
            finally:
                _Localizador._ocupado = False
            if spec is None or spec.loader is None:
                return None
            spec.loader = _Envolve(spec.loader)
            return spec

    def _remendar(modulo):
        TrayIcon = modulo.TrayIcon
        original = TrayIcon.getIcon
        marca = _ler("whatsapp-symbolic.svg")
        modelo = _ler("whatsapp-symbolic-count.svg")

        # Corpo do dígito e largura do vão, por quantidade de dígitos.
        # Medidos a 22 px, que é o tamanho que importa.
        TAMANHOS = {1: (104, 24), 2: (82, 20)}

        def _svg(qtd, cor):
            if qtd <= 0:
                return marca.replace("#ffffff", cor)
            # Capado em 9+: três dígitos viram borrão a 22 px e o vão come
            # metade da bolha. Contador ilegível custa a marca e não devolve
            # nada.
            texto = str(qtd) if qtd <= 9 else "9+"
            corpo, traco = TAMANHOS[len(texto)]
            return (modelo.replace("{color}", cor)
                          .replace("{number}", texto)
                          .replace("{size}", str(corpo))
                          .replace("{stroke}", str(traco)))

        @staticmethod
        def getIcon(theme=TrayIcon.Type.Default, qtd=0):
            # O tema `default` é do ZapZap e não se mexe nele.
            if theme == TrayIcon.Type.Default:
                return original(theme, qtd)
            cor = "#241f31" if theme == TrayIcon.Type.SDark else "#ffffff"
            return TrayIcon._TrayIcon__build(_svg(int(qtd or 0), cor))

        TrayIcon.getIcon = getIcon

    sys.meta_path.insert(0, _Localizador())


try:
    _encadear_original()
except Exception as e:                        # noqa: BLE001
    print(f"[zapzap-whatsapp-icon] sitecustomize original não encadeado: {e}",
          file=sys.stderr)

try:
    _instalar()
except Exception as e:                        # noqa: BLE001
    # O ZapZap tem de abrir mesmo que o remendo não entre.
    print(f"[zapzap-whatsapp-icon] gancho não instalado: {e}", file=sys.stderr)
