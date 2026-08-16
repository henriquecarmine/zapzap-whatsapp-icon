# Ícone de bandeja do WhatsApp — monocromático, com contador discreto

Marca do WhatsApp em cor única, para bandeja do sistema, com o número de
mensagens não lidas **sobreposto na mesma cor** — sem pílula vermelha.

```
gerar.py 0   →  só a marca
gerar.py 3   →  marca com "3" no canto inferior direito
gerar.py 47  →  marca com "9+"
```

## Por que existe

O ZapZap (cliente de WhatsApp para Linux) tem ícone simbólico, mas:

1. **O símbolo é o dele, não o do WhatsApp** — um "Z" dentro da bolha.
2. **O contador é uma pílula vermelha**, igual nos três temas
   (`default`, `symbolic_light`, `symbolic_dark`). Numa bandeja onde todo o
   resto é monocromático, é a única coisa colorida, e o olho fica preso nela.

Verificado em `zapzap/assets/icons/tray_icon.py`, versão 7.4:

```python
_DEFAULT_NOTIFICATION = """
  <rect ... style="fill: rgb(255, 0, 0); ..." rx="19.653"/>
  <text style="fill: rgb(255,255,255); ...">{number}</text>
"""
```

## Decisões de desenho, e o que as motivou

**Bolha cheia com o fone vazado**, não bolha contornada com fone dentro. A 22
pixels — que é o tamanho que importa — contorno mais figura interna vira
mistura. Silhueta sólida com furo mantém a forma.

**O vão atrás do número é buraco, não pintura.** Pintar um fundo exigiria
adivinhar a cor do painel, e num painel translúcido a tinta vira mancha
sólida. O furo é feito por máscara e é transparente de verdade.

**O dígito é ancorado no canto**, não centrado num ponto. Centrado, "12"
vazava para fora do quadro à direita e embaixo. Ancorado, não tem como
estourar, venham quantos dígitos vierem. (Erro já pago no ícone do Wi-Fi.)

**Capado em `9+`.** Renderizado a 22 px e olhado: um dígito lê, dois ficam
apertados mas legíveis, três viram borrão e o vão come metade da bolha.
Contador ilegível é pior que contador nenhum — custa a legibilidade da marca
e não devolve nada.

## Instalação

```bash
sudo dnf install ./zapzap-whatsapp-icon-*.noarch.rpm
zapzap-whatsapp-icon --ativar
```

Feche e reabra o ZapZap, e escolha um ícone **simbólico** em
*Configurações → Aparência*. Para voltar atrás:

```bash
zapzap-whatsapp-icon --desativar
```

## Como funciona, e por que assim

O ZapZap não aceita ícone de fora: nada de `QIcon.fromTheme`, nada de caminho
configurável. O desenho é montado de modelos SVG dentro de `tray_icon.py`, e
o flatpak é **somente leitura**.

A saída é não escrever nada lá dentro. O `flatpak override` aponta o
`PYTHONPATH` do aplicativo para um gancho; Python importa `sitecustomize`
sozinho na partida, e o gancho instala um localizador que remenda
`TrayIcon.getIcon` no momento em que o módulo é carregado. O flatpak continua
se atualizando pelo Flathub normalmente.

Duas armadilhas que custaram caro, medidas e documentadas no código:

**O gancho sombreia o `sitecustomize` da distribuição.** Python importa um
só, o primeiro do caminho. No runtime do flatpak é justamente ele que
acrescenta `/app/.../site-packages`; sem encadear, o PyQt6 some e o
aplicativo não abre.

**O flatpak recusa compartilhar `/usr` com o sandbox** — *"o caminho /usr
está reservado pelo Flatpak"* —, porque o sandbox tem o `/usr` dele. Apontar
o `PYTHONPATH` para a cópia do pacote deixava o gancho inalcançável e o
remendo falhava em silêncio: o instalador dizia "Ligado", o override estava
aplicado, e o ícone continuava o original. Por isso o `--ativar` copia o
gancho para `~/.local/share` antes de apontar.

## O que ele troca

| superfície | de onde vinha o verde |
|---|---|
| bandeja | `TrayIcon.getIcon(tema)` |
| notificação | `IconRenderer.default_icon` chamava sem tema |
| janela e barra de tarefas | `app.setWindowIcon(TrayIcon.getIcon())`, sem tema |
| menu de aplicativos | ícone do tema, exportado pelo flatpak |

As três primeiras se resolvem no gancho: `getIcon()` chamado **sem
argumento** passou a seguir a escolha do usuário em vez de cair no verde. A
quarta é o tema de ícones, e o `--ativar` instala uma variante por tema —
clara no `breeze-dark`, escura no `breeze`, cinza médio no `hicolor`.

Ícone de aplicativo **não é tingido** pelo tema: ele desenha com a cor do
arquivo. Uma versão única com `currentColor` saiu invisível sobre painel
escuro. E as variantes vão em pastas que o índice do tema **declara** — o
breeze não declara `apps/scalable`, e arquivo em pasta não declarada é
ignorado sem aviso.

## Fora de alcance

A notificação espelhada do celular pelo KDE Connect **não** pode ser trocada.
Grampeando o barramento na hora que uma chega:

```
string "KDE Connect"
string "kdeconnect"        ← app_icon: o ícone pequeno
string "image_data"        ← o logo grande: 66×66, RGBA, bytes crus
```

O desenho vem pronto do Android como pixels. Não há nome de ícone para
redirecionar nem arquivo para substituir.

## Sobre a marca

O símbolo do WhatsApp é marca registrada da Meta. Aqui ele é usado para
identificar o serviço a que o cliente se conecta, que é o mesmo motivo pelo
qual o próprio ZapZap se chama assim. Este projeto não tem vínculo com a Meta
nem com o ZapZap.

## Arquivos

- `whatsapp-symbolic.svg` — a marca, sem contador
- `whatsapp-symbolic-count.svg` — modelo com `{color}` `{number}` `{size}` `{stroke}`
- `gerar.py` — escolhe corpo e vão pela quantidade de dígitos
