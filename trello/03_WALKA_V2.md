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
- Każdy zwykły atak bohatera korzysta ze statystyki `Walka`.
- Cała walka, niezależnie od liczby rund, kosztuje 1 Akcję.
- Zarówno bohater, jak i przeciwnik posiadają HP.
- Bohater posiada dodatkowo osobny system Ran.
- Naturalne 20 podczas ataku oznacza 2 trafienia i dwukrotne rozpatrzenie obrażeń.
- Naturalne 1 podczas ataku oznacza automatyczne pudło.
- Walka nie posiada maksymalnego limitu rund. Trwa aż do pokonania jednej ze stron albo skutecznego opuszczenia walki, jeśli dana walka na to pozwala.
- Mechanicznie walka zawsze odbywa się przeciwko jednemu przeciwnikowi.
- Karta i grafika przeciwnika mogą przedstawiać grupę, np. bandę bandytów, watahę lub oddział, ale mechanicznie cała grupa jest rozpatrywana jako jeden przeciwnik z jedną pulą statystyk i HP.

### HP bohatera i Rany

- Bazowe maksymalne HP bohatera wynosi `10 HP`.
- Atrybuty, wyposażenie, przedmioty i inne efekty mogą zwiększać maksymalne HP bohatera.
- Zwykłe ataki przeciwników zadają obrażenia w HP, tak samo jak ataki bohatera zadają obrażenia w HP przeciwnika.
- Jeżeli HP bohatera spadnie do `0`, bohater traci przytomność i walka natychmiast się kończy porażką bohatera.
- Po utracie przytomności bohater otrzymuje `1 Ranę`.
- Bohater pozostaje na heksie, na którym został pokonany. Nie wraca automatycznie do pola startowego ani lokacji.
- Po odzyskaniu przytomności bohater ma `1 HP`.
- Utrata przytomności natychmiast kończy całą turę bohatera. Wszystkie niewykorzystane Akcje przepadają.
- Rana jest osobnym, trwałym stanem bohatera i będzie wpływać na różne elementy gry; dokładny system Ran zostanie opisany później w osobnym etapie projektowym.
- W podstawowym systemie walki nie stosujemy obecnie zwykłych ataków zadających Ranę bezpośrednio z pominięciem HP. Taka możliwość może pojawić się później jako specjalny efekt.
- Aktualne HP bohatera pozostaje między walkami. Przykładowo bohater kończący walkę z `4/10 HP` nadal ma `4/10 HP` po powrocie do mapy.
- HP i Rany są leczone osobno.
- Jedzenie, mikstury, odpoczynek oraz odpowiednie efekty mogą odnawiać HP.
- Rany są leczone w odpowiednich lokacjach zgodnie z osobnym systemem leczenia Ran.
- Wyleczenie Rany nie odnawia automatycznie HP.
- Odnowienie HP nie usuwa automatycznie Ran.

### Konsekwencje przegranej walki

- Po zejściu do `0 HP` bohater otrzymuje 1 Ranę, odzyskuje przytomność z `1 HP`, pozostaje na aktualnym heksie i jego tura natychmiast się kończy.
- Bohater traci Złoto zależnie od Poziomu Świata: Poziom I — `1 Złoto`, Poziom II — `2 Złota`, Poziom III — `3 Złota`, Poziom IV — `4 Złota`.
- Bohater dodatkowo traci `1 losowy Przedmiot` ze swojego ekwipunku.
- Przy losowaniu utraconego Przedmiotu karty ekwipunku są zasłaniane, a gracz wybiera jedną kartę bez wiedzy, jaki Przedmiot wskazuje.
- Wybrany w ciemno Przedmiot trafia na odpowiedni stos odrzuconych.
- Przegrana nie przenosi bohatera z aktualnego heksu.

### Broń i obrażenia

