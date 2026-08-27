# Rise & Glory — QUESTY FINAL

Ten plik jest źródłem prawdy dla Questów gotowych do implementacji.

Do `QUESTY_FINAL.md` trafia wyłącznie Quest, którego fabuła, etapy, warunki, porażki, przejścia, finały, nagrody i trwałe skutki są wystarczająco domknięte, aby przepisać go do `rg_content/quests_final.py` bez wymyślania mechaniki podczas kodowania.

## Zasada flag

Nie zapisujemy osobnej trwałej flagi za każdą drobną czynność.

Rozróżniamy:

- **stan tymczasowy Questa** — używany tylko podczas aktualnego Questa; po zakończeniu znika,
- **przedmiot/informację questową** — np. `Instrukcja Trolfa`; po zakończeniu domyślnie znika,
- **trwały wynik Questa** — zapisujemy tylko wtedy, gdy przyszła zawartość świata może go sprawdzać.

Domyślny standard trwałego wyniku:

`qXX_result = <nazwa_zakonczenia>`

Jedna taka wartość ma zastępować kilka osobnych flag typu `npc_zyje`, `dzwon_istnieje`, `bohater_zna_tajemnice`, jeśli wszystkie wynikają już jednoznacznie z osiągniętego zakończenia.

---

# QUEST 1 — Dzwon między nami

## Status

**GOTOWY DO KODOWANIA**

## Dane główne

**ID:** `dzwon_miedzy_nami`  
**Stały numer:** `1`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Miejsce rozpoczęcia:** Elarin  
**Dodatkowa lokacja:** Valdren  
**Handel przed rozpoczęciem:** TAK  
**Porzucenie:** TAK do momentu wejścia w etap finałowy  
**Limit czasu:** brak  
**Główne statystyki:** Dyplomacja, Nauka, Intryga  
**Wskazówka nagrody:** Złoto, ekwipunek lub wyjątkowy Towarzysz.

## Założenie fabularne

Nocami z okolic starego cmentarza w Elarin słychać bicie dzwonu. Mieszkańcy chcą, aby ktoś sprawił, że dzwon zamilknie.

Bohater może rozwiązać problem przez odkrycie mechanizmu dzwonu i jego pochodzenia albo przez poznanie człowieka, który nocami uruchamia dzwon.

---

# KARTA GŁÓWNA — ETAP 1

## Co dzieje się na cmentarzu?

### OPCJA 1A — Wypytaj mieszkańców

**Typ:** test  
**Statystyka:** Dyplomacja  
**Próg:** 12  
**Koszt:** 1 Akcja

**Sukces:** mieszkańcy wskazują starą kaplicę i dzwonnicę związaną z dawnym opiekunem cmentarza.

→ dobierz rozwinięcie **1A — Dzwonnica**.

**Porażka:** standardowa porażka Questa. Quest pozostaje aktywny i można ponowić próbę.

**Nat 1 / Nat 20:** zasady standardowe.

### OPCJA 1B — Zbadaj ślady na cmentarzu

**Typ:** test  
**Statystyka:** Nauka  
**Próg:** 10  
**Koszt:** 1 Akcja

**Sukces:** bohater zauważa nietypowy grób regularnie odwiedzany przez kogoś z Elarin. Świeże kwiaty, wosk i pozostawiane jedzenie prowadzą do rodziny dawnego opiekuna.

→ dobierz rozwinięcie **1B — Grób opiekuna**.

**Porażka:** standardowa porażka Questa. Quest pozostaje aktywny i można ponowić próbę.

**Nat 1 / Nat 20:** zasady standardowe.

---

# ROZWINIĘCIE 1A — Dzwonnica

Bohater dociera do starej kaplicy i pomieszczenia z dzwonem.

Dostępne są trzy niezależne działania.

## OPCJA 1A-1 — Przeszukaj okno

**Typ:** eksploracja / bez rzutu  
**Koszt:** 1 Akcja  
**Limit:** tylko 1 raz na Quest

Bohater odnajduje stare rzeczy opiekuna, ale podczas przeszukiwania wypada z okna pod wpływem niewidzialnej siły.

**Efekt:**
- +1 Rana,
- +4 Złota,
- +1 losowa Zbroja.

Po rozpatrzeniu bohater pozostaje na rozwinięciu **1A**.

Opcja zostaje trwale wyszarzona dla tego Questa. Nie tworzy trwałej flagi świata.

## OPCJA 1A-2 — Zablokuj mechanizm

**Typ:** koszt / bez rzutu  
**Koszt:** 1 Akcja  
**Zużywa:**
- 4 Drewna,
- 1 Wytrych.

Po opłaceniu kosztu mechanizm zostaje zatrzymany.

→ **FINAŁ A — Uciszony dzwon**.

## OPCJA 1A-3 — Przeszukaj zapasy opiekuna

**Typ:** eksploracja / bez rzutu  
**Koszt:** 1 Akcja  
**Limit:** tylko 1 raz na Quest

**Natychmiastowa nagroda:**
- +2 Drewna,
- +1 Żelazo,
- +3 Zioła lecznicze.

W notatkach bohater znajduje informację, że mechanizm dzwonu zbudował rzemieślnik z Valdren.

→ dobierz rozwinięcie **1C — Rzemieślnik z Valdren**.  
→ utwórz Znacznik Questa `1` w Valdren.

Opcja zostaje wyszarzona. Nie tworzy trwałej flagi świata.

---

# ROZWINIĘCIE 1C — Rzemieślnik z Valdren

Etap można rozpatrywać dopiero po fizycznym dotarciu bohatera do Valdren.

## OPCJA 1C-1 — Rozpytaj rzemieślników

**Statystyka:** Dyplomacja  
**Próg:** 11  
**Koszt:** 1 Akcja

**Sukces:** bohater odnajduje Trolfa, członka gildii, który przed laty montował dzwon.

→ przejdź do **Spotkania z Trolfem**.

**Porażka:** standardowa porażka Questa.

## OPCJA 1C-2 — Szukaj znaków gildii

**Statystyka:** Intryga  
**Próg:** 13  
**Koszt:** 1 Akcja

**Sukces:** bohater odnajduje Trolfa i dodatkowo odkrywa, że rzemieślnik szczególnie ceni stary metal oraz odzysk z porzuconych konstrukcji.

**Stan tymczasowy Questa:** `trolf_leverage = true`.

→ przejdź do **Spotkania z Trolfem**.

**Porażka:** standardowa porażka Questa.

`trolf_leverage` jest stanem aktualnego Questa, a nie flagą świata. Znika po zakończeniu Questa.

---

# SPOTKANIE Z TROLFEM

Trolf pamięta kaplicę i uważa, że dzwon jest wart więcej jako metal niż jako porzucona konstrukcja.

Etap jest punktem bez powrotu dla ścieżki Trolfa.

## OPCJA T1 — Pozwól Trolfowi zabrać dzwon

**Typ:** decyzja bez rzutu  
**Koszt:** 1 Akcja

Trolf wraz z ludźmi jedzie do Elarin, demontuje dzwon i zabiera go do Valdren.

→ **FINAŁ B — Dzwon Trolfa**.

## OPCJA T2 — Kup wiedzę o mechanizmie

**Typ:** płatność / bez rzutu  
**Koszt Akcji:** 1

**Zużywa:**
- 3 Złota normalnie,
- 2 Złota, jeśli `trolf_leverage = true`.

Bohater otrzymuje tymczasowy przedmiot questowy:

`Instrukcja Trolfa`

Następnie musi fizycznie wrócić do Elarin.

### Powrót do dzwonnicy

**Wymaga:** `Instrukcja Trolfa`  
**Koszt:** 1 Akcja  
**Rzut:** brak

Bohater zatrzymuje mechanizm bez zużywania 4 Drewna i Wytrycha.

→ **FINAŁ A — Uciszony dzwon**.

---

# ROZWINIĘCIE 1B — Grób opiekuna

Ślady prowadzą do **Eldana**, syna dawnego opiekuna cmentarza.

## OPCJA 1B-1 — Skłoń Eldana do rozmowy

**Statystyka:** Dyplomacja  
**Próg:** 11  
**Koszt:** 1 Akcja

**Sukces:** Eldan przyznaje, że nocami przychodzi do kaplicy i uruchamia dzwon, wspominając ojca. Obiecuje przestać, ale prosi, aby bohater nie ujawniał jego udziału mieszkańcom.

→ dobierz rozwinięcie **1D — Tajemnica Eldana**.

**Porażka:** standardowa porażka Questa. Eldan zamyka się w sobie, ale rozmowę można ponowić zgodnie z ogólnymi zasadami.

---

# ROZWINIĘCIE 1D — Tajemnica Eldana

Etap jest punktem bez powrotu dla ścieżki Eldana.

## OPCJA E1 — Zachowaj tajemnicę

