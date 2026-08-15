# Zagrożenia autorskie V1

Ten dokument zawiera Zagrożenia projektowane przez użytkownika. Asystent porządkuje zapis techniczny bez zmiany założeń fabularnych i mechanicznych.

## 1. Choroba wśród drzew

**Poziom Świata:** 2  
**Typ:** zaraza lasu / sabotaż / produkcja Drewna

### Opis fabularny

Krążą plotki, że pewna grupa ludzi wypuściła do lasów zarazę, która zjada drzewa od środka. Trzeba powstrzymać ten proceder albo uratować zakażone drzewa, zanim choroba zniszczy kolejne miejsca pozyskiwania Drewna.

### Rozmieszczenie

**Liczba Znaczników Zagrożenia:** 3.  
**Podstawowo:** trzy heksy `LAS`, na których znajdują się miejsca produkcji Drewna / kopalnie Drewna.  
**Awaryjnie:** trzy heksy `LAS` bez miejsc produkcji Drewna.

Wszystkie trzy znaczniki należą do tej samej instancji Zagrożenia i otrzymują ten sam widoczny numer na żetonie, np. `2`, aby było jasne, że są częścią jednego problemu.

### Efekt

Na wszystkich trzech oznaczonych heksach wycinka i produkcja Drewna są całkowicie zablokowane. Każdy z trzech znaczników musi zostać rozwiązany osobno. Po rozwiązaniu znacznika na konkretnym heksie blokada Drewna na tym heksie natychmiast znika, ale pozostałe znaczniki i ich blokady nadal działają. Całe Zagrożenie kończy się dopiero po rozwiązaniu wszystkich trzech znaczników.

### Metoda 1 — Wytrop ich i zwiąż trucicieli

**Test:** Intryga DC 14.  
**Wymaga:** `Lina` — nie jest zużywana.  
**Porażka:** „Zgubiłeś trop i także siebie w lesie.” Bohater traci 2 Akcje.

### Metoda 2 — Przekup ich i przepędź

**Test:** Handel DC 11.  
**Zużywa:** 6 Złota przy rozpoczęciu próby.  
**Porażka:** „Płacisz i zapewniają cię, że odejdą. Po chwili zauważasz, że ferajna nadal zatruwa młode łodygi.” Bohater traci dodatkowo 1 Akcję, dany znacznik pozostaje aktywny, a wydane 6 Złota nie wraca.

### Metoda 3 — Daj im do zrozumienia, że nie tylko oni potrzebują drewna

**Test:** Dyplomacja DC 15.  
**Zużywa:** 3 Złota przy rozpoczęciu próby.  
**Porażka:** rozmowa przeradza się w groźby. Bohater traci 1 Punkt Legendy, nie mniej niż do 0. Wydane 3 Złota nie wraca, a dany znacznik pozostaje aktywny.

### Rozwiązywanie znaczników

Każdy z trzech numerowanych znaczników reprezentuje osobny punkt tego samego Zagrożenia i musi zostać skutecznie rozwiązany. Sukces przy jednym znaczniku:

- usuwa tylko ten konkretny znacznik;
- odblokowuje wycinkę i produkcję Drewna tylko na tym heksie;
- nie usuwa pozostałych dwóch znaczników;
- nie kończy całego Wydarzenia, dopóki na mapie pozostaje choć jeden znacznik tego Zagrożenia.

Każdy z trzech znaczników korzysta z tych samych trzech metod rozwiązania opisanych powyżej.

### Nagroda

„Udało ci się zaradzić leśnemu problemowi i uratować zakażone drzewa.”

Po rozwiązaniu wszystkich trzech znaczników **każdy bohater, który skutecznie rozwiązał co najmniej jeden znacznik tego Zagrożenia, otrzymuje pełną nagrodę**:

- **4 Drewna**;
- do następnej Rady **każde jego miejsce produkcji Drewna produkuje +1 Drewna**.

Jeżeli kilka znaczników rozwiążą różni bohaterowie, każdy z tych bohaterów otrzymuje powyższą nagrodę po całkowitym zakończeniu Zagrożenia.

---

## 2. Lawiny w górach

**Status:** zatwierdzone — poza techniczną integracją z przyszłą mechaniką Szlaków Handlowych  
**Poziom Świata:** 1  
**Typ:** zagrożenie terenowe / zablokowane górskie szlaki

### Opis fabularny

Potężne lawiny zeszły na kilka górskich szlaków. Kamienie, śnieg i połamane drzewa zasypały przejścia, utrudniając podróż przez góry. Bohater może spróbować znaleźć śmiałków, którzy oczyszczą drogę, albo samemu wspiąć się po niebezpiecznych górach i znaleźć bezpieczne przejście dla pozostałych.

