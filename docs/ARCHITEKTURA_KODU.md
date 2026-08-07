# Architektura kodu Rise & Glory

Ten dokument opisuje odpowiedzialnosc pakietow po uporzadkowaniu projektu. Nowy kod powinien trafiać do warstwy zgodnej z jego rola zamiast ponownie rozrastac katalog glowny.

## Katalog glowny

- `main.py` — jedyny punkt startowy gry. Uruchamia `rg_core.app` i nie zawiera zasad gry ani ekranow.

## `rg_core` — skladanie aplikacji

- `app.py` — glowna petla Pygame, zmiana stanow/ekranow i laczenie podsystemow.
- `data.py` — stale globalne, konfiguracja ekranu, tereny, archetypy bohaterow oraz tworzenie poczatkowego stanu bohatera.
- `setup.py` — przygotowanie graczy i pionkow oraz instalacja integracji runtime.
- `quest_runtime.py` — lacznik pomiedzy questami i walka.
- `bootstrap.py` — tymczasowa mapa dawnych nazw modulow na nowe pakiety. Nie dodawac tutaj zasad gry.

`rg_core` moze laczyc warstwy, ale nie powinien przechowywac rozbudowanych zasad konkretnego systemu.

## `rg_engine` — czyste zasady gry

Moduly w tym katalogu powinny w miare mozliwosci dzialac bez Pygame.

- `models.py` — definicje danych: `ItemDefinition`, `EnemyDefinition`, `QuestOption`, `QuestStage`, `QuestDefinition`, `RuntimeGameState`.
- `heroes.py` — stan bohatera, Rany, leczenie, trening i bonusy pomocnikow.
- `items.py` — ekwipunek, plecak, sloty, KP, bron i normalizacja przedmiotow.
- `combat.py` — `CombatSession` oraz rozstrzyganie rund walki i ucieczki.
- `quests.py` — rejestr questow, etapy, testy, nagrody, porazki i zakonczenie questa.
- `locations.py` — operacje wykonywane w lokacjach: zakup, zatrudnienie, trening, leczenie, ekwipunek.
- `council.py` — handel Rady Bohaterow: `AssetRef`, `TradeSide`, `TradeOffer`, `CouncilUsage` oraz walidacja transakcji.
- `world.py` — poziom swiata i globalny stan graczy.
- `world_events.py` — aktywne Wydarzenie Swiata i modyfikatory wynikajace z wydarzen.
- `turns.py` — inicjatywa i `TurnManager`.
- `savegame.py` — serializacja stanu gry.
- `devtools.py` — flagi i operacje testowe menu programisty.

### Najwazniejsze klasy silnika

`CombatSession` reprezentuje jedna trwajaca walke: gracza, przeciwnika, numer rundy, log i metadane.

`TradeOffer` reprezentuje kompletna dwustronna oferte handlu podczas Rady. Zawiera `TradeSide` dla obu graczy oraz stan obu akceptacji.

`CouncilUsage` pilnuje wykorzystanych limitow handlu danego gracza podczas jednej Rady.

`TurnManager` przechowuje kolejnosc graczy, aktywna pozycje, numer rundy i cykl Rady.

`RuntimeGameState` jest docelowym modelem stanu calej partii do dalszej integracji Save/Load.

## `rg_content` — zawartosc gry

Tutaj trafiaja konkretne karty, przeciwnicy i dane swiata. Content korzysta z reguł silnika, ale nie powinien rysowac UI.

- `enemies.py` — konkretni przeciwnicy i ich parametry.
- `quests.py` — konkretne definicje questow.
- `world_events.py` — konkretne karty Wydarzen Swiata.
- `locations.py` — pule sklepow, pomocnikow, towarow, questow i inicjalizacja ofert lokacji.

Docelowo kolejne duze pule contentu mozna wydzielac np. do `items.py`, `helpers.py` lub osobnych plikow talii.

## `rg_world` — plansza i eksploracja

- `map.py` — `Camera`, `Tile`, `HeroToken`, geometria heksow, tekstury i podstawowe renderowanie planszy.
- `generation.py` — generowanie mapy i rozmieszczanie lokacji.
- `adventure.py` — znaczniki przygod i wydarzenie przygodowe na planszy.

Docelowo logike renderowania mapy mozna jeszcze oddzielic od modeli `Tile`/`HeroToken`, ale obecny podzial usuwa te elementy z katalogu glownego i izoluje system planszy.

## `rg_ui` — Pygame i prezentacja

Ta warstwa rysuje i obsluguje klikniecia. Nie powinna samodzielnie zmieniac zasad gry, jesli istnieje odpowiednia operacja w `rg_engine`.

- `common.py` — wspolne `Button`, panele, zawijanie tekstu i obszary UI.
- `screens.py` — menu, wybor graczy, inicjatywa i pozostale ekrany ogolne.
- `hud.py` — HUD glownej mapy.
- `city.py` — ekran miasta/wsi/zamku.
- `combat.py` — prezentacja i kontrolki walki; reguly deleguje do `rg_engine.combat`.
- `council.py` — ekran Rady Bohaterow; reguly handlu deleguje do `rg_engine.council`.
- `quest.py` — wyswietlanie aktywnego questa i przyciskow opcji.
- `player_board.py` — planszetka bohatera.
- `dev_menu.py` — F8 Menu programisty.
- `tooltip.py` — tooltip lokacji na mapie.
- `intro.py` — intro rozgrywki.
- `start_intro.py`, `start_intro_base.py`, `title_flow.py` — ekran tytulowy, poczatkowe intro, muzyka i flow menu.
- `dice_animation.py`, `premium_dice.py` — animacja k20.
- `combat_image_fit.py` — dopasowanie grafiki przeciwnika do ekranu walki.

## `rg_legacy` — zgodnosc przejsciowa

- `satanic_forces.py`
- `satanic_combat.py`

Te pliki istnieja tylko po to, aby zachowac zgodnosc pierwszego questa z dawnym API. Nie dodawac do nich nowej mechaniki. Gdy wszystkie testy i wywolania przejda bezposrednio na wspolny silnik, caly `rg_legacy` powinien zostac usuniety.

## Zasada zaleznosci

Preferowany kierunek:

```text
main.py
  -> rg_core
      -> rg_ui
      -> rg_world
      -> rg_content
      -> rg_engine

rg_ui      -> rg_engine / rg_content / rg_world
rg_world   -> rg_engine / rg_content
rg_content -> rg_engine
rg_engine  -> nie powinien zalezec od rg_ui
```

Jesli nowa funkcja zmienia zasady gry, najpierw powinna powstac w `rg_engine`, a UI powinno ja tylko wywolac. Jesli jest to nowa karta, przeciwnik lub quest — trafia do `rg_content`. Jesli dotyczy wygladu/klikniec — trafia do `rg_ui`.
