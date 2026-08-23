# ALFA — początek alfy (do ukończenia)

**Status:** AKTYWNY PLAN DOMKNIĘCIA GRY

## Cel

Celem tego etapu nie jest dodawanie wszystkich planowanych systemów i pełnego contentu. Celem jest jak najszybsze doprowadzenie Rise & Glory do stanu, w którym można rozpocząć normalną partię, przejść przez Poziomy Świata I–IV, rozpocząć Legendarny Quest, wygrać solo albo we dwóch i zobaczyć pełne zakończenie partii.

To jest nadrzędna roadmapa do pierwszej kompletnej ALFY. Jeżeli jakiś pomysł nie jest potrzebny do rozegrania pełnej partii od startu do końca, nie powinien blokować ukończenia ALFY.

---

# 0. MUST HAVE — CO MUSI DZIAŁAĆ, ŻEBY GRA BYŁA GRYWALNA

Poniższa lista jest bramką dla grywalnej ALFY. Nie chodzi o pełny content, perfekcyjny balans ani finalny wygląd. Chodzi o to, żeby osoba uruchamiająca grę mogła bez pomocy programisty rozpocząć normalną partię, grać przez wszystkie jej fazy i doprowadzić ją do prawidłowego zwycięstwa.

Jeżeli którykolwiek z poniższych punktów blokuje pełną partię, gra nie jest jeszcze uznawana za grywalną.

## 0.1. Start partii i podstawowa pętla

- [ ] Da się rozpocząć nową partię dla 2–6 graczy.
- [ ] Każdy gracz otrzymuje bohatera, początkowe statystyki, zasoby i wyposażenie wymagane do startu.
- [ ] Mapa generuje się poprawnie wraz z wymaganymi lokacjami i obiektami.
- [ ] Kolejność tur działa od pierwszego gracza aż do końca partii.
- [ ] Bohater posiada działające Akcje i może je normalnie wydawać.
- [ ] Ruch po mapie działa i respektuje koszty terenu.
- [ ] Runda poprawnie przechodzi w kolejną rundę.
- [ ] Gra nie wpada w stan, z którego nie da się kontynuować partii.

## 0.2. Rozwój bohatera

- [ ] Bohater może zdobywać Punkty Legendy.
- [ ] Bohater może rozwijać swoją siłę w trakcie partii przez zdobywanie nagród, Złota i wyposażenia.
- [ ] Statystyki Walka, Handel, Intryga, Dyplomacja, Kultura i Nauka działają w testach tam, gdzie są wymagane.
- [ ] Ekwipunek można zdobywać, zakładać i wykorzystywać.
- [ ] HP, Rany i podstawowe leczenie nie mogą blokować dalszej gry przez brak obsługi stanu bohatera.

## 0.3. Questy — główne źródło progresji

- [ ] Gracz może otrzymać/przyjąć Quest.
- [ ] Limit aktywnych Questów działa.
- [ ] Quest można rozpocząć, wykonywać etapami i ukończyć albo przegrać.
- [ ] Testy k20 i alternatywne metody rozwiązania działają.
- [ ] Quest może wymagać podróży, zasobów, przedmiotów albo walki.
- [ ] Nagrody i Punkty Legendy są poprawnie przyznawane.
- [ ] Questy istnieją dla wszystkich Poziomów Świata I–IV.
- [ ] Pula Questów jest wystarczająca, aby pełna partia nie zatrzymała się z powodu braku contentu.

## 0.4. Walka

- [ ] Da się rozpocząć walkę i doprowadzić ją do zwycięstwa, porażki albo legalnego opuszczenia walki.
- [ ] HP, KP, trafienie, obrażenia i podstawowe efekty wyposażenia działają.
- [ ] Przeciwnik wykonuje swoje działania poprawnie.
- [ ] Porażka bohatera ma obsłużone konsekwencje i pozwala później kontynuować partię.
- [ ] Zwycięstwo poprawnie przyznaje loot/nagrodę i wraca do wcześniejszego flow gry.
- [ ] Walka działa również wtedy, gdy została uruchomiona przez Quest albo Zagrożenie.
- [ ] Istnieje minimalna pula przeciwników oraz boss/finał potrzebny do pełnej partii.

