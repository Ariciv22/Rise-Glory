# Zagrożenia testowe V1

**Status:** zestaw testowy do implementacji modułu 01 — Żywy Świat / Zagrożenia  
**Zakres:** 6 Zagrożeń łącznie: istniejący projekt „Rozbójnicy na trakcie” + 5 nowych Zagrożeń.  
**Balans:** wartości DC, nagród i kar są wartościami startowymi dla Alfy i mogą zostać skorygowane później w module balansu bez zmiany zasad systemu Zagrożeń.

Każde Zagrożenie poniżej korzysta z zamkniętych zasad modułu 01: efekt działa od chwili wejścia problemu do gry, badanie jest osobne dla każdego bohatera, „Zbadaj problem” kosztuje 1 Akcję, próba rozwiązania kosztuje kolejną 1 Akcję, metody są ukryte do osobistego zbadania, nagroda jest wspólna niezależnie od wybranej skutecznej metody, a porażka nie osłabia problemu domyślnie.

---

## 1. Rozbójnicy na trakcie

**ID:** `bandits_on_the_road`  
**Poziom Świata:** 1  
**Typ:** Zagrożenie fizyczne / walka / konflikt społeczny  
**Rozmieszczenie podstawowe:** losowy przechodni heks.  
**Fallback:** inny losowy przechodni heks.  
**Efekt:** handel Towarami jest mniej opłacalny — cena sprzedaży Towarów jest obniżona o 1 Złoto, dopóki Rozbójnicy pozostają aktywni.  
**Nagroda po rozwiązaniu:** 3 Złota + 1 Punkt Legendy.

### Metody

1. **Walka — Zaatakuj obóz**  
   Uruchamia pełną Walkę z grupą Rozbójników.  
   **Porażka:** standardowe konsekwencje przegranej Walki.

2. **Intryga — Zakradnij się i zniszcz zapasy**  
   `Intryga DC 11`.  
   **Porażka:** utrata 2 Złota.

3. **Dyplomacja — Zmuś ich do opuszczenia traktu**  
   `Dyplomacja DC 12`.  
   **Porażka:** 1 Rana.

---

## 2. Skażone studnie

**ID:** `poisoned_wells`  
**Poziom Świata:** 1  
**Typ:** problem osady / zatrucie / sabotaż  
**Rozmieszczenie podstawowe:** losowa Wieś (`location_kind = village`).  
**Fallback:** losowe Miasto (`location_kind = city`).  
**Efekty:** w dotkniętej lokacji leczenie jest całkowicie zablokowane; zakup Jedzenia w tej lokacji kosztuje dodatkowo 1 Złoto.  
**Nagroda po rozwiązaniu:** 4 Złota + 1 Punkt Legendy.

### Metody

1. **Nauka — Oczyść źródło wody**  
   `Nauka DC 11`.  
   **Porażka:** 1 Rana.

2. **Intryga — Odnajdź sprawcę zatrucia**  
   `Intryga DC 12`.  
   **Porażka:** utrata 2 Złota.

3. **Handel — Sprowadź zapasy czystej wody i medykamenty**  
   `Handel DC 10`.  
   **Zużywa:** 2 Złota przy rozpoczęciu próby.  
   **Porażka:** wydane Złoto przepada bez dodatkowej kary.

---

## 3. Wataha z Czarnego Lasu

**ID:** `black_forest_pack`  
**Poziom Świata:** 1  
**Typ:** bestie / teren / walka  
**Rozmieszczenie podstawowe:** losowy Las (`terrain = forest`).  
**Fallback:** losowe Wzgórza (`terrain = hills`).  
**Efekt:** wejście na heks z tym Zagrożeniem kosztuje dodatkowo 1 Akcję ruchu ponad normalny koszt terenu.  
**Nagroda po rozwiązaniu:** 3 Złota + 1 Punkt Legendy.

### Metody

1. **Walka — Poluj na watahę**  
   Uruchamia pełną Walkę z Watahą Wilków.  
   **Porażka:** standardowe konsekwencje przegranej Walki.

2. **Intryga — Zastaw serię pułapek**  
   `Intryga DC 11`.  
   **Wymaga:** posiadania `Lina` — przedmiot nie jest zużywany.  
   **Porażka:** 1 Rana.

3. **Nauka — Wytrop legowisko i odetnij watahę od szlaku**  
   `Nauka DC 12`.  
   **Porażka:** 1 Rana.

---

## 4. Szept z katakumb

