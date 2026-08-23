# 14 — Ekwipunek i archetypy

**Status projektowy:** OBOWIĄZUJĄCE USTALENIA

**Status Kanban:** DO ZROBIENIA — fundament ekwipunku istnieje w silniku, ale pełny katalog 280 kart, archetypy i przyszłe bonusy zestawów wymagają implementacji.

## Cel

Ustalić jeden obowiązujący katalog ekwipunku Rise & Glory, z którego mają korzystać sklepy, nagrody, questy, loot i ekran bohatera.

## Obowiązujące zasady katalogu

- Bohater ma 8 slotów założonego EQ: **Broń, Zbroja, Hełm, Buty, Rękawice, Amulet, Pierścień 1, Pierścień 2**.
- Dwa sloty pierścieni korzystają z jednej wspólnej puli kart Pierścieni.
- Istnieje 7 kategorii kart EQ: **Broń, Zbroja, Hełmy, Buty, Rękawice, Amulety, Pierścienie**.
- Każda kategoria ma **40 różnych kart**: 10 Zwykłych, 10 Rzadkich, 10 Epickich i 10 Legendarnych.
- Razem katalog zawiera **280 różnych kart EQ**.
- Każda karta ma dokładnie jeden archetyp zestawu.
- Archetyp jest tagiem zestawu niezależnym od jakości przedmiotu.
- Docelowo archetypy otrzymają bonusy za **2 / 4 / 6** założonych pasujących elementów. Konkretne bonusy 2/4/6 są jeszcze do ustalenia i nie wolno ich wymyślać bez osobnej decyzji projektowej.
- Przedmioty tej samej jakości nie muszą mieć tej samej ceny. Cena ma zależeć od realnej siły, liczby efektów i synergii. Przedmiot z dwoma dobrymi efektami ma być droższy niż porównywalny przedmiot z jednym efektem.
- Przedmiot droższy nie musi być bezwzględnie lepszy. Katalog ma zawierać sidegrade’y, warunki, ryzyko, efekty sytuacyjne i elementy pod różne buildy.
- Część mocnych kart może mieć wadę lub warunek aktywacji.
- Zwykłe przedmioty mogą mieć jeden prosty efekt albo dwa małe efekty za wyższą cenę.
- Rzadkie przedmioty zwykle mają dwa efekty albo jeden wyraźnie mocniejszy efekt.
- Epickie przedmioty mają tworzyć build i najczęściej łączyć 2–3 efekty lub mechanikę warunkową.
- Legendarne przedmioty mają być unikalne mechanicznie, a nie tylko dawać większe liczby. Zasadniczo nie pojawiają się w zwykłym sklepie i mają pochodzić głównie z ważnych questów, bossów i nagród legendarnych.
- Dla Zbroi obowiązuje bazowa skala jakości: **Zwykła 12 KP, Rzadka 14 KP, Epicka 16 KP, Legendarna 18 KP**. Efekty dodatkowe mogą tę wartość modyfikować.
- Dla Broni przechowujemy osobno premię do trafienia i wartość obrażeń.
- Obecna statystyka gry nazywa się **Nauka**. Archetyp **Wielki Mędrzec** jest archetypem stricte związanym z Nauką.

## 18 archetypów EQ

1. **Krwawy Berserker** — Rany, niskie HP, ryzyko, wysoka ofensywa.
2. **Żelazny Strażnik** — KP, redukcja obrażeń, reakcje obronne, przeżywalność.
3. **Cień** — skradanie, pierwszy cios, uniki, ucieczka, osłabianie przeciwnika.
4. **Łowca Potworów** — bestie, bossowie, legendarni przeciwnicy, celność i krytyki.
5. **Runiczny Uczony** — runy, artefakty, Nauka i kontrola testów związanych z wiedzą.
6. **Złoty Kupiec** — złoto, ceny, kupno, sprzedaż i ekonomia.
7. **Królewski Dyplomata** — interakcje społeczne, dwór, negocjacje i questy społeczne.
8. **Kronikarz** — Kultura, sława, opowieści i efekty związane z questami.
9. **Wędrowiec** — ruch, trudny teren, podróże i ucieczka.
10. **Dowódca Kompanii** — pomocnicy, Kompania i współpraca z towarzyszami.
11. **Uzdrowiciel** — HP, Rany, leczenie i regeneracja.
12. **Tkacz Losu** — przerzuty, naturalne 1/20 i manipulacja k20.
13. **Mistrz Oręża** — archetyp stricte pod atrybut **Walka**.
14. **Mistrz Gildii** — archetyp stricte pod atrybut **Handel**.
15. **Srebrny Język** — archetyp stricte pod atrybut **Dyplomacja**.
16. **Mistrz Intryg** — archetyp stricte pod atrybut **Intryga**.
17. **Wielki Mędrzec** — archetyp stricte pod atrybut **Nauka**.
18. **Mistrz Kultury** — archetyp stricte pod atrybut **Kultura**.

---

# BROŃ — 40 kart

## Zwykłe — 10

| # | Nazwa | Archetyp | Trafienie | Obrażenia | Efekt | Cena |
|---:|---|---|---:|---:|---|---:|
| 1 | Prosty miecz | Mistrz Oręża | +0 | 1 | +1 Walka podczas pierwszego ataku w walce. | 7 |
| 2 | Sztylet cienia | Mistrz Intryg | +1 | 1 | +1 Intryga. | 8 |
| 3 | Topór rzeźnika | Krwawy Berserker | -1 | 2 | Mając co najmniej 1 Ranę: +1 do pierwszego trafienia w walce. | 9 |
| 4 | Włócznia myśliwska | Łowca Potworów | +1 | 1 | +1 obrażenie przeciw bestiom. | 10 |
| 5 | Kostur adepta | Wielki Mędrzec | +0 | 1 | +1 Nauka. | 8 |
| 6 | Szabla karawaniarza | Mistrz Gildii | +0 | 1 | +1 Handel. | 8 |
| 7 | Rapier posła | Srebrny Język | +1 | 1 | +1 Dyplomacja. | 9 |
| 8 | Ostrze pieśniarza | Mistrz Kultury | +0 | 1 | +1 Kultura. | 8 |
| 9 | Kij wędrowca | Wędrowiec | +0 | 1 | +1 do prób ucieczki. | 7 |
| 10 | Miecz kaprala | Dowódca Kompanii | +0 | 1 | Gdy w walce korzystasz z Pomocnika: +1 do pierwszego ataku. | 9 |

## Rzadkie — 10

