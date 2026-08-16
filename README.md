# Bandeja monocromática — WhatsApp (ZapZap) e Telegram

Marcas em cor única para a bandeja do sistema, sem nada colorido: o WhatsApp
com o número de mensagens não lidas **sobreposto na mesma cor** — sem pílula
vermelha —, e o Telegram com a mesma tinta e o mesmo anel, no lugar do avião
de contorno fino do Breeze e do ponto azul de não lidas.

```
gerar.py 0   →  só a marca
gerar.py 3   →  marca com "3" no canto inferior direito
gerar.py 47  →  marca com "9+"
```

Dois comandos, um por aplicativo: `zapzap-whatsapp-icon` e
`telegram-tray-icon`. O pacote ainda se chama `zapzap-whatsapp-icon`, que já
não cobre o que ele faz — renomear é conversa para quando houver um terceiro.

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

**Bolha contornada com o fone cheio dentro**, que é a geometria canônica —
conferida contra os favicons autênticos do WhatsApp Web, extraídos do cache
dentro do próprio ZapZap. A primeira versão daqui era o negativo disso, bolha
cheia com o fone vazado, e o fone saía estreito demais.

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

## Telegram

Aqui não há remendo em programa nenhum, e é bom que não haja: o Telegram
**já** pede o ícone ao tema. Grampeando o `StatusNotifierItem` dele:

```
Id       = "TelegramDesktop"
IconName = "org.telegram.desktop-symbolic"
```

Quem responde é o Breeze, e responde mal para uma fileira monocromática:

1. **O avião é de contorno fino.** Medido, o glifo do Breeze tem cerca de
   metade da tinta da marca do WhatsApp ao lado. Na fileira, ele some.
2. **O ponto de não lidas é azul** (`#3daee9`, na classe `ColorScheme-Accent`).
   É a pílula vermelha do ZapZap outra vez, de outra cor.

```bash
telegram-tray-icon --ativar       # liga
telegram-tray-icon --desativar    # devolve o tema anterior
```

Nada é escrito em `/usr` nem dentro do flatpak.

### Como o ícone chega à bandeja, e as três descobertas que custaram caro

**O nome pedido não é o nome anunciado.** O Telegram publica
`org.telegram.desktop-symbolic`, mas a bandeja do Plasma busca
`telegram-panel`. Flagrado com inotify nas pastas de tema: reiniciando o
painel, o arquivo aberto foi
`/usr/share/icons/breeze-dark/status/22/telegram-panel.svg`. Trocar só o nome
anunciado não muda nada na fileira — embora uma notificação com esse mesmo
nome já mostrasse o desenho novo, o que por um tempo fez parecer que o
problema era cache. Por isso o mesmo desenho é gravado sob os três nomes.

**Acrescentar arquivo a um tema do sistema não adianta.** Com o desenho em
`~/.local/share/icons/breeze-dark/status/{22,24}`, sob todos os nomes, com
`index.theme` copiado e cache limpo, o painel continuou lendo o do `/usr`.
Testado também numa pasta que vem *antes* do `/usr` no `XDG_DATA_DIRS`: mesmo
resultado. Num tema que existe nos dois lugares, o do sistema ganha.

**Tema próprio funciona.** Trocando o tema de ícones para um que só existe no
lar do usuário — o `kora`, instalado aqui, usado como cobaia —, a bandeja
mudou na hora. Então é isso que o `--ativar` faz: monta em
`~/.local/share/icons/breeze-mono` um tema pequeno, com as marcas do Telegram
e nada mais, **herdando** o tema em uso. O resto da fileira continua vindo do
tema herdado, e `--desativar` devolve a escolha anterior.

Um efeito colateral honesto: o Plasma reescreve o tema de ícones sozinho
quando o esquema de cores vai de claro para escuro. Quando isso acontece, a
escolha se perde e a bandeja volta ao ícone do sistema; o `--estado` avisa,
e `--ativar` de novo resolve.

### Se não aparecer ícone nenhum

Antes de suspeitar do desenho, olhe se o item não está desligado:

```bash
grep disabledStatusNotifiers ~/.config/plasma-org.kde.plasma.desktop-appletsrc
```