## 0.5. Świat, Wydarzenia i Zagrożenia

- [ ] Rada uruchamia Wydarzenia Świata zgodnie z cyklem partii.
- [ ] Wydarzenie Świata potrafi nałożyć swój efekt i później go zakończyć.
- [ ] Zagrożenia mogą pojawić się na mapie, działać i zostać rozwiązane.
- [ ] Aktywne Zagrożenie rzeczywiście wpływa na grę zgodnie ze swoją kartą.
- [ ] Pula Wydarzeń Świata istnieje dla Poziomów I–IV.
- [ ] Gra nie zatrzymuje się, jeżeli jedno Wydarzenie nie może zostać prawidłowo rozmieszczone.

## 0.6. Rada Bohaterów

- [ ] Rada uruchamia się we właściwym momencie.
- [ ] Można przejść cały flow Rady od wejścia do opuszczenia jej przez wszystkich graczy.
- [ ] Wydarzenie Świata jest rozpatrywane.
- [ ] Podstawowy handel/oferty działają bez możliwości zablokowania sesji.
- [ ] Po zakończeniu Rady gra wraca do normalnej partii i rozpoczyna kolejny cykl.

## 0.7. Poziomy Świata I–IV

- [ ] Poziom I działa od początku partii.
- [ ] Po osiągnięciu progu lidera gra przechodzi na Poziom II.
- [ ] Następnie poprawnie przechodzi na III i IV.
- [ ] Po zmianie Poziomu Świata gra używa właściwych Questów i Wydarzeń.
- [ ] Przeciwnicy/nagrody posiadają przynajmniej podstawowe skalowanie wymagane do dalszej gry.
- [ ] Zmiana Poziomu Świata nie psuje aktywnych Questów, Zagrożeń ani bieżącego stanu partii.

Obowiązujące progi:

- Poziom Świata I: 0–9 Punktów Legendy lidera,
- Poziom Świata II: 10–19,
- Poziom Świata III: 20–29,
- Poziom Świata IV: 30+.

## 0.8. Legendarny Quest — droga do zwycięstwa

- [ ] Gracz z 35 Punktami Legendy może rozpocząć dostępny Legendarny Quest SOLO.
- [ ] Dwóch graczy mających minimum 30 Punktów Legendy każdy może rozpocząć dostępny Legendarny Quest DUO.
- [ ] Bohater może być związany tylko z jednym aktywnym Questem Legendarnym — albo solo, albo duo.
- [ ] Legendarny Quest posiada kilka etapów i da się go faktycznie ukończyć w normalnej partii.
- [ ] Quest solo wymaga od jednego bohatera samodzielnego poradzenia sobie z różnymi typami problemów.
- [ ] W duo każdy z dwóch graczy wykonuje realną część Questa, a część etapów może być wspólna.
- [ ] Wspólny Quest posiada czytelny stan postępu Bohatera A, Bohatera B i etapów wspólnych.
- [ ] Ukończenie solo daje zwycięstwo jednemu graczowi.
- [ ] Ukończenie duo daje pełne wspólne zwycięstwo obu graczom.

## 0.9. Koniec partii

- [ ] Gra rozpoznaje ukończenie Legendarnego Questa jako warunek zwycięstwa.
- [ ] Nie można przypadkowo kontynuować normalnej partii po jej formalnym zakończeniu.
- [ ] Rozstrzygnięcie końca bieżącej rundy działa zgodnie z przyjętymi zasadami.
- [ ] Ekran zwycięstwa pokazuje zwycięzcę albo dwóch zwycięzców.
- [ ] Powstaje ostatni wpis Kroniki.
- [ ] Da się wyświetlić „Kronikę Waszej Legendy”.
- [ ] Z ekranu końcowego da się wrócić do menu i rozpocząć nową partię.

## 0.10. Minimalny content

Do uznania gry za grywalną nie potrzebujemy setek kart, ale potrzebujemy wystarczającej liczby elementów, żeby pełna partia nie zapętlała się na kilku tych samych treściach ani nie zatrzymała się z braku dostępnej zawartości.

