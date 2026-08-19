# 03 — Walka V2

**Status Kanban:** DO ZROBIENIA

## Cel
Kompletna podstawowa walka do alfy Rise & Glory.

## Zatwierdzone zasady 1–70

### 1. Przebieg walki
- Bohater zawsze rozpoczyna rundę.
- Standardowy atak: `k20 + Walka + premie wyposażenia` przeciwko KP przeciwnika.
- Każdy zwykły atak korzysta ze statystyki `Walka`.
- Cała walka kosztuje 1 Akcję niezależnie od liczby rund.
- Walka trwa bez limitu rund do zwycięstwa, porażki albo skutecznego opuszczenia walki.
- Mechanicznie zawsze walczy się z jednym przeciwnikiem. Grafika/karta może przedstawiać grupę, ale grupa ma jedną pulę statystyk i HP.
- Po pudle bohatera przeciwnik normalnie wykonuje swoje działanie.

### 2. HP bohatera i Rany
- Bazowe maksymalne HP bohatera: `10`.
- Atrybuty, wyposażenie i efekty mogą zwiększać maksymalne HP.
- Bohater i przeciwnik zadają sobie obrażenia w HP.
- Przy `0 HP` bohater traci przytomność i walka natychmiast się kończy.
- Po porażce bohater otrzymuje `1 Ranę`, pozostaje na aktualnym heksie, odzyskuje przytomność z `1 HP`, a jego tura natychmiast się kończy; niewykorzystane Akcje przepadają.
- Aktualne HP pozostaje między walkami.
- Jedzenie, mikstury, odpoczynek i odpowiednie efekty leczą HP.
- HP i Rany są leczone osobno. Leczenie Rany nie odnawia automatycznie HP i odwrotnie.
- Rany leczy się w odpowiednich lokacjach. Szczegółowy system konsekwencji Ran zostanie opisany później.
- Na obecnym etapie zwykłe ataki nie zadają Ran bezpośrednio z pominięciem HP.

### 3. Porażka
- Bohater traci Złoto według Poziomu Świata: I `1`, II `2`, III `3`, IV `4`.
- Dodatkowo traci 1 losowy Przedmiot wyłącznie z plecaka.
- Aktualnie założone Przedmioty nie wchodzą do losowania.
- Kwalifikujące się karty w plecaku są zasłaniane; gracz wybiera jedną w ciemno i odrzuca ją.
- Przedmioty kluczowe/questowe/wymagane przez aktywny cel są chronione i nie biorą udziału w losowaniu.
- Jeśli w plecaku nie ma kwalifikującego się Przedmiotu, utrata Przedmiotu jest pomijana; kara w Złocie i Rana nadal obowiązują.

### 4. Broń, obrażenia i Nat 1/20
- Broń ma osobno premię do trafienia i wartość obrażeń, np. `+2 trafienia / 2 obrażenia`.
- Atak bez broni zadaje 1 obrażenie i nie ma premii broni.
- Przeciwnik zadaje stałą liczbę obrażeń HP określoną na karcie.
- Nat 1 = automatyczne pudło.
- Nat 20 = automatyczne trafienie i podwójne rozpatrzenie ataku broni.
- Przy Nat 20 obrażenia broni są mnożone x2.
- Jeżeli broń nakłada efekt czasowy, np. krwawienie, efekt jest rozpatrywany jak dwa zastosowania; jeśli efekt odnawia/przedłuża czas, czas zostaje odpowiednio przedłużony dwukrotnie.
- Jeżeli efekt broni zadaje dodatkowe obrażenia, przy Nat 20 te obrażenia również są mnożone x2.

### 5. Skalowanie przeciwników
Poziom I korzysta z wartości bazowych karty.
- Poziom I: bez modyfikatora.
- Poziom II: `+2 KP`, `+2 do trafienia`, `+2 HP`.
- Poziom III: `+3 KP`, `+3 do trafienia`, `+3 HP`.
- Poziom IV: `+4 KP`, `+4 do trafienia`, `+4 HP`.
- Obrażenia przeciwnika nie rosną automatycznie z Poziomem Świata.
- Bossowie i przeciwnicy legendarni mogą mieć własne dodatkowe skalowanie.

### 6. Obrona i wyposażenie
- Zbroja zwiększa KP i może mieć dodatkowe efekty.
- Tarcze, hełmy, pierścienie i inne elementy wyposażenia również mogą zwiększać KP, jeśli karta tak mówi.
- Akcja `Obrona` zastępuje atak i daje na razie `+2 KP` przeciwko najbliższemu atakowi przeciwnika. Po tym ataku bonus znika.
- Nat 20 przeciwnika jest automatycznym trafieniem i ignoruje premię KP z Obrony.
- Po Obronie przeciwnik normalnie wykonuje działanie.
- Bohater może zmienić wyposażenie w walce. Zmiana zużywa całe działanie bohatera w rundzie, po czym przeciwnik normalnie działa.
- Zmiana wyposażenia polega na wybraniu przedmiotu z plecaka; nowy przedmiot zostaje założony, a poprzednio wyposażony wraca do plecaka w ramach jednego działania.