`TelegramDesktop` nessa lista significa *Configurar bandeja → Entradas →
Desativado*. O item continua vivo e ativo no barramento — some só o desenho,
e não há fatia para ícone nenhum ocupar. Foi assim que esta busca começou:
horas atrás do ícone errado, quando o que faltava era a entrada.

### Não é contador, e não dá para ser

O Telegram não expõe a contagem para fora. Pela bandeja ele só troca o **nome**
do ícone entre três estados — normal, `-attention`, `-mute` — e o balão de
dica vem sem número (`"Telegram Desktop"`, e mais nada). Procurei também o
sinal de contagem do Unity, que outros clientes emitem, e ele não está no
binário. Então o que este pacote pode dizer é "tem mensagem", não "tem 3".
Prometer contador aqui seria prometer o que não há de onde tirar.

### Decisões de desenho

**Anel e tinta medidos contra a marca do WhatsApp**, não escolhidos: 19,1 de
tinta e 1,6 de anel num quadro de 22, lidos do `whatsapp-symbolic.svg` deste
projeto renderizado a 22 px. As duas marcas dividem a mesma fileira; medir uma
contra a outra é mais barato que descobrir o desencontro depois, no painel.

**A proporção do avião foi traçada do ícone real** — o PNG de 256 px que o
próprio Telegram entrega no flatpak —, comparando a caixa do avião branco com
a do disco: 0,5254 do diâmetro de largura, centro deslocado em −0,0381 e
+0,0254. O traçado é o simbólico de 16 px do Telegram, silhueta cheia, feito
para tamanho pequeno.

Vale registrar o que a medição desmentiu: a olho, o avião parecia leve demais
dentro do anel, e o impulso era aumentá-lo. Contada a tinta, ele já tinha
**mais** massa que o fone do WhatsApp (37,1 contra 29,4 unidades²). O que
enfraquece é a ponta fina se desmanchando no antisserrilhado, não o tamanho.
Aumentar teria estragado a proporção traçada para consertar um problema que
não era esse.

**Cheio alerta, oco silencia.** O Breeze separa os dois estados pela cor, azul
contra cinza, e cor está fora de questão. Sobra a forma. A 16 px o furo fecha
e os dois viram o mesmo ponto; a 22 px, que é onde o ícone vive, a diferença
lê.

**Com ponto, a marca encolhe para 0,85 e se encosta na margem superior
esquerda**, cedendo o canto — mesma solução do contador do WhatsApp, e pela
mesma razão: marca contornada não tem área sólida para o vão furar, então o
vão não pode cair sobre o traço. Havia uma máscara de vão aqui; medida a
folga, ela deu zero — a marca, ao ceder o canto, já não encostava no ponto.
Máscara que não corta nada saiu do arquivo.

**Os três estados vão em `status/22` e `status/24`.** Pedindo 22, o Plasma
serviu o de 24 (`kiconfinder6 org.telegram.desktop-symbolic 22`). Cobrir só um
dos dois deixa parte dos tamanhos de painel com o ícone antigo.

Uma ferramenta que engana: o `kiconfinder6` respondia com o **nosso** arquivo
enquanto o painel desenhava o do sistema. Ele resolve por um caminho que a
bandeja não usa. Quem deu a resposta certa foi olhar a tela e grampear as
pastas — não perguntar a quem parecia saber.

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

## Sobre as marcas

O símbolo do WhatsApp é marca registrada da Meta; o do Telegram, do Telegram
Messenger. Aqui eles são usados para identificar os serviços a que os clientes
se conectam, que é o mesmo motivo pelo qual o próprio ZapZap se chama assim.
Este projeto não tem vínculo com a Meta, com o Telegram nem com o ZapZap.

## Arquivos

- `whatsapp-symbolic.svg` — a marca, sem contador
- `whatsapp-symbolic-count.svg` — modelo com `{color}` `{number}` `{size}` `{stroke}`
- `gerar.py` — escolhe corpo e vão pela quantidade de dígitos
- `telegram-symbolic.svg` — a marca do Telegram
- `telegram-attention-symbolic.svg` — com não lidas, ponto cheio
- `telegram-mute-symbolic.svg` — com não lidas silenciadas, ponto oco
