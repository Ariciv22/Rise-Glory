# 02 — Questy i Testy: wspólny silnik

**Status Kanban:** GOTOWE DO IMPLEMENTACJI

## Cel

Stworzyć jeden wspólny system Questów. Nowy Quest ma być przede wszystkim zestawem danych, etapów, opcji, warunków, akapitów i konsekwencji, a nie osobno programowaną mechaniką.

Podstawowy test:

`k20 + odpowiednia statystyka + bonusy >= poziom trudności`

Statystyki: Walka, Handel, Intryga, Dyplomacja, Kultura, Nauka.

## Finalne zasady projektowe — 2026-08-16

### 1. Jedna Talia Questów

- W grze istnieje jedna główna **Talia Questów**. Nie dzielimy Questów na talie Nauki, Intrygi, Handlu itd.
- Każdy Quest ma Poziom Świata I, II, III lub IV.
- Przy aktualnym Poziomie Świata dobierane są wyłącznie Questy tego poziomu.
- Quest niższego poziomu już posiadany przez bohatera pozostaje aktywny po awansie świata i można go dokończyć.
- Ten sam Quest nie może być równocześnie posiadany przez dwóch bohaterów.
- Quest może być oznaczony jako unikalny dla rozgrywki.

### 2. Stały numer Questa

- Każdy Quest ma stały numer przypisany do jego treści we wszystkich rozgrywkach.
- Przykład: „Spór o studnie” może zawsze mieć numer `13`, a inny Quest zawsze `16`.
- Numer nie jest przydzielany dynamicznie i nie jest recyklingowany między różnymi Questami.
- Ten sam numer służy do identyfikacji Znaczników Questa i jego kart rozwinięcia.

### 3. Limit Questów

- Bohater może posiadać maksymalnie **3 główne Questy** jednocześnie.
- Nierozpoczęty Quest także zajmuje miejsce w limicie.
- Karty rozwinięcia należą do swojego głównego Questa i nie zajmują dodatkowych miejsc.
- Przy limicie 3/3 gracz nie dobiera czwartego Questa do prywatnego podglądu.
- Podczas Rady może widzieć Quest będący elementem jawnej oferty, mimo że sam ma już 3/3, ponieważ samo oglądanie cudzej oferty nie oznacza dobrania Questa.

### 4. Kiedy Quest jest rozpoczęty

- Samo dobranie, posiadanie i czytanie karty nie rozpoczyna Questa.
- Quest staje się rozpoczęty dopiero po wykonaniu pierwszej właściwej akcji: testu, walki, interakcji ze Znacznikiem Questa lub innej akcji opisanej przez Quest.
- Nierozpoczęty Quest może być handlowany podczas Rady.
- Rozpoczęty Quest nie może być sprzedany ani przekazany innemu bohaterowi.

### 5. Porzucenie i powrót do talii

- Nierozpoczęty Quest można odrzucić/oddać; może wrócić do odpowiedniej Talii Questów i zostać potasowany, nawet jeśli gracz przeczytał kartę.
- Rozpoczęty, porzucony Quest nie wraca normalnie do talii. Trafia do historii jako `Porzucony`.
- Rozpoczęty unikalny Quest po porzuceniu lub przegraniu nie wraca już do puli w tej rozgrywce.
- Wszystkie jego aktywne Znaczniki Questów znikają z mapy i wracają do kieszonki/puli żetonów.

### 6. Koszt Akcji

- Podgląd Questa, etapu i metod: **0 Akcji**.
- Wybranie metody i rozpoczęcie próby: domyślnie **1 Akcja**.
- Ponowna próba: domyślnie **1 Akcja**.
- Bohater może ponawiać test w tej samej turze, jeśli ma Akcje.
- Konkretna karta może nadpisywać koszt.

### 7. Porażki

- Quest ma maksymalnie **5 żetonów porażki na cały Quest**.
- Piąta porażka domyślnie przegrywa Quest.
- Zwykła porażka: następny test w tym Queście ma `+1` do progu trudności.
- Naturalne 1: automatyczna porażka i następny test ma `+2` do progu trudności.
- Modyfikator dotyczy najbliższego testu i nie kumuluje się bez końca.
- Karta może mieć własną konsekwencję porażki i może np. natychmiast zakończyć Quest.

### 8. Nat 1 i Nat 20

- Nat 20 = automatyczny sukces **tylko aktualnego testu**.
- Nat 20 nie zalicza kolejnego etapu ani kolejnego testu.
- Nat 1 = automatyczna porażka.
- Domyślnie Nat 20 używa zwykłej ścieżki sukcesu, a Nat 1 zwykłej ścieżki porażki.
- Konkretna karta może jednak posiadać osobny akapit/efekt dla Nat 20 lub Nat 1.

### 9. Przygotuj się

- Mechanikę `Przygotuj się` można wykorzystać maksymalnie **1 raz na cały Quest**.
- Używa się jej bezpośrednio przed konkretnym testem.
- Koszt: **1 Akcja**.
- Bonus: **+2 do tego jednego testu**.
- Po użyciu Quest otrzymuje trwałe oznaczenie `Przygotowanie wykorzystane`.