- Każda broń posiada dwa osobne parametry: premię do trafienia oraz wartość obrażeń.
- Przykładowy zapis broni może wyglądać jak `+2 do trafienia / 2 obrażenia`.
- Atak bez broni zadaje bazowo 1 obrażenie i nie otrzymuje premii broni.
- Przeciwnik zadaje stałą liczbę obrażeń HP określoną na swojej karcie. Podstawowe obrażenia przeciwnika nie są losowane jako zakres.

### Skalowanie przeciwników Poziomem Świata

Poziom Świata I korzysta z bazowych statystyk przeciwnika zapisanych na jego karcie. Od Poziomu Świata II przeciwnicy otrzymują dodatkowe modyfikatory:

- Poziom Świata I: wartości bazowe, bez dodatkowego modyfikatora.
- Poziom Świata II: `+2 KP`, `+2 do trafienia`, `+2 HP`.
- Poziom Świata III: `+3 KP`, `+3 do trafienia`, `+3 HP`.
- Poziom Świata IV: `+4 KP`, `+4 do trafienia`, `+4 HP`.

To skalowanie zastępuje wcześniejszy wariant skalowania samego HP `+2/+4/+6/+8`.

- Na obecnym etapie Poziom Świata skaluje wyłącznie KP, premię do trafienia i HP przeciwnika.
- Stała liczba obrażeń HP zadawanych przez przeciwnika nie otrzymuje automatycznego bonusu z Poziomu Świata.
- Przeciwnicy legendarni i bossowie mogą mieć dodatkowe własne skalowanie określone osobno.

### Zbroja i obrona bohatera

- Zbroja w podstawowym założeniu zwiększa KP bohatera.
- Zbroje mogą również posiadać dodatkowe efekty poza premią do KP.
- Inne elementy wyposażenia defensywnego, takie jak tarcze, hełmy, pierścienie lub inne przedmioty, również mogą zwiększać KP, jeśli ich karta tak stanowi.
- Premie i efekty defensywne wynikają z konkretnej karty przedmiotu.

### Akcja Obrona

- Bohater może zamiast zwykłego ataku wybrać działanie `Obrona`.
- Obrona zużywa działanie bohatera w danej rundzie walki.
- Obrona zwiększa defensywę bohatera na działanie przeciwnika w tej rundzie, np. przez czasową premię do KP.
- Dokładna wartość premii i ewentualne dodatkowe warianty Obrony zostaną ustalone później.
- Po wykonaniu Obrony przeciwnik normalnie wykonuje swoje działanie.

### Zmiana wyposażenia podczas walki

- Bohater może zmieniać wyposażenie podczas trwającej walki.
- Zmiana wyposażenia zużywa całe działanie bohatera w danej rundzie walki.
- Po zmianie wyposażenia bohater nie wykonuje normalnego ataku w tej samej rundzie, chyba że konkretny efekt wyraźnie stanowi inaczej.
- Po zmianie wyposażenia przeciwnik normalnie wykonuje swoje działanie w tej rundzie.

### Pomocnicy w walce

- Pomocnik może wspierać bohatera podczas walki.
- Rodzaj pomocy wynika z karty Pomocnika i może obejmować np. premię do Walki, trafienia, obrażeń, KP albo inny efekt bojowy.

### Przedmioty używane w walce

- Podczas walki można używać jednorazowych przedmiotów i efektów, takich jak mikstury, bomby, zwoje, jedzenie lub inne przedmioty dopuszczone przez ich kartę.
- Użycie takiego przedmiotu zużywa działanie bohatera w danej rundzie walki zamiast wykonania ataku.
- Po wykorzystaniu przedmiotu bohater nie wykonuje dodatkowo normalnego ataku w tej samej rundzie, chyba że konkretny efekt wyraźnie stanowi inaczej.
- Po użyciu przedmiotu przeciwnik normalnie wykonuje swoje działanie w tej rundzie.
- Przedmioty i efekty lecznicze używane w trakcie walki leczą HP, a nie Rany.
- Rany nie są leczone w trakcie walki przez zwykłe mikstury/jedzenie; leczenie Ran odbywa się w odpowiednich lokacjach zgodnie z zasadami gry.