**Typ:** decyzja bez rzutu  
**Koszt:** 1 Akcja

Eldan pozostaje w Elarin i dotrzymuje obietnicy, że nie będzie więcej uruchamiał dzwonu.

→ **FINAŁ C — Tajemnica Eldana**.

## OPCJA E2 — Wydaj Eldana

**Typ:** decyzja bez rzutu  
**Koszt:** 1 Akcja

Bohater informuje mieszkańców. Eldan zostaje wypędzony z Elarin.

→ **FINAŁ D — Wygnanie Eldana**.

---

# FINAŁY I NAGRODY

## FINAŁ A — Uciszony dzwon

**Nagroda:**
- 7 Złota,
- losowy Hełm,
- +2 Punkty Legendy.

**Trwały wynik:**

`q01_result = "dzwon_uciszony"`

**Znaczenie:** dzwon nadal znajduje się w Elarin, ale jego mechanizm został zatrzymany.

**Kronika:** Bohater uciszył stary dzwon w Elarin, pozostawiając go w kaplicy.

## FINAŁ B — Dzwon Trolfa

**Nagroda:**
- 9 Złota,
- 4 Wytrychy,
- 1 Krótki Miecz,
- +1 Punkt Legendy.

**Trwały wynik:**

`q01_result = "dzwon_zabrany"`

**Znaczenie:** Trolf zdemontował dzwon; nie znajduje się już w Elarin.

**Kronika:** Bohater pozwolił Trolfowi zabrać stary dzwon z Elarin.

## FINAŁ C — Tajemnica Eldana

**Nagroda:**
- 11 Złota,
- Towarzysz **Bran**,
- +1 Punkt Legendy.

**Bran — Duchowość:** +1 do dowolnego rzutu, maksymalnie 2 razy na rundę Gracza.

Obecność Brana jest przechowywana przez normalny system Towarzyszy i nie wymaga osobnej flagi.

**Trwały wynik:**

`q01_result = "tajemnica_eldana"`

**Znaczenie:** Eldan pozostał w Elarin, bohater zachował jego tajemnicę, a dzwon przestał być uruchamiany.

**Kronika:** Bohater zachował tajemnicę Eldana i zakończył nocne bicie dzwonu bez wydawania go mieszkańcom.

## FINAŁ D — Wygnanie Eldana

**Nagroda:**
- 14 Złota,
- losowy Hełm,
- losowy Pierścień,
- +2 Punkty Legendy.

**Trwały wynik:**

`q01_result = "eldan_wygnany"`

**Znaczenie:** Eldan został wypędzony z Elarin po ujawnieniu prawdy przez bohatera.

Nie zapisujemy osobnej flagi `Eldan pamięta bohatera` — przyszły Quest może wywnioskować to bezpośrednio z `q01_result = "eldan_wygnany"`.

**Kronika:** Bohater ujawnił mieszkańcom prawdę o nocnym dzwonie, doprowadzając do wygnania Eldana.

---

# Minimalny stan implementacyjny Questa 1

## Trwałe dane po zakończeniu

Tylko:

`q01_result`

z jedną z wartości:

- `dzwon_uciszony`,
- `dzwon_zabrany`,
- `tajemnica_eldana`,
- `eldan_wygnany`.

## Dane tymczasowe podczas Questa

Mogą istnieć wyłącznie w runtime aktywnego Questa:

- wykorzystanie opcji `Przeszukaj okno`,
- wykorzystanie opcji `Przeszukaj zapasy`,
- `trolf_leverage`,
- przedmiot questowy `Instrukcja Trolfa`,
- odkryte rozwinięcia,
- aktywny Znacznik Questa w Valdren,
- liczba porażek,
- wykorzystanie `Przygotuj się`.

Nie trafiają do trwałych flag świata po zakończeniu.

## Sprzątanie po zakończeniu

Po każdym finale system:

1. usuwa Znaczniki Questa `1`,
2. usuwa `Instrukcję Trolfa`, jeśli nadal istnieje,
3. usuwa tymczasowy stan `trolf_leverage`,
4. zwraca odkryte karty rozwinięć do puli,
5. zapisuje tylko osiągnięte zakończenie i `q01_result`,
6. dodaje odpowiedni wpis do Kroniki.

---

# Standard skrótowy dla Questów 2–23

Questy 2–23 są zapisane w formie produkcyjnej, ale przed zakodowaniem wymagają akceptacji projektowej oraz wpisania finalnych wartości nagród przez właściciela projektu.

Jeżeli przy opcji nie zapisano inaczej:

- koszt próby = **1 Akcja**,
- porażka = **standardowa porażka Questa**, możliwość ponowienia,
- Nat 1 / Nat 20 = zasady standardowe,
- `Przygotuj się` = zgodnie ze wspólnym silnikiem,
- piąta porażka = przegranie Questa,
- odkryte informacje pomocnicze są stanem tymczasowym i znikają po zakończeniu,
- po finale usuwane są wszystkie Znaczniki i przedmioty questowe,
- trwałym stanem jest przede wszystkim pojedyncze `qXX_result`,
- nagrody oznaczone `DO USTALENIA` nie są wymyślane podczas kodowania — muszą zostać zatwierdzone przed implementacją.

---

# QUEST 2 — Pomocnik kata

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `pomocnik_kata`  
**Stały numer:** `2`  
**Poziom Świata:** I  
**Długość:** Długi  
**Unikalny:** TAK  
**Start:** Valdren  
**Statystyki:** Dyplomacja, Intryga, Nauka  
**Limit czasu:** 3 własne tury od pierwszej wykonanej akcji Questa; po czasie egzekucja odbywa się bez bohatera i Quest zostaje przegrany.  
**Wskazówka nagrody:** Złoto, Legenda, wpływ na los Orena i Mardeka.

## Założenie

Kat Garran potrzebuje pomocnika przy egzekucji ośmiu skazańców. Ósmy, księgowy **Oren Veld**, został dopisany do listy po odkryciu, że urzędnik **Mardek Voss** kradnie pieniądze z podatków.

## ETAP 1 — Oferta Garrana

- **Przyjmij pracę** — bez rzutu → rozwinięcie **2A — Szafot**.
- **Dyplomacja 11 — wypytaj Garrana** → odkryj, że ósme nazwisko dopisano później; stan `podejrzenie_listy` → **2A**.
- **Intryga 13 — obejrzyj dokumenty** → odkryj inny atrament i późniejszy podpis; stan `lista_zmieniona` → **2B — Trop korupcji**.

## ROZWINIĘCIE 2A — Szafot

Oren próbuje zwrócić uwagę bohatera.

- **Dyplomacja 12 — porozmawiaj z Orenem** → poznaj historię ksiąg podatkowych i nazwisko Mardeka; `zeznanie_orena` → **2B**.
- **Intryga 12 — przeszukaj rzeczy Orena** → znajdź fragment księgi rachunkowej; `ksiega_orena` → **2B**.
- **Zignoruj Orena i wykonuj polecenia** — bez rzutu → odblokowuje natychmiast **FINAŁ A**.

## ROZWINIĘCIE 2B — Trop korupcji

- **Nauka 11 — sprawdź pieczęcie i dokument** → twardy dowód zmiany listy; `dowod_falszerstwa`.
- **Intryga 14 — śledź posłańca** → dowód łapówki od Mardeka; `dowod_lapowki`.
- **Dyplomacja 12 — odnajdź kancelarię Mardeka** → przejdź do rozwinięcia **2C — Ostatnia godzina**.

Uzyskanie dowolnego twardego dowodu również odblokowuje **2C**.

## ROZWINIĘCIE 2C — Ostatnia godzina

Punkt bez powrotu.

### FINAŁ A — Ręce kata

**Opcja:** wykonaj umowę z Garranem. Bez rzutu. Wszystkich ośmiu skazańców, w tym Orena, stracono.

`q02_result = "rece_kata"`

**Nagroda:** DO USTALENIA. Profil: najwyższa zapłata od kata, niska Legenda.

**Kronika:** Bohater pomógł Garranowi przeprowadzić egzekucję ośmiu skazańców.

### FINAŁ B — Ósmy skazaniec

**Dyplomacja 14**, próg **12**, jeśli bohater posiada `dowod_falszerstwa` lub `dowod_lapowki`.

Sukces: egzekucja Orena zostaje oficjalnie wstrzymana, dowody trafiają do władz, a Mardek traci stanowisko i zostaje zatrzymany.

