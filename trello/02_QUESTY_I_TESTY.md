# 02 — Questy i Testy: wspólny silnik

**Status Kanban:** W TRAKCIE PROJEKTOWANIA

## Cel

Stworzyć jeden wspólny system Questów. Każdy przyszły Quest powinien być przede wszystkim zestawem danych, etapów, opcji, warunków i konsekwencji, a nie osobno programowaną mechaniką.

Podstawowy test:

`k20 + odpowiednia statystyka + bonusy >= poziom trudności`

Statystyki: Walka, Handel, Intryga, Dyplomacja, Kultura, Nauka.

## Punkty do działania

- [ ] Stworzyć jeden wspólny model Questa.
- [ ] Obsłużyć Quest składający się z wielu etapów.
- [ ] Każdy etap może mieć kilka dostępnych opcji.
- [ ] Opcje mogą wykorzystywać różne statystyki.
- [ ] Opcje mogą posiadać różne poziomy trudności.
- [ ] Opcja może kosztować Złoto.
- [ ] Opcja może wymagać Towaru.
- [ ] Opcja może wymagać Przedmiotu.
- [ ] Opcja może wymagać Pomocnika lub konkretnego typu Pomocnika.
- [ ] Opcja może zużywać Towar, Przedmiot, Złoto lub wyjątkowo Pomocnika.
- [ ] Opcja może prowadzić do walki.
- [ ] Opcja może prowadzić do następnego etapu.
- [ ] Opcja może prowadzić do alternatywnego etapu lub jednego z kilku finałów.
- [ ] Różne wybory mogą prowadzić do różnych konsekwencji.
- [ ] Obsłużyć sukces.
- [ ] Obsłużyć porażkę.
- [ ] Obsłużyć Nat 1.
- [ ] Obsłużyć Nat 20.
- [ ] Obsłużyć maksymalnie 5 porażek Questa.
- [ ] Obsłużyć ponowną próbę.
- [ ] Obsłużyć mechanikę „Przygotuj się”.
- [ ] Zapisywać historię przebiegu Questa.
- [ ] Obsłużyć Złoto jako nagrodę.
- [ ] Obsłużyć Punkty Legendy jako nagrodę.
- [ ] Obsłużyć Towary jako nagrodę.
- [ ] Obsłużyć Przedmioty jako nagrodę.
- [ ] Obsłużyć małe nagrody i efekty w trakcie Questa.
- [ ] Obsłużyć przedmioty/informacje questowe istniejące tylko w ramach danego Questa.
- [ ] Obsłużyć utratę Questa.
- [ ] Obsłużyć porzucenie Questa.
- [ ] Quest może wymagać konkretnej lokacji.
- [ ] Quest może wymagać konkretnego heksu.
- [ ] Quest może tworzyć jeden lub wiele celów na mapie.
- [ ] Quest może zawierać walkę.
- [ ] Quest może mieć kilka różnych metod ukończenia.
- [ ] Quest może posiadać limit czasu.
- [ ] Quest może mieć punkt bez powrotu.
- [ ] Quest może odblokowywać lub blokować opcje na podstawie wcześniejszych decyzji.
- [ ] Quest może wpływać na przyszłe Questy i świat przez flagi historii.
- [ ] Quest może zmieniać świat po ukończeniu lub porażce.
- [ ] Obsłużyć jedną wspólną Talię Questów.
- [ ] Obsłużyć Questy Poziomu Świata I–IV.
- [ ] Obsłużyć stały numer przypisany do konkretnego Questa.
- [ ] Obsłużyć Znaczniki Questów z numerem odpowiadającym karcie Questa.
- [ ] Obsłużyć karty rozwinięcia/finału należące do głównego Questa.
- [ ] Przebudować „Szatańskie siły” na wzorcowy Quest wspólnego systemu.
- [ ] Przygotować kilka prostych Questów testowych.
- [ ] Przygotować punkt integracji z Kroniką Świata.