### Efekty statusowe

- System walki będzie obsługiwał efekty statusowe.
- Do możliwych statusów należą m.in. zatrucie, krwawienie, ogłuszenie, podpalenie, osłabienie KP i inne podobne efekty.
- Czas działania statusu określa karta lub efekt, który go nakłada, np. karta broni może wskazywać konkretną liczbę rund działania.
- Ponowne nałożenie tego samego statusu nie kumuluje jego siły; odnawia czas trwania efektu.
- Ogłuszenie powoduje utratę całego działania bohatera w danej rundzie. Przeciwnik nadal wykonuje swój normalny atak.
- Wszystkie statusy bojowe znikają po zakończeniu walki.
- Dokładna lista statusów, sposób nakładania i zdejmowania zostaną dopracowane osobno.

### Zdolności specjalne przeciwników

- Przeciwnicy będą mogli posiadać specjalne zdolności i dodatkowe efekty.
- Szczegółowy system zdolności zostanie rozwinięty później.
- Ogólny kierunek: co określoną liczbę rund przeciwnik może wykonywać rzut uruchamiający dodatkowy efekt, a wynik rzutu kością określa, jaki efekt wystąpił.
- Częstotliwość, warunek aktywacji oraz sposób działania zdolności są określane indywidualnie przez kartę danego przeciwnika.

### Zdolności bojowe bohaterów

- Dodatkowe specjalne zdolności bojowe bohaterów zostaną zaprojektowane później.
- Na obecnym etapie podstawowa walka opiera się na statystyce Walka, ekwipunku, Pomocnikach, przedmiotach i podstawowych działaniach bojowych.

### Bossowie i fazy walki

- Bossowie mogą posiadać kilka faz walki.
- Przejście do kolejnej fazy może następować np. po spadku HP poniżej określonego progu.
- Jeżeli atak bohatera obniży HP bossa poniżej progu kolejnej fazy, boss przechodzi do nowej fazy natychmiast, jeszcze przed swoim najbliższym działaniem.
- Kolejna faza może zmieniać zdolności, zachowanie, sposób ataku, statystyki lub inne zasady bossa zgodnie z jego kartą.

### Ucieczka i przekupstwo

- Nieudana próba ucieczki powoduje natychmiastowy atak przeciwnika, po czym walka trwa dalej, jeśli bohater nie został pokonany.
- Podstawowe sposoby opuszczenia walki to test Intrygi albo przekupienie przeciwnika określoną liczbą Złota.
- Wymagany poziom testu Intrygi i koszt przekupstwa określa karta przeciwnika lub konkretnej walki.
- Nie każda walka pozwala na ucieczkę.
- Nie każda walka pozwala na przekupstwo.
- Niektóre walki mogą całkowicie blokować zarówno ucieczkę, jak i przekupienie przeciwnika.
- Jeśli bohater skutecznie ucieknie i później ponownie rozpocznie walkę z tym samym przeciwnikiem, przeciwnik rozpoczyna nową walkę z pełnym HP.
- Jeśli bohater zostanie pokonany, ten sam przeciwnik również odzyskuje pełne HP przed kolejną próbą walki, niezależnie od tego, czy podejmie ją ten sam czy inny bohater.
- Po skutecznej ucieczce walka się kończy, bohater pozostaje na aktualnym heksie i może normalnie wykorzystać pozostałe Akcje swojej tury.

### Walka jako część Questa

- Jeżeli bohater przegrywa walkę będącą etapem Questa, Quest otrzymuje znacznik porażki zgodnie z ogólnym systemem porażek Questów.
- Po odzyskaniu przytomności i rozpoczęciu kolejnej swojej tury bohater może ponownie podjąć walkę.
- Jeżeli Quest udostępnia inne możliwe kroki lub drogi rozwiązania, bohater może zamiast ponownej walki wybrać inną dostępną drogę.
- Sama porażka w walce nie wymusza automatycznego porzucenia całego Questa, o ile nie nastąpiła kończąca Quest liczba porażek albo karta nie stanowi inaczej.