`q02_result = "osmy_skazaniec"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda, mało/średnio Złota, możliwa wdzięczność Orena.

**Kronika:** Bohater ujawnił manipulację listą skazańców i uratował Orena przed egzekucją.

### FINAŁ C — Brudny kompromis

**Intryga 15**, próg **13** z dowolnym twardym dowodem.

Sukces: bohater szantażuje Mardeka. Oren znika z listy i zostaje potajemnie wypuszczony, ale Mardek zachowuje stanowisko. Bohater otrzymuje zapłatę za milczenie.

`q02_result = "brudny_kompromis"`

**Nagroda:** DO USTALENIA. Profil: dużo Złota, niska Legenda.

**Kronika:** Bohater uratował Orena poprzez tajny układ z Mardekiem, pozostawiając skorumpowanego urzędnika u władzy.

**Runtime:** `podejrzenie_listy`, `lista_zmieniona`, `zeznanie_orena`, `ksiega_orena`, `dowod_falszerstwa`, `dowod_lapowki`.

---

# QUEST 3 — Ostatni spichlerz

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `ostatni_spichlerz`  
**Numer:** `3`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Thalwen  
**Statystyki:** Dyplomacja, Intryga, Handel, Nauka, Walka.

## ETAP 1 — Głód pod murami klasztoru

- **Dyplomacja 11 — porozmawiaj z mieszkańcami** → poznaj skalę głodu; `glod_potwierdzony`.
- **Dyplomacja 12 — porozmawiaj z przeorem** → poznaj argument o zimowej rezerwie; `stanowisko_klasztoru`.
- **Intryga 13 — zakradnij się do spichlerza** → poznaj realną ilość zboża; `realne_zapasy`.

Dowolny sukces → **3A — Kto kontroluje chleb**.

## ROZWINIĘCIE 3A — Kto kontroluje chleb

- **Handel 12 — prześledź rynek zboża** → odkryj, że Radomir wykupił dużą część lokalnego zboża i spekuluje ceną; `radomir_spekuluje`.
- **Nauka 11 — policz zimową rezerwę** → ustal, że klasztor może oddać część żywności bez ryzyka całkowitego wyczerpania zapasów; `mozliwy_podzial`.
- **Intryga 14 — sprawdź planowane transporty** → odkryj plan sprzedaży części zboża do Valdren; `sprzedaz_valdren`.

→ **3B — Noc pod spichlerzem**.

## ROZWINIĘCIE 3B — Noc pod spichlerzem

Punkt bez powrotu.

### FINAŁ A — Zamknięte bramy

**Dyplomacja 14** albo **Walka 13**. Bohater powstrzymuje tłum i broni spichlerza. Klasztor zachowuje zapasy, ale głód w Thalwen trwa.

`q03_result = "zamkniete_bramy"`

**Nagroda:** DO USTALENIA. Profil: zapłata klasztoru, umiarkowana/niska Legenda.

### FINAŁ B — Podzielony chleb

**Dyplomacja 14**, próg **12**, jeśli odkryto `mozliwy_podzial` albo `sprzedaz_valdren`. Mnisi wydają część zapasów mieszkańcom i zachowują realną rezerwę zimową.

`q03_result = "podzielony_chleb"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda, umiarkowane Złoto, pozytywny skutek dla Thalwen.

### FINAŁ C — Chleb zabrany siłą

Wybierz metodę: **Intryga 14**, **Walka 14** albo **Dyplomacja 15**. Mieszkańcy przejmują spichlerz. Głód zostaje chwilowo złagodzony, lecz klasztor traci rezerwę i obwinia bohatera.

`q03_result = "chleb_sila"`

**Nagroda:** DO USTALENIA. Profil: Legenda wśród mieszkańców, możliwy loot/zapasy, negatywna relacja z klasztorem wynikająca z finału.

**Runtime:** `glod_potwierdzony`, `stanowisko_klasztoru`, `realne_zapasy`, `radomir_spekuluje`, `mozliwy_podzial`, `sprzedaz_valdren`.

---

# QUEST 4 — Żelazo pod sianem

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `zelazo_pod_sianem`  
**Numer:** `4`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Norven  
**Dodatkowa lokacja:** Vargard  
**Statystyki:** Nauka, Dyplomacja, Intryga.

## ETAP 1 — Arsenał w stodole

- **Nauka 11** → większość broni jest stara i pochodzi z jednego okresu; `stara_bron`.
- **Dyplomacja 12** → gospodarz opowiada o dawnej wiejskiej straży; `historia_strazy`.
- **Intryga 13** → odkryj świeże sztuki broni oraz ślady regularnego wynoszenia uzbrojenia; `nowa_bron`.

Dowolny sukces → **4A — Seran i dawna straż**. Jeśli wybrano trop dokumentów, utwórz Znacznik `4` w Vargard.

## ROZWINIĘCIE 4A — Seran i dawna straż

- **Nauka 12 w Vargard** → stare rejestry potwierdzają legalny arsenał obronny Norven; `stare_dokumenty`.
- **Intryga 14 w Norven** → nocą odkryj szkolenia mieszkańców prowadzone przez Serana; `szkolenia_serana`.
- **Dyplomacja 13** → Seran przyznaje, że dokłada nową broń, bo uważa wieś za bezbronną; `motyw_serana`.

→ **4B — Los arsenału**.

## ROZWINIĘCIE 4B — Los arsenału

### FINAŁ A — Rozbrojona wieś

Bez rzutu: przekaż arsenał władzom Vargard. Seran zostaje zatrzymany, a Norven traci broń.

`q04_result = "rozbrojona_wies"`

**Nagroda:** DO USTALENIA. Profil: zapłata władz, umiarkowana Legenda.

### FINAŁ B — Straż Norven

**Dyplomacja 14**, próg **12** z `stare_dokumenty`. Władze uznają odbudowaną straż i legalizują kontrolowaną część arsenału.

`q04_result = "straz_norven"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda i trwały pozytywny skutek świata wynikający z wyniku.

### FINAŁ C — Broń w cieniu

**Intryga 15**, próg **13** z `szkolenia_serana`. Bohater pomaga ukryć najlepszą broń przed władzami. Seran kontynuuje potajemne szkolenia.

`q04_result = "tajny_arsenal"`

**Nagroda:** DO USTALENIA. Profil: możliwy ekwipunek/loot, niska Legenda, ryzykowny skutek świata.

---

# QUEST 5 — Ogród umarłego

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `ogrod_umartego`  
**Numer:** `5`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Eryndor  
**Dodatkowa lokacja:** Stary Ogród  
**Statystyki:** Nauka, Kultura, Intryga, Dyplomacja.

## ETAP 1 — Kwiaty na zwłokach

- **Nauka 11** → odkryj czarne nasiono zaszyte w ciele; `odkryto_nasiono`.
- **Kultura 12** → rozpoznaj symbole Strażników Ogrodów; `straznicy_ogrodow`.
- **Intryga 13** → znajdź mapę oraz wzmiankę o alchemiku Calvenie; `trop_calvena`.

Dowolny sukces → **5A — Nasiono**.

## ROZWINIĘCIE 5A — Nasiono

- **Nauka 13** → bezpiecznie wydobądź i zabezpiecz nasiono; przedmiot questowy `Nasiono Ogrodu`.
- **Kultura 13** → ustal, że zmarły miał zwrócić nasiono do Starego Ogrodu; utwórz Znacznik `5` w Starym Ogrodzie.
- **Dyplomacja 12** przy tropie Calvena → odnajdź alchemika i poznaj jego ofertę zakupu; `oferta_calvena`.

→ **5B — Los nasiona**.

## ROZWINIĘCIE 5B — Los nasiona

### FINAŁ A — Ostatnie kwiaty

**Nauka 12**. Bohater niszczy nasiono w sposób, który nie pozwala mu ponownie się zakorzenić. Stary Ogród pozostaje martwy.

`q05_result = "nasiono_zniszczone"`

**Nagroda:** DO USTALENIA. Profil: umiarkowana Legenda, materiały badawcze.

### FINAŁ B — Ogród powraca

Wymaga dotarcia do Znacznika w Starym Ogrodzie. **Nauka 13**, automatyczny sukces, jeśli wcześniej bezpiecznie wydobyto `Nasiono Ogrodu`. Ogród odżywa.

`q05_result = "ogrod_odrodzony"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda, dostęp/korzyść związana z odrodzonym Ogrodem.

### FINAŁ C — Cena nasienia

Wymaga `oferta_calvena` i `Nasiono Ogrodu`. Bez rzutu: sprzedaj nasiono Calvenowi.

`q05_result = "nasiono_sprzedane"`

**Nagroda:** DO USTALENIA. Profil: najwyższe Złoto, niska Legenda.

---

# QUEST 6 — Za zamkniętą bramą

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `za_zamknieta_brama`  
**Numer:** `6`  
**Poziom Świata:** I  
**Długość:** Długi  
**Unikalny:** TAK  
**Start:** Lirion  
**Statystyki:** Nauka, Dyplomacja, Intryga, Walka.

## ETAP 1 — Kordon

- **Dyplomacja 11** → dowódca Varlen pokazuje rozmieszczenie przypadków; `mapa_choroby`.
- **Nauka 12** → na ubraniu chorego odnajdź czarny pył i resztki zboża; `trop_zboza`.
- **Intryga 13** → odkryj, że Malven przekupuje straż i wyprowadza swoich ludzi; `malven_omija_kordon`.