## Ustalenia projektowe — 2026-08-15

### 1. Koszt Akcji i podstawowy przebieg testu

- Sam podgląd Questa, etapu i dostępnych metod kosztuje 0 Akcji.
- Wybranie metody i podjęcie próby kosztuje domyślnie 1 Akcję.
- Ponowna próba po porażce również kosztuje 1 Akcję.
- Bohater może ponawiać próby w tej samej turze, jeżeli posiada jeszcze Akcje.
- Konkretna karta może nadpisywać domyślne zasady, jeżeli wymaga tego fabuła lub mechanika.

### 2. Porażki

- Limit wynosi 5 żetonów porażki na cały Quest.
- Piąta porażka domyślnie oznacza przegranie Questa.
- Zwykła porażka powoduje, że następny test w tym Queście ma próg trudności wyższy o 1.
- Naturalne 1 powoduje automatyczną porażkę niezależnie od bonusów i sprawia, że następny test ma próg trudności wyższy o 2.
- Karta Questa może posiadać własne konsekwencje porażki i może nadpisywać regułę domyślną, np. natychmiast zakończyć Quest po przegranej określonej walce.
- Wpływ liczby porażek na końcową ilość Złota pozostaje do ponownego przemyślenia podczas dalszego projektowania/balansu.

### 3. Naturalne 20 i Naturalne 1

- Naturalne 20 automatycznie zalicza wyłącznie test, na którym zostało wyrzucone.
- Naturalne 20 nie zalicza automatycznie następnego etapu ani kolejnego testu.
- Naturalne 1 jest automatyczną porażką.
- Konkretna opcja może dodatkowo posiadać specjalny efekt Nat 20 lub Nat 1, np. dodatkowy loot, alarm, walkę albo inną konsekwencję.

### 4. „Przygotuj się”

- Każdy Quest pozwala domyślnie użyć mechaniki „Przygotuj się” maksymalnie 1 raz podczas całego Questa.
- „Przygotuj się” wybiera się bezpośrednio przed podjęciem konkretnego testu.
- Koszt przygotowania: 1 Akcja.
- Efekt: +2 do jednego najbliższego wybranego testu.
- Po wykorzystaniu Quest otrzymuje trwałe oznaczenie „Przygotowanie wykorzystane”.
- Bonusu nie można kumulować ani użyć ponownie w tym samym Queście.

### 5. Wymaga i Zużywa

Questy używają wspólnego standardu znanego z Zagrożeń:

- `Wymaga` — bohater musi posiadać wskazany element, ale go nie traci.
- `Zużywa` — wskazany element zostaje wydany po świadomym wybraniu metody i przepada również wtedy, gdy próba zakończy się porażką.

Opcje mogą wymagać lub zużywać m.in. Złoto, Towary, Przedmioty i Pomocników. Zużycie Pomocnika ma być rozwiązaniem wyjątkowym, używanym tylko wtedy, gdy karta wyraźnie tego wymaga.

### 6. Opcje bez rzutu

- Nie każda metoda musi wymagać testu k20.
- Jeżeli opcja polega np. na zapłaceniu określonej kwoty, pokazaniu wymaganego przedmiotu lub zużyciu konkretnego zasobu, może zakończyć się automatycznie po spełnieniu warunków.
- Jedna opcja może uruchomić kilka efektów jednocześnie, np. przejście do finału, nagrodę, zmianę flagi historii, usunięcie znacznika i wpis do Kroniki.

### 7. Rozgałęzienia i zakończenia

- Quest może rozgałęziać się na różne ścieżki zależnie od wyborów i wyników.
- Różne ścieżki nie powinny być fałszywym wyborem; muszą różnić się ryzykiem, kosztem, konsekwencją, nagrodą albo dalszą historią.
- Ostatnia część Questa może rozdzielić się np. na trzy zupełnie różne zakończenia.
- Poszczególne zakończenia mogą mieć inne konsekwencje dla świata i inne nagrody.
- Przyszłe etapy i przyszłe zakończenia są ukryte przed graczem do czasu ich odkrycia.