| # | Nazwa | Archetyp | Trafienie | Obrażenia | Efekt | Cena |
|---:|---|---|---:|---:|---|---:|
| 11 | Krwawy topór | Krwawy Berserker | +0 | 2 | Mając Ranę: +1 obrażenie. | 14 |
| 12 | Miecz bastionu | Żelazny Strażnik | +1 | 2 | Podczas walki +1 KP. | 16 |
| 13 | Igła nocy | Cień | +2 | 1 | Pierwsze trafienie w walce zadaje +1 obrażenie. | 16 |
| 14 | Harpun bestiobójcy | Łowca Potworów | +1 | 2 | Przeciw bestiom dodatkowo +1 trafienia. | 16 |
| 15 | Runiczne ostrze | Runiczny Uczony | +1 | 1 | +1 Nauka; pierwszy test związany z runą lub artefaktem w turze ma +1. | 17 |
| 16 | Pozłacany pałasz | Złoty Kupiec | +0 | 2 | +1 Handel; pierwsza sprzedaż podczas wizyty daje +1 monetę. | 17 |
| 17 | Rapier pojedynkowicza | Mistrz Oręża | +2 | 1 | +1 Walka w pierwszej rundzie walki. | 15 |
| 18 | Ostrze ballady | Kronikarz | +1 | 1 | +1 Kultura; +1 do pierwszego testu Questa Kultury w turze. | 17 |
| 19 | Laska pielgrzyma | Uzdrowiciel | +0 | 1 | Leczenie Ran w lokacji kosztuje o 1 monetę mniej za Ranę. | 15 |
| 20 | Kościane ostrze losu | Tkacz Losu | +1 | 1 | Raz na walkę możesz przerzucić własny rzut ataku. | 18 |

## Epickie — 10

| # | Nazwa | Archetyp | Trafienie | Obrażenia | Efekt | Cena |
|---:|---|---|---:|---:|---|---:|
| 21 | Topór ostatniej furii | Krwawy Berserker | +1 | 3 | Mając Ranę: dodatkowo +1 trafienia; przy połowie HP lub mniej jeszcze +1 obrażenie. | 25 |
| 22 | Ostrze twierdzy | Żelazny Strażnik | +1 | 2 | +1 KP; pierwszy trafiony atak przeciwnika w walce zadaje o 1 mniej obrażenia. | 26 |
| 23 | Bezgłośny kieł | Cień | +3 | 1 | Pierwsze trafienie: przeciwnik ma -1 do następnego ataku. | 23 |
| 24 | Pogromca potworów | Łowca Potworów | +2 | 2 | Przeciw bestiom i przeciwnikom legendarnym: +1 obrażenie. | 24 |
| 25 | Gwiezdny kostur | Runiczny Uczony | +1 | 2 | +2 Nauka; raz na turę możesz przerzucić test Nauki. | 27 |
| 26 | Miecz księcia monet | Złoty Kupiec | +1 | 2 | +2 Handel; pierwszy zakup podczas wizyty kosztuje o 1 monetę mniej. | 27 |
| 27 | Królewski rapier | Królewski Dyplomata | +2 | 2 | +2 Dyplomacja; pierwszy test Dyplomacji w turze ma +1. | 27 |
| 28 | Klinga kronikarza | Kronikarz | +1 | 2 | +2 Kultura; pierwszy test Questa Kultury w turze można przerzucić. | 27 |
| 29 | Włócznia horyzontu | Wędrowiec | +2 | 2 | Pierwszy trudny teren w turze kosztuje o 1 Akcję mniej. | 24 |
| 30 | Miecz chorążego | Dowódca Kompanii | +1 | 2 | Gdy używasz Pomocnika w walce: +1 trafienia i +1 obrażenie. | 26 |

## Legendarne — 10

| # | Nazwa | Archetyp | Trafienie | Obrażenia | Efekt | Dostępność |
|---:|---|---|---:|---:|---|---|
| 31 | Ojciec Krwi | Krwawy Berserker | +2 | 3 | Każda Rana daje +1 trafienia, maks. +2; przy 3 Ranach +1 obrażenie. | Legendarny loot/quest |
| 32 | Ostatni Bastion | Żelazny Strażnik | +2 | 2 | +2 KP; raz na walkę anuluj jedno trafienie przeciwnika. | Legendarny loot/quest |
| 33 | Bezimienny Sztylet | Cień | +4 | 1 | Pierwszy atak walki traktuje naturalne 19 jak trafienie krytyczne. | Legendarny loot/quest |
| 34 | Łuk Księżycowego Łowcy | Łowca Potworów | +3 | 2 | Przeciw legendarnym przeciwnikom +2 obrażenia; naturalne 20 zadaje dodatkowo +1 obrażenie. | Legendarny loot/quest |
| 35 | Kostur Gwiezdnego Skryby | Wielki Mędrzec | +2 | 2 | +2 Nauka; raz na turę możesz potraktować wynik testu Nauki jak naturalne 10 na kości. | Legendarny loot/quest |
| 36 | Złoty Kieł | Mistrz Gildii | +1 | 2 | +2 Handel; pierwszy zakup -2 monety, pierwsza sprzedaż +2 monety. | Legendarny loot/quest |
| 37 | Strażnik Przysięgi | Srebrny Język | +3 | 2 | +2 Dyplomacja; raz na turę możesz przerzucić test Dyplomacji. | Legendarny loot/quest |
| 38 | Pieśń Stali | Mistrz Kultury | +2 | 2 | +2 Kultura; po ukończeniu questa otrzymujesz +1 do następnego testu w tej turze. | Legendarny loot/quest |
| 39 | Laska Białego Uzdrowiciela | Uzdrowiciel | +1 | 2 | Leczenie Ran -1 moneta za Ranę; raz na turę efekt leczenia HP leczy dodatkowo 1 HP. | Legendarny loot/quest |
| 40 | Przecinacz Losu | Tkacz Losu | +2 | 2 | Raz na walkę przerzut ataku; raz na walkę naturalne 1 możesz zamienić na wynik 10. | Legendarny loot/quest |

---

# ZBROJE — 40 kart

**Bazowe KP jakości:** Zwykła 12, Rzadka 14, Epicka 16, Legendarna 18.

## Zwykłe — 10

| # | Nazwa | Archetyp | KP | Efekt | Cena |
|---:|---|---|---:|---|---:|
| 1 | Przeszywanica wojownika | Mistrz Oręża | 12 | +1 Walka w pierwszej rundzie walki. | 8 |
| 2 | Skóra rzeźnika | Krwawy Berserker | 12 | Mając Ranę: +1 do pierwszego ataku w walce. | 9 |
| 3 | Kaftan intryganta | Mistrz Intryg | 12 | +1 Intryga. | 8 |
| 4 | Skóra tropiciela | Łowca Potworów | 12 | +1 do pierwszego testu lub ataku przeciw bestii. | 8 |
| 5 | Szata adepta | Wielki Mędrzec | 12 | +1 Nauka. | 8 |
| 6 | Kamizela kupiecka | Mistrz Gildii | 12 | +1 Handel. | 8 |
| 7 | Surkot posła | Srebrny Język | 12 | +1 Dyplomacja. | 8 |
| 8 | Strój kronikarza | Mistrz Kultury | 12 | +1 Kultura. | 8 |
| 9 | Pancerz podróżny | Wędrowiec | 12 | +1 do prób ucieczki. | 7 |
| 10 | Płaszcz medyka | Uzdrowiciel | 12 | Pierwsza leczona Rana podczas wizyty kosztuje o 1 monetę mniej. | 9 |

