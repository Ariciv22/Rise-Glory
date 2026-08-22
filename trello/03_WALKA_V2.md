# 03 — Walka V2

**Status Kanban:** W TRAKCIE — fundament zasad 1–70 zaimplementowany; decyzje 71–130 zapisane, 84 odłożone

## Cel
Kompletna podstawowa walka do alfy Rise & Glory.

## Stan implementacji — 2026-08-19
- [x] HP bohatera i przeciwnika oraz trwałe HP między walkami.
- [x] Ataki k20, KP, Nat 1 i Nat 20.
- [x] Broń: osobna premia do trafienia i obrażenia oraz efekty przy trafieniu.
- [x] Skalowanie przeciwników Poziomem Świata: KP, trafienie i HP.
- [x] Obrona `+2 KP` do początku następnej tury bohatera.
- [x] Zmiana wyposażenia jako działanie w walce.
- [x] Używanie jednorazowych przedmiotów bojowych z automatycznym trafieniem efektu.
- [x] Bazowy silnik statusów i ich czasu działania.
- [x] Bazowy silnik specjalnych zdolności przeciwników z rzutem na trafienie i opcjonalną tabelą efektu.
- [x] Wielofazowi bossowie.
- [x] Ucieczka przez Intrygę oraz osobne przekupstwo.
- [x] Porażka: 1 Rana, 1 HP, utrata Złota, koniec tury, pozostanie na heksie.
- [x] Utrata zakrytego Przedmiotu wyłącznie z plecaka; przedmioty oznaczone jako kluczowe/questowe są chronione.
- [x] Ekran walki ukrywa wszystkie statystyki przeciwnika poza HP.
- [x] Ekran Zwycięstwo i osobny stos `Pokonani wrogowie` gracza.
- [x] Integracja porażki/zwycięstwa z istniejącą walką Questa i Zagrożenia przez wspólny silnik.
- [x] Testy silnika HP, porażki, obrażeń, Obrony, Nat 20, przedmiotów i przekupstwa.
- [ ] Do uzupełniania wraz z contentem: konkretne karty statusów, zdolności przeciwników, bossowie, loot i wartości przedmiotów.
- [ ] System konsekwencji Ran jest doprecyzowany projektowo w zasadach 121–130, ale wymaga implementacji i ustalenia brakujących wartości liczbowych.

## Zatwierdzone zasady walki

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
- Rany leczy się w odpowiednich lokacjach. Szczegółowy system konsekwencji Ran opisują zasady 121–130.
- Zwykłe ataki nie zadają Ran bezpośrednio z pominięciem HP. Specjalne zdolności i efekty mogą zadawać Rany bezpośrednio, jeśli tekst karty wyraźnie tak stanowi.

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
- Akcja `Obrona` zastępuje atak i daje na razie `+2 KP` do początku następnej tury bohatera w walce. Premia obejmuje wszystkie ataki przeciwnika wykonane przed tym momentem, również kilka ataków w ramach jednej zdolności.
- Nat 20 przeciwnika jest automatycznym trafieniem i ignoruje premię KP z Obrony.
- Po Obronie przeciwnik normalnie wykonuje działanie.
- Bohater może zmienić wyposażenie w walce. Zmiana zużywa całe działanie bohatera w rundzie, po czym przeciwnik normalnie działa.
- Zmiana wyposażenia polega na wybraniu przedmiotu z plecaka; nowy przedmiot zostaje założony, a poprzednio wyposażony wraca do plecaka w ramach jednego działania.

### 7. Pomocnicy i przedmioty
- Pomocnik może pomagać w walce zgodnie ze swoją kartą, np. premią do Walki, trafienia, obrażeń, KP albo innym efektem.
- W walce można używać mikstur, jedzenia, bomb, zwojów i innych dopuszczonych przedmiotów.
- Użycie przedmiotu zastępuje atak bohatera w rundzie; potem przeciwnik normalnie wykonuje działanie.
- Zwykłe leczenie przedmiotem odnawia HP, nie Rany. Specjalne, rzadkie lub drogie Przedmioty i Pomocnicy mogą usuwać Rany, jeśli ich karta wyraźnie tak stanowi.
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
- Częstotliwość i moment użycia zdolności określa indywidualnie karta przeciwnika.
- Nie wykonuje się osobnego rzutu sprawdzającego, czy specjalna zdolność w ogóle się aktywuje.
- Gdy zgodnie z kartą przychodzi moment specjalnego ataku, przeciwnik od razu wykonuje normalny rzut na trafienie przeciw KP bohatera.
- Jeśli specjalna zdolność nie jest atakiem, np. leczeniem własnego HP, rozpatruje się ją zgodnie z tekstem karty bez rzutu na trafienie.
- Karta może wymagać dodatkowego rzutu wyłącznie wtedy, gdy sama zdolność posiada tabelę możliwych efektów.
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