**ID:** `whispers_from_catacombs`  
**Poziom Świata:** 1  
**Typ:** klątwa / miejsce / pełna Walka  
**Rozmieszczenie podstawowe:** losowy Zamek (`location_kind = castle`).  
**Fallback:** losowe Miasto (`location_kind = city`).  
**Efekty:** trening w dotkniętej lokacji jest całkowicie zablokowany; leczenie w tej lokacji kosztuje dodatkowo 1 Złoto.  
**Nagroda po rozwiązaniu:** 5 Złota + 2 Punkty Legendy.

### Metody

1. **Kultura — Odpraw rytuał oczyszczenia**  
   `Kultura DC 12`.  
   **Porażka:** 1 Rana.

2. **Nauka — Odczytaj runy i przełam klątwę**  
   `Nauka DC 13`.  
   **Wymaga:** posiadania `Pochodnia` — przedmiot nie jest zużywany.  
   **Porażka:** utrata 2 Złota.

3. **Walka — Pokonaj Przeklętego Strażnika**  
   Uruchamia pełną Walkę z Przeklętym Strażnikiem.  
   **Porażka:** standardowe konsekwencje przegranej Walki.

---

## 5. Rozruchy na targu

**ID:** `market_riots`  
**Poziom Świata:** 1  
**Typ:** konflikt społeczny / ekonomia  
**Rozmieszczenie podstawowe:** losowe Miasto (`location_kind = city`).  
**Fallback:** losowa Wieś (`location_kind = village`).  
**Efekt:** w dotkniętej lokacji kupowanie i sprzedawanie jest całkowicie zablokowane. Pozostałe funkcje lokacji działają normalnie.  
**Nagroda po rozwiązaniu:** 4 Złota + 1 Punkt Legendy.

### Metody

1. **Dyplomacja — Doprowadź strony do porozumienia**  
   `Dyplomacja DC 11`.  
   **Porażka:** utrata 2 Złota.

2. **Kultura — Uspokój tłum i odbuduj zaufanie**  
   `Kultura DC 12`.  
   **Porażka:** utrata 1 Punktu Legendy, nie mniej niż 0.

3. **Handel — Pokryj najpilniejsze zobowiązania kupców**  
   Metoda bez rzutu — automatyczny sukces po spełnieniu warunków.  
   **Zużywa:** 4 Złota przy rozpoczęciu próby.

---

## 6. Zawalona przełęcz

**ID:** `collapsed_pass`  
**Poziom Świata:** 1  
**Typ:** teren / utrudnienie ruchu  
**Rozmieszczenie podstawowe:** losowe Góry (`terrain = mountain`).  
**Fallback:** losowe Wzgórza (`terrain = hills`).  
**Efekt:** koszt wejścia na heks z tym Zagrożeniem jest zwiększony o 1 Akcję ponad normalny koszt terenu. Bohater znajdujący się już na heksie w chwili powstania Zagrożenia może go opuścić za normalny koszt ruchu.  
**Nagroda po rozwiązaniu:** 4 Złota + 1 Punkt Legendy.

### Metody

1. **Nauka — Wyznacz bezpieczną drogę przez osuwisko**  
   `Nauka DC 11`.  
   **Porażka:** 1 Rana.

2. **Intryga — Przedostań się bocznym przejściem**  
   `Intryga DC 12`.  
   **Wymaga:** posiadania `Lina` — przedmiot nie jest zużywany.  
   **Porażka:** 1 Rana.

3. **Handel — Zatrudnij ludzi do oczyszczenia przełęczy**  
   `Handel DC 10`.  
   **Zużywa:** 3 Złota przy rozpoczęciu próby.  
   **Porażka:** wydane Złoto przepada bez dodatkowej kary.

---

## Pokrycie systemu przez zestaw testowy

Zestaw sześciu Zagrożeń celowo sprawdza różne części modułu:

- pełna Walka: Rozbójnicy, Wataha, Szept z katakumb;
- wszystkie sześć statystyk bohatera;
- testy k20 oraz metoda automatyczna bez rzutu;
- wymagania typu `posiadaj` i koszty typu `zużywa`;
- blokady leczenia, treningu oraz handlu;
- lokalne modyfikatory kosztu ruchu;
- efekty ekonomiczne;
- rozmieszczenie po typie lokacji i po typie terenu;
- fallback rozmieszczenia;
- różne konsekwencje porażki;
- wspólna nagroda niezależna od wybranej metody.

Po wdrożeniu tych sześciu Zagrożeń moduł 01 powinien mieć wystarczający zestaw testowy do sprawdzenia pełnego flow przed przejściem do balansu i tworzenia większej talii Wydarzeń Świata.