## Rzadkie — 10

| # | Nazwa | Archetyp | KP | Efekt | Cena |
|---:|---|---|---:|---|---:|
| 11 | Pancerz berserkera | Krwawy Berserker | 14 | Mając Ranę: +1 obrażenie; -1 do prób ucieczki. | 15 |
| 12 | Kolczuga gwardzisty | Żelazny Strażnik | 14 | Pierwszy atak przeciwnika w walce ma -1 do trafienia. | 15 |
| 13 | Pancerz nocnego szlaku | Cień | 14 | +1 Intryga i +1 do ucieczki. | 17 |
| 14 | Łuskowa zbroja łowcy | Łowca Potworów | 14 | +1 Walka przeciw bestiom. | 14 |
| 15 | Runiczna kolczuga | Runiczny Uczony | 14 | +1 Nauka; +1 do testów artefaktów i run. | 17 |
| 16 | Pancerz gildii | Złoty Kupiec | 14 | +1 Handel; pierwsza sprzedaż podczas wizyty +1 moneta. | 17 |
| 17 | Zbroja ambasadora | Królewski Dyplomata | 14 | +1 Dyplomacja i +1 Kultura. | 18 |
| 18 | Pancerz trubadura | Kronikarz | 14 | +1 Kultura; pierwszy test Kultury w turze ma +1. | 17 |
| 19 | Zbroja szlaku | Wędrowiec | 14 | Pierwszy trudny teren w turze kosztuje o 1 Akcję mniej. | 15 |
| 20 | Pancerz wróżbity | Tkacz Losu | 14 | Raz na turę możesz przerzucić naturalne 1 w teście poza walką. | 18 |

## Epickie — 10

| # | Nazwa | Archetyp | KP | Efekt | Cena |
|---:|---|---|---:|---|---:|
| 21 | Krwawa płyta | Krwawy Berserker | 16 | Mając Ranę: +1 trafienia i +1 obrażenie; -1 do prób ucieczki. | 26 |
| 22 | Płyta Żelaznego Muru | Żelazny Strażnik | 16 | Dodatkowo +1 KP; pierwsze otrzymane obrażenie w walce jest zmniejszone o 1. | 28 |
| 23 | Tkana Noc | Cień | 16 | +2 Intryga; pierwszy atak przeciwnika w walce ma -1 do trafienia. | 27 |
| 24 | Smocza łuska łowcy | Łowca Potworów | 16 | +1 trafienia i +1 obrażenie przeciw bestiom. | 25 |
| 25 | Pancerz runiczny | Runiczny Uczony | 16 | +2 Nauka; raz na turę przerzut testu Nauki. | 27 |
| 26 | Pancerz Księcia Kupców | Złoty Kupiec | 16 | +2 Handel; pierwszy zakup podczas wizyty -1 moneta. | 27 |
| 27 | Zbroja Królewskiego Poselstwa | Królewski Dyplomata | 16 | +2 Dyplomacja i +1 Kultura. | 26 |
| 28 | Pancerz Wielkiego Kronikarza | Kronikarz | 16 | +2 Kultura; pierwszy test questa w turze ma +1. | 26 |
| 29 | Zbroja Horyzontu | Wędrowiec | 16 | Pierwszy trudny teren -1 Akcja; +1 do ucieczki. | 25 |
| 30 | Pancerz Kapitana | Dowódca Kompanii | 16 | Z Pomocnikiem: +1 KP i +1 do testu wspieranego jego premią. | 27 |

## Legendarne — 10

| # | Nazwa | Archetyp | KP | Efekt | Dostępność |
|---:|---|---|---:|---|---|
| 31 | Zbroja Siedmiu Blizn | Krwawy Berserker | 18 | Każda Rana daje +1 do pierwszego ataku walki, maks. +3. | Legendarny loot/quest |
| 32 | Mur Artium | Żelazny Strażnik | 18 | Dodatkowo +2 KP; raz na walkę anuluj otrzymane obrażenia z jednego trafienia. | Legendarny loot/quest |
| 33 | Płaszcz Bezksiężycowej Nocy | Cień | 18 | +2 Intryga; pierwszy atak przeciwnika ma -2 do trafienia. | Legendarny loot/quest |
| 34 | Pancerz Pogromcy Smoków | Łowca Potworów | 18 | +2 Walka przeciw bestiom i legendarnym przeciwnikom. | Legendarny loot/quest |
| 35 | Szata Tysiąca Run | Runiczny Uczony | 18 | +2 Nauka; ignorujesz pierwszy negatywny status nałożony na ciebie w każdej walce. | Legendarny loot/quest |
| 36 | Złota Zbroja Dziesięciu Gildii | Złoty Kupiec | 18 | +2 Handel; pierwszy zakup -2, pierwsza sprzedaż +2 monety. | Legendarny loot/quest |
| 37 | Pancerz Pierwszego Ambasadora | Srebrny Język | 18 | +2 Dyplomacja i +1 Kultura; raz na turę przerzut Dyplomacji. | Legendarny loot/quest |
| 38 | Szata Wiecznej Ballady | Mistrz Kultury | 18 | +2 Kultura; po pierwszym nieudanym teście questa w turze otrzymujesz +2 do jego ponowienia. | Legendarny loot/quest |
| 39 | Zbroja Białego Zakonu | Uzdrowiciel | 18 | Leczenie Ran -1 moneta za Ranę; +2 maks. HP. | Legendarny loot/quest |
| 40 | Pancerz Przeznaczenia | Tkacz Losu | 18 | Raz na walkę możesz wymusić przerzut udanego ataku przeciwnika. | Legendarny loot/quest |

---

# HEŁMY — 40 kart

## Zwykłe — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 1 | Żelazny hełm fechmistrza | Mistrz Oręża | +1 Walka w pierwszej rundzie walki. | 7 |
| 2 | Przyłbica rzeźnika | Krwawy Berserker | Mając Ranę: +1 do pierwszego ataku. | 7 |
| 3 | Kaptur intryganta | Mistrz Intryg | +1 Intryga. | 7 |
| 4 | Czapka tropiciela | Łowca Potworów | +1 do pierwszego testu przeciw bestii. | 7 |
| 5 | Czapka uczonego | Wielki Mędrzec | +1 Nauka. | 7 |
| 6 | Kapelusz kupca | Mistrz Gildii | +1 Handel. | 7 |
| 7 | Opaska posła | Srebrny Język | +1 Dyplomacja. | 7 |
| 8 | Wieniec pieśniarza | Mistrz Kultury | +1 Kultura. | 7 |
| 9 | Kaptur podróżnika | Wędrowiec | +1 do ucieczki. | 6 |
| 10 | Czepek medyka | Uzdrowiciel | Pierwszy efekt leczenia HP w turze leczy +1 HP. | 8 |

