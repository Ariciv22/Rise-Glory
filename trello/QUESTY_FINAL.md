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