- [ ] Questy dla I, II, III i IV Poziomu Świata.
- [ ] Wydarzenia Świata dla I, II, III i IV Poziomu Świata.
- [ ] Reprezentatywne Zagrożenia.
- [ ] Zwykli oraz mocniejsi przeciwnicy.
- [ ] Bossowie/finałowi przeciwnicy tam, gdzie są potrzebni.
- [ ] Podstawowy katalog wyposażenia dla wszystkich używanych slotów.
- [ ] Co najmniej kilka grywalnych Legendarnych Questów solo.
- [ ] Co najmniej kilka grywalnych Legendarnych Questów duo.
- [ ] Minimalna warstwa fabularna/NPC potrzebna do zrozumienia, co dzieje się w świecie i dlaczego bohater wykonuje dane zadania.

## 0.11. Krytyczne UX i stabilność

- [ ] Wszystkie przyciski konieczne do przejścia pełnej partii są dostępne i działają.
- [ ] Gracz wie, czyja jest aktualnie tura i ile ma Akcji.
- [ ] Gracz widzi aktualny Poziom Świata i swoje Punkty Legendy.
- [ ] Gracz potrafi sprawdzić aktywne Questy, stan bohatera, wyposażenie i najważniejsze efekty świata.
- [ ] Nie istnieje znany błąd, który regularnie uniemożliwia kontynuowanie pełnej partii.
- [ ] Nie istnieje obowiązkowa mechanika wymagająca ręcznej ingerencji programisty lub edycji stanu gry.
- [ ] Pełną partię można przejść od menu startowego do ekranu zwycięstwa bez używania konsoli developerskiej.

## BRAMKA: „GRA JEST GRYWALNA”

Rise & Glory uznajemy za **grywalne**, gdy co najmniej jedna pełna partia testowa może przejść bez ingerencji programisty następujący ciąg:

**Nowa gra → wybór bohaterów → mapa → tury i ruch → Questy / Walka / Rada / Wydarzenia → Punkty Legendy → Poziom I → II → III → IV → Legendarny Quest solo lub duo → zwycięstwo → Kronika → ekran końcowy.**

Dopiero po osiągnięciu tej bramki dokładamy systemy, których brak nie uniemożliwia pełnej partii.

---

# A. RDZEŃ — domknięcie tego, co już istnieje

## 1. Walka V2

- [ ] Dokończyć wyłącznie brakujące elementy konieczne do pełnej gry.
- [ ] Dokończyć konsekwencje Ran w minimalnym zakresie wymaganym do ALFY.
- [ ] Przygotować minimalny zestaw przeciwników i bossów potrzebny do pełnej partii.
- [ ] Nie dodawać nowych dużych mechanik walki przed ukończeniem ALFY.
- [ ] Wykonać regresję Walki.

## 2. Regresja gotowego rdzenia

Bez dalszego rozbudowywania mechanik:

- [ ] pełny test Zagrożeń,
- [ ] pełny test Questów i Testów,
- [ ] pełny test Rady Bohaterów,
- [ ] naprawić tylko błędy blokujące i poważne problemy UX,
- [ ] po przejściu regresji oznaczyć te moduły jako GOTOWE.

---

# B. PROGRESJA — pełna droga od początku do Poziomu IV

## 3. Poziom Świata i progresja

Domknąć istniejący fundament tak, aby jedna partia mogła płynnie przechodzić przez wszystkie cztery poziomy.

Obowiązujące progi:

- Poziom Świata I: 0–9 Punktów Legendy lidera,
- Poziom Świata II: 10–19,
- Poziom Świata III: 20–29,
- Poziom Świata IV: 30+.

Do ALFY wymagane:

- [ ] poprawne przechodzenie I → II → III → IV,
- [ ] odpowiednie talie Questów/Wydarzeń dla poziomów,
- [ ] podstawowe skalowanie przeciwników i nagród,
- [ ] czytelny komunikat zmiany świata,
- [ ] integracja zmiany poziomu z Kroniką,
- [ ] wystarczająca liczba Questów i Wydarzeń, aby każda faza była grywalna.

Nie trzeba przed ALFĄ dopinać wszystkich przyszłych zależności sklepów, produkcji, pełnego katalogu EQ itd., jeżeli nie blokują pełnej partii.

---

# C. FINAŁ — Legendarny Quest i koniec gry

## 4. Legendarny Quest SOLO