## Rzadkie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 11 | Przyłbica furii | Krwawy Berserker | Mając Ranę: +1 trafienia; przy połowie HP lub mniej dodatkowo +1 obrażenie. | 17 |
| 12 | Hełm gwardzisty | Żelazny Strażnik | +1 KP; pierwszy atak przeciwnika ma -1 trafienia. | 17 |
| 13 | Maska bez twarzy | Cień | +1 Intryga i +1 Dyplomacja. | 16 |
| 14 | Hełm wielkiego łowcy | Łowca Potworów | +1 trafienia przeciw bestiom i +1 do ucieczki. | 16 |
| 15 | Diadem badacza | Wielki Mędrzec | +2 Nauka. | 14 |
| 16 | Korona rachmistrza | Mistrz Gildii | +1 Handel; pierwsza sprzedaż podczas wizyty +1 moneta. | 15 |
| 17 | Diadem dworski | Srebrny Język | +2 Dyplomacja. | 14 |
| 18 | Maska aktora | Mistrz Kultury | +1 Kultura; pierwszy test Kultury w turze ma +1. | 15 |
| 19 | Hełm chorążego | Dowódca Kompanii | Gdy masz aktywnego Pomocnika: +1 do statystyki, którą ten Pomocnik wspiera w danym teście. | 16 |
| 20 | Opaska wróżbity | Tkacz Losu | Raz na turę przerzut naturalnego 1 poza walką. | 18 |

## Epickie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 21 | Rogaty Hełm Krwi | Krwawy Berserker | Mając Ranę: +1 trafienia i +1 obrażenie; -1 Dyplomacja. | 24 |
| 22 | Wielka Przyłbica Bastionu | Żelazny Strażnik | +2 KP; pierwszy krytyk przeciwnika w walce zadaje zwykłe, a nie podwójne obrażenia. | 27 |
| 23 | Maska Nocnego Księcia | Cień | +2 Intryga; pierwszy atak przeciwnika ma -2 trafienia. | 26 |
| 24 | Korona Łowów | Łowca Potworów | +1 Walka; przeciw bossom dodatkowo +1 trafienia i +1 obrażenie. | 26 |
| 25 | Diadem Gwiazd | Runiczny Uczony | +2 Nauka; raz na turę przerzut Nauki. | 26 |
| 26 | Korona Złotej Gildii | Złoty Kupiec | +2 Handel; pierwszy zakup podczas wizyty -1 moneta. | 25 |
| 27 | Korona Królewskiego Posła | Królewski Dyplomata | +2 Dyplomacja i +1 Kultura. | 25 |
| 28 | Wieniec Wielkiego Barda | Kronikarz | +2 Kultura; pierwszy test Questa Kultury w turze można przerzucić. | 26 |
| 29 | Hełm Dowódcy Pięciu | Dowódca Kompanii | Przy 3+ Pomocnikach: +1 Walka i +1 KP. | 25 |
| 30 | Maska Przeznaczenia | Tkacz Losu | Raz na turę po rzucie testu poza walką możesz użyć wyniku 10 zamiast wyniku kości. | 28 |

## Legendarne — 10

| # | Nazwa | Archetyp | Efekt | Dostępność |
|---:|---|---|---|---|
| 31 | Korona Krwawego Króla | Krwawy Berserker | Każda Rana daje +1 do pierwszego ataku, maks. +3; naturalne 20 zadaje +1 dodatkowe obrażenie. | Legendarny loot/quest |
| 32 | Hełm Ostatniego Bastionu | Żelazny Strażnik | +2 KP; raz na walkę po rzucie przeciwnika możesz anulować jego trafienie. | Legendarny loot/quest |
| 33 | Twarz Nocy | Mistrz Intryg | +3 Intryga; pierwszy atak walki ma +3 trafienia. | Legendarny loot/quest |
| 34 | Korona Rogatego Łowcy | Łowca Potworów | +2 Walka przeciw bossom; przeciw bestiom naturalne 19–20 jest krytykiem. | Legendarny loot/quest |
| 35 | Korona Archimaga | Wielki Mędrzec | +3 Nauka; raz na turę przerzut testu Nauki lub artefaktu. | Legendarny loot/quest |
| 36 | Korona Złotego Króla | Mistrz Gildii | +3 Handel; pierwszy zakup -2, pierwsza sprzedaż +2 monety. | Legendarny loot/quest |
| 37 | Korona Sześciu Tronów | Srebrny Język | +2 Dyplomacja; na początku tury wybierz +1 Dyplomacja albo +1 Kultura do końca tury. | Legendarny loot/quest |
| 38 | Korona Tysiąca Opowieści | Mistrz Kultury | +3 Kultura; ukończenie questa daje +1 do następnego testu. | Legendarny loot/quest |
| 39 | Aureola Białego Zakonu | Uzdrowiciel | Leczenie Ran -1 moneta za Ranę; +2 maks. HP; jedzenie leczy +1 HP. | Legendarny loot/quest |
| 40 | Korona Złamanej Gwiazdy | Tkacz Losu | Raz na turę po zobaczeniu wyniku testu możesz go przerzucić albo użyć wyniku 10. | Legendarny loot/quest |

---

# BUTY — 40 kart

## Zwykłe — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 1 | Buty wojownika | Mistrz Oręża | Po wejściu do walki pierwszy atak ma +1. | 7 |
| 2 | Ciężkie buty strażnika | Żelazny Strażnik | +1 KP przeciw pierwszemu atakowi przeciwnika. | 7 |
| 3 | Buty rzeźnika | Krwawy Berserker | Mając Ranę: +1 do pierwszego ataku po ruchu. | 8 |
| 4 | Buty przemytnika | Mistrz Intryg | +1 Intryga. | 7 |
| 5 | Buty myśliwego | Łowca Potworów | +1 do ucieczki lub pościgu związanego z bestiami. | 7 |
| 6 | Sandały badacza | Wielki Mędrzec | +1 Nauka podczas testów związanych z podróżą i ruinami. | 8 |
| 7 | Buty karawaniarza | Mistrz Gildii | +1 Handel w Questach Ekonomicznych. | 7 |
| 8 | Buty posła | Srebrny Język | +1 Dyplomacja w pierwszym teście po dotarciu do nowej lokacji. | 8 |
| 9 | Buty artysty | Mistrz Kultury | +1 Kultura w mieście lub podczas wydarzenia kulturowego. | 7 |
| 10 | Buty sanitariusza | Uzdrowiciel | Po wejściu do lokacji pierwsze leczenie Ran kosztuje o 1 monetę mniej. | 8 |