### 10. Wymaga i Zużywa

Wspólny standard z Zagrożeniami:

- `Wymaga` — element trzeba posiadać, ale nie jest tracony.
- `Zużywa` — element jest wydawany w chwili świadomego wyboru metody i przepada także po porażce.
- System może obsługiwać Złoto, Towary, Przedmioty i Pomocników.
- Zużywanie Pomocnika jest rozwiązaniem wyjątkowym i musi być jawnie opisane na karcie.

### 11. Opcje bez rzutu

- Nie każda metoda wymaga k20.
- Zapłata, pokazanie wymaganego przedmiotu, zużycie zasobu albo czysta decyzja fabularna mogą działać automatycznie.
- Jedna opcja może uruchomić wiele efektów jednocześnie: zmianę etapu, nagrodę, flagę historii, usunięcie znacznika, walkę lub wpis do Kroniki.

### 12. Rozgałęzienia i zakończenia

- Quest może mieć alternatywne ścieżki i kilka różnych zakończeń.
- Ostatnia część historii może np. rozbić się na trzy różne finały.
- Różne drogi muszą różnić się co najmniej jednym z elementów: ryzykiem, kosztem, konsekwencją, nagrodą albo historią.
- Przyszłe etapy i alternatywne finały są ukryte do czasu odkrycia.
- Porażka może cofnąć gracza do wcześniejszego etapu, jeśli karta tak mówi.
- Quest może zostać formalnie ukończony bez nagrody lub z negatywną konsekwencją dla świata.
- Historia zapisuje dokładnie osiągnięte zakończenie, nie tylko status `ukończony`.

### 13. Blokowanie i odblokowywanie metod

- Wybory, sukcesy, porażki, przedmioty questowe i flagi historii mogą odblokować nowe opcje.
- Mogą też zablokować wcześniej znane opcje.
- Znana, lecz utracona opcja pozostaje wyszarzona z krótkim powodem niedostępności.
- Nie każdy Quest musi używać tej mechaniki.

### 14. Flagi historii

- Quest może zapisywać trwałe flagi decyzji i skutków, np. uratowanie konkretnej postaci, sojusz lub zdradę.
- Przyszłe Questy mogą opcjonalnie sprawdzać te flagi.
- Nie projektujemy wszystkich powiązań z góry; system ma jedynie zapewnić przyszłościowy punkt integracji.

### 15. Przedmioty i informacje questowe

- Quest może nadawać elementy istniejące tylko w ramach historii, np. `Klucz do krypty`, `Zapiski alchemika`, `Hasło strażników`.
- Nie muszą zajmować normalnego ekwipunku i nie muszą być handlowalne.
- Domyślnie znikają wraz z zakończeniem Questa, chyba że karta mówi inaczej.

### 16. Znaczniki Questów

- Quest może utworzyć jeden albo wiele Znaczników Questów na mapie.
- Wszystkie znaczniki tego samego Questa mają ten sam stały numer, np. trzy osobne żetony `13`.
- Znaczniki nie mają koloru gracza.
- Karta mówi, którego numeru szuka bohater.
- Kilka znaczników można domyślnie rozpatrywać w dowolnej kolejności, chyba że karta mówi inaczej.
- Znacznik może pojawić się na heksie zajętym już przez bohatera lub inny obiekt.
- Wejście na heks nie uruchamia Questa automatycznie; gracz świadomie wybiera akcję.
- Obcy bohater może wejść na heks, ale nie może rozwiązać cudzego Questa.
- Po zakończeniu/porzuceniu/przegraniu Questa jego znaczniki znikają i wracają do kieszonki żetonów.

### 17. Podróż

- Kolejne etapy mogą wymagać różnych lokacji i heksów.
- Zakończenie etapu może wskazać nowy cel podróży albo utworzyć nowe Znaczniki Questa.

### 18. Walka w Queście

- Walka używa wspólnego systemu Walki i cała sekwencja pozostaje częścią opłaconej Akcji Questa.
- Domyślna przegrana walki powoduje standardowe konsekwencje Walki oraz **1 żeton porażki Questa**.
- Quest pozostaje aktywny, chyba że była to piąta porażka.
- Karta może jawnie nadpisać regułę i np. zakończyć Quest natychmiast po przegranej walce.
- Etap może mieć punkt bez powrotu blokujący porzucenie lub opuszczenie trwającej sekwencji.

### 19. Limity czasu

- Quest może posiadać opcjonalny limit czasu.
- Jeśli limit istnieje, gracz widzi go od początku.
- Możliwe typy: liczba rund, własnych tur, `do następnej Rady` lub inny jawnie zapisany termin.
- Przekroczenie czasu może oznaczać przegraną, alternatywne zakończenie albo inny efekt karty.

### 20. Nagrody

