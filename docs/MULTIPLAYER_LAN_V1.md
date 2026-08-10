# Multiplayer LAN v1

## Cel

Pierwszy multiplayer Rise & Glory działa w jednej sieci lokalnej LAN/Wi-Fi i nie wymaga hostingu internetowego. Jeden komputer tworzy serwer gry, a pozostali gracze łączą się z nim po prywatnym adresie IPv4, np. `192.168.1.25`.

LAN jest pierwszym środowiskiem sieciowym, ale architektura pozostaje klient-serwer. Docelowo ten sam model zostanie wykorzystany przez Internet po przeniesieniu serwera na maszynę dostępną publicznie.

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

Serwer jest źródłem prawdy. Klient wysyła zamiar wykonania akcji, a serwer sprawdza jej legalność i rozsyła zatwierdzony stan wszystkim graczom.

## Aktualnie zaimplementowane

### Warstwa sieciowa

- `rg_network/protocol.py` — protokół JSON/TCP, wersjonowanie i port `27840`.
- `rg_network/lan_server.py` — serwer LAN dla maksymalnie 6 graczy.
- `rg_network/lan_client.py` — klient LAN odbierający komunikaty w osobnym wątku.
- `rg_network/game_state.py` — autorytatywny stan pierwszej rozgrywki LAN.
- `tests/test_network_lan.py` — test lobby, startu, wspólnego snapshotu, ruchu i zmiany tury.

### Integracja z grą

Przycisk `Multiplayer` w menu prowadzi do działającego trybu LAN. Gracz może:

- utworzyć lobby LAN,
- zobaczyć adres IPv4 hosta i port,
- dołączyć do lobby przez IPv4 hosta,
- grać w lobby do 6 osób,
- wybrać jeden z 6 archetypów bohatera na własnym komputerze,
- ustawić lub cofnąć status `Gotowy`,
- rozpocząć grę jako host po gotowości wszystkich,
- otrzymać tę samą mapę i ten sam stan początkowy na wszystkich komputerach,
- zobaczyć wszystkich bohaterów na wspólnej mapie,
- wykonywać ruch tylko podczas swojej tury,
- widzieć ruch zatwierdzony przez serwer na wszystkich komputerach,
- zakończyć własną turę,
- zobaczyć zmianę aktywnego gracza i reset jego akcji na wszystkich klientach.

## Autorytatywny serwer

W LAN v1 serwer tworzy wspólną mapę, bohaterów, miejsca startowe i inicjatywę. Klient nie generuje sobie niezależnej „prawdziwej” wersji partii.

Przykład ruchu:

```text
Klient Kamila -> move_request: heks 37
Serwer -> sprawdza, czy to tura Kamila
Serwer -> sprawdza sąsiedztwo, przechodniość i koszt akcji
Serwer -> zmienia pozycję w swoim GameState
Serwer -> rozsyła nowy GameState wszystkim klientom
```

To samo podejście ma docelowo objąć rzuty k20, złoto, sklepy, Questy, walkę, Wydarzenia Świata i handel.

## Port

Domyślny port:

```text
TCP 27840
```

Na etapie LAN portu nie przekierowujemy na routerze do Internetu.

## Jak uruchomić z poziomu gry

Na każdym komputerze uruchamiamy normalnie:

```text
python main.py
```

Następnie:

### Host

1. `Multiplayer`.
2. `Uruchom Multiplayer LAN`.
3. `Utwórz grę LAN`.
4. Wpisz imię bohatera.
5. Kliknij `Utwórz lobby`.
6. Gra pokaże adres, np. `192.168.1.25:27840`.
7. Przekaż ten adres pozostałym graczom.

### Pozostali gracze

1. `Multiplayer`.
2. `Uruchom Multiplayer LAN`.
3. `Dołącz do gry LAN`.
4. Wpisz imię oraz IPv4 hosta, np. `192.168.1.25`.
5. Kliknij `Połącz`.

### Lobby

Każdy wybiera bohatera i klika `Gotowy`. Host otrzymuje możliwość `Rozpocznij grę`. Po starcie wszyscy otrzymują ten sam snapshot świata.

Jeżeli Windows Firewall zapyta o dostęp dla Pythona, należy zezwolić na połączenia w używanej sieci prywatnej.

## Tryb konsolowy do diagnostyki

Serwer można nadal uruchomić osobno:

```text
python -m rg_network.lan_server
```

Klient diagnostyczny:

```text
python -m rg_network.lan_client 192.168.1.25 --name Wiktor
```

Komendy klienta diagnostycznego:

```text
hero 1
hero 2
...
hero 6
ready
unready
start
move ID_HEKSA
end
say TEKST
ping
quit
```

## Co jeszcze NIE jest zsynchronizowane

LAN v1 jest grywalnym vertical slice'em mapy i tur, ale nie oznacza jeszcze pełnej sieciowej wersji całej gry. Obecnie nie podpinamy przez serwer:

- wejścia do miast, wsi i zamków,
- zakupów i sprzedaży,
- pobierania i wykonywania Questów,
- walki,
- Przygód,
- Wydarzeń Świata,
- Rady Bohaterów i handlu,
- Kroniki Świata,
- reconnectu po zerwanym połączeniu,
- zapisu/wznowienia partii sieciowej.

Po piątej pełnej rundzie licznik Rady jest widoczny, ale sieciowa Rada nie została jeszcze zaimplementowana.

## Następne etapy

1. Synchronizacja wejścia do lokacji i ich wspólnego stanu.
2. Serwerowe zakupy, sprzedaż, leczenie, trening i pobieranie Questów.
3. Synchronizacja testów k20 i Questów.
4. Synchronizacja walki.
5. Wydarzenia Świata i Zagrożenia jako element wspólnego GameState.
6. Pełna sieciowa Rada Bohaterów: oferty publiczne, negocjacje, Czat i Logi handlu.
7. Kronika Świata pobierająca zdarzenia z autorytatywnego serwera.
8. Reconnect oraz zapisy partii.

## Zasada rozwoju

Od tego etapu każda nowa mechanika, która zmienia stan partii, powinna być projektowana tak, aby serwer mógł ją zatwierdzić. Dzięki temu nie będziemy później przepisywać całej gry z lokalnego modelu na multiplayer.