### 8. Blokowanie i odblokowywanie opcji

- Wcześniejsze decyzje, sukcesy, porażki, przedmioty questowe i flagi historii mogą odblokowywać nowe metody.
- Mogą również trwale blokować wcześniej dostępne możliwości.
- Znana wcześniej, ale utracona opcja pozostaje widoczna jako wyszarzona z krótkim powodem niedostępności.
- Nowa opcja może pojawić się dopiero po spełnieniu określonego warunku.
- Nie każdy Quest musi korzystać z tej mechaniki.

### 9. Przedmioty i informacje questowe

- Quest może nadawać tymczasowe elementy fabularne, np. „Klucz do krypty”, „Zapiski alchemika”, „Hasło strażników”.
- Elementy questowe nie muszą zajmować normalnego ekwipunku ani być przedmiotami handlowymi.
- Domyślnie znikają wraz z zakończeniem Questa, chyba że karta mówi inaczej.

### 10. Lokacje, podróż i Znaczniki Questów

- Quest może prowadzić gracza przez kilka różnych miejsc na mapie.
- Ukończenie etapu może zmienić cel i wymusić fizyczną podróż do kolejnej lokacji lub heksu.
- Quest może tworzyć jeden albo wiele Znaczników Questów.
- Wszystkie znaczniki należące do tego samego Questa mają ten sam numer Questa.
- Przykład: jeżeli „Spór o studnie” ma numer 13 i tworzy trzy cele, na mapie pojawiają się trzy oddzielne znaczniki z numerem `13`.
- Znaczniki nie mają koloru właściciela.
- Numer Questa jest stały i przypisany do konkretnej treści w każdej rozgrywce. Przykładowo Quest nr 13 zawsze pozostaje Questem nr 13, a Quest nr 16 zawsze Questem nr 16.
- Numer nie jest nadawany dynamicznie podczas partii i nie jest recyklingowany między różnymi Questami.
- Karta Questa wskazuje numer odpowiadającego jej znacznika.
- Jeżeli Quest ma kilka równoległych znaczników, domyślnie można rozpatrywać je w dowolnej kolejności, chyba że karta mówi inaczej.
- Zakończenie etapu może natychmiast tworzyć kolejne znaczniki tego samego Questa.
- Znacznik może pojawić się na heksie, na którym już stoi bohater.
- Samo wejście na heks Znacznika Questa nie uruchamia interakcji automatycznie.
- Bohater świadomie wybiera odpowiednią akcję po prawej stronie interfejsu.
- Inny bohater może wejść na heks znacznika, ale nie może rozwiązywać cudzego Questa.

### 11. Walki w Questach

- Cała walka uruchomiona jako część opcji Questa korzysta ze wspólnego systemu Walki.
- Po standardowej przegranej walce bohater ponosi zwykłe konsekwencje porażki w Walce oraz otrzymuje 1 żeton porażki Questa.
- Domyślnie Quest pozostaje aktywny i można wrócić do próby później, o ile nie była to piąta porażka.
- Konkretna karta może wyraźnie określić surowszy skutek, np. natychmiastowe zakończenie Questa po przegranej walce.
- Etap może posiadać „punkt bez powrotu”, po którym nie można porzucić Questa lub opuścić trwającej sekwencji, dopóki nie zostanie rozstrzygnięta.

### 12. Historia, świat i konsekwencje przyszłościowe

- Quest może trwale zmieniać świat.
- Różne finały mogą np. usuwać obiekt, tworzyć nowego handlarza, uruchamiać Zagrożenie albo zmieniać przyszłe możliwości.
- Ważne wybory i zakończenia trafiają do Kroniki Świata jako krótka opowieść o tym, kto, gdzie i co zrobił.
- Nie zapisujemy każdego rzutu ani każdej drobnej próby do Kroniki.
- System może przechowywać proste flagi historii, np. informację o uratowaniu postaci, sojuszu albo zdradzie.
- Przyszłe Questy mogą opcjonalnie sprawdzać takie flagi i zmieniać tekst, dostępne opcje lub konsekwencje.
- Projektując takie zależności trzeba zachować przyszłościowość, ale nie każdy Quest musi być powiązany z innymi.
- Quest może dawać niewielkie nagrody lub loot również w trakcie historii, a nie wyłącznie na końcu.