→ **6A — Magazyn Pod Trzema Kołami**.

## ROZWINIĘCIE 6A — Źródło choroby

- **Nauka 13** → potwierdź skażone zboże jako źródło; `zrodlo_potwierdzone`.
- **Intryga 14** → dokumenty pokazują, że Malven znał pierwsze przypadki i je ukrywał; `dowod_malvena`.
- **Zniszcz skażone zboże** — bez rzutu, dostępne po `zrodlo_potwierdzone`; `zboze_zniszczone`.

→ **6B — Kryzys kwarantanny**.

## ROZWINIĘCIE 6B — Kryzys kwarantanny

### FINAŁ A — Żelazny kordon

**Dyplomacja 14** albo **Walka 13**. Pełna kwarantanna zostaje utrzymana. Choroba nie wychodzi poza dzielnicę, ale część zamkniętych ludzi umiera.

`q06_result = "zelazny_kordon"`

**Nagroda:** DO USTALENIA. Profil: umiarkowana Legenda, zapłata miasta.

### FINAŁ B — Lazaret Lirion

**Nauka 14**, próg **12**, jeśli `zboze_zniszczone`. Chorych izoluje się osobno, zdrowych wyprowadza pod obserwację, a miasto tworzy lazaret. Jeżeli zdobyto `dowod_malvena`, Malven zostaje zatrzymany w epilogu finału bez osobnej trwałej flagi.

`q06_result = "lazaret"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda i trwała poprawa zdolności miasta do reagowania na choroby.

### FINAŁ C — Otwarte bramy

**Dyplomacja 15** albo **Intryga 14**. Kordon zostaje przełamany. Mieszkańcy odzyskują wolność, lecz po kilku dniach choroba pojawia się w innych częściach miasta.

`q06_result = "otwarte_bramy"`

**Nagroda:** DO USTALENIA. Profil: krótki zysk/poparcie części mieszkańców, niska Legenda, negatywny skutek świata.

---

# QUEST 7 — Ziarno za murami

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `ziarno_za_murami`  
**Numer:** `7`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Valdren  
**Dodatkowa lokacja:** Durnhal jako planowany cel transportu  
**Statystyki:** Handel, Intryga, Dyplomacja, Nauka.

## ETAP 1 — Wozy przy bramie

- **Handel 11** → dokumenty potwierdzają zakup zboża przed zakazem i trzykrotnie wyższą cenę w Durnhal; `legalny_zakup`.
- **Nauka 12** → oceń miejskie rezerwy; `realne_zapasy`.
- **Intryga 13** → odkryj boczną bramę i system łapówek; `boczna_brama`.

→ **7A — Zakaz i jego beneficjenci**.

## ROZWINIĘCIE 7A — Zakaz i jego beneficjenci

- **Handel 13** → odkryj zaniżoną cenę skupu i prywatne magazyny części rajców; `niesprawiedliwy_skup`.
- **Intryga 14** → zdobądź księgę łapówek Gerolda Vane; `dowod_gerolda`.
- **Dyplomacja 12** → poznaj gotowość rady do częściowego kompromisu, jeśli ktoś udowodni bezpieczeństwo rezerw; `rada_negocjuje`.

→ **7B — Decyzja przy bramie**.

## ROZWINIĘCIE 7B — Decyzja przy bramie

### FINAŁ A — Zboże zostaje

Bez rzutu: poprzyj konfiskatę transportu. Valdren zwiększa rezerwy. Marven traci część majątku. Jeśli istnieje `dowod_gerolda`, urzędnik zostaje zatrzymany w epilogu.

`q07_result = "zboze_zostalo"`

**Nagroda:** DO USTALENIA. Profil: zapłata miasta, umiarkowana Legenda.

### FINAŁ B — Otwarty handel

**Handel 14**, próg **12** z `realne_zapasy`. Część zboża zostaje w Valdren, część legalnie jedzie do Durnhal, a miasto płaci uczciwszą cenę.

`q07_result = "otwarty_handel"`

**Nagroda:** DO USTALENIA. Profil: Legenda + relacje handlowe / Złoto w równowadze.

### FINAŁ C — Nocny transport

**Intryga 14**, próg **12** z `boczna_brama`. Bohater przeprowadza wozy poza miasto nocą.

`q07_result = "nocny_transport"`

**Nagroda:** DO USTALENIA. Profil: dużo Złota od Marvena, niska Legenda, ryzyko niedoboru w Valdren.

---

# QUEST 8 — Martwy pokład

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `martwy_poklad`  
**Numer:** `8`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Eryndor  
**Dodatkowe miejsca:** port, wybrzeże, stara latarnia  
**Statystyki:** Nauka, Intryga, Handel, Dyplomacja.

## ETAP 1 — Srebrna Mewa

- **Nauka 12** → objawy choroby i osad w kubkach wskazują na wspólne źródło; `podejrzenie_wody`.
- **Intryga 11** → ustal, że łódź ratunkowa została spuszczona świadomie; utwórz Znacznik `8` przy starej latarni.
- **Handel 11** → manifest pokazuje nieoficjalny zakup dodatkowych beczek wody; `dodatkowe_beczki`.

→ **8A — Załoga i woda**.

## ROZWINIĘCIE 8A — Załoga i woda

Po dotarciu do latarni bohater odnajduje siedmiu żywych marynarzy.

- **Nauka 13** → potwierdź zatrucie wodą zamiast zarazy; `zatrucie_potwierdzone`.
- **Intryga 13** → znak na beczkach i księgi dostaw prowadzą do Dalvena; `dowod_dalvena`.
- **Dyplomacja 13** przy `dowod_dalvena` → Dalven proponuje zapłatę za milczenie; `oferta_dalvena`.

→ **8B — Los statku**.

## ROZWINIĘCIE 8B — Los statku

### FINAŁ A — Ogień na wodzie

Bez rzutu: statek i ładunek zostają spalone jako potencjalne źródło zarazy.

`q08_result = "statek_spalony"`

**Nagroda:** DO USTALENIA. Profil: bezpieczeństwo portu, umiarkowana Legenda, utracony majątek.

### FINAŁ B — Srebrna Mewa wraca

**Nauka 14**, próg **11** z `zatrucie_potwierdzone`. Skażone zapasy są niszczone, statek oczyszczony, a załoga wraca. Jeśli istnieje `dowod_dalvena`, jego proceder zostaje zamknięty.

`q08_result = "mewa_uratowana"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda, możliwa nagroda od armatora/załogi.

### FINAŁ C — Cena ciszy

**Dyplomacja 14**, próg **12** z `oferta_dalvena`. Oficjalny raport mówi o przypadkowym zepsuciu wody, Dalven pozostaje bezkarny.

`q08_result = "dalven_ukryty"`

**Nagroda:** DO USTALENIA. Profil: wysokie Złoto, niska Legenda.

---

# QUEST 9 — Ostatnia woda

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `ostatnia_woda`  
**Numer:** `9`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Elarin  
**Dodatkowe miejsce:** pola i wzgórza powyżej wsi  
**Statystyki:** Dyplomacja, Nauka, Handel, Intryga.

## ETAP 1 — Bójka o strumień

- **Dyplomacja 11** → poznaj konflikt wokół tamy Rovenów; `spor_rovenow`.
- **Nauka 11** → ustal, że tama nie wyjaśnia całego spadku przepływu; `brakujaca_woda`.
- **Intryga 12** → znajdź stare prawo o maksymalnie jednej trzeciej przepływu; przedmiot questowy `Stare Prawo Wody`.

→ utwórz Znacznik `9` na wzgórzach i przejdź do **9A — Powyżej wsi**.

## ROZWINIĘCIE 9A — Powyżej wsi

Bohater odkrywa, że hodowca Bran Cord skierował część strumienia do zbiornika dla bydła, co uruchomiło cały łańcuch konfliktu.

- **Nauka 12** → dokładnie policz przepływ i możliwość stworzenia wspólnego systemu; `pelny_model_wody`.
- **Dyplomacja 12** → Bran przyznaje, że próbował ratować stado, nie szkodzić wsi; `motyw_brana`.
- **Handel 13** → ustal, że Rovenowie są gotowi zapłacić za oficjalne poparcie ich pierwszeństwa do wody; `oferta_rovenow`.

→ **9B — Podział wody**.

## ROZWINIĘCIE 9B — Podział wody

### FINAŁ A — Dawne koryto

**Dyplomacja 14**, próg **12** z `Stare Prawo Wody`. Kanał Brana zostaje ograniczony, tama Rovenów częściowo rozebrana, a przepływ wraca do starego podziału.

`q09_result = "dawne_koryto"`