### Informacje o przeciwniku

- Przed rozpoczęciem walki wszystkie statystyki i informacje mechaniczne przeciwnika są ukryte.
- Gracz nie zna przed walką m.in. HP, KP, premii do trafienia, obrażeń, możliwości ucieczki lub przekupstwa ani specjalnych zdolności przeciwnika.
- Sposób ujawniania informacji już podczas samej walki zostanie doprecyzowany osobno.

### Loot i bossowie

- Przeciwnicy są reprezentowani przez karty potworów/przeciwników.
- Karta przeciwnika określa loot możliwy lub przyznawany po jego pokonaniu.
- Boss zawsze posiada specjalną nagrodę poza zwykłym rozstrzygnięciem walki; dokładny rodzaj nagrody określa karta bossa lub powiązany scenariusz/Quest.

### Ekran zakończenia walki

- Po zwycięstwie wyświetlany jest osobny ekran `Zwycięstwo`.
- Ekran pokazuje pokonanego przeciwnika, otrzymany loot i nagrody oraz aktualny stan bohatera, w tym istotne Rany.
- Statusy bojowe są już usunięte w momencie zakończenia walki.
- Dopiero po zatwierdzeniu ekranu gracz wraca do odpowiedniego kontekstu: mapy, Questa, Zagrożenia albo Przygody.

## Punkty do działania