- [ ] odblokowanie od 35 Punktów Legendy,
- [ ] bohater może mieć tylko jedną aktywną ścieżkę legendarną,
- [ ] po wejściu w solo nie może równocześnie wejść w duo,
- [ ] Quest solo jest trudniejszy przekrojowo: jeden bohater musi sam poradzić sobie z różnymi rodzajami problemów,
- [ ] Quest Legendarny jest wieloetapową mini-kampanią, a nie pojedynczym testem,
- [ ] może korzystać z NPC, wcześniejszych decyzji, flag historii, walki, podróży, zasobów i różnych statystyk,
- [ ] część Legendarnych Questów może być dostępna tylko solo.

## 5. Legendarny Quest DUO

- [ ] możliwość wejścia od 30 Punktów Legendy na każdego z dwóch bohaterów,
- [ ] maksymalnie dwóch bohaterów,
- [ ] obaj muszą zaakceptować wspólną drogę,
- [ ] po wejściu w duo obaj są zablokowani przed rozpoczęciem innego Legendarnego Questa,
- [ ] brak zdrady w finale — udane ukończenie oznacza pełne zwycięstwo obu graczy,
- [ ] każdy gracz musi realnie wykonać własną część,
- [ ] część etapów może być wykonywana równolegle przez obu bohaterów w różnych miejscach mapy,
- [ ] część etapów jest wspólna,
- [ ] nie sumujemy automatycznie statystyk bohaterów,
- [ ] specjalizacje mają się uzupełniać, np. Walka + Nauka albo Dyplomacja + Handel,
- [ ] część Legendarnych Questów może być dostępna wyłącznie dla duo.

### Minimalny UI duo

Wspólny Quest Legendarny ma własny panel:

- Bohater A — postęp własnych etapów,
- Bohater B — postęp własnych etapów,
- Etapy wspólne,
- status finału.

Pełny ogólny system Towarzysza nie jest wymagany do ALFY. Wspólne Legendy mają otrzymać własną, węższą integrację.

## 6. Zakończenie partii

- [ ] ukończenie Legendarnego Questa oznacza zwycięstwo solo albo duo,
- [ ] domknąć zasadę zakończenia bieżącej rundy po zwycięstwie,
- [ ] ekran zwycięstwa,
- [ ] ostatni wpis Kroniki,
- [ ] ekran „Kronika Waszej Legendy”,
- [ ] powrót do menu,
- [ ] możliwość rozpoczęcia nowej partii.

---

# D. CONTENT MINIMUM — tylko tyle, ile potrzeba do pełnej partii

## 7. Questy

- [ ] wystarczająca pula Questów dla Poziomu I,
- [ ] wystarczająca pula Questów dla Poziomu II,
- [ ] wystarczająca pula Questów dla Poziomu III,
- [ ] wystarczająca pula Questów dla Poziomu IV,
- [ ] kilka rozbudowanych Questów fabularnych pokazujących zmiany świata,
- [ ] kilka Questów Legendarnych solo,
- [ ] kilka Questów Legendarnych duo.

Nie projektować setek Questów przed pierwszą pełną partią.

## 8. Wydarzenia Świata i Zagrożenia

- [ ] wystarczająca pula Wydarzeń dla I–IV,
- [ ] kilka reprezentatywnych Zagrożeń,
- [ ] wykorzystać istniejący silnik zamiast dodawać nową mechanikę.

## 9. Przeciwnicy i bossowie

- [ ] minimalny zestaw zwykłych przeciwników,
- [ ] kilka mocniejszych przeciwników,
- [ ] bossowie potrzebni do Questów i finałów.

## 10. Ekwipunek

Pełny katalog 280 kart pozostaje celem docelowym, ale nie blokuje ALFY.

Do pierwszej kompletnej ALFY:

- [ ] reprezentatywny zestaw przedmiotów dla wszystkich slotów,
- [ ] kilka jakości,
- [ ] wystarczająca różnorodność, aby testować buildy i nagrody,
- [ ] pełne 280 kart uzupełniać dopiero po potwierdzeniu, że rdzeń gry działa i jest grywalny.

---

# E. SYSTEMY UPROSZCZONE NA ALFĘ

## 11. Kronika Świata — wersja minimalna

Kronika nie ma blokować ukończenia gry rozbudowanym UI.