**Nagroda:** DO USTALENIA. Profil: Legenda, niewielkie/średnie Złoto.

### FINAŁ B — Trzy kanały

**Zużywa:** 4 Drewna, 4 Kamienia, 2 Żelaza. Następnie **Nauka 14**, próg **12** z `pelny_model_wody`. Powstaje wspólny zbiornik i trzy kontrolowane kanały.

`q09_result = "trzy_kanaly"`

**Nagroda:** DO USTALENIA. Profil: najwyższa Legenda / trwała poprawa Elarin, mniejsza gotówka ze względu na koszt materiałów.

### FINAŁ C — Woda dla bogatszych

Wymaga `oferta_rovenow`. **Handel 13**. Rovenowie otrzymują uprzywilejowany dostęp do wody, drobni rolnicy tracą część zbiorów.

`q09_result = "woda_rovenow"`

**Nagroda:** DO USTALENIA. Profil: wysokie Złoto, niska Legenda.

---

# QUEST 10 — Fałszywy król

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `falszywy_krol`  
**Numer:** `10`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Lirion  
**Statystyki:** Handel, Intryga, Nauka, Dyplomacja.

## ETAP 1 — Monety Davena

- **Nauka 11** → nowe falsyfikaty wykonano innymi narzędziami niż stare monety Davena; `inne_narzedzia`.
- **Handel 12** → fałszywki pojawiają się przy dużych wypłatach miejskiego skarbca; `trop_skarbca`.
- **Intryga 12** → odnajdź zbiegłego Davena w starym młynie; `daven_odnaleziony`.

→ **10A — Mennica**.

## ROZWINIĘCIE 10A — Mennica

Daven wskazuje urzędnika **Olvara Renna**.

- **Intryga 14** → odnajdź magazyn z fałszywkami, prawdziwymi monetami i księgami; `magazyn_olvara`.
- **Nauka 13** → bilans kruszcu ujawnia brak prawdziwego metalu; `dowod_kruszcu`.
- **Dyplomacja 13** przy `daven_odnaleziony` → Daven zgadza się zeznawać przeciw Olvarowi; `wspolpraca_davena`.

→ **10B — Dwóch fałszerzy**.

## ROZWINIĘCIE 10B — Dwóch fałszerzy

### FINAŁ A — Dwóch fałszerzy

Wymaga `magazyn_olvara` albo `dowod_kruszcu`. Bez rzutu: oddaj Olvara i Davena władzom. Olvar odpowiada za nowy proceder, Daven wraca do więzienia za stare fałszerstwa.

`q10_result = "obaj_skazani"`

**Nagroda:** DO USTALENIA. Profil: Legenda + zapłata mennicy.

### FINAŁ B — Fałszerz mennicy

**Dyplomacja 14**, próg **12** z `wspolpraca_davena` oraz dowodem przeciw Olvarowi. Kara Davena zostaje zamieniona na nadzorowaną pracę przy wykrywaniu falsyfikatów.

`q10_result = "daven_mennica"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda, przyszła przychylność mennicy/Davena.

### FINAŁ C — Ostatnia fałszywa moneta

**Intryga 15**, próg **13** z `magazyn_olvara`. Daven zabiera część prawdziwych monet Olvara i ucieka, dzieląc się łupem z bohaterem.

`q10_result = "daven_uciekl"`

**Nagroda:** DO USTALENIA. Profil: najwyższe Złoto, niska Legenda.

---

# QUEST 11 — Dzwony na trwogę

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `dzwony_na_trwoge`  
**Numer:** `11`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Thalwen  
**Statystyki:** Kultura, Dyplomacja, Walka.

## ETAP 1 — Nocny alarm

- **Kultura 11** → odczytaj dawną sekwencję dzwonów: uzbrojeni ludzie nadchodzą z północy, jest ich ponad dwudziestu; `odczytano_sygnal`.
- **Dyplomacja 12** → zorganizuj barykady, schronienia i straże; `wies_gotowa`.
- **Walka 12** → rozbij zwiad i poznaj plan Harkela: podpalić stodoły, wywołać panikę i uderzyć główną drogą; `plan_najazdu`.

→ **11A — Harkel pod Thalwen**.

## ROZWINIĘCIE 11A — Harkel pod Thalwen

### FINAŁ A — Dzwony odpowiedziały

**Kultura 14**, próg **12** z `odczytano_sygnal`. Bohater poprawnie uruchamia stary system alarmowy. Odpowiadają dzwony i ognie sąsiednich osad. Harkel uznaje, że region jest już zmobilizowany i wycofuje ludzi.

`q11_result = "dzwony_odpowiedzialy"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda, trwały skutek kulturowo-obronny.

### FINAŁ B — Cena krwi

**Dyplomacja 14**, próg **12** z `wies_gotowa`. Bohater spotyka Harkela i przekonuje go, że łup nie zrekompensuje strat. Banda odchodzi, ale nadal istnieje.

`q11_result = "harkel_odszedl"`

**Nagroda:** DO USTALENIA. Profil: Legenda, brak łupu z walki, możliwa przyszła konsekwencja Harkela.

### FINAŁ C — Krew przed świtem

**Walka 14**, próg **12** z `plan_najazdu`. Thalwen urządza zasadzkę i rozbija bandę Harkela. Wieś ponosi rany, ale zagrożenie zostaje usunięte.

`q11_result = "banda_rozbita"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda + możliwy loot po bandzie.

---

# QUEST 12 — Prawo gościny

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `prawo_gosciny`  
**Numer:** `12`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Lirion, gospoda „Pod Białym Jeleniem”  
**Statystyki:** Kultura, Dyplomacja, Intryga.

## ETAP 1 — Czterech martwych gości

- **Kultura 11** → rozpoznaj rytuał Ostatniej Gościny; `ostatnia_goscina`.
- **Dyplomacja 12** → Herman Vell wspomina pieśń i pytanie o Prawo Pierwszego Stołu; `pierwszy_stol_trop`.
- **Intryga 12** → przy podróżnych znajdź znak białego jelenia pod siedmioma gwiazdami; `znak_domow_goscinnych`.

→ **12A — Domy Gościnne**.

## ROZWINIĘCIE 12A — Domy Gościnne

- **Kultura 13** → poznaj historię Domów Gościnnych i zasadę, że zmarłego pod dachem żegna gospodarz lub wyznaczona osoba; `prawo_gosciny_poznane`.
- **Kultura 12** przy `pierwszy_stol_trop` → poznaj Prawo Pierwszego Stołu; `pierwszy_stol_poznany`.
- **Przeszukaj stary pierwszy stół** — bez rzutu po poznaniu jednego z tropów → księga gości z czterema nazwiskami i piątym: Erem Aldor; utwórz trop do Erema.

→ **12B — Erem i Korzeń Drogi**.

## ROZWINIĘCIE 12B — Erem i Korzeń Drogi

- **Dyplomacja 11** → Erem przyznaje, że znalazł podróżnych martwych i tylko odprawił rytuał; `zeznanie_erema`.
- **Intryga 13** → w zamkniętej części gospody odnajdź stary gliniany dzban; `dzban_korzenia`.
- **Kultura 14** przy `dzban_korzenia` → rozpoznaj Korzeń Drogi: koncentrat, który wypito nierozcieńczony; `przyczyna_smierci`.

Punkt bez powrotu → finały.

### FINAŁ A — Ostatni goście

**Kultura 14**, próg **11**, jeśli znane są `zeznanie_erema` i `przyczyna_smierci`. Prawda zostaje ujawniona, Erem oczyszczony, zmarli pochowani zgodnie z tradycją.

`q12_result = "prawda_ujawniona"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda / kulturowa nagroda.

### FINAŁ B — Pierwszy stół

Dostępny po `pierwszy_stol_poznany`. **Dyplomacja 13**. Herman przywraca bezpieczną, współczesną wersję zwyczaju: jeden stół i prosty posiłek dziennie dla podróżnego bez pieniędzy.

`q12_result = "pierwszy_stol"`

**Nagroda:** DO USTALENIA. Profil: Legenda + przyszły punkt spotkań podróżnych i informatorów.

### FINAŁ C — Zapomniany zwyczaj

**Intryga 13**. Oficjalnie śmierć przypisuje się zepsutemu alkoholowi. Erem nie zostaje oskarżony, ale prawdziwa historia znika, a Herman płaci za dyskrecję.

`q12_result = "zwyczaj_zapomniany"`

**Nagroda:** DO USTALENIA. Profil: więcej Złota, mało Legendy.

---

# QUEST 13 — Złodziej złodzieja

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `zlodziej_zlodzieja`  
**Numer:** `13`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** trakt w pobliżu Valdren  
**Statystyki:** Intryga, Dyplomacja, Walka, Handel.

## ETAP 1 — Prośba Rogara

Bandyta Rogar chce odzyskać skrzynię skradzioną jego bandzie przez **Czarne Psy**.