### 15. Doprecyzowania 71–80
- **71. Statusy na przeciwniku:** normalne statusy bojowe mogą działać również na przeciwników, a nie wyłącznie na bohatera.
- **72. Specjalne ataki przeciwnika:** specjalny atak nie trafia automatycznie. Jeśli specjalna zdolność jest atakiem, przeciwnik musi wykonać normalny rzut na trafienie przeciw KP bohatera. `Obrona +2 KP` działa również przeciw takiemu specjalnemu atakowi.
- **73. Śmierć od statusu:** jeśli okresowy efekt statusu na początku rundy przeciwnika obniży jego HP do `0`, przeciwnik ginie natychmiast i nie wykonuje już działania w tej rundzie.
- **74. Limit leczenia HP:** leczenie nie może podnieść aktualnego HP powyżej `max_hp`. Nadmiar leczenia przepada.
- **75. Loot przy pełnym plecaku:** jeśli bohater nie ma miejsca na zdobyty Przedmiot, może odrzucić własny Przedmiot z plecaka, aby zrobić miejsce, albo pozostawić/porzucić nowy loot.
- **76. Przekupstwo:** skuteczne przekupstwo kończy walkę bez zwycięstwa. Bohater płaci koszt, nie otrzymuje lootu, a przeciwnik nie trafia do stosu `Pokonani wrogowie`.
- **77. Ucieczka:** skuteczna ucieczka również nie daje lootu i przeciwnik nie jest uznawany za pokonanego ani nie trafia do `Pokonanych wrogów`.
- **78. Źródło ostatnich obrażeń:** zabicie przeciwnika bombą, zwojem, statusem albo innym legalnym efektem jest pełnoprawnym zwycięstwem. Bohater otrzymuje normalny loot, a przeciwnik trafia do `Pokonanych wrogów`.
- **79. Kilka progów fazy bossa naraz:** jeśli jeden efekt obrażeń przekroczy kilka progów faz bossa, wszystkie przekroczone progi są rozpatrywane i boss od razu przechodzi do końcowej osiągniętej fazy przed swoim następnym działaniem.
- **80. Odkrywanie specjalnych ataków:** po pierwszym użyciu specjalnego ataku przez przeciwnika atak staje się ujawniony w interfejsie jako poznany; gracz widzi od tego momentu, że przeciwnik posiada ten nowy atak.

### 16. Doprecyzowania 81–90
- **81. Nat 1 / Nat 20 na specjalnym ataku:** specjalny atak przeciwnika korzystający z rzutu na trafienie podlega normalnym zasadom krytycznym: Nat 1 oznacza automatyczne pudło, a Nat 20 automatyczne trafienie.
- **82. Krytyczne obrażenia przeciwnika:** Nat 20 przeciwnika podwaja obrażenia jego ataku.
- **83. Krytyk specjalnego ataku:** jeśli specjalny atak przy trafieniu zadaje obrażenia i nakłada dodatkowy efekt, Nat 20 podwaja zarówno obrażenia, jak i rozpatrzenie efektu zgodnie z zasadami krytyka.
- **84. Odporności/immunitety przeciwników:** decyzja odłożona do późniejszego projektowania konkretnych przeciwników i statusów.
- **85. Ujawnianie odporności:** jeśli system odporności zostanie wykorzystany i bohater pierwszy raz spróbuje nałożyć status, na który przeciwnik jest odporny, odporność zostaje wtedy odkryta i od tej chwili jest widoczna w UI tej walki.
- **86. Ogłuszenie przeciwnika:** ogłuszony przeciwnik całkowicie traci swoje działanie w rundzie, analogicznie do ogłuszonego bohatera.
- **87. Wiele statusów naraz:** jedna postać może posiadać jednocześnie kilka różnych statusów, np. Krwawienie, Zatrucie, Podpalenie i Osłabienie KP.
- **88. Kolejność statusów:** jeśli kilka statusów rozpatruje się w tym samym momencie, ich efekty są wykonywane w kolejności ich nałożenia.
- **89. Leczenie przeciwników:** przeciwnicy i bossowie mogą posiadać specjalne zdolności leczące własne HP. Leczenie nie może przekroczyć ich `max_hp`.
- **90. Porzucony loot i odrzucone rzeczy:** loot pozostawiony po zwycięstwie oraz rzeczy odrzucone przez bohatera przy robieniu miejsca nie przepadają. Zostają na aktualnym heksie w mieszku i mogą zostać później podniesione zgodnie z zasadami obsługi mieszka.