## Rzadkie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 11 | Kroki berserkera | Krwawy Berserker | Mając Ranę: +1 do ucieczki i +1 do pierwszego ataku w walce. | 16 |
| 12 | Buty straży | Żelazny Strażnik | Po ruchu +1 KP przeciw pierwszemu atakowi przeciwnika w tej turze. | 14 |
| 13 | Bezgłośne buty | Cień | +1 Intryga i +1 do ucieczki. | 15 |
| 14 | Kroki tropiciela | Łowca Potworów | Pierwszy trudny teren -1 Akcja; +1 do pierwszego testu przeciw bestii. | 17 |
| 15 | Buty odkrywcy ruin | Runiczny Uczony | +1 Nauka; pierwszy górski/trudny heks w turze kosztuje o 1 Akcję mniej. | 17 |
| 16 | Buty kupieckiego gońca | Złoty Kupiec | +1 Handel; po pierwszym zakupie w turze kolejny łatwy ruch kosztuje o 1 Akcję mniej, min. 0. | 18 |
| 17 | Buty królewskiego kuriera | Królewski Dyplomata | +1 Dyplomacja; pierwszy test po wejściu do wymaganej lokacji questa ma +1. | 16 |
| 18 | Kroki wędrowca | Wędrowiec | Pierwszy trudny teren w turze kosztuje o 1 Akcję mniej. | 15 |
| 19 | Buty chorążego | Dowódca Kompanii | Z Pomocnikiem Przewodnikiem lub efektem podróżnym: +1 do testów ruchowych i ucieczki. | 14 |
| 20 | Buty szczęściarza | Tkacz Losu | Raz na turę przerzut próby ucieczki. | 15 |

## Epickie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 21 | Buty Krwawego Pościgu | Krwawy Berserker | Mając Ranę: pierwszy trudny teren ma koszt zmniejszony o 1; po ruchu +1 trafienia do pierwszego ataku. | 25 |
| 22 | Kroki Bastionu | Żelazny Strażnik | Po ruchu +2 KP przeciw pierwszemu atakowi przeciwnika. | 23 |
| 23 | Ślady Cienia | Cień | +2 Intryga; raz na turę przerzut próby ucieczki. | 25 |
| 24 | Buty Wielkiego Łowcy | Łowca Potworów | Pierwszy trudny teren -1 Akcja; przeciw bestiom +1 trafienia. | 25 |
| 25 | Sandały Kartografa Run | Runiczny Uczony | +2 Nauka podczas podróży/ruin; pierwszy trudny teren -1 Akcja. | 26 |
| 26 | Złote Buty Karawan | Złoty Kupiec | +2 Handel; pierwszy ruch po wykonaniu transakcji kosztuje o 1 Akcję mniej. | 26 |
| 27 | Kroki Ambasadora | Królewski Dyplomata | +2 Dyplomacja; pierwszy test w nowej lokacji ma +1. | 24 |
| 28 | Buty Pieśniarza Dróg | Kronikarz | +2 Kultura; po wejściu do miasta pierwszy test Kultury ma +1. | 24 |
| 29 | Sandały Niestrudzonego | Wędrowiec | Pierwsze dwa trudne tereny w turze kosztują po 1 Akcję mniej. | 27 |
| 30 | Kroki Przeznaczenia | Tkacz Losu | Raz na turę nieudany test ruchu lub ucieczki możesz potraktować jak wynik 10 na kości. | 27 |

## Legendarne — 10

| # | Nazwa | Archetyp | Efekt | Dostępność |
|---:|---|---|---|---|
| 31 | Krwawe Ostrogi | Krwawy Berserker | Mając Ranę: +1 trafienia po ruchu; pierwszy trudny teren w turze ma koszt zmniejszony o 1. | Legendarny loot/quest |
| 32 | Kroki Nieporuszonego | Żelazny Strażnik | Po ruchu +2 KP do pierwszego ataku przeciwnika przed twoją następną turą. | Legendarny loot/quest |
| 33 | Ślady Nigdzie | Cień | +2 Intryga; raz na turę po normalnym ruchu możesz wykonać dodatkowy ruch o 1 łatwy heks. | Legendarny loot/quest |
| 34 | Buty Polującego Księżyca | Łowca Potworów | Pierwszy trudny teren -1 Akcja; po wejściu na heks z bestią +2 do pierwszego ataku. | Legendarny loot/quest |
| 35 | Sandały Gwiezdnego Kartografa | Wielki Mędrzec | Pierwszy trudny teren zawsze kosztuje jak łatwy; +2 Nauka. | Legendarny loot/quest |
| 36 | Złote Kroki Imperium | Mistrz Gildii | +2 Handel; raz na turę po wykonaniu transakcji możesz wykonać dodatkowy ruch o 1 łatwy heks. | Legendarny loot/quest |
| 37 | Kroki Srebrnego Posła | Srebrny Język | +2 Dyplomacja; pierwsza podróż w turze do celu aktywnego Questa Dyplomacji kosztuje o 1 Akcję mniej. | Legendarny loot/quest |
| 38 | Buty Pieśni Świata | Mistrz Kultury | +2 Kultura; odwiedzenie nowej lokacji daje +1 do następnego testu w tej turze. | Legendarny loot/quest |
| 39 | Buty Pięciu Towarzyszy | Dowódca Kompanii | Przy 3+ Pomocnikach pierwszy trudny teren w turze kosztuje 1 Akcję. | Legendarny loot/quest |
| 40 | Buty Wędrowca Światów | Wędrowiec | Pierwsze dwa trudne tereny w turze nie zwiększają kosztu ruchu. | Legendarny loot/quest |

---

# RĘKAWICE — 40 kart

## Zwykłe — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 1 | Rękawice fechmistrza | Mistrz Oręża | +1 do pierwszego ataku w walce. | 7 |
| 2 | Karwasze strażnika | Żelazny Strażnik | +1 KP w pierwszej rundzie walki. | 7 |
| 3 | Rękawice rzeźnika | Krwawy Berserker | Mając Ranę: pierwsze trafienie w walce zadaje +1 obrażenie. | 8 |
| 4 | Rękawice złodzieja | Mistrz Intryg | +1 Intryga. | 7 |
| 5 | Rękawiczki skryby | Wielki Mędrzec | +1 Nauka. | 7 |
| 6 | Rękawice kupca | Mistrz Gildii | +1 Handel. | 7 |
| 7 | Rękawiczki negocjatora | Srebrny Język | +1 Dyplomacja. | 7 |
| 8 | Rękawice kronikarza | Mistrz Kultury | +1 Kultura. | 7 |
| 9 | Rękawice zielarza | Uzdrowiciel | Każdy efekt leczenia HP leczy +1 HP. | 8 |
| 10 | Rękawice przewodnika | Wędrowiec | +1 do prób ucieczki. | 6 |

