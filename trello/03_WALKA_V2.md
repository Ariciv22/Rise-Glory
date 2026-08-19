# 03 — Walka V2

**Status Kanban:** DO ZROBIENIA

## Cel

Stworzyć kompletną podstawową walkę wystarczającą do pierwszej alfy.

Bohater rozpoczyna każdą rundę walki.

Atak bohatera:

`k20 + Walka + premie wyposażenia`

Jeżeli wynik osiąga lub przekracza KP przeciwnika, atak trafia.

## Zatwierdzone zasady

### Podstawy walki

- Bohater rozpoczyna każdą rundę walki.
- Atak bohatera to `k20 + Walka + premie wyposażenia` przeciwko KP przeciwnika.
- Cała walka, niezależnie od liczby rund, kosztuje 1 Akcję.
- Bohater korzysta z systemu Ran, a przeciwnik posiada HP.
- Naturalne 20 podczas ataku oznacza 2 trafienia i dwukrotne rozpatrzenie obrażeń.
- Naturalne 1 podczas ataku oznacza automatyczne pudło.
- Walka nie posiada maksymalnego limitu rund. Trwa aż do pokonania jednej ze stron albo skutecznego opuszczenia walki, jeśli dana walka na to pozwala.

### Broń i obrażenia

- Każda broń posiada dwa osobne parametry: premię do trafienia oraz wartość obrażeń.
- Przykładowy zapis broni może wyglądać jak `+2 do trafienia / 2 obrażenia`.
- Atak bez broni zadaje bazowo 1 obrażenie i nie otrzymuje premii broni.
- Przeciwnik zadaje stałą liczbę Ran/obrażeń określoną na swojej karcie. Podstawowe obrażenia przeciwnika nie są losowane jako zakres.

### Skalowanie przeciwników Poziomem Świata

Poziom Świata I korzysta z bazowych statystyk przeciwnika zapisanych na jego karcie. Od Poziomu Świata II przeciwnicy otrzymują dodatkowe modyfikatory:

- Poziom Świata I: wartości bazowe, bez dodatkowego modyfikatora.
- Poziom Świata II: `+2 KP`, `+2 do trafienia`, `+2 HP`.
- Poziom Świata III: `+3 KP`, `+3 do trafienia`, `+3 HP`.
- Poziom Świata IV: `+4 KP`, `+4 do trafienia`, `+4 HP`.

To skalowanie zastępuje wcześniejszy wariant skalowania samego HP `+2/+4/+6/+8`.

- Na obecnym etapie Poziom Świata skaluje wyłącznie KP, premię do trafienia i HP przeciwnika.
- Stała liczba Ran/obrażeń zadawanych przez przeciwnika nie otrzymuje automatycznego bonusu z Poziomu Świata.
- Przeciwnicy legendarni i bossowie mogą mieć dodatkowe własne skalowanie określone osobno.

### Zbroja i obrona bohatera

- Zbroja w podstawowym założeniu zwiększa KP bohatera.
- Zbroje mogą również posiadać dodatkowe efekty poza premią do KP.
- Inne elementy wyposażenia defensywnego, takie jak tarcze, hełmy, pierścienie lub inne przedmioty, również mogą zwiększać KP, jeśli ich karta tak stanowi.
- Premie i efekty defensywne wynikają z konkretnej karty przedmiotu.

### Pomocnicy w walce

- Pomocnik może wspierać bohatera podczas walki.
- Rodzaj pomocy wynika z karty Pomocnika i może obejmować np. premię do Walki, trafienia, obrażeń, KP albo inny efekt bojowy.

### Przedmioty używane w walce

- Podczas walki można używać jednorazowych przedmiotów i efektów, takich jak mikstury, bomby, zwoje, jedzenie lub inne przedmioty dopuszczone przez ich kartę.
- Użycie takiego przedmiotu zużywa działanie bohatera w danej rundzie walki zamiast wykonania ataku.
- Po wykorzystaniu przedmiotu bohater nie wykonuje dodatkowo normalnego ataku w tej samej rundzie, chyba że konkretny efekt wyraźnie stanowi inaczej.

### Efekty statusowe

- System walki będzie obsługiwał efekty statusowe.
- Do możliwych statusów należą m.in. zatrucie, krwawienie, ogłuszenie, podpalenie, osłabienie KP i inne podobne efekty.
- Dokładna lista statusów, czas działania, sposób nakładania i zdejmowania zostaną dopracowane osobno.

### Zdolności specjalne przeciwników

