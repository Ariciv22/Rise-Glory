# Multiplayer LAN v1

## Cel

Pierwszy etap multiplayera Rise & Glory ma dzialac bez publicznego hostingu i bez Internetu. Gracze znajduja sie w tej samej sieci lokalnej LAN/Wi-Fi. Jeden komputer uruchamia serwer Rise & Glory, a pozostale komputery lacza sie do jego prywatnego adresu IPv4.

Docelowo ten sam model klient-serwer ma zostac wykorzystany przez Internet. LAN jest pierwszym srodowiskiem testowym, a nie osobnym zestawem zasad gry.

## Architektura

```text
Komputer hosta
  Rise & Glory Server :27840
          |
          +-- klient Wiktora
          +-- klient Kamila
          +-- klient Gracza 3
          +-- klient Gracza 4
          +-- klient Gracza 5
          +-- klient Gracza 6
```

Serwer jest zrodlem prawdy. Klienci nie powinni docelowo samodzielnie ustalac wynikow rzutow, zmieniac zlota ani modyfikowac stanu swiata bez zatwierdzenia serwera.

## Aktualnie zaimplementowany fundament

Pakiet `rg_network` nie zalezy od Pygame i korzysta w pierwszej wersji tylko z biblioteki standardowej Pythona.

- `rg_network/protocol.py` — komunikaty JSON rozdzielane znakiem nowej linii, wersjonowanie protokolu i domyslny port.
- `rg_network/lan_server.py` — serwer TCP lobby dla maksymalnie 6 graczy.
- `rg_network/lan_client.py` — klient TCP z odbieraniem wiadomosci w osobnym watku.
- `tests/test_network_lan.py` — test polaczenia dwoch klientow, gotowosci i rozpoczecia sesji.

Serwer obsluguje obecnie:

- dolaczenie maksymalnie 6 graczy,
- przydzielenie hosta pierwszemu graczowi,
- liste graczy w lobby,
- status Gotowy / Oczekiwanie,
- prosty czat testowy,
- przekazanie roli hosta kolejnej osobie po rozlaczeniu hosta,
- rozpoczecie sesji przez hosta, gdy jest co najmniej 2 graczy i wszyscy sa gotowi,
- ping/pong do testowania polaczenia.

## Port

Domyslny port serwera LAN:

```text
TCP 27840
```

Port nie powinien byc na tym etapie przekierowywany na routerze do Internetu. Ta wersja jest przeznaczona do zaufanej sieci lokalnej.

## Pierwszy test na dwoch komputerach

Oba komputery musza znajdowac sie w tej samej sieci lokalnej i posiadac aktualna wersje repozytorium Rise & Glory.

### 1. Komputer hosta

W katalogu glownego projektu uruchom:

```text
python -m rg_network.lan_server
```

Serwer wyswietli np.:

```text
Rise & Glory - LAN server
Adres dla graczy: 192.168.1.25:27840
Maksymalnie graczy: 6
```

Adres `192.168.1.25` jest przykladem. Pozostali gracze uzywaja adresu wyswietlonego na komputerze hosta.

Jesli Windows Firewall zapyta o dostep dla Pythona, nalezy zezwolic na polaczenia w sieci prywatnej, w ktorej wykonywany jest test.

### 2. Pierwszy klient

Na komputerze hosta albo innym komputerze w tej samej sieci:

```text
python -m rg_network.lan_client 192.168.1.25 --name Wiktor
```

### 3. Drugi klient

Na drugim komputerze:

```text
python -m rg_network.lan_client 192.168.1.25 --name Kamil
```

Tak samo mozna dolaczyc kolejnych graczy az do 6 osob.

### 4. Komendy testowego klienta

```text
ready
unready
start
say TEKST
ping
quit
```

`ready` ustawia gotowosc. `start` moze wykonac tylko host i dopiero po gotowosci wszystkich graczy.

## Co oznacza obecny etap

Ten commit tworzy dzialajaca warstwe polaczenia LAN i lobby. Nie oznacza jeszcze, ze cala obecna rozgrywka Pygame jest zsynchronizowana miedzy komputerami.

Kolejny etap musi podpiac `LanClient` do ekranu `Multiplayer` w grze i zsynchronizowac przygotowanie partii oraz stan mapy.

## Kolejnosc dalszej implementacji

1. Podpiecie LAN lobby bezposrednio do ekranu `Multiplayer` zamiast obecnego placeholdera.
2. Wybieranie imienia i bohatera przez kazdego gracza na jego komputerze.
3. Host zatwierdza start po gotowosci 2–6 graczy.
4. Serwer tworzy jeden stan mapy i wysyla go wszystkim klientom.
5. Serwer ustala inicjatywe i aktywnego gracza.
6. Pierwsza synchronizowana akcja: ruch pionka po heksach.
7. Synchronizacja `Koniec tury` i resetu 4 akcji.
8. Synchronizacja lokacji, sklepow, Questow, walki i Rady Bohaterow.
9. Reconnect i zapisy partii po ustabilizowaniu podstawowej rozgrywki.

## Zasada techniczna

Multiplayer nie moze polegac na zaufaniu do klienta. Docelowo klient wysyla zamiar, np. `move_request`, a serwer sprawdza legalnosc ruchu i dopiero rozglasza zatwierdzony wynik wszystkim graczom.

Przyklad:

```text
Klient Kamila -> chce wejsc na heks 37
Serwer -> sprawdza ture, sasiedztwo, koszt ruchu i pozostale akcje
Serwer -> zatwierdza ruch
Serwer -> wysyla wszystkim: Kamil jest na heksie 37, pozostaly 3 akcje
```

Ta sama zasada bedzie dotyczyc rzutow k20, zakupow, Questow, walki, Wydarzen Swiata i handlu.