## Rzadkie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 11 | Dłonie berserkera | Krwawy Berserker | Mając Ranę: +1 trafienia i +1 obrażenie pierwszego ataku. | 17 |
| 12 | Karwasze muru | Żelazny Strażnik | +1 KP; pierwszy atak przeciwnika ma -1 trafienia. | 17 |
| 13 | Rękawice szabrownika | Cień | +1 Intryga; ukończenie Questa Intrygi z nagrodą pieniężną daje +1 monetę. | 16 |
| 14 | Rękawice łucznika | Łowca Potworów | +1 trafienia; przeciw bestiom dodatkowo +1 trafienia. | 16 |
| 15 | Rękawice runiczne | Runiczny Uczony | +1 Nauka; pierwszy test artefaktu w turze ma +1. | 15 |
| 16 | Rękawice targowego księcia | Złoty Kupiec | +1 Handel; pierwsza sprzedaż podczas wizyty +1 moneta. | 15 |
| 17 | Rękawice dworskie | Królewski Dyplomata | +1 Dyplomacja i +1 Kultura. | 17 |
| 18 | Dłonie medyka | Uzdrowiciel | Leczenie Ran -1 moneta za Ranę; jedzenie leczy +1 HP. | 18 |
| 19 | Rękawice chorążego | Dowódca Kompanii | Z Pomocnikiem: +1 do statystyki wspieranej przez jego efekt w danym teście. | 15 |
| 20 | Rękawice hazardzisty | Tkacz Losu | Raz na turę przerzut naturalnego 1 w teście. | 18 |

## Epickie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 21 | Dłonie Krwawego Ostrza | Krwawy Berserker | Mając Ranę: +1 trafienia i +1 obrażenie; naturalne 20 zadaje +1 dodatkowe obrażenie. | 26 |
| 22 | Karwasze Twierdzy | Żelazny Strażnik | +2 KP w pierwszej rundzie; pierwsze otrzymane obrażenie w walce jest zmniejszone o 1. | 27 |
| 23 | Rękawice Nocnego Zabójcy | Cień | +2 Intryga; pierwszy atak w walce ma +2 trafienia. | 25 |
| 24 | Dłonie Pogromcy | Łowca Potworów | +1 trafienia i +1 obrażenie przeciw bestiom. | 23 |
| 25 | Rękawice Mistrza Run | Runiczny Uczony | +2 Nauka; raz na turę przerzut Nauki. | 26 |
| 26 | Złote Rękawice Gildii | Złoty Kupiec | +2 Handel; pierwszy zakup -1 moneta, pierwsza sprzedaż +1 moneta. | 27 |
| 27 | Rękawice Wielkiego Posła | Królewski Dyplomata | +2 Dyplomacja i +1 Kultura. | 25 |
| 28 | Dłonie Pieśni | Kronikarz | +2 Kultura; pierwszy test Questa Kultury w turze ma +1. | 24 |
| 29 | Rękawice Kapitana | Dowódca Kompanii | Z Pomocnikiem: +1 trafienia w walce i +1 do testu wspieranego przez Pomocnika. | 26 |
| 30 | Dłonie Przeznaczenia | Tkacz Losu | Raz na walkę możesz użyć wyniku 10 zamiast wyniku własnego rzutu ataku. | 28 |

## Legendarne — 10

| # | Nazwa | Archetyp | Efekt | Dostępność |
|---:|---|---|---|---|
| 31 | Dłonie Krwawego Boga | Krwawy Berserker | Mając Ranę: +1 trafienia i +1 obrażenie; naturalne 20 zadaje +1 dodatkowe obrażenie. | Legendarny loot/quest |
| 32 | Karwasze Wiecznego Bastionu | Żelazny Strażnik | +2 KP; raz na walkę redukuj obrażenia jednego trafienia do 0. | Legendarny loot/quest |
| 33 | Rękawice Bezimiennego | Mistrz Intryg | +3 Intryga; pierwszy atak walki uznaje naturalne 19 za krytyk. | Legendarny loot/quest |
| 34 | Dłonie Wielkiego Łowcy | Łowca Potworów | +2 do trafienia przeciw bossom; krytyk przeciw bestii zadaje +1 dodatkowe obrażenie. | Legendarny loot/quest |
| 35 | Rękawice Archirun | Wielki Mędrzec | +3 Nauka; raz na turę po rzucie Nauki wybierz przerzut albo +2 do wyniku. | Legendarny loot/quest |
| 36 | Złote Dłonie Imperatora | Mistrz Gildii | +3 Handel; pierwszy zakup -2, pierwsza sprzedaż +2 monety. | Legendarny loot/quest |
| 37 | Dłonie Srebrnego Języka | Srebrny Język | +2 Dyplomacja i +1 Kultura; raz na turę przerzut jednego z tych testów. | Legendarny loot/quest |
| 38 | Dłonie Białego Ojca | Uzdrowiciel | Leczenie Ran -1 moneta; leczenie HP +2; +1 maks. HP. | Legendarny loot/quest |
| 39 | Dłonie Pięciu Przysiąg | Dowódca Kompanii | Gdy Pomocnik daje premię liczbową do testu, zwiększ tę premię o dodatkowe +1. | Legendarny loot/quest |
| 40 | Dłonie Kości Świata | Tkacz Losu | Raz na turę po rzucie wybierz: przerzut albo użycie wyniku 10. | Legendarny loot/quest |

---

# AMULETY — 40 kart

## Zwykłe — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 1 | Kamień wojownika | Mistrz Oręża | +1 Walka przy pełnym HP. | 7 |
| 2 | Talizman ochrony | Żelazny Strażnik | +1 KP. | 8 |
| 3 | Oko szpiega | Mistrz Intryg | +1 Intryga. | 7 |
| 4 | Ząb wilka | Łowca Potworów | +1 do pierwszego testu lub ataku przeciw bestii. | 7 |
| 5 | Znak mędrca | Wielki Mędrzec | +1 Nauka. | 7 |
| 6 | Moneta gildii | Mistrz Gildii | +1 Handel. | 7 |
| 7 | Pieczęć posła | Srebrny Język | +1 Dyplomacja. | 7 |
| 8 | Medalion pieśni | Mistrz Kultury | +1 Kultura. | 7 |
| 9 | Znak pielgrzyma | Wędrowiec | +1 maks. HP i +1 do ucieczki. | 10 |
| 10 | Kamień zdrowia | Uzdrowiciel | +1 maks. HP. | 7 |