### 17. Doprecyzowania 91–100
- **91. Podnoszenie mieszka:** podnoszenie rzeczy z mieszka znajdującego się na heksie jest darmowe i nie kosztuje Akcji.
- **92. Własność mieszka:** zawartość mieszka może podnieść dowolny bohater, nie tylko bohater, który pozostawił tam przedmioty lub loot.
- **93. Kilka mieszków na jednym heksie:** osobne źródła pozostawionych rzeczy tworzą osobne mieszki; nie są automatycznie łączone w jeden wspólny mieszek.
- **94. Czas istnienia mieszka:** mieszek pozostaje na heksie bez limitu czasu, aż jego zawartość zostanie zabrana.
- **95. Złoto z lootu:** Złoto nie zajmuje miejsca w plecaku. Po zwycięstwie może zostać dodane do bohatera niezależnie od limitu Przedmiotów i od tego, czy część fizycznego lootu pozostaje w mieszku.
- **96. Status bohatera a zakończenie walki:** status okresowy bohatera jest rozpatrywany dopiero na początku jego rzeczywistej rundy. Jeśli przeciwnik zostanie pokonany wcześniej, np. w swojej własnej rundzie przez legalny efekt bohatera, walka kończy się i kolejna runda bohatera już nie następuje, więc jego status nie zadaje kolejnego obrażenia. Po zakończeniu walki statusy bojowe znikają. Jeśli jednak runda bohatera faktycznie się rozpocznie i obrażenia statusowe obniżą jego HP do `0`, następuje normalna porażka.
- **97. Leczenie przeciwnika jako działanie:** specjalna zdolność leczenia własnego HP zużywa całe działanie przeciwnika; przeciwnik nie wykonuje wtedy normalnego ataku, chyba że jego karta wyraźnie stanowi inaczej.
- **98. Atak wielokrotny:** specjalna zdolność może wykonywać kilka osobnych ataków w jednym działaniu, np. dwa ataki. Każdy z nich wykonuje osobny rzut na trafienie i jest rozpatrywany osobno.
- **99. Obrona przeciw atakowi wielokrotnemu:** `Obrona +2 KP` nie znika po pierwszym ataku. Trwa do początku następnej tury bohatera w walce, dzięki czemu obejmuje wszystkie ataki przeciwnika wykonane wcześniej w tej samej rundzie. Ta zasada zastępuje wcześniejsze założenie, że Obrona działa tylko przeciw najbliższemu pojedynczemu atakowi.
- **100. Usuwanie statusów:** Przedmioty i zdolności mogą usuwać statusy podczas walki, jeśli ich efekt tak stanowi. Użycie Przedmiotu usuwającego status normalnie zużywa całe działanie bohatera w rundzie.

