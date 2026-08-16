# Remontar a bandeja numa máquina nova

Ordem de instalação do que compõe esta fileira. Cada peça vive num
repositório próprio; esta lista existe porque a **ordem** e os **ajustes de
painel** não estão em nenhum deles.

## 1. Os ícones do WhatsApp e do Telegram (este repositório)

```bash
./build.sh
cp dist/zapzap-whatsapp-icon-*.tar.gz ~/rpmbuild/SOURCES/
rpmbuild -ba zapzap-whatsapp-icon.spec
sudo dnf install ~/rpmbuild/RPMS/noarch/zapzap-whatsapp-icon-*.noarch.rpm

zapzap-whatsapp-icon --ativar     # marca do WhatsApp no ZapZap em flatpak
telegram-tray-icon --ativar       # marca do Telegram na bandeja
```

O `telegram-tray-icon --ativar` **troca o tema de ícones** para `breeze-mono`,
que herda o tema em uso e só substitui as marcas do Telegram. Se o Plasma
reescrever o tema sozinho (ele faz isso ao alternar claro/escuro), rode de
novo — o `--estado` avisa quando isso aconteceu.

## 2. O widget de wifi

```bash
git clone https://github.com/henriquecarmine/plasma-wifi-generation
cd plasma-wifi-generation && ./build.sh
kpackagetool6 --type Plasma/Applet --install package
```

## 3. O widget de clima

```bash
sudo dnf install kweather        # o aplicativo que o clique abre
git clone https://github.com/henriquecarmine/plasma-clima
cd plasma-clima
kpackagetool6 --type Plasma/Applet --install package
```

Configuração do lugar: botão direito no ícone → *Configurar*. O padrão vem em
Monte Mor, SP (−22,94667 / −47,31583, altitude 561 m). Elias Fausto é
−23,04278 / −47,37389, altitude 579 m.

## 4. Ajustes de painel, que nenhum pacote faz

Estes são cliques, e é por isso que estão escritos:

- **Bandeja → Configurar → Entradas:** o Telegram precisa estar como
  *Mostrado* ou *Automático*. Uma vez ele estava como **Desativado** e o
  ícone simplesmente não existia na fileira — horas foram gastas procurando
  defeito no desenho antes de olhar essa lista. No arquivo, isso aparece como
  `disabledStatusNotifiers=TelegramDesktop` em
  `~/.config/plasma-org.kde.plasma.desktop-appletsrc`.
- **Relógio → Configurar → Aparência:** fonte **Noto Sans**, que é a oficial
  do Plasma 6 e a que os números dos widgets usam. Vinha em Red Hat Display,
  destoando do "6" do wifi e da temperatura do clima.
- **Widgets na bandeja:** wifi e clima moram *dentro* da bandeja, não soltos
  no painel — é onde o desenho de um slot quadrado faz sentido.
- **Applet de redes do KDE, desativado.** Ele duplica o widget de wifi e
  enche a tela de avisos quando uma conexão falha em laço. Desativar tem uma
  sutileza: **não basta tirá-lo de `extraItems`**. O Plasma reativa sozinho
  qualquer applet de bandeja que ele considere novidade, e "novidade" é o que
  não está em `knownItems` — limpar as duas listas fazia o applet voltar a
  cada reinício, com outro identificador. O que gruda é: fora de
  `extraItems`, **dentro** de `knownItems`, e sem grupo de instância. Tudo em
  `~/.config/plasma-org.kde.plasma.desktop-appletsrc`, com o plasmashell
  parado.
- **Avisos de conexão do Fedora:** o lugar certo de desligar é nas
  **configurações de rede** do sistema, não no adaptador — dica do dono da
  máquina, depois de a gente perder tempo silenciando o mensageiro em vez da
  origem.
- **Avisos do NetworkManager silenciados** (pop-up desligado, histórico
  mantido):

  ```bash
  kwriteconfig6 --file plasmanotifyrc --group Applications --group plasma_nm \
      --key ShowPopups false
  ```

  Vale lembrar que o barulho costuma ser sintoma: um cabo que não recebe DHCP
  faz o NetworkManager tentar de 45 em 45 segundos, e cada volta gera aviso.
  Curar a causa é `nmcli connection modify "<perfil>" connection.autoconnect no`.

## Ordem que importa

O `--ativar` do Telegram mexe no tema de ícones; rode-o **antes** de conferir
a aparência dos widgets, senão você julga a fileira com o tema errado.

Depois de instalar ou atualizar qualquer widget, reinicie o painel:

```bash
systemctl --user restart plasma-plasmashell.service
```

E atualize widget sempre com o painel **parado** — com ele no ar, o Plasma
perde a instância do applet e grava a configuração sem ela ao sair.