## Rzadkie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 11 | Krwawy rubin | Krwawy Berserker | Mając Ranę: +1 obrażenie w walce. | 13 |
| 12 | Kamień Stalowego Serca | Żelazny Strażnik | +1 KP i +1 maks. HP. | 17 |
| 13 | Oko Nocy | Cień | +1 Intryga; pierwszy test Intrygi po wejściu do lokacji ma +1. | 15 |
| 14 | Trofeum bestiobójcy | Łowca Potworów | +1 Walka przeciw bestiom i +1 maks. HP. | 16 |
| 15 | Kamień pamięci | Runiczny Uczony | +1 Nauka; raz na turę przerzut naturalnego 1 w teście Nauki. | 16 |
| 16 | Amulet sześciu monet | Złoty Kupiec | +1 Handel; pierwszy zakup podczas wizyty -1 moneta. | 15 |
| 17 | Pieczęć dworu | Królewski Dyplomata | +1 Dyplomacja i +1 Kultura. | 17 |
| 18 | Medalion wielkiej pieśni | Kronikarz | +1 Kultura; pierwszy test Questa Kultury w turze ma +1. | 15 |
| 19 | Serce drużyny | Dowódca Kompanii | Przy 3+ Pomocnikach +1 maks. HP. | 14 |
| 20 | Amulet medyka | Uzdrowiciel | Leczenie Ran kosztuje o 1 monetę mniej za Ranę. | 15 |

## Epickie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 21 | Serce Krwawego Wilka | Krwawy Berserker | Mając Ranę: +1 trafienia i +1 obrażenie; +1 maks. HP. | 26 |
| 22 | Serce Bastionu | Żelazny Strażnik | +2 KP i +1 maks. HP. | 26 |
| 23 | Talizman Cienia | Cień | +2 Intryga i +1 do ucieczki. | 23 |
| 24 | Oko Wielkiego Łowcy | Łowca Potworów | +1 Walka; przeciw bossom dodatkowo +1 trafienia i +1 obrażenie. | 26 |
| 25 | Oko Wyroczni | Runiczny Uczony | +2 Nauka; raz na turę przerzut testu Nauki. | 28 |
| 26 | Złote Serce Kupca | Złoty Kupiec | +2 Handel; pierwszy zakup -1, pierwsza sprzedaż +1 monetę. | 27 |
| 27 | Pieczęć Królewskiego Dworu | Królewski Dyplomata | +2 Dyplomacja i +1 Kultura. | 25 |
| 28 | Serce Opowieści | Kronikarz | +2 Kultura; pierwszy test aktywnego questa w turze ma +1. | 24 |
| 29 | Serce Podróżnika | Wędrowiec | +2 maks. HP; pierwszy trudny teren w turze -1 Akcja. | 26 |
| 30 | Oko Przeznaczenia | Tkacz Losu | Raz na turę przerzut dowolnego testu poza walką. | 28 |

## Legendarne — 10

| # | Nazwa | Archetyp | Efekt | Dostępność |
|---:|---|---|---|---|
| 31 | Serce Krwawego Boga | Krwawy Berserker | Mając Ranę: +1 trafienia i +1 obrażenie; raz na walkę naturalne 19 traktujesz jak krytyk. | Legendarny loot/quest |
| 32 | Serce Nieugiętego | Żelazny Strażnik | +2 KP i +2 maks. HP; raz na walkę zamiast spaść do 0 HP pozostajesz z 1 HP. | Legendarny loot/quest |
| 33 | Oko Bezksiężycowej Nocy | Mistrz Intryg | +3 Intryga; pierwszy atak przeciwnika ma -2 trafienia. | Legendarny loot/quest |
| 34 | Kieł Prastarego Smoka | Łowca Potworów | +2 Walka przeciw bossom; +2 obrażenia przeciw legendarnym przeciwnikom. | Legendarny loot/quest |
| 35 | Gwiazda Artium | Wielki Mędrzec | +3 Nauka; raz na turę możesz użyć wyniku 10 zamiast rzutu Nauki. | Legendarny loot/quest |
| 36 | Serce Złotego Imperium | Mistrz Gildii | +3 Handel; pierwszy zakup -2, pierwsza sprzedaż +2 monety. | Legendarny loot/quest |
| 37 | Pieczęć Sześciu Królestw | Srebrny Język | +3 Dyplomacja; raz na turę przerzut testu Dyplomacji. | Legendarny loot/quest |
| 38 | Pieśń Zamknięta w Krysztale | Mistrz Kultury | +3 Kultura; po ukończeniu questa +1 do następnego testu. | Legendarny loot/quest |
| 39 | Serce Białego Boga | Uzdrowiciel | +3 maks. HP; leczenie Ran -1 moneta; efekty leczenia HP leczą +2 HP. | Legendarny loot/quest |
| 40 | Złamane Serce Losu | Tkacz Losu | Raz na turę po nieudanym teście możesz stracić 1 HP i przerzucić test. | Legendarny loot/quest |

---

# PIERŚCIENIE — 40 kart

Bohater ma dwa sloty pierścieni. Oba korzystają z tej samej puli 40 kart.

## Zwykłe — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 1 | Pierścień wojownika | Mistrz Oręża | +1 Walka. | 7 |
| 2 | Pierścień strażnika | Żelazny Strażnik | +1 KP. | 8 |
| 3 | Pierścień intryganta | Mistrz Intryg | +1 Intryga. | 7 |
| 4 | Pierścień łowcy | Łowca Potworów | +1 do pierwszego testu lub ataku przeciw bestii. | 7 |
| 5 | Pierścień uczonego | Wielki Mędrzec | +1 Nauka. | 7 |
| 6 | Pierścień kupiecki | Mistrz Gildii | +1 Handel. | 7 |
| 7 | Pierścień dyplomaty | Srebrny Język | +1 Dyplomacja. | 7 |
| 8 | Pierścień opowieści | Mistrz Kultury | +1 Kultura. | 7 |
| 9 | Pierścień podróżnika | Wędrowiec | +1 do ucieczki. | 6 |
| 10 | Pierścień uzdrowiciela | Uzdrowiciel | Efekty leczenia HP leczą +1 HP. | 8 |