### 13. Długość i poziom Questa

- Gracz widzi oznaczenie długości: `Krótki`, `Średni` albo `Długi`.
- Nie pokazujemy osobnej etykiety typu „Łatwy / Trudny”.
- Trudność i poziom zawartości wynikają przede wszystkim z Poziomu Świata Questa.
- Questy posiadają Poziom Świata I, II, III lub IV.
- Przy aktualnym Poziomie Świata dobierane są Questy odpowiadające temu poziomowi.
- Po przejściu świata na wyższy poziom Questy niższego poziomu nie są już normalnie dobierane.
- Już posiadany Quest niższego poziomu nie znika i może zostać normalnie dokończony.

### 14. Jedna Talia Questów

- Rezygnujemy z osobnych talii Nauki, Intrygi, Handlu itd.
- W grze istnieje jedna wspólna Talia Questów.
- Polecenie „Dobierz Quest” losuje kartę odpowiednią dla aktualnego Poziomu Świata.
- Po dobraniu gracz może zobaczyć nazwę, opis wprowadzający, długość, wskazówkę dotyczącą możliwej nagrody, ewentualny limit czasu oraz pierwszy cel.
- Następnie świadomie przyjmuje albo odrzuca Quest.
- Jeżeli odrzuca nierozpoczęty Quest, karta może wrócić do odpowiedniej talii/puli i zostać potasowana.
- Ten sam nieunikalny Quest nie może być jednocześnie posiadany przez dwóch bohaterów.
- Quest może być oznaczony jako unikalny dla danej rozgrywki.
- Unikalny Quest po definitywnym ukończeniu/przegraniu nie wraca do zwykłego obiegu.
- Po wyczerpaniu puli danego Poziomu Świata można ponownie tasować dozwolone nieunikalne karty ze stosu odrzuconych.

### 15. Limit posiadanych Questów

- Bohater może posiadać maksymalnie 3 główne Questy jednocześnie.
- Limit obejmuje zarówno Questy rozpoczęte, jak i nierozpoczęte.
- Normalnie przy stanie 3/3 bohater nie dobiera czwartego Questa nawet tylko do podglądu.
- Rada jest wyjątkiem prezentacyjnym: Questy występujące w handlu/ofertach mogą być widoczne nawet graczowi z limitem 3/3, ponieważ i tak są publicznie prezentowane w Radzie.
- Karty rozwinięcia/finału należące do już posiadanego Questa nie są liczone jako kolejne Questy i nie zajmują dodatkowych miejsc w limicie.

### 16. Kiedy Quest jest rozpoczęty

- Samo dobranie, przyjęcie i przeczytanie Questa nie oznacza jeszcze rozpoczęcia jego historii.
- Quest staje się „rozpoczęty” dopiero po wykonaniu pierwszej właściwej akcji tego Questa: testu, walki, interakcji ze znacznikiem lub innej akcji określonej przez kartę.
- Nierozpoczęty Quest może zostać sprzedany/przekazany podczas Rady.
- Po rozpoczęciu Quest staje się osobistą historią bohatera i nie może być normalnie sprzedawany ani przekazywany.

### 17. Porzucenie i przegranie Questa

