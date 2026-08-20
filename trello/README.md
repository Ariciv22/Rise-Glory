# Rise & Glory — Kanban ALFA 0.1

Ten katalog jest roboczą roadmapą rozwoju gry. Każdy główny moduł ma osobny dokument z checklistą działań i Definition of Done.

**Stan zweryfikowany: 2026-08-20 na podstawie aktualnego kodu, integracji i plików testowych w repozytorium.**

## Kolumny Kanban

1. **BACKLOG** — moduł nie ma jeszcze właściwej implementacji.
2. **DO ZROBIENIA** — istnieje fundament/prototyp, ale moduł wymaga jeszcze istotnej implementacji.
3. **W TRAKCIE** — aktualnie rozwijany główny moduł.
4. **DO TESTÓW** — zasadnicza implementacja istnieje; przed uznaniem modułu za zamknięty potrzebny jest pełny test/regresja w grze.
5. **GOTOWE** — implementacja przeszła pełne testy i nie ma znanych blokujących braków.
6. **WSTRZYMANE** — celowo poza aktualnym zakresem prac.

## Zasady pracy

- Jeden dokument = jeden główny moduł.
- Szczegóły modułu są checklistą wewnątrz dokumentu.
- Status w tym README ma odzwierciedlać **faktyczny stan kodu**, a nie wyłącznie historyczny status zapisany w nagłówku dokumentu modułu.
- Maksymalnie jeden duży moduł powinien być głównym aktywnym modułem w **W TRAKCIE**.
- Moduł z częściową implementacją, który nie jest aktualnym priorytetem, może pozostawać w **DO ZROBIENIA**.
- Po zasadniczym zakończeniu implementacji moduł trafia do **DO TESTÓW**.
- Dopiero po pełnym teście/regresji trafia do **GOTOWE**.
- Multiplayer LAN pozostaje w **WSTRZYMANE** do czasu ukończenia grywalnej ALFY 0.1.
- Nie ustawiamy sztucznych terminów.
- Nie dodajemy nowych głównych modułów bez osobnej decyzji projektowej.

## Aktualny stan modułów

### DO TESTÓW

1. [Żywy Świat — Zagrożenia i problemy na mapie](01_ZYWY_SWIAT_ZAGROZENIA.md)  
   Zaimplementowany silnik Zagrożeń, wiedza bohatera, znaczniki, metody rozwiązania, koszty, ponowne próby, integracja z Wydarzeniami Świata i testy silnika/UI. Dalsza praca to głównie regresja i dokładanie contentu.

2. [Questy i Testy — wspólny silnik](02_QUESTY_I_TESTY.md)  
   Zaimplementowany wspólny silnik Questów, talie, etapy, limity, porażki, rozwinięcia, Księga Questów, znaczniki, integracje z walką/lokacjami/Radą/Kroniką oraz testy. Dalsza praca to regresja i nowe Questy jako content.

8. [Rada Bohaterów](08_RADA_BOHATEROW.md)  
   Istnieje rozbudowany silnik Rady i handlu, publiczne oferty, luźne negocjacje, limity, obsługa pojemności, UI oraz osobne testy Rady/rynku. Moduł wymaga pełnego testu end-to-end całego flow Rady w normalnej partii.

### W TRAKCIE

3. [Walka V2](03_WALKA_V2.md)  
   Fundament zasad 1–70 jest zaimplementowany: HP, KP, obrażenia, Obrona, przedmioty bojowe, statusy, specjalne zdolności, bossowie, ucieczka/przekupstwo, porażka, ekran zwycięstwa i integracja z Questami/Zagrożeniami. Do dalszej pracy pozostaje głównie content oraz osobny system konsekwencji Ran.

### DO ZROBIENIA — FUNDAMENT/PROTOTYP JUŻ ISTNIEJE