## Rzadkie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 11 | Pierścień krwi | Krwawy Berserker | Mając Ranę: +1 obrażenie. | 13 |
| 12 | Pierścień tarczy | Żelazny Strażnik | +1 KP; pierwszy atak przeciwnika ma -1 trafienia. | 17 |
| 13 | Pierścień szeptów | Cień | +1 Intryga; pierwszy test Questa Intrygi w turze ma +1. | 16 |
| 14 | Pierścień pełnego księżyca | Łowca Potworów | Przy pełnym HP: +1 trafienia i +1 KP. | 17 |
| 15 | Pierścień run | Runiczny Uczony | +1 Nauka; raz na turę przerzut naturalnego 1 w teście Nauki. | 16 |
| 16 | Pierścień złotego szlaku | Złoty Kupiec | +1 Handel; pierwsza sprzedaż podczas wizyty +1 moneta. | 15 |
| 17 | Pierścień ambasadora | Królewski Dyplomata | +1 Dyplomacja i +1 Kultura. | 17 |
| 18 | Pierścień pieśni | Kronikarz | +1 Kultura; pierwszy test Questa Kultury w turze ma +1. | 15 |
| 19 | Pierścień kompanii | Dowódca Kompanii | Przy 3+ Pomocnikach +1 do testu wykonywanego z pomocą Pomocnika. | 15 |
| 20 | Pierścień fortuny | Tkacz Losu | Raz na turę przerzut naturalnego 1. | 18 |

## Epickie — 10

| # | Nazwa | Archetyp | Efekt | Cena |
|---:|---|---|---|---:|
| 21 | Pierścień Krwawego Ostrza | Krwawy Berserker | Mając Ranę: +1 trafienia i +1 obrażenie. | 23 |
| 22 | Pierścień Ocalenia | Żelazny Strażnik | +1 KP; raz na walkę anuluj jedno trafienie przeciwnika. | 27 |
| 23 | Pierścień Samotnego Wilka | Cień | Jeśli nie masz Pomocnika: +1 Walka i +2 Intryga. | 25 |
| 24 | Pierścień Wielkiego Łowcy | Łowca Potworów | +1 Walka; przeciw bestiom dodatkowo +1 trafienia i +1 obrażenie. | 26 |
| 25 | Pierścień Sześciu Run | Runiczny Uczony | +2 Nauka; raz na turę przerzut Nauki. | 26 |
| 26 | Pierścień Bogacza | Złoty Kupiec | Przy 15+ monetach: +2 Handel i +1 KP. | 25 |
| 27 | Pierścień Królewskiej Pieczęci | Królewski Dyplomata | +2 Dyplomacja i +1 Kultura. | 24 |
| 28 | Pierścień Kronik | Kronikarz | +2 Kultura; raz na turę możesz przerzucić test aktywnego questa. | 27 |
| 29 | Pierścień Pięciu Towarzyszy | Dowódca Kompanii | Przy 3+ Pomocnikach: +1 Walka i +1 do testów wspieranych przez Pomocnika. | 25 |
| 30 | Pierścień Drugiej Szansy | Tkacz Losu | Raz na turę przerzut dowolnego nieudanego testu. | 28 |

## Legendarne — 10

| # | Nazwa | Archetyp | Efekt | Dostępność |
|---:|---|---|---|---|
| 31 | Pierścień Czterech Ran | Krwawy Berserker | Każda Rana daje +1 do pierwszego ataku, maks. +3; przy 3 Ranach +1 obrażenie. | Legendarny loot/quest |
| 32 | Pierścień Wiecznego Strażnika | Żelazny Strażnik | +2 KP; pierwsze otrzymane trafienie każdej walki zadaje o 1 mniej obrażenia. | Legendarny loot/quest |
| 33 | Pierścień Pustki | Mistrz Intryg | +2 Intryga; raz na walkę wymuś przerzut udanego ataku przeciwnika. | Legendarny loot/quest |
| 34 | Pierścień Łowcy Legend | Łowca Potworów | Przeciw bossom +2 trafienia i +2 obrażenia; naturalne 20 zadaje +1 dodatkowe obrażenie. | Legendarny loot/quest |
| 35 | Pierścień Mędrca Gwiazd | Wielki Mędrzec | +3 Nauka; raz na turę po rzucie testu Nauki możesz dodać +3 do wyniku. | Legendarny loot/quest |
| 36 | Pierścień Złotego Króla | Mistrz Gildii | +3 Handel; pierwszy zakup -2, pierwsza sprzedaż +2 monety. | Legendarny loot/quest |
| 37 | Pierścień Pierwszego Ambasadora | Srebrny Język | +3 Dyplomacja; raz na turę przerzut Dyplomacji lub Kultury. | Legendarny loot/quest |
| 38 | Pierścień Wiecznej Opowieści | Mistrz Kultury | +3 Kultura; po ukończeniu questa +2 do następnego testu. | Legendarny loot/quest |
| 39 | Pierścień Białej Gwiazdy | Uzdrowiciel | Leczenie Ran -1 moneta; +2 maks. HP; raz na turę pierwszy efekt leczenia HP leczy +2 dodatkowe HP. | Legendarny loot/quest |
| 40 | Pierścień Chaosu | Tkacz Losu | Na początku tury rzuć k6; wynik wskazuje jedną z sześciu statystyk, która otrzymuje +2 do końca tury. | Legendarny loot/quest |

---

# Kontrola kompletności katalogu

| Kategoria | Zwykłe | Rzadkie | Epickie | Legendarne | Razem |
|---|---:|---:|---:|---:|---:|
| Broń | 10 | 10 | 10 | 10 | 40 |
| Zbroje | 10 | 10 | 10 | 10 | 40 |
| Hełmy | 10 | 10 | 10 | 10 | 40 |
| Buty | 10 | 10 | 10 | 10 | 40 |
| Rękawice | 10 | 10 | 10 | 10 | 40 |
| Amulety | 10 | 10 | 10 | 10 | 40 |
| Pierścienie | 10 | 10 | 10 | 10 | 40 |
| **Łącznie** | **70** | **70** | **70** | **70** | **280** |

## Kolejne decyzje do podjęcia

- [ ] Ustalić bonus **2 elementów** dla każdego z 18 archetypów.
- [ ] Ustalić bonus **4 elementów** dla każdego z 18 archetypów.
- [ ] Ustalić bonus **6 elementów** dla każdego z 18 archetypów.
- [ ] Po zatwierdzeniu bonusów setowych przeprowadzić osobny balans wartości przedmiotów względem systemu 2/4/6.
- [ ] Ustalić dokładną liczbę kopii każdej karty w taliach/źródłach dropu.
- [ ] Ustalić rozkład zwykłych, rzadkich i epickich kart na Poziomy Świata I–IV.
- [ ] Ustalić źródło każdej karty legendarnej: Quest Legendarny, boss, Zagrożenie, wydarzenie lub inne specjalne źródło.
- [ ] Wdrożyć katalog do danych gry i połączyć go ze sklepami, lootem, questami, ekranem bohatera i modalem szczegółów przedmiotu.

## Zasada nadrzędna

Ten dokument jest od momentu zatwierdzenia **obowiązującą listą projektową EQ**. Stare placeholdery i krótkie listy przedmiotów w kodzie nie są źródłem prawdy dla docelowego contentu. Silnik może nadal zawierać stare wpisy do czasu implementacji katalogu, ale przy dalszym projektowaniu należy korzystać z tej listy.