- [ ] HP przeciwnika.
- [ ] HP bohatera — bazowo 10, z możliwością zwiększania maksimum.
- [ ] Trwałe zachowanie aktualnego HP bohatera między walkami.
- [ ] Utrata przytomności przy 0 HP i natychmiastowe zakończenie walki.
- [ ] Przyznanie 1 Rany po utracie przytomności.
- [ ] Bohater po porażce pozostaje na aktualnym heksie i odzyskuje przytomność z 1 HP.
- [ ] Utrata przytomności kończy całą turę i usuwa pozostałe Akcje.
- [ ] Utrata Złota po porażce zależna od Poziomu Świata.
- [ ] Losowa utrata 1 Przedmiotu z ekwipunku po porażce przez wybór zakrytej karty.
- [ ] Osobny system leczenia HP oraz Ran.
- [ ] KP przeciwnika.
- [ ] Atak bohatera.
- [ ] Każdy zwykły atak korzysta ze statystyki Walka.
- [ ] Atak przeciwnika.
- [ ] Obrażenia bohatera w HP przeciwnika.
- [ ] Stałe obrażenia HP przeciwnika określane na karcie.
- [ ] Rany bohatera — szczegółowy system do zaprojektowania później.
- [ ] Każda broń posiada osobną premię do trafienia i wartość obrażeń.
- [ ] Atak bez broni zadaje 1 obrażenie bez premii broni.
- [ ] Zbroja określa KP bohatera i może posiadać dodatkowe efekty.
- [ ] Obsłużyć premie do KP z innych elementów wyposażenia, np. tarczy, hełmu lub pierścienia.
- [ ] Obsłużyć akcję Obrona zamiast ataku.
- [ ] Ustalić dokładną premię i warianty akcji Obrona.
- [ ] Obsłużyć zmianę wyposażenia podczas walki jako całe działanie bohatera w rundzie.
- [ ] Po zmianie wyposażenia przeciwnik wykonuje normalne działanie.
- [ ] Obsłużyć bojowe efekty Pomocników.
- [ ] Obsłużyć używanie przedmiotów jednorazowych podczas walki zamiast ataku bohatera w danej rundzie.
- [ ] Po użyciu przedmiotu przeciwnik wykonuje normalne działanie.
- [ ] Przedmioty lecznicze w walce leczą HP, nie Rany.
- [ ] Obsłużyć leczenie HP przez jedzenie, mikstury, odpoczynek i efekty.
- [ ] Obsłużyć system statusów.
- [ ] Czas statusu określany przez kartę/efekt.
- [ ] Ponowne nałożenie statusu odnawia jego czas zamiast kumulować siłę.
- [ ] Ogłuszenie odbiera działanie bohatera w rundzie.
- [ ] Wszystkie statusy bojowe znikają po zakończeniu walki.
- [ ] Obsłużyć Nat 20.
- [ ] Obsłużyć Nat 1.
- [ ] Kolejne rundy walki bez sztywnego limitu rund.
- [ ] Mechanicznie zawsze jeden przeciwnik; grupa może być przedstawiona jako jedna karta/grafika.
- [ ] Pokonanie przeciwnika.
- [ ] Pokonanie bohatera przez zejście do 0 HP.
- [ ] Ucieczka.
- [ ] Ucieczka poprzez test Intrygi.
- [ ] Przekupstwo za Złoto.
- [ ] Obsłużyć walki bez możliwości ucieczki i przekupstwa.
- [ ] Nieudana ucieczka uruchamia natychmiastowy atak przeciwnika.
- [ ] Po ucieczce przeciwnik przy kolejnej walce ma pełne HP.
- [ ] Po pokonaniu bohatera przeciwnik przy kolejnej walce ma pełne HP.
- [ ] Po skutecznej ucieczce bohater pozostaje na heksie i zachowuje pozostałe Akcje.
- [ ] Cała walka kosztuje 1 Akcję.
- [ ] Przegrana walki w Queście dodaje znacznik porażki.
- [ ] Po porażce Quest może pozwalać na ponowną walkę lub wybór innego dostępnego kroku.
- [ ] Wszystkie informacje mechaniczne przeciwnika są ukryte przed rozpoczęciem walki.
- [ ] Doprecyzować ujawnianie informacji o przeciwniku już podczas walki.
- [ ] Specjalne zdolności bojowe bohaterów — projekt późniejszy.
- [ ] Nagrody po walce.
- [ ] Loot określany przez kartę przeciwnika.
- [ ] Walka jako etap Questa.
- [ ] Walka jako część Zagrożenia.
- [ ] Walka jako część Przygody.
- [ ] Skalowanie przeciwników Poziomem Świata: KP, trafienie i HP.
- [ ] Zdolności specjalne przeciwników aktywowane zgodnie z regułą na karcie.
- [ ] Bossowie.
- [ ] Wieloetapowe fazy bossów.
- [ ] Natychmiastowe przejście bossa do nowej fazy po przekroczeniu progu HP.
- [ ] Boss posiada specjalną nagrodę.
- [ ] Przeciwnicy legendarni.
- [ ] Czytelny ekran zakończenia walki.
- [ ] Ekran Zwycięstwo z lootem, nagrodami i stanem bohatera.
- [ ] Przygotować podstawową pulę przeciwników.
- [ ] Przygotować przynajmniej jednego bossa testowego.
- [ ] Przygotować punkt integracji z Kroniką Świata dla ważnych walk.

## Do dopracowania później

- Szczegółowe konsekwencje i działanie systemu Ran.
- Co dzieje się z losową utratą Przedmiotu, jeśli bohater nie posiada żadnego kwalifikującego się Przedmiotu.
- Czy wyposażone aktualnie Przedmioty również wchodzą do losowania utraty po porażce.
- Ewentualne specjalne efekty zadające Rany bezpośrednio z pominięciem HP.
- Dokładna wartość i warianty akcji Obrona.
- Dokładna lista i pula specjalnych efektów przeciwników.
- Dokładne tabele/rzuty określające dodatkowe efekty podczas walki.
- Dokładna lista statusów i zasady ich działania.
- Indywidualne zdolności bossów i przeciwników legendarnych.
- Specjalne zdolności bojowe bohaterów.
- Sposób ujawniania statystyk i zdolności przeciwnika już po rozpoczęciu walki.
- Konkretne pule lootu i wartości nagród.

## Definition of Done

Walka może zostać uruchomiona z Questa, Przygody lub Zagrożenia, przejść przez wszystkie rundy i zakończyć się poprawną nagrodą, porażką albo ucieczką.