- Gracz może świadomie porzucić Quest, o ile nie znajduje się za punktem bez powrotu lub karta nie zabrania porzucenia.
- Porzucenie domyślnie nie kosztuje Akcji.
- Wszystkie aktywne Znaczniki Questów tego zadania znikają.
- Rozpoczęty i porzucony Quest trafia do historii jako `Porzucony`, a nie jako zwykła porażka.
- Nierozpoczęty Quest może zostać oddany do odpowiedniej talii/puli i ponownie potasowany nawet wtedy, gdy właściciel przeczytał jego treść.
- Przegrany rozpoczęty Quest trafia do historii jako niepowodzenie wraz z informacją, na jakim etapie historia się zakończyła.
- Karta może określać dodatkową konsekwencję przegrania Questa dla świata.

### 18. Limity czasu

- Silnik Questów ma obsługiwać opcjonalne limity czasu.
- Limit czasu jest widoczny graczowi od początku, jeśli dany Quest go posiada.
- Karta może używać różnych typów terminów, np. liczby rund, własnych tur albo terminu „do następnej Rady”.
- Przekroczenie czasu może oznaczać przegraną, alternatywne zakończenie lub inną konsekwencję określoną przez kartę.

### 19. Nagrody

- Karta początkowa nie musi podawać dokładnej matematycznej nagrody.
- Gracz otrzymuje wskazówkę, czego może spodziewać się po Queście.
- Różne zakończenia mogą posiadać różne rzeczywiste nagrody.
- Quest może przyznawać Złoto, Punkty Legendy, Towary, Przedmioty i inne efekty.
- Dokładna zasada zmniejszania Złota w zależności od liczby porażek pozostaje otwarta i wymaga osobnej decyzji/balansu.

### 20. Karty rozwinięcia i finału

- Jeden główny Quest może posiadać dodatkowe karty rozwinięcia/finału.
- Wszystkie należą mechanicznie do jednego Questa i nie zwiększają limitu 3 Questów.
- Karty rozwinięcia mogą być oznaczane np. jako `13A`, `13B`, `13C`, przy zachowaniu dużego, wspólnego numeru `13` identyfikującego całą historię.
- Główna karta może wskazać dokładnie, którą kartę rozwinięcia należy dobrać w wyniku danego wyboru.
- Nieodkryte alternatywne rozwinięcia/finały pozostają ukryte, dzięki czemu nie spoilerują innych ścieżek.
- Rozwinięcie nie tworzy kolejnego poziomu rozwinięć. Nie budujemy struktury `13 -> 13B -> 13B2`.
- Wizualnie zdobyte karty jednego Questa są układane poziomo, jedna przy/za drugą, aby tworzyły czytelną rozwijającą się historię.
- Kliknięcie odkrytej części pozwala wrócić do przeczytanej wcześniej treści.

## Punkty otwarte na kolejną sesję

- Ostateczna zasada wpływu liczby porażek na wysokość nagrody w Złocie.
- Dokładna techniczna obsługa kart rozwinięcia w jednej Talii Questów: w jaki sposób pozostają w talii, ale nie mogą zostać wylosowane jako samodzielny główny Quest.
- Czy jeden główny Quest może mieć kilka kart rozwinięcia aktywnych jednocześnie.
- Jak obsłużyć sytuację techniczną, w której wskazana karta rozwinięcia jest niedostępna lub brakuje jej w talii/puli.
- Ostateczne szczegóły wizualnego oznaczenia kart głównych i kart rozwinięcia.
- Dokończyć pozostałe pytania projektowe Modułu 2 przed rozpoczęciem pełnej przebudowy silnika.

## Ważna zasada projektowa

Nie tworzyć fałszywego wyboru, np. `Nauka 12` albo `Intryga 14`, jeżeli obie opcje prowadzą dokładnie do tego samego rezultatu.

Różne drogi powinny różnić się przynajmniej jednym elementem: ryzykiem, kosztem, konsekwencją, nagrodą albo dalszym przebiegiem historii.

## Definition of Done

Można stworzyć nowy wieloetapowy Quest z testami, alternatywnymi drogami, walką, Znacznikami Questów, rozwinięciami/finałami, historią decyzji i nagrodami bez pisania osobnej mechaniki tylko dla tego Questa.