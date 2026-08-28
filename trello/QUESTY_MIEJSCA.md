# Rise & Glory — Miejsca tworzone przez Questy

## Status

**ZASADA PROJEKTOWA — ZATWIERDZONA**

## Idea

Quest może nie tylko zmienić flagę świata, relację z NPC albo dać nagrodę. Wybrane zakończenia Questów mogą również **utworzyć nowe trwałe Miejsce na mapie świata**.

Takie Miejsce powstaje dopiero wtedy, gdy gracz osiągnie odpowiedni finał Questa. Po utworzeniu staje się normalnym elementem świata i może później otrzymać własne akcje, mechaniki, wydarzenia i powiązania z kolejnymi Questami.

## Zasada działania

1. Quest posiada finał, który może utworzyć Miejsce.
2. Finał zapisuje standardowy trwały wynik Questa, np.:
   - `q05_result = "ogrod_odrodzony"`
3. Ten wynik jest wystarczającą informacją, że dane Miejsce istnieje. Nie tworzymy dodatkowej flagi typu `stary_ogrod_aktywny = true`, jeśli wynika to już jednoznacznie z `q05_result`.
4. Po zakończeniu Questa system tworzy lub aktywuje odpowiedni Znacznik Miejsca na mapie.
5. Miejsce pozostaje na mapie po zakończeniu Questa.
6. Miejsce nie jest już Znacznikiem Questa i nie jest usuwane podczas sprzątania Questa.
7. Konkretne działania dostępne w takim Miejscu będą definiowane osobno w dokumentacji Miejsc i w kodzie gry.

## Co może później oferować Miejsce

W zależności od miejsca mogą to być między innymi:

- pozyskiwanie materiałów,
- leczenie,
- handel,
- unikalny sklep,
- badania,
- crafting,
- wynajmowanie Pomocników,
- nowe Questy,
- Przygody,
- specjalne wydarzenia,
- premie dla bohatera lub regionu,
- wpływ na wojny i obronę regionu,
- produkcja Towarów,
- dostęp do unikalnych receptur albo technologii.

Nie każdy punkt musi posiadać wszystkie te możliwości.

## Rozdzielenie odpowiedzialności

### Quest

Quest określa:

- **czy** miejsce powstaje,
- **gdzie** powstaje,
- **jaki finał** je tworzy,
- nazwę miejsca,
- podstawowy opis fabularny.

### System Miejsc

Osobna dokumentacja i kod określają później:

- jakie akcje można tam wykonywać,
- koszty akcji,
- dostępne zasoby,
- cooldowny i limity,
- handel i ceny,
- możliwe wydarzenia,
- powiązania z innymi systemami gry.

Dzięki temu nie musimy podczas projektowania każdego Questa od razu projektować całej ekonomii nowego Miejsca.

---

# Pierwsze zatwierdzone zastosowanie

## Quest 5 — Ogród umarłego

### Finał B — Ogród powraca

Po osiągnięciu finału:

`q05_result = "ogrod_odrodzony"`

na mapie powstaje trwałe Miejsce:

**Stary Ogród**

Stary Ogród pozostaje aktywny do końca rozgrywki.

Na etapie projektowania Questa nie ustalamy jeszcze pełnej listy akcji dostępnych w Ogrodzie. Zostaną one zaprojektowane później w module Miejsc.

Potencjalne kierunki dla Starego Ogrodu:

- pozyskiwanie rzadkich ziół,
- leczenie,
- materiały alchemiczne,
- nowe Questy,
- unikalny zielarz lub badacz,
- receptury związane z roślinami i alchemią.

## Ważna zasada implementacyjna

Należy rozróżnić:

- **Znacznik Questa** — tymczasowy, usuwany po zakończeniu Questa,
- **Znacznik Miejsca** — trwały, może zostać utworzony przez finał Questa i pozostaje na mapie.

W przyszłości inne Questy również mogą tworzyć Miejsca zgodnie z tym samym mechanizmem.
