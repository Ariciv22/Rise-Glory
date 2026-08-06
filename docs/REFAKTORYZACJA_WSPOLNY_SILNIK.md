# Rise & Glory — wspólny silnik

## Bezpieczne gałęzie

- `backup/przed-refaktoryzacja-2026-08-06` — nieruszana kopia projektu sprzed refaktoryzacji.
- `glowny_main` — dotychczasowa główna wersja gry.
- `refactor/wspolny-silnik-v1` — gałąź migracji do wspólnego silnika.

## Podział projektu

### `rg_engine/`

Kod zasad niezależny od Pygame i wyglądu ekranów:

- `models.py` — wspólne modele przedmiotu, przeciwnika, questa i stanu gry,
- `items.py` — rejestr przedmiotów, plecak, wyposażanie, zdejmowanie, premie i sprzedaż,
- `heroes.py` — Rany, leczenie, pokonanie oraz trening,
- `combat.py` — wspólne rozpatrywanie rund walki i ucieczki,
- `quests.py` — etapy, testy, koszty, porażki, nagrody i stan questa,
- `locations.py` — zakupy, pomocnicy, trening, leczenie i ekwipunek w lokacji,
- `world.py` — poziom świata i skalowanie,
- `council.py` — model transakcji podczas Rady,
- `savegame.py` — wersjonowany format zapisu JSON.

Moduły w tym katalogu nie powinny rysować interfejsu ani wczytywać grafik.

### `rg_content/`

Dane konkretnej zawartości gry:

- `enemies.py` — definicje przeciwników,
- `quests.py` — definicje questów.

Nowy quest lub przeciwnik powinien być przede wszystkim nowym wpisem danych, a nie osobnym silnikiem.

### Warstwa interfejsu

- `rg_quest_ui.py` — jedna pozioma karta używana przez wszystkie questy,
- `rg_quest_runtime.py` — łączy quest z ogólnym ekranem walki,
- `rg_combat.py` — zachowany ekran walki, korzystający ze wspólnej logiki,
- `rg_city_screen.py` — zachowany wygląd lokacji oraz wspólne zakładki usług i questów.

### Warstwa zgodności

- `rg_satanic_forces.py`,
- `rg_satanic_combat.py`.

Pliki zachowują dawne nazwy funkcji dla testów i istniejących importów. Nie zawierają już osobnego silnika questa. Po migracji wszystkich odwołań będzie można je bezpiecznie usunąć.

## Dodawanie przeciwnika

Przeciwnika rejestruje się w `rg_content/enemies.py` za pomocą `EnemyDefinition`.

Najważniejsze pola:

```python
EnemyDefinition(
    enemy_id="wilk",
    name="Wilk",
    base_hp=3,
    armor_class=10,
    attack_bonus=1,
    wounds=1,
    image="wilk",
    can_escape=True,
    scale_with_world=True,
)
```

Ekran, rzuty, obrażenia i skalowanie obsługuje wspólny moduł walki.

## Dodawanie questa

Quest rejestruje się w `rg_content/quests.py` jako `QuestDefinition`. Każdy etap zawiera listę `QuestOption`.

Obsługiwane rodzaje opcji:

- test statystyki,
- wymagane materiały,
- koszt złota,
- wymagany przedmiot,
- dobrowolna walka,
- walka uruchamiana po porażce,
- przejście do kolejnego etapu,
- ukończenie questa.

Przykład testu:

```python
QuestOption(
    option_id="quest_1_nauka",
    label="Odczytaj runy",
    stat="Nauka",
    threshold=12,
)
```

Przykład walki:

```python
QuestOption(
    option_id="quest_3_walka",
    label="Pokonaj strażnika",
    option_type="combat",
    enemy_id="przeklety_zolnierz",
)
```

Nie należy tworzyć kolejnego pliku typu `rg_nazwa_questa.py`, chyba że quest wymaga całkowicie wyjątkowego interfejsu, którego nie da się opisać danymi.

## Dodawanie przedmiotu

Przedmioty rejestruje się przez `ItemDefinition` w `rg_engine/items.py` lub w przyszłym katalogu danych przedmiotów.

Wspólny format jest używany jednocześnie w:

- sklepie,
- plecaku,
- wyposażeniu,
- nagrodzie questa,
- walce,
- zapisie gry.

Startowe przedmioty zapisane dawniej jako tekst są automatycznie migrowane do wspólnego formatu przy tworzeniu bohatera.

## Aktualne zasady testów questów

- wykonanie albo ponowienie etapu kosztuje 1 akcję,
- każda porażka dodaje 1 znacznik,
- zwykła porażka daje `+1` do następnego testu,
- naturalne 1 daje zamiast tego `+2`,
- kara nie kumuluje się,
- czwarty znacznik przegrywa quest,
- naturalne 20 zalicza bieżący test i dokładnie jeden kolejny zwykły test dostępny natychmiast,
- znaczniki porażki zmniejszają tylko nagrodę w złocie.

## Stan migracji

Podłączone do wspólnego silnika:

- stan bohatera,
- startowy ekwipunek,
- plecak i wyposażenie,
- zakupy i sprzedaż przedmiotów,
- trening,
- leczenie,
- Rany i pokonanie,
- walka,
- poziom świata,
- quest „Szatańskie siły”,
- pozioma karta questa,
- podstawowy model Rady i handlu,
- wersjonowany format zapisu.

Nadal wymagają osobnego wdrożenia zawartości lub pełnego ekranu:

- talia Wydarzeń Świata,
- interfejs handlu podczas Rady,
- automatyczne odświeżanie sklepów po zmianie poziomu świata,
- pełne wczytywanie zapisu do obiektów Pygame,
- Questy Legendarne i zakończenie gry,
- kolejne questy, przygody, przeciwnicy i przedmioty.

## Testy

Czysta logika wspólnego silnika posiada testy w plikach `tests/test_engine_*.py`. Każda nowa reguła powinna otrzymać test niezależny od Pygame, zanim zostanie podłączona do ekranu.