- Przeciwnicy będą mogli posiadać specjalne zdolności i dodatkowe efekty.
- Szczegółowy system zdolności zostanie rozwinięty później.
- Ogólny kierunek: co określoną liczbę rund przeciwnik może wykonywać rzut uruchamiający dodatkowy efekt, a wynik rzutu kością określa, jaki efekt wystąpił.
- Częstotliwość, warunek aktywacji oraz sposób działania zdolności są określane indywidualnie przez kartę danego przeciwnika.

### Bossowie i fazy walki

- Bossowie mogą posiadać kilka faz walki.
- Przejście do kolejnej fazy może następować np. po spadku HP poniżej określonego progu.
- Kolejna faza może zmieniać zdolności, zachowanie, sposób ataku, statystyki lub inne zasady bossa zgodnie z jego kartą.

### Ucieczka i przekupstwo

- Nieudana próba ucieczki powoduje natychmiastowy atak przeciwnika, po czym walka trwa dalej, jeśli bohater nie został pokonany.
- Podstawowe sposoby opuszczenia walki to test Intrygi albo przekupienie przeciwnika określoną liczbą Złota.
- Wymagany poziom testu Intrygi i koszt przekupstwa określa karta przeciwnika lub konkretnej walki.
- Nie każda walka pozwala na ucieczkę.
- Nie każda walka pozwala na przekupstwo.
- Niektóre walki mogą całkowicie blokować zarówno ucieczkę, jak i przekupienie przeciwnika.

### Loot i bossowie

- Przeciwnicy są reprezentowani przez karty potworów/przeciwników.
- Karta przeciwnika określa loot możliwy lub przyznawany po jego pokonaniu.
- Boss zawsze posiada specjalną nagrodę poza zwykłym rozstrzygnięciem walki; dokładny rodzaj nagrody określa karta bossa lub powiązany scenariusz/Quest.

## Punkty do działania

- [ ] HP przeciwnika.
- [ ] KP przeciwnika.
- [ ] Atak bohatera.
- [ ] Atak przeciwnika.
- [ ] Obrażenia bohatera.
- [ ] Stałe obrażenia/Rany przeciwnika określane na karcie.
- [ ] Rany bohatera.
- [ ] Każda broń posiada osobną premię do trafienia i wartość obrażeń.
- [ ] Atak bez broni zadaje 1 obrażenie bez premii broni.
- [ ] Zbroja określa KP bohatera i może posiadać dodatkowe efekty.
- [ ] Obsłużyć premie do KP z innych elementów wyposażenia, np. tarczy, hełmu lub pierścienia.
- [ ] Obsłużyć bojowe efekty Pomocników.
- [ ] Obsłużyć używanie przedmiotów jednorazowych podczas walki zamiast ataku bohatera w danej rundzie.
- [ ] Obsłużyć system statusów.
- [ ] Obsłużyć Nat 20.
- [ ] Obsłużyć Nat 1.
- [ ] Kolejne rundy walki bez sztywnego limitu rund.
- [ ] Pokonanie przeciwnika.
- [ ] Pokonanie bohatera.
- [ ] Ucieczka.
- [ ] Ucieczka poprzez test Intrygi.
- [ ] Przekupstwo za Złoto.
- [ ] Obsłużyć walki bez możliwości ucieczki i przekupstwa.
- [ ] Nieudana ucieczka uruchamia natychmiastowy atak przeciwnika.
- [ ] Cała walka kosztuje 1 Akcję.
- [ ] Nagrody po walce.
- [ ] Loot określany przez kartę przeciwnika.
- [ ] Walka jako etap Questa.
- [ ] Walka jako część Zagrożenia.
- [ ] Walka jako część Przygody.
- [ ] Skalowanie przeciwników Poziomem Świata: KP, trafienie i HP.
- [ ] Zdolności specjalne przeciwników aktywowane zgodnie z regułą na karcie.
- [ ] Bossowie.
- [ ] Wieloetapowe fazy bossów.
- [ ] Boss posiada specjalną nagrodę.
- [ ] Przeciwnicy legendarni.
- [ ] Czytelny ekran zakończenia walki.
- [ ] Przygotować podstawową pulę przeciwników.
- [ ] Przygotować przynajmniej jednego bossa testowego.
- [ ] Przygotować punkt integracji z Kroniką Świata dla ważnych walk.

## Do dopracowania później

- Dokładna lista i pula specjalnych efektów przeciwników.
- Dokładne tabele/rzuty określające dodatkowe efekty podczas walki.
- Dokładna lista statusów i zasady ich działania.
- Indywidualne zdolności bossów i przeciwników legendarnych.
- Konkretne pule lootu i wartości nagród.

## Definition of Done

Walka może zostać uruchomiona z Questa, Przygody lub Zagrożenia, przejść przez wszystkie rundy i zakończyć się poprawną nagrodą, porażką albo ucieczką.