### 7. Pomocnicy i przedmioty
- Pomocnik może pomagać w walce zgodnie ze swoją kartą, np. premią do Walki, trafienia, obrażeń, KP albo innym efektem.
- W walce można używać mikstur, jedzenia, bomb, zwojów i innych dopuszczonych przedmiotów.
- Użycie przedmiotu zastępuje atak bohatera w rundzie; potem przeciwnik normalnie wykonuje działanie.
- Leczenie przedmiotem odnawia HP, nie Rany.
- Ofensywne przedmioty jednorazowe, np. bomby i zwoje, na obecnym etapie trafiają automatycznie bez rzutu na trafienie.
- Ze względu na pewne trafienie takie przedmioty mają być odpowiednio drogie/wartościowe.
- Zużyty przedmiot jednorazowy trafia na stos odrzuconych Przedmiotów.

### 8. Statusy
- System obsługuje statusy, np. zatrucie, krwawienie, ogłuszenie, podpalenie, osłabienie KP.
- Czas statusu określa karta/efekt.
- Ponowne nałożenie tego samego statusu nie zwiększa jego siły; odnawia/przedłuża czas działania.
- Efekty okresowe statusu rozpatruje się na początku rundy postaci dotkniętej statusem, przed jej działaniem.
- Ogłuszenie odbiera całe działanie bohatera w rundzie; przeciwnik normalnie działa.
- Wszystkie statusy bojowe znikają po zakończeniu walki.
- Szczegółową listę statusów dopracujemy później.

### 9. Zdolności przeciwników
- Przeciwnicy mogą mieć specjalne zdolności.
- Częstotliwość i zasady zdolności określa indywidualnie karta przeciwnika.
- Gdy przychodzi runda zdolności specjalnej, przeciwnik najpierw wykonuje rzut sprawdzający, czy specjalny efekt w ogóle się aktywuje.
- Jeśli aktywacja się powiedzie, karta może wymagać kolejnego rzutu określającego konkretny efekt z tabeli wyników.
- Zdolność specjalna zajmuje działanie przeciwnika tak jak normalny atak; nie daje automatycznie dodatkowego darmowego ataku, chyba że karta wyraźnie stanowi inaczej.
- Specjalne zdolności bohaterów zaprojektujemy później.

### 10. Bossowie
- Boss może mieć kilka faz.
- Po przekroczeniu progu HP, np. 50%, nowa faza uruchamia się natychmiast przed kolejnym działaniem bossa.
- Faza może zmieniać statystyki, ataki, zachowanie i zdolności.
- Boss zawsze ma specjalną nagrodę określoną przez kartę/scenariusz/Quest.

### 11. Ucieczka i przekupstwo
- Podstawowe sposoby opuszczenia walki: test `Intrygi` albo przekupstwo za określoną liczbę Złota.
- Wymagania określa karta przeciwnika/walki.
- Nie każda walka pozwala na ucieczkę lub przekupstwo; część blokuje obie opcje.
- Jeżeli dana opcja jest dostępna, jej przycisk jest widoczny w interfejsie walki.
- Przy przekupstwie gracz widzi dokładny koszt, np. `Przekup — 8 Złota`.
- Jeśli gracz nie ma wystarczającej ilości Złota, przycisk przekupstwa pozostaje widoczny, ale jest wyszarzony i nieaktywny.
- Nieudana ucieczka powoduje natychmiastowy atak przeciwnika, po czym walka trwa dalej, jeśli bohater nadal ma HP.
- Po skutecznej ucieczce bohater zostaje na aktualnym heksie i zachowuje pozostałe Akcje.
- Przy ponownej walce po ucieczce albo porażce przeciwnik zaczyna z pełnym HP.

### 12. Walka w Queście
- Przegrana walka będąca etapem Questa dodaje znacznik porażki.
- Quest pozostaje aktywny, o ile jego zasady/liczba porażek go nie kończą.
- W kolejnej turze bohater może ponownie walczyć albo wybrać inną dostępną drogę rozwiązania Questa.

### 13. Informacje o przeciwniku
- Przed walką wszystkie informacje mechaniczne przeciwnika są ukryte.
- Po rozpoczęciu walki gracz widzi wyłącznie aktualne i maksymalne HP przeciwnika.
- KP, premia do trafienia, obrażenia i zdolności pozostają ukryte.
- Dostępność ucieczki/przekupstwa jest komunikowana przez odpowiednie przyciski, a przy przekupstwie widoczny jest koszt.

### 14. Loot, zwycięstwo i pokonani wrogowie
- Karta przeciwnika określa jego loot.
- Po zwycięstwie karta przeciwnika trafia do osobnej talii/stosu `Pokonani wrogowie`, a nie do zwykłego stosu odrzuconych.
- Każdy gracz może posiadać własny stos `Pokonani wrogowie`.
- Quest/Zagrożenie może w przyszłości określić wyjątek.
- Po zwycięstwie bohater zachowuje pozostałe Akcje i może kontynuować turę.
- Wyświetlany jest osobny ekran `Zwycięstwo` z pokonanym przeciwnikiem, lootem/nagrodami oraz stanem bohatera. Po zatwierdzeniu gracz wraca do mapy/Questa/Zagrożenia/Przygody.

## Do dopracowania później
- Pełny system Ran i ich konsekwencji.
- Specjalne efekty zadające Rany bezpośrednio.
- Pełna lista statusów.
- Konkretne zdolności przeciwników, bossów i bohaterów.
- Konkretne pule lootu i wartości nagród.

## Definition of Done
Walka może zostać uruchomiona z Questa, Przygody lub Zagrożenia, przejść przez wszystkie rundy i zakończyć się poprawnym zwycięstwem, porażką albo ucieczką.