4. [Przygody na mapie V2](04_PRZYGODY_NA_MAPIE_V2.md)  
   W repo istnieje starszy działający prototyp Przygody z żetonem, overlayem, rzutem i testami (`rg_world/adventure.py`), ale nie jest to jeszcze docelowy, danychowy system Przygód V2 z wieloma opcjami i kartami.

9. [Kronika Świata](09_KRONIKA_SWIATA.md)  
   Istnieje centralny fundament Kroniki (`rg_engine/world_chronicle.py`) i integracje z rozwiązaniem Zagrożeń oraz Questów. Brakuje jeszcze pełnego pokrycia wszystkich ważnych typów wydarzeń, numerów rund, szerszego UI/historii i finałowej Kroniki.

10. [Poziom Świata i progresja partii](10_POZIOM_SWIATA_I_PROGRESJA.md)  
   Istnieje działająca logika Poziomu Świata, progi Legendy, awans świata, kolejka komunikatów, talie Wydarzeń Świata I–IV, stosy odrzuconych, podstawowe skalowanie przeciwników i testy. Nadal trzeba domknąć wszystkie integracje progresji, nagród, sklepów, jakości przedmiotów i pozostałych systemów.

### BACKLOG

5. [Kopalnie i Miejsca Produkcji](05_KOPALNIE_I_MIEJSCA_PRODUKCJI.md)  
   Brak docelowego systemu Miejsc Produkcji/Kopalń.

6. [Towarzysz — wspólna wyprawa 2 bohaterów](06_TOWARZYSZ_WSPOLNA_WYPRAWA.md)  
   Zasady kierunkowe istnieją, ale brak docelowej implementacji wspólnej wyprawy dwóch bohaterów.

7. [Tożsamość Bohaterów](07_TOZSAMOSC_BOHATEROW.md)  
   Podstawowe archetypy, statystyki i wyposażenie istnieją, ale moduł charakterystycznych zdolności i wyraźnie różnych stylów gry nie został jeszcze zaimplementowany.

11. [Legendarny Quest i koniec gry](11_LEGENDARNY_QUEST_I_KONIEC_GRY.md)  
   Brak docelowego systemu Legendarnego Questa, rozstrzygnięcia końca partii i ekranu finałowego.

12. [Balans i grywalna ALFA 0.1](12_BALANS_I_ALFA_0_1.md)  
   Końcowy etap po domknięciu mechanik: pełne partie 2–6 graczy, balans ekonomii, tempa Legendy, trudności, downtime, UX i usuwanie placeholderów.

### GOTOWE

Na ten moment nie oznaczamy żadnego dużego modułu jako formalnie **GOTOWE**, ponieważ repo nie ma świeżego pełnego przebiegu regresji całej gry potwierdzającego Definition of Done. Moduły 01, 02 i 08 są już jednak na etapie **DO TESTÓW**, a nie implementacji od zera.

### WSTRZYMANE

13. [Multiplayer LAN](13_MULTIPLAYER_LAN.md)  
   W repo istnieją już elementy/prototypy sieciowe i testy, ale zgodnie z decyzją projektową moduł pozostaje wstrzymany do czasu grywalnej ALFY 0.1.

## Najbliższa kolejność prac

1. Dokończyć aktualny moduł **Walka V2**.
2. Wykonać pełną regresję **Zagrożeń**, **Questów** i **Rady Bohaterów** i po pozytywnym wyniku przenieść je do **GOTOWE**.
3. Następnie domykać moduły z istniejącym fundamentem: **Przygody V2**, **Kronika Świata**, **Poziom Świata i progresja**.
4. Dopiero potem wejść w moduły bez właściwej implementacji: **Kopalnie**, **Towarzysz**, **Tożsamość Bohaterów**, **Legendarny Quest**.
5. Na końcu pełny **Balans i ALFA 0.1**.

## Ważna zasada dla Kroniki

Kronika Świata jest późniejszym modułem, ale wcześniejsze systemy powinny już zostawiać miejsca, z których można emitować ważne zdarzenia do Kroniki. Część takich integracji już istnieje dla Questów i Zagrożeń.