- **Dyplomacja 11** → Rogar przyznaje, że w skrzyni są dokumenty kompromitujące jego paserów; `dokumenty_rogara`.
- **Intryga 12** → odtwórz pierwotny napad i odkryj, że skrzynia należała wcześniej do kupca Edrena Valla; zawiera też 12 Złota wypłat dla robotników; `prawdziwi_wlasciciele`.
- **Przyjmij zlecenie bez pytań** — bez rzutu.

→ utwórz Znacznik `13` przy kamieniołomie i przejdź do **13A — Czarne Psy**.

## ROZWINIĘCIE 13A — Czarne Psy

Wybierz sposób odzyskania całej skrzyni:

- **Intryga 13 — zakradnij się i ukradnij skrzynię** → `skrzynia_odzyskana`, dodatkowo `znana_kryjowka`.
- **Handel 14 — wykup skrzynię od Vareka** → zużyj **6 Złota** po sukcesie; `skrzynia_odzyskana`.
- **Walka 13 — zmusić bandę do porzucenia łupu** → `skrzynia_odzyskana`.

→ **13B — Do kogo należy łup**.

## ROZWINIĘCIE 13B — Do kogo należy łup

### FINAŁ A — Honor między złodziejami

Wymaga `skrzynia_odzyskana`. Bez rzutu: oddaj całość Rogarowi. Robotnicy tracą wypłaty, a jego sieć paserów pozostaje bezpieczna.

`q13_result = "rogar_odzyskal"`

**Nagroda:** DO USTALENIA. Profil: zapłata Rogara, niska Legenda.

### FINAŁ B — To, co skradzione

Dostępny po `prawdziwi_wlasciciele`. Bez rzutu: oddaj skrzynię Edrenowi i wypłaty robotnikom, a dokumenty przekaż władzom.

`q13_result = "lup_zwrocony"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda, mniejsze Złoto, Rogar staje się wrogi z samego wyniku finału.

### FINAŁ C — Trzeci złodziej

**Intryga 15**, próg **13** z `znana_kryjowka`. Bohater podrzuca fałszywe ślady tak, aby Rogar i Varek obwiniali siebie nawzajem, po czym zatrzymuje skrzynię.

`q13_result = "trzeci_zlodziej"`

**Nagroda:** DO USTALENIA. Profil: najwyższy loot/Złoto, bardzo niska Legenda, przyszły konflikt band.

---

# QUEST 14 — Pogrzeb przy drodze

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `pogrzeb_przy_drodze`  
**Numer:** `14`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** losowy przejezdny heks traktu Elarin–Artium  
**Statystyki:** Kultura, Dyplomacja, Intryga.

## ETAP 1 — Świadek Drogi

Bohater trafia na pogrzeb Sarvena należącego do **Ludzi Szarego Traktu**.

- **Kultura 11** → rozpoznaj lud i zwyczaj, według którego obcy podróżny staje się Świadkiem Drogi; `szary_trakt`.
- **Dyplomacja 11** → Mara opowiada o śmierci brata po obronie grupy przed wilkami; `historia_sarvena`.
- **Intryga 12** → rany są prawdziwe, ale grób leży dokładnie między starymi kamieniami granicznymi; `sporna_granica`.

→ **14A — Obrzęd i ziemia**.

## ROZWINIĘCIE 14A — Obrzęd i ziemia

- **Kultura 12** → poznaj znaczenie wody, chleba, pustej sakiewki, gwoździa i trzech kamieni oraz prawo Świadka do jednego pytania o zmarłego; `obrzad_drogi`.
- **Dyplomacja 13** po przybyciu właściciela Derrona → odkryj, że boi się precedensu i przyszłego cmentarza, nie samego pochówku; `obawa_derrora`.
- **Intryga 13** → jeden z kamieni granicznych został przesunięty, a pole Derrona weszło na dawny pas drogi; `przesuniety_kamien`.
- **Kultura 13** → stare Prawo Drogi pozwala pochować bezrolnego podróżnego na historycznym pasie traktu; `prawo_drogi`.

→ **14B — Los Sarvena**.

## ROZWINIĘCIE 14B — Los Sarvena

### FINAŁ A — Kamień przy drodze

**Kultura 14**, próg **12** z `przesuniety_kamien` lub `prawo_drogi`. Obrzęd odbywa się w całości, a bohater formalnie staje się Świadkiem Drogi.

`q14_result = "swiadek_drogi"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda / przychylność Ludzi Szarego Traktu.

### FINAŁ B — Dwa pożegnania

Dostępny po `obrzad_drogi`. **Dyplomacja 13**. Sarven zostaje pochowany przy trakcie według własnej tradycji, ale jego imię zostaje też wpisane do księgi zmarłych w pobliskiej kaplicy. Derron otrzymuje potwierdzenie, że nie powstanie tu cmentarz.

`q14_result = "dwa_pozegnania"`

**Nagroda:** DO USTALENIA. Profil: Legenda i dobra relacja obu stron.

### FINAŁ C — Droga bez końca

**Dyplomacja 14**. Mara zgadza się przenieść ciało na lokalny cmentarz. Konflikt o ziemię znika, ale obrzęd Szarego Traktu zostaje przerwany; trzeciego kamienia nie kładzie się przy grobie.

`q14_result = "obrzad_przerwany"`

**Nagroda:** DO USTALENIA. Profil: pragmatyczna nagroda, niska Legenda wśród wędrowców.

---

# QUEST 15 — Świeca, która nie gaśnie

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `swieca_ktora_nie_gasnie`  
**Numer:** `15`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Eryndor  
**Dodatkowa lokacja:** pracownia Alrena poza miastem  
**Główna statystyka:** Nauka  
**Dodatkowe:** Intryga, Handel.

## ETAP 1 — Niemożliwy płomień

- **Nauka 11 — zbadaj płomień** → nie potrzebuje zewnętrznego powietrza, pod wodą tworzy pęcherzyki; `samopodtrzymanie`.
- **Nauka 12 — zbadaj świecę** → knot łączy się z metalowym rdzeniem zawierającym proszek; `metalowy_rdzen`.
- **Intryga 11 — ustal pochodzenie** → przedmiot należał do badacza Alrena Vossa; utwórz Znacznik `15` przy jego pracowni.

→ **15A — Pracownia Alrena**.

## ROZWINIĘCIE 15A — Pracownia Alrena

- **Nauka 12 — odczytaj notatki** → prototyp może gwałtownie rozszczelnić się pod koniec reakcji; `ryzyko_eksplozji`.
- **Nauka 13 — rozbierz jeden z nieudanych rdzeni** → dwa składniki samodzielnie wytwarzają gaz i ciepło potrzebne płomieniowi; `zasada_reakcji`.

Jeśli bohater posiada oba odkrycia, finał naprawy jest znacznie łatwiejszy.

→ **15B — Los wynalazku**.

## ROZWINIĘCIE 15B — Los wynalazku

### FINAŁ A — Ostatni płomień

**Nauka 13**. Bohater bezpiecznie oddziela reagenty i niszczy prototyp.

`q15_result = "prototyp_zniszczony"`

**Nagroda:** DO USTALENIA. Profil: umiarkowana Legenda / materiały badawcze.

### FINAŁ B — Ogień Alrena

**Nauka 15**, próg **12**, jeśli znane są `ryzyko_eksplozji` i `zasada_reakcji`. Bohater dodaje zawór bezpieczeństwa i tworzy stabilną **Lampę Alrena**.

`q15_result = "lampa_alrena"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda + unikatowy przedmiot/technologia do przyszłych wypraw.

### FINAŁ C — Cena wynalazku

**Handel 13**. Teral Morn kupuje prototyp i notatki mimo ostrzeżenia o ryzyku. Technologia trafia do jego kopalń.

`q15_result = "prototyp_sprzedany"`

**Nagroda:** DO USTALENIA. Profil: najwyższe Złoto, niska Legenda, możliwa przyszła konsekwencja technologiczna.

---

# QUEST 16 — Fałszywy bohater

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `falszywy_bohater`  
**Numer:** `16`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** Norven  
**Statystyki:** Walka, Dyplomacja, Intryga, Kultura.

## ETAP 1 — Bohater Norven

Garrik przywozi łeb bestii i odbiera hołdy, lecz następnej nocy dochodzi do kolejnego ataku.

- **Kultura 11** → trofeum pochodzi od młodego skalnego drapieżcy; dorosłe osobniki w tym okresie żyją parami; `mlody_osobnik`.
- **Dyplomacja 12** → historia Garrika jest niespójna; `garrik_klamie`.
- **Intryga 11** → ślady nowego ataku należą do znacznie większej bestii; `dorosla_bestia`.

→ **16A — Prawda o trofeum**.

## ROZWINIĘCIE 16A — Prawda o trofeum

- **Intryga 13** → znajdź świadka potwierdzającego, że Garrik tylko dobił młode stworzenie uwięzione we wnykach; `dowod_oszustwa`.
- **Walka 12** → dotrzyj po śladach do rannego pasterza i bezpiecznie go wyprowadź; poznaj legowisko dorosłej bestii; `legowisko`.
- **Dyplomacja 13**, próg **11** z `dowod_oszustwa` → publicznie skonfrontuj Garrika; przyznaje się do kłamstwa; `garrik_przyznal`.

→ utwórz Znacznik `16` przy legowisku i przejdź do **16B — Prawdziwa bestia**.

## ROZWINIĘCIE 16B — Prawdziwa bestia

**Spotkanie bojowe:** `Dorosły skalny drapieżca` — bazowo 5 HP, KP 12, atak +2, obrażenia 1, skaluje się z Poziomem Świata.

### FINAŁ A — Bohater za drugim razem

**Dyplomacja 14**, próg **12** z `garrik_przyznal`. Garrik zgadza się iść z bohaterem. W walce daje **+1 do Walki** wyłącznie przeciw tej bestii. Po zwycięstwie prawda o pierwszym oszustwie wychodzi na jaw, ale Garrik rzeczywiście staje do walki i dostaje drugą szansę.

`q16_result = "garrik_odkupiony"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda / możliwe trofeum bestii.