- Karta początkowa pokazuje **wskazówkę**, czego można spodziewać się jako nagrody, a nie pełną matematyczną listę.
- Quest może dawać małe nagrody także w trakcie historii.
- Finały mogą mieć różne nagrody.
- **Usuwamy globalną redukcję Złota za liczbę porażek.** Porażki nie obcinają automatycznie końcowej wypłaty.
- Jeśli konkretny Quest ma zmniejszać nagrodę za błędy, musi to wynikać z jego własnych zasad.

### 21. Długość Questa

- Gracz widzi tylko długość i Poziom Świata, bez osobnej etykiety trudności.
- `Krótki` = 1 karta rozwinięcia.
- `Średni` = 2 karty rozwinięcia.
- `Długi` = 3 karty rozwinięcia.
- Jest to standard konstrukcyjny dla głównej ścieżki historii.

### 22. Osobna Talia Rozwinięć Questów

- Karty rozwinięcia **nie są częścią głównej Talii Questów**.
- Istnieje osobna **Talia/Pula Rozwinięć Questów**.
- Rozwinięcie wyciąga się tylko wtedy, gdy aktualna karta lub Księga Questów wskazuje konkretny identyfikator, np. `13A` albo `13C`.
- Nie wykładamy kilku alternatywnych rozwinięć na zapas.
- Rozwinięcie pojawia się dopiero wtedy, gdy historia realnie idzie do przodu.
- Odkryte rozwinięcia pozostają wsunięte poziomo pod kartą główną do końca Questa, tworząc widoczną historię.
- Po zakończeniu Questa rozwinięcia wracają do swojej puli/przegródki.
- Fizycznie rozwinięcia mogą być przechowywane w kasetkach zakresami, np. `0–20`, `21–40`, `41–60`, itd., a wewnątrz uporządkowane po numerach.

### 23. Księga Questów

- Gra posiada osobną **Księgę Questów** z numerowanymi akapitami.
- Gracz czyta wyłącznie akapit wskazany przez aktualną kartę/wynik.
- Numer akapitu i numer karty rozwinięcia to dwa osobne systemy.
- Przykład: wynik może powiedzieć `Sukces → przeczytaj 54A`; akapit `54A` może następnie nakazać `dobierz rozwinięcie 13C`.
- Porażka może wskazywać inny akapit, np. `54Z`.
- Nat 1/Nat 20 używają domyślnego sukcesu/porażki, chyba że karta jawnie wskazuje osobny akapit krytyczny.
- Akapit może zawierać czysty wybór fabularny bez rzutu.

### 24. Kronika i historia Questa

- Odkryte karty/akapity można później przeglądać jako przebytą ścieżkę.
- Nie pokazujemy alternatywnych, nieodkrytych ścieżek.
- Ważne decyzje i finały trafiają do Kroniki Świata jako krótka opowieść: kto, gdzie i co zrobił.
- Nie zapisujemy do Kroniki każdego rzutu k20.

## Wymagania implementacyjne Modułu 2

- [ ] Wspólny model QuestDefinition / QuestStage / QuestOption.
- [ ] Stały numer Questa, poziom świata, długość i wskazówka nagrody.
- [ ] Limit 3 głównych Questów.
- [ ] Stan `nierozpoczęty / rozpoczęty / ukończony / przegrany / porzucony`.
- [ ] Handel wyłącznie nierozpoczętymi Questami.
- [ ] 5 żetonów porażki.
- [ ] Nat 1/Nat 20 według nowych zasad.
- [ ] `Przygotuj się` 1× na Quest.
- [ ] `Wymaga` / `Zużywa`.
- [ ] Opcje testowe, beztestowe i walki.
- [ ] Alternatywne etapy i zakończenia.
- [ ] Flagi historii i questowe elementy tymczasowe.
- [ ] Punkt bez powrotu i limity czasu.
- [ ] Osobny rejestr kart rozwinięcia.
- [ ] Polecenia akapitów Księgi Questów.
- [ ] Znaczniki Questów i ich sprzątanie.
- [ ] Pełna nagroda Złota niezależnie od liczby porażek, chyba że karta mówi inaczej.
- [ ] Standardowa przegrana walki = 1 porażka Questa, nie automatyczna utrata Questa.
- [ ] Przebudować „Szatańskie siły” jako wzorcowy Quest systemu.
- [ ] Dodać testy jednostkowe nowych reguł.
- [ ] Punkt integracji z Kroniką Świata.

## Ważna zasada projektowa

Nie tworzyć fałszywego wyboru, np. `Nauka 12` albo `Intryga 14`, jeżeli obie opcje prowadzą dokładnie do tego samego rezultatu. Różne drogi powinny różnić się przynajmniej jednym elementem: ryzykiem, kosztem, konsekwencją, nagrodą albo dalszym przebiegiem historii.

## Definition of Done

Można stworzyć nowy Quest z testami, decyzjami bez rzutu, walką, podróżą, Znacznikami Questów, osobnymi kartami rozwinięcia, Księgą Questów, różnymi finałami, historią decyzji i nagrodami bez pisania osobnej mechaniki wyłącznie dla tej jednej karty.