### 18. Doprecyzowania 101–110
- **101. Pusty mieszek:** po zabraniu ostatniej rzeczy mieszek natychmiast znika z heksu.
- **102. Częściowe podnoszenie:** bohater może zabrać z mieszka tylko wybrane rzeczy, a pozostałą zawartość zostawić na później.
- **103. Mieszek a walka:** rzeczy z mieszka można podnosić i przekładać wyłącznie poza walką, z normalnego widoku mapy.
- **104. Przenoszenie rzeczy między mieszkiem a bohaterem:** bohater znajdujący się na heksie z mieszkiem może swobodnie przenosić rzeczy pomiędzy mieszkiem a swoim ekwipunkiem/plecakiem. Może odłożyć własny Przedmiot do mieszka, zrobić miejsce i od razu zabrać inną rzecz z tego mieszka; takie przekładanie nie kosztuje Akcji.
- **105. Kontrataki i reakcje:** Przedmioty, Pomocnicy i zdolności mogą posiadać efekty reaktywne, np. „gdy przeciwnik cię trafi, zadaj mu 1 obrażenie”.
- **106. Zabicie reakcją:** jeśli legalny kontratak lub reakcja obniży HP przeciwnika do `0` w jego własnej turze, walka kończy się natychmiast jako zwycięstwo bohatera.
- **107. Wielokrotny atak a porażka:** jeśli jeden z kolejnych ataków w ramach wielokrotnego ataku obniży HP bohatera do `0`, walka kończy się natychmiast; pozostałe ataki nie są już wykonywane.
- **108. Statusy i Ogłuszenie:** na początku rundy najpierw rozpatruje się efekty statusów przypadające na ten moment, a dopiero potem Ogłuszenie odbiera działanie postaci, jeśli nadal żyje i walka trwa.
- **109. Zmiana fazy bossa:** wejście w nową fazę może leczyć bossa albo zwiększyć jego `max_hp`, jeśli konkretna karta lub scenariusz tak stanowi.
- **110. Faza od obrażeń statusowych:** jeśli obrażenia statusowe na początku rundy bossa przekroczą próg fazy, nowa faza uruchamia się natychmiast jeszcze przed działaniem bossa.

### 19. Doprecyzowania 111–120
- **111. Moment reakcji po trafieniu:** kontratak lub reakcja uruchamia się dopiero po pełnym rozpatrzeniu trafienia przeciwnika, w tym obrażeń i efektów nakładanych przez ten atak.
- **112. Reakcja przy 0 HP:** jeśli atak przeciwnika obniży HP bohatera do `0`, walka kończy się porażką i reakcje/kontrataki bohatera z tego trafienia już się nie uruchamiają.
- **113. Kilka reakcji na jedno trafienie:** jeśli bohater posiada kilka legalnych reakcji wyzwalanych tym samym trafieniem, np. z Tarczy i Pomocnika, wszystkie mogą zostać uruchomione przez to samo zdarzenie.
- **114. Pudło specjalnego ataku:** jeśli specjalny atak przeciwnika nie trafi, efekty zależne od trafienia, np. Krwawienie, również nie zostają nałożone.
- **115. Brak osobnego rzutu aktywacji:** nie wykonuje się dodatkowego rzutu sprawdzającego, czy specjalna zdolność się aktywuje. Gdy przychodzi jej moment zgodnie z kartą, specjalny atak od razu wykonuje rzut na trafienie. Ta zasada zastępuje wcześniejsze założenie o osobnym rzucie aktywacji i ma ograniczyć liczbę rzutów oraz obliczeń.
- **116. Krytyki w ataku wielokrotnym:** każdy atak składający się na zdolność wielokrotną ma własny rzut i własne Nat 1/Nat 20. Nat 20 podwaja wyłącznie ten konkretny atak i jego efekt zgodnie z zasadami krytyka, a nie całą zdolność wielokrotną.
- **117. Nat 1 w ataku wielokrotnym:** Nat 1 powoduje automatyczne pudło tylko konkretnego ataku, na którym wypadło. Pozostałe ataki w tej samej zdolności są dalej wykonywane, o ile walka wcześniej się nie zakończyła.
- **118. Leczenie przy zmianie fazy:** nowa faza bossa może zwiększyć `max_hp` oraz jednocześnie uleczyć bossa lub ustawić jego HP zgodnie z efektem fazy, ale wyłącznie wtedy, gdy konkretna karta/scenariusz wyraźnie tak stanowi.
- **119. Ujawnianie nowej fazy i ataków:** wejście w nową fazę nie ujawnia automatycznie graczowi jej mechaniki ani nowych ataków. Nowy atak, efekt lub zdolność staje się widoczna wtedy, gdy przeciwnik faktycznie jej użyje.
- **120. Log walki:** ekran walki posiada przewijany log pokazujący rozpatrzone zdarzenia, m.in. rzuty, trafienia i pudła, obrażenia, statusy, leczenie, użyte fazy/zdolności bossa oraz reakcje. Log nie ujawnia ukrytych mechanik, dopóki nie zostaną faktycznie użyte lub odkryte.