### FINAŁ B — Prawdziwy bohater

Bohater walczy sam z Dorosłym skalnym drapieżcą. Po zwycięstwie Garrik zostaje publicznie zdemaskowany i wypędzony z Norven.

`q16_result = "bohater_prawdziwy"`

**Nagroda:** DO USTALENIA. Profil: najwyższa Legenda + loot z bestii.

### FINAŁ C — Legenda za złoto

Bohater zgadza się utrzymać oszustwo. Najpierw pokonuje bestię bez pomocy Garrika, potem wykonuje **Intrygę 13**, aby upozorować jego drugie zwycięstwo. Sukces → Garrik pozostaje bohaterem i dzieli się nagrodą. Porażka Intrygi → prawda wychodzi na jaw i Quest kończy się Finałem B bez dodatkowej zapłaty Garrika.

`q16_result = "legenda_garrika"`

**Nagroda:** DO USTALENIA. Profil: dużo Złota, mało Legendy.

---

# QUEST 17 — Miód wiedźmy

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `miod_wiedzmy`  
**Numer:** `17`  
**Poziom Świata:** I  
**Długość:** Krótki  
**Unikalny:** TAK  
**Start:** Elarin  
**Statystyki:** Walka, Handel.

## ETAP 1 — Zaczarowane ule

- **Walka 11** → podejdź mimo agresywnych pszczół i odkryj, że niosą czerwony pyłek z lasu; `trop_wrzosu`.
- **Handel 11** → oceń miód i odkryj, że zielarze oraz karczmarze zapłacą za niego wielokrotnie więcej niż za zwykły; `wartosc_miodu`.

→ **17A — Mira z lasu**.

## ROZWINIĘCIE 17A — Mira z lasu

Mira nie zaczarowała uli. Uprawia rzadki **krwawy wrzos**, który zwiększa agresję pszczół, ale nadaje miodowi wyjątkowe właściwości.

### FINAŁ A — Zwyczajny miód

**Walka 13**. Bohater przepędza oswojone wilki Miry i zmusza ją do opuszczenia okolicy. Wrzos znika, pszczoły uspokajają się, miód staje się zwyczajny.

`q17_result = "mira_wygnana"`

**Nagroda:** DO USTALENIA. Profil: zapłata Radana, umiarkowana Legenda.

### FINAŁ B — Czerwony miód

**Handel 14**, próg **12** z `wartosc_miodu`. Bohater tworzy umowę: Radan prowadzi ule, Mira kontroluje wrzos, a Elarin zaczyna produkować Czerwony Miód.

`q17_result = "czerwony_miod"`

**Nagroda:** DO USTALENIA. Profil: Legenda + trwały towar/zasób świata.

### FINAŁ C — Tani ul

**Handel 13**. Bohater wykorzystuje strach Radana i organizuje sprzedaż pasieki za zaniżoną cenę kupcowi, który następnie dogaduje się z Mirą.

`q17_result = "pasieka_sprzedana"`

**Nagroda:** DO USTALENIA. Profil: wysokie Złoto, niska Legenda.

---

# QUEST 18 — Trzy filiżanki

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `trzy_filazanki`  
**Numer:** `18`  
**Poziom Świata:** I  
**Długość:** Krótki  
**Unikalny:** TAK  
**Start:** losowy przejezdny heks traktu Valdren–Durnhal  
**Statystyki:** Kultura, Handel.

## ETAP 1 — Stół Trzech

- **Kultura 11** → rozpoznaj dawny zwyczaj kupiecki: sprzedający, kupujący i świadek piją z trzech filiżanek; `stol_trzech`.
- **Handel 11** → Olan wyjaśnia, że dwadzieścia lat temu kupiec zapłacił tylko połowę ceny ziemi, a dziś jego syn Darven przejeżdża traktem; `stary_dlug`.

→ **18A — Trzeci przy stole**.

## ROZWINIĘCIE 18A — Trzeci przy stole

Darven przybywa i odmawia odpowiedzialności za dług ojca.

### FINAŁ A — Trzecia filiżanka

**Kultura 13**. Bohater potwierdza ważność dawnego obyczaju i zostaje świadkiem. Darven spłaca stary dług.

`q18_result = "stary_dlug_splacony"`

**Nagroda:** DO USTALENIA. Profil: Legenda / wdzięczność Olana.

### FINAŁ B — Nowy rachunek

**Handel 14**. Bohater negocjuje nową umowę: część płatności teraz, reszta w towarach w kolejnych latach.

`q18_result = "nowa_umowa"`

**Nagroda:** DO USTALENIA. Profil: balans Złota i Legendy, możliwa przyszła relacja handlowa.

### FINAŁ C — Czwarty przy stole

**Handel 13**. Bohater wykupuje od Olana roszczenie poniżej jego wartości i sam staje się wierzycielem Darvena.

`q18_result = "roszczenie_bohatera"`

**Nagroda:** DO USTALENIA. Profil: najwyższy potencjał finansowy, niska Legenda.

---

# QUEST 19 — Samotny grób

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `samotny_grob`  
**Numer:** `19`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** losowy przejezdny heks w pobliżu Artium  
**Statystyki:** Kultura, Nauka, Walka.

## ETAP 1 — Własne imię

Na samotnym nagrobku pojawia się imię bohatera albo jednego z jego aktualnych Towarzyszy oraz dzisiejsza data.

- **Nauka 11** → litery nie zostały wykute; kamień zmienia strukturę pod wpływem czarnych korzeni; `czarne_korzenie`.
- **Kultura 11** → legenda o Grobach Oczekujących mówi, że grób nie przepowiada śmierci, lecz wybiera ofiarę; `legenda_grobu`.

→ **19A — Pod kamieniem**.

## ROZWINIĘCIE 19A — Pod kamieniem

- **Nauka 13** z `czarne_korzenie` → to podziemny organizm żywiący się szczątkami; nagrobek jest przynętą; `organizm_grobu`.
- **Kultura 13** z `legenda_grobu` → dokładny rytuał wymaga zastąpienia imienia żywego imieniem człowieka dawno zmarłego; `rytual_imienia`.

→ **19B — Zanim zajdzie słońce**.

## ROZWINIĘCIE 19B — Zanim zajdzie słońce

### FINAŁ A — Imię skreślone

**Kultura 14**, próg **12** z `rytual_imienia`. Imię bohatera znika, ale Grób Oczekujący pozostaje przy drodze i może kiedyś wybrać kogoś innego.

`q19_result = "imie_skreslone"`

**Nagroda:** DO USTALENIA. Profil: kulturowa wiedza / umiarkowana Legenda.

### FINAŁ B — Grób bez imienia

**Nauka 14**, próg **12** z `organizm_grobu`. Bohater odcina strukturę od powierzchni bez niszczenia rdzenia. Nagrobek przestaje wybierać podróżnych, a organizm można później badać.

`q19_result = "grob_unieszkodliwiony"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda / naukowy materiał lub wiedza.

### FINAŁ C — Pusty dół

**Walka 14**. Bohater schodzi pod grób i niszczy centralny rdzeń siłą. Każda porażka tego testu oprócz standardowego żetonu porażki daje **+1 Ranę**.

`q19_result = "rdzen_zniszczony"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda + możliwy loot z podziemnej komory.

---

# QUEST 20 — Kamień szczęścia

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `kamien_szczescia`  
**Numer:** `20`  
**Poziom Świata:** I  
**Długość:** Krótki  
**Unikalny:** TAK  
**Start:** Valdren  
**Statystyki:** Kultura, Handel.

## ETAP 1 — Szczęście za cztery monety