Do ALFY zapisujemy przede wszystkim:

- [ ] Wydarzenia Świata,
- [ ] ważne rozwiązane Zagrożenia,
- [ ] ważne ukończone Questy,
- [ ] zmianę Poziomu Świata,
- [ ] rozpoczęcie Legendarnego Questa,
- [ ] rozpoczęcie wspólnego Legendarnego Questa,
- [ ] ukończenie Legendarnego Questa,
- [ ] zwycięzcę albo dwóch zwycięzców.

UI może być prostą chronologiczną listą. Ikony, filtrowanie i dodatkowa prezentacja mogą zostać dodane później.

## 12. Przygody na mapie — wersja minimalna

Nie budować osobnego dużego silnika, jeśli istniejący silnik Questów może obsłużyć potrzebne elementy.

Przygoda w ALFIE:

- krótki opis,
- 2–3 opcje,
- test / koszt / walka / decyzja,
- natychmiastowa konsekwencja,
- koniec.

Przygoda nie zajmuje slotu Questa i nie jest wieloetapowym zadaniem.

## 13. Towarzysz — odłożony poza Legendarnym Questem

Pełny system wspólnej wyprawy dwóch bohaterów zostaje po ALFIE.

Na potrzeby ALFY implementujemy tylko funkcje potrzebne do dwuosobowych Legendarnych Questów.

Nie blokujemy ALFY przez:

- wspólne chodzenie pionków,
- pełną wspólną walkę,
- ogólny podział każdego rodzaju nagrody,
- ogólne wspólne Questy poza Legendarnymi.

---

# F. RZECZY, KTÓRE NIE BLOKUJĄ ALFY

Poniższe systemy mogą być rozwijane po uzyskaniu pierwszej pełnej grywalnej partii:

- pełne Kopalnie i Miejsca Produkcji,
- pełny system Towarzysza,
- pełna Tożsamość Bohaterów i unikalne zdolności wszystkich archetypów,
- pełne 280 kart ekwipunku,
- bonusy zestawów 2/4/6,
- rozbudowane Przygody V2,
- rozbudowana Kronika,
- Multiplayer LAN,
- dodatkowe typy produkcji,
- dalsze duże mechaniki, które nie są wymagane do zakończenia partii.

---

# G. TEST PEŁNEJ GRY

Po ukończeniu punktów A–E natychmiast przechodzimy do pełnych partii.

## Kolejność

1. [ ] Pełna partia 2 graczy od startu do Legendarnego Questa i ekranu końcowego.
2. [ ] Naprawić błędy blokujące.
3. [ ] Pełna partia 4 graczy.
4. [ ] Naprawić problemy z tempem, downtime i balansem.
5. [ ] Pełna partia 6 graczy.
6. [ ] Sprawdzić szczególnie wyścig Legendy: solo 35 kontra duo 30+30.
7. [ ] Sprawdzić, czy gracz z tyłu nadal ma realną drogę do zwycięstwa.
8. [ ] Sprawdzić, czy duo nie jest zawsze lepsze od solo.
9. [ ] Sprawdzić długość pełnej partii.
10. [ ] Usunąć krytyczne placeholdery i błędy UX.
11. [ ] Zamrozić zasady pierwszej grywalnej ALFY.

---

# Definition of Done — POCZĄTEK ALFY UKOŃCZONY

Etap jest ukończony, gdy można:

1. rozpocząć normalną partię 2–6 graczy,
2. rozwijać bohatera i zdobywać Punkty Legendy,
3. przejść przez Poziomy Świata I, II, III i IV,
4. wykonywać Questy, walczyć, handlować i reagować na Wydarzenia Świata,
5. przy 30 Legendy wejść z drugim graczem na dostępną ścieżkę Legendarnego Questa duo,
6. przy 35 Legendy rozpocząć dostępny Legendarny Quest solo,
7. ukończyć Legendarny Quest,
8. poprawnie rozstrzygnąć zwycięstwo solo albo dwóch graczy,
9. zobaczyć ekran końcowy i „Kronikę Waszej Legendy”,
10. zakończyć partię bez ingerencji programisty i bez blokujących błędów.

**Najważniejsza zasada tego etapu:** najpierw kompletna gra od początku do końca. Rozszerzenia dopiero później.