### 20. Doprecyzowania 121–130 — Rany
- **121. Limit Ran:** bohater może posiadać maksymalnie `4 Rany`. Otrzymanie czwartej Rany uruchamia pełne Pokonanie.
- **122. Konsekwencje Ran:** przy `1 Ranie` bohater otrzymuje `-1 do wszystkich testów`. Przy `2 Ranach` zachowuje karę za pierwszą Ranę i dodatkowo ma obniżone maksymalne HP; dokładna wartość obniżenia pozostaje do ustalenia. Przy `3 Ranach` kara do wszystkich testów wynosi `-2`, bohater nadal ma obniżone maksymalne HP i dodatkowo otrzymuje `-2 do Ruchu`.
- **123. Czwarta Rana:** jeżeli bohater posiada 3 Rany i otrzyma kolejną, natychmiast zostaje Pokonany i traci przytomność. Nie może już wykonać żadnego dalszego działania w bieżącej turze, wszystkie niewykorzystane Akcje przepadają, a tura przechodzi do kolejnego gracza. Bohater nie wraca na pole startowe.
- **124. Stan nieprzytomności i następna tura:** po otrzymaniu czwartej Rany bohater pozostaje nieprzytomny na dokładnie tym samym polu/heksie do początku swojej następnej tury. Dopiero na początku tej następnej tury licznik Ran zostaje cofnięty z `4` do `3`, bohater odzyskuje przytomność z `1 HP` i pozostaje na tym samym heksie.
- **125. Leczenie Ran w lokacji:** Rany można leczyć w odpowiednich lokacjach. Cena leczenia jednej Rany rośnie wraz z Poziomem Świata; dokładny cennik dla poziomów I–IV pozostaje do ustalenia.
- **126. Leczenie Ran przez Przedmioty i Pomocników:** specjalne, odpowiednio rzadkie lub drogie Przedmioty oraz Pomocnicy mogą usuwać Rany, jeżeli ich karta wyraźnie tak stanowi. Mogą działać również podczas walki, jeśli ich karta na to pozwala.
- **127. Rana po trafieniu:** przeciwnik może posiadać zdolność, która po skutecznym trafieniu zadaje bohaterowi bezpośrednio Ranę, nawet jeśli HP bohatera nie spadło do `0`.
- **128. Rana bez rzutu na trafienie:** karta lub efekt może zadać Ranę bez rzutu na trafienie, jeżeli tekst efektu wprost tak stanowi. Taki efekt nie jest sprawdzany przeciw KP.
- **129. Nadmiar Ran:** jeśli bohater ma 3 Rany, a pojedynczy efekt miałby zadać więcej niż 1 Ranę, czwarta Rana natychmiast uruchamia Pokonanie, a wszystkie Rany ponad limit są ignorowane.
- **130. Rozliczenie pełnego Pokonania:** w chwili otrzymania czwartej Rany bohater zostaje nieprzytomny na swoim aktualnym heksie i natychmiast traci możliwość dalszego działania; jego tura kończy się, a niewykorzystane Akcje przepadają. Traci Złoto zgodnie z zasadą porażki zależną od Poziomu Świata oraz 1 losowy, niezałożony Przedmiot wyłącznie z plecaka; założony ekwipunek oraz chronione Przedmioty kluczowe/questowe nie biorą udziału w losowaniu. Licznik Ran pozostaje na `4` przez okres nieprzytomności. Dopiero na początku następnej tury tego bohatera Rany cofają się do `3`, bohater odzyskuje przytomność z `1 HP` i nadal pozostaje na tym samym heksie.

## Do dopracowania później
- Dokładna wartość obniżenia `max_hp` przy 2 i 3 Ranach.
- Dokładny cennik leczenia Ran na Poziomach Świata I–IV.
- Pełna lista statusów.
- Konkretne zdolności przeciwników, bossów i bohaterów.
- Konkretne pule lootu i wartości nagród.
- Decyzja, czy konkretni przeciwnicy mogą posiadać odporności/immunitety na statusy.

## Definition of Done
Walka może zostać uruchomiona z Questa, Przygody lub Zagrożenia, przejść przez wszystkie rundy i zakończyć się poprawnym zwycięstwem, porażką albo ucieczką.