- **Kultura 11** → kamień jest dawnym symbolem Dnia Dobrego Losu, nigdy nie był magiczny; `prawdziwy_zwyczaj`.
- **Handel 12** → pierwsze zwycięstwa kupujących są ustawiane przez współpracujące stoiska; `mechanizm_oszustwa`.

→ **20A — Co sprzedać ludziom**.

## ROZWINIĘCIE 20A — Co sprzedać ludziom

### FINAŁ A — Zwykły kamień

Dostępny po `mechanizm_oszustwa`. **Handel 13**. Bohater publicznie pokazuje schemat sprzedaży i powiązanie Belda ze stoiskami. Proceder się kończy.

`q20_result = "oszustwo_ujawnione"`

**Nagroda:** DO USTALENIA. Profil: Legenda, niewielkie Złoto.

### FINAŁ B — Dobry Los

Dostępny po `prawdziwy_zwyczaj`. **Kultura 13**, próg **11**, jeśli znany jest także `mechanizm_oszustwa`. Beldo zaczyna sprzedawać kamienie uczciwie jako symbol odnowionego Dnia Dobrego Losu.

`q20_result = "dzien_dobrego_losu"`

**Nagroda:** DO USTALENIA. Profil: Legenda + trwały element kultury Valdren.

### FINAŁ C — Szczęście kosztuje

**Handel 14**. Bohater dołącza do Belda i usprawnia system prowizji oraz ustawionych pierwszych wygranych.

`q20_result = "wspolnik_belda"`

**Nagroda:** DO USTALENIA. Profil: najwyższe Złoto, bardzo niska Legenda.

---

# QUEST 21 — Kruk z pierścieniem

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `kruk_z_pierscieniem`  
**Numer:** `21`  
**Poziom Świata:** I  
**Długość:** Krótki  
**Unikalny:** TAK  
**Start:** okolice Eryndor  
**Główna statystyka:** Handel.

## ETAP 1 — Błyszczący przewodnik

**Handel 11** → pierścień jest wart około 8–10 Złota i nosi znak gildii jubilerów Eryndor; `znak_jubilera`.

Podążenie za krukiem nie wymaga rzutu. Ptak prowadzi do przewróconego wozu i rannego jubilera **Terena**.

→ **21A — Rozrzucony ładunek**.

## ROZWINIĘCIE 21A — Rozrzucony ładunek

**Handel 12** → sprawdź manifest i rozróżnij własność Terena od biżuterii powierzonej mu przez klientów; `manifest_terena`.

Następnie bohater zbiera rozrzucone kosztowności; jest to element fabuły, nie osobny test.

### FINAŁ A — Uczciwa prowizja

Bez rzutu: zwróć całość Terenowi.

`q21_result = "uczciwy_zwrot"`

**Nagroda:** DO USTALENIA. Profil: umiarkowana nagroda + dobra relacja z jubilerem.

### FINAŁ B — Prawo znalazcy

**Handel 13**. Przed rozpoczęciem zbierania bohater negocjuje legalny procent od wartości odzyskanego towaru.

`q21_result = "prowizja"`

**Nagroda:** DO USTALENIA. Profil: więcej Złota niż A, umiarkowana Legenda.

### FINAŁ C — Błyszczące znalezisko

**Handel 14**. Bohater rozpoznaje elementy, których Teren po wypadku nie potrafi dokładnie policzyć, i zatrzymuje najcenniejszą część.

`q21_result = "czesc_zatrzymana"`

**Nagroda:** DO USTALENIA. Profil: najwyższy loot/biżuteria, mało Legendy.

---

# QUEST 22 — Porzucony namiot

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `porzucony_namiot`  
**Numer:** `22`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** las w okolicy Thalwen  
**Statystyki:** Nauka, Intryga.

## ETAP 1 — Ciepła kolacja

- **Nauka 11** → jedzenie jest świeże, a żywica palona przy wejściu powoduje senność i utratę przytomności; `usypiajacy_dym`.
- **Intryga 12** → ślady wskazują ludzi przeciąganych w las, a ktoś później wrócił ponownie rozpalić ogień; obóz jest przynętą; `oboz_przyneta`.

Dowolny sukces → utwórz Znacznik `22` w leśnej kryjówce i przejdź do **22A — Łowcy podróżnych**.

## ROZWINIĘCIE 22A — Łowcy podróżnych

W kryjówce znajduje się trzech żywych jeńców.

### FINAŁ A — Obóz bez dymu

**Nauka 13**, próg **11** z `usypiajacy_dym`. Bohater neutralizuje opary i wykorzystuje pewność bandytów, że wszyscy zasnęli, aby uwolnić jeńców i zniszczyć zapas żywicy.

`q22_result = "jency_uratowani"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda / możliwe materiały lub wdzięczność jeńców.

### FINAŁ B — Łowcy złapani

**Intryga 14**, próg **12** z `oboz_przyneta`. Bohater pozoruje utratę przytomności, odwraca zasadzkę i doprowadza do schwytania bandy.

`q22_result = "banda_schwytana"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda + możliwa nagroda władz/loot bandytów.

### FINAŁ C — Ciepła kolacja

**Intryga 13**. Bohater zawiera układ z przywódcą bandy: bierze część zgromadzonego łupu i odchodzi. Jeńcy pozostają w rękach bandytów, a proceder trwa.

`q22_result = "uklad_z_banda"`

**Nagroda:** DO USTALENIA. Profil: dużo Złota/loot, bardzo niska Legenda, negatywny skutek świata.

---

# QUEST 23 — Wędrowny dom

## Status

**DOMKNIĘTY — DO AKCEPTACJI I USTALENIA NAGRÓD**

## Dane główne

**ID:** `wedrowny_dom`  
**Numer:** `23`  
**Poziom Świata:** I  
**Długość:** Średni  
**Unikalny:** TAK  
**Start:** las pomiędzy Norven a Durnhal  
**Główna statystyka:** Nauka.

## ETAP 1 — Chatka na nogach

- **Nauka 11** → ruch jest mechaniczny; w nogach pracują przekładnie, łańcuchy i przeciwwagi; `to_maszyna`.
- **Nauka 12** po `to_maszyna` → trasa prowadzi między starymi znacznikami, a jeden z nich został przewrócony; `uszkodzony_znacznik`.

→ **23A — Pracownia Mervena**.

## ROZWINIĘCIE 23A — Pracownia Mervena

Podczas postoju bohater wchodzi do pustego domu. Notatki pokazują, że **Merven** stworzył mobilną pracownię kursującą między placami budowy i kopalniami. Konstruktor zmarł dawno temu, ale maszyna nadal wykonuje ostatni program.

- **Nauka 13** → zrozum układ sterowania i rolę znaczników trasy; `sterowanie_mervena`.
- **Nauka 12** → zbadaj alchemiczny rdzeń cieplny i układ przeciwwag; `naped_mervena`.

→ **23B — Nowa droga**.

## ROZWINIĘCIE 23B — Nowa droga

### FINAŁ A — Ostatni krok

**Nauka 12**. Bohater bezpiecznie odłącza główną przekładnię. Dom zatrzymuje się na zawsze i może zostać później rozebrany.

`q23_result = "dom_zatrzymany"`

**Nagroda:** DO USTALENIA. Profil: materiały konstrukcyjne / umiarkowana Legenda.

### FINAŁ B — Dom wraca na drogę

**Nauka 14**, próg **12** z `uszkodzony_znacznik`. Bohater odtwarza znacznik i przywraca oryginalną trasę. Wędrowny Dom ponownie kursuje jako mobilna pracownia świata.

`q23_result = "trasa_naprawiona"`

**Nagroda:** DO USTALENIA. Profil: wysoka Legenda + dostęp do mobilnego punktu badawczego.

### FINAŁ C — Nowa droga

**Nauka 15**, próg **13** z `sterowanie_mervena`. Bohater zmienia system znaczników i programuje nową trasę, prowadząc konstrukcję do wybranego celu fabularnego.

`q23_result = "dom_przeprogramowany"`

**Nagroda:** DO USTALENIA. Profil: unikatowy wpływ na świat / technologia, umiarkowana-wysoka Legenda.

---

# Stan pliku po domknięciu

- Quest 1 ma zatwierdzone dotychczasowe nagrody i pełną specyfikację.
- Questy 2–23 mają zamknięte: fabułę, etapy, testy, progi, koszty, przejścia, główne finały A/B/C, minimalne trwałe wyniki, Kronikę w sensie wynikającym z opisów finałów oraz wymagany stan runtime.
- Questy 2–23 **nie mają jeszcze finalnych liczb Złota, Legendy i lootu**, ponieważ wartości te mają zostać zatwierdzone przed kodowaniem.
- Żaden Quest 2–23 nie trafia jeszcze do `rg_content/quests_final.py` bez osobnej akceptacji.