### Rozmieszczenie

**Liczba Znaczników Zagrożenia:** 5.  
**Podstawowo:** pięć różnych heksów `GÓRY`.

Wszystkie pięć znaczników należy do tej samej instancji Zagrożenia i powinno posiadać ten sam widoczny numer identyfikacyjny na żetonie.

### Efekt

Każdy z pięciu oznaczonych górskich szlaków jest zablokowany przez lawinę. Przez dany heks nie można przejść, dopóki jego znacznik nie zostanie skutecznie rozwiązany.

### Rozwiązywanie znaczników

Każdy z pięciu znaczników musi zostać rozwiązany osobno. Sukces przy jednym znaczniku:

- usuwa tylko tę konkretną lawinę;
- natychmiast otwiera przejście przez ten heks dla **wszystkich bohaterów**;
- nie usuwa pozostałych czterech lawin;
- nie kończy całego Zagrożenia, dopóki na mapie pozostaje choć jeden jego znacznik.

Ideą Zagrożenia jest stopniowe odnajdywanie i oczyszczanie przejść, aby kolejne drogi przez góry stawały się dostępne także dla innych graczy.

### Metoda 1 — Znajdź śmiałków do oczyszczenia szlaku

**Test:** Handel DC 16.  
**Zużywa:** 12 Złota przy rozpoczęciu próby.  
**Porażka:** śmiałkowie przyjmują zapłatę lub zaliczkę, ale po zobaczeniu rozmiaru osuwiska rezygnują. Wydane 12 Złota nie wraca, a znacznik pozostaje aktywny.

### Metoda 2 — Samemu przejdź przez góry i znajdź bezpieczną drogę

**Test:** Walka DC 17 — test reprezentuje siłę fizyczną, sprawność i wytrzymałość podczas wspinaczki; gra nie posiada osobnej statystyki `Siła`.  
**Wymaga:** `Lina` — nie jest zużywana.  
**Porażka:** podczas wspinaczki bohater traci oparcie i zostaje ranny. Otrzymuje **1 Ranę**, a znacznik pozostaje aktywny.

### Nagroda

Po całkowitym rozwiązaniu Zagrożenia, do następnej Rady **każdy Szlak Handlowy przechodzący przez góry daje +2 Złota więcej**.

Dokładna mechanika Szlaków Handlowych nie jest jeszcze ustalona i musi zostać zaprojektowana w osobnym module. Przy implementacji tego Zagrożenia bonus należy potraktować jako zależność od przyszłego systemu Szlaków Handlowych, a nie wymyślać jego działania na potrzeby tej karty.

### Zależność do późniejszego ustalenia

- Dokładne techniczne działanie bonusu `+2 Złota` zostanie określone dopiero wraz z mechaniką Szlaków Handlowych.

---

## 3. Zniszczone mosty na wzgórzach — szkic

**Status:** w projektowaniu  
**Typ:** zagrożenie terenowe / zablokowane przejścia

### Opis fabularny — ZATWIERDZONY KIERUNEK

Dwa mosty znajdujące się na wzgórzach zostały zniszczone. Przeprawy prowadzące przez mosty są niedostępne i bohaterowie nie mogą z nich korzystać, dopóki konstrukcje nie zostaną naprawione.

### Rozmieszczenie — ZATWIERDZONE

**Liczba Znaczników Zagrożenia:** 2.  
**Podstawowo:** dwa różne miejsca przepraw na heksach `WZGÓRZA`.

Oba znaczniki należą do tej samej instancji Zagrożenia i powinny posiadać ten sam widoczny numer identyfikacyjny na żetonie.

### Efekt — ZATWIERDZONY KIERUNEK

Każdy zniszczony most blokuje przejście wykorzystujące daną przeprawę. Po skutecznej naprawie konkretnego mostu jego przejście zostaje ponownie otwarte dla wszystkich bohaterów.

### Cel Zagrożenia — ZATWIERDZONE

Aby całkowicie zakończyć Zagrożenie, oba mosty muszą zostać naprawione.

### Do doprecyzowania

- Poziom Świata.
- Czy każdy z dwóch mostów jest rozwiązywany osobno i czy naprawa jednego usuwa tylko jego znacznik.
- Sposoby naprawy mostu — minimum 2 metody zgodnie z zasadami systemu Zagrożeń.
- Statystyki i DC metod.
- Wymagane lub zużywane materiały, przedmioty albo Złoto.
- Konsekwencje porażek.
- Nagroda.
- Techniczny sposób reprezentowania zablokowanej przeprawy/mostu na mapie zostanie ustalony przy implementacji, bez zmiany zatwierdzonego efektu fabularnego.