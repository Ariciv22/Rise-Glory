# 01 — Żywy Świat: Zagrożenia i problemy na mapie

**Status Kanban:** W TRAKCIE

## Cel

Wydarzenia Świata mają rzeczywiście zmieniać planszę. Część wydarzeń tworzy fizyczne problemy na mapie, które pozostają aktywne do czasu rozwiązania przez bohatera.

## Główny flow

Wydarzenie Świata → pojawia się problem → Znacznik Zagrożenia trafia na mapę → zaczyna działać efekt → bohater dociera na heks → wybiera „Zbadaj problem” → płaci 1 Akcję → poznaje dostępne sposoby rozwiązania → metody stają się jawne dla wszystkich graczy → bohater wybiera sposób rozwiązania → płaci koszt podjęcia próby → sukces albo porażka → po sukcesie problem znika → efekt przestaje działać → wydarzenie zostaje zakończone → Kronika zapisuje wydarzenie.

## Zatwierdzone zasady projektowe

1. **Każde Zagrożenie zawsze posiada co najmniej 1 aktywny negatywny efekt.** Efekt działa tak długo, jak długo Zagrożenie pozostaje aktywne, chyba że sama karta wyraźnie określa dodatkową regułę.
2. **Zasięg efektu jest definiowany indywidualnie przez każde Zagrożenie.** Efekt może być globalny, regionalny albo lokalny. Nie wszystkie Zagrożenia muszą oddziaływać na cały świat.
3. **Jedno Zagrożenie może posiadać kilka aktywnych efektów jednocześnie.** Nie ma obowiązku stosowania więcej niż jednego efektu — minimum pozostaje 1. Liczba efektów wynika z projektu konkretnego Zagrożenia.
4. **Zagrożenia nie eskalują automatycznie wraz z upływem czasu.** Efekty Zagrożenia pozostają niezmienne aż do jego rozwiązania lub innego zakończenia określonego przez kartę; samo pozostawienie problemu na mapie przez kolejne rundy lub Rady nie zwiększa jego siły ani nie dodaje nowych efektów.
5. **Efekty kilku aktywnych Zagrożeń mogą się kumulować.** Jeżeli dwa lub więcej Zagrożeń modyfikuje tę samą wartość lub zasadę, ich efekty sumują się, o ile konkretna karta wyraźnie nie stanowi inaczej. Przykład: dwa aktywne efekty `-1 Złoto` do sprzedaży Towarów dają łącznie `-2 Złoto`.
6. **Skumulowane efekty Zagrożeń mogą całkowicie wyłączyć daną możliwość.** Nie stosujemy automatycznego minimum `1`, jeśli kilka negatywnych efektów sprowadzi daną wartość lub możliwość do zera. Jeżeli np. cena sprzedaży Towaru zostanie obniżona do `0 Złota`, sprzedaż tego Towaru jest niedostępna tak długo, jak długo utrzymuje się efekt powodujący ten stan.
7. **Pojedyncze Zagrożenie może bezpośrednio całkowicie zablokować konkretną mechanikę, obiekt lub miejsce.** Nie musi do tego dochodzić przez kumulowanie kilku modyfikatorów. Jeżeli wynika to z treści karty, Zagrożenie może np. zablokować wydobycie w kopalni, korzystanie z określonej funkcji lokacji albo przejście przez wskazany heks. Blokada trwa tak długo, jak określa karta, najczęściej do rozwiązania Zagrożenia.
8. **Wszystkie aktywne Zagrożenia są jawne dla wszystkich graczy w zakresie ich istnienia, lokalizacji i aktywnego wpływu na świat.** Gracze widzą nazwę Zagrożenia, jego znacznik na mapie i działające efekty.
9. **Sposoby rozwiązania Zagrożenia nie są jawne zdalnie.** Gracz nie może z drugiego końca mapy podejrzeć dostępnych metod rozwiązania problemu. Samo dotarcie na heks również nie ujawnia metod automatycznie.
10. **Aby poznać sposoby rozwiązania Zagrożenia, bohater znajdujący się na jego heksie musi świadomie kliknąć akcję „Zbadaj problem”.** Dopiero wtedy gra ujawnia dostępne metody rozwiązania. Samo wejście na heks Zagrożenia nie uruchamia badania i nie pokazuje tych opcji automatycznie.
11. **Akcja „Zbadaj problem” kosztuje 1 Akcję.** Koszt jest ponoszony w momencie rozpoczęcia badania i dopiero po jego opłaceniu gracz poznaje dostępne metody rozwiązania Zagrożenia.
12. **Po zbadaniu Zagrożenia poznane metody rozwiązania pozostają odkryte na stałe, dopóki Zagrożenie pozostaje aktywne.** Nie trzeba ponownie badać tego samego problemu w kolejnych turach.
13. **Po pierwszym zbadaniu Zagrożenia odkryte metody stają się jawne dla wszystkich graczy.** Wiedza o sposobach rozwiązania problemu jest wspólna dla całej grupy rywalizujących bohaterów, a nie przypisana wyłącznie do bohatera, który wykonał badanie.
14. **Po zbadaniu Zagrożenia podjęcie konkretnej próby rozwiązania kosztuje dodatkowo 1 Akcję.** Badanie i próba rozwiązania są dwiema osobnymi czynnościami: 1 Akcja za „Zbadaj problem” oraz 1 Akcja za rozpoczęcie wybranej metody rozwiązania.
15. **Porażka próby rozwiązania nie powoduje ponownego ukrycia metod.** Raz odkryte sposoby rozwiązania pozostają jawne i nie wymagają ponownego użycia akcji „Zbadaj problem”.
16. **Inny bohater może skorzystać z wcześniej odkrytych metod bez ponownego badania.** Po dotarciu na heks już zbadanego Zagrożenia może od razu wybrać jedną z jawnych metod i zapłacić wyłącznie koszt podjęcia próby rozwiązania.
17. **Po zbadaniu Zagrożenia przy każdej metodzie ujawniana jest używana statystyka oraz poziom trudności DC.** Gracze wiedzą, czym wykonują próbę i jaki wynik muszą osiągnąć.
18. **Konsekwencja porażki nie jest pokazywana przed wybraniem metody.** Gracz zna sposób działania metody, statystykę i DC, ale ryzyko wynikające z niepowodzenia pozostaje ukryte do momentu rozpatrzenia próby.
19. **Dokładna nagroda za sukces nie jest pokazywana przed wybraniem metody.** Nagroda zostaje ujawniona dopiero po skutecznym rozwiązaniu problemu.
20. **Każde Zagrożenie posiada co najmniej 2 różne metody rozwiązania i może posiadać 3 lub więcej metod.** Liczba metod wynika z projektu konkretnego problemu; trzy metody są jak najbardziej dopuszczalne.
21. **Metoda rozwiązania może mieć dodatkowe wymagania poza statystyką.** Może wymagać np. określonej ilości Złota, Towaru, konkretnego Przedmiotu albo Pomocnika. Jeśli bohater nie spełnia wymogu, metoda jest dla niego niedostępna.
22. **Po zbadaniu Zagrożenia dodatkowe wymagania każdej metody są jawne.** Gracz widzi przed wyborem, czy metoda wymaga np. Złota, Towaru, konkretnego Przedmiotu albo Pomocnika.
23. **Metoda typu „Walka” uruchamia pełną walkę.** Nie jest zastępowana pojedynczym testem statystyki Walka. Rozwiązanie taką metodą przechodzi przez właściwy system walki z przeciwnikiem lub przeciwnikami przypisanymi do Zagrożenia.
24. **Różne metody tego samego Zagrożenia mogą mieć różne konsekwencje porażki.** Ryzyko wynika z charakteru wybranej drogi i może być inne dla Walki, Intrygi, Dyplomacji lub innych metod.
25. **Różne metody rozwiązania tego samego Zagrożenia nie zmieniają nagrody za sukces.** Zagrożenie posiada jedną wspólną nagrodę za rozwiązanie niezależnie od wybranej skutecznej metody.
26. **Podgląd wcześniej odkrytych metod jest darmowy.** Gracz może bez kosztu Akcji ponownie sprawdzić znane metody, statystyki, DC i wymagania. 1 Akcja jest pobierana dopiero przy rozpoczęciu konkretnej próby rozwiązania.
27. **Po nieudanej próbie ten sam bohater może ponownie podjąć to Zagrożenie dopiero w swojej następnej turze.** Nie może zużyć kolejnej Akcji w tej samej turze, aby natychmiast ponowić próbę.
28. **Przy kolejnej próbie bohater może wybrać inną odkrytą metodę rozwiązania.** Porażka Walki nie blokuje późniejszej próby Intrygi, Dyplomacji ani innej dostępnej drogi.
29. **Koszty dodatkowych wymagań metody są zużywane w momencie rozpoczęcia próby.** Jeżeli metoda wymaga wydania np. Złota lub Towarów, zasoby zostają wydane niezależnie od tego, czy próba zakończy się sukcesem czy porażką.
30. **Porażka w metodzie „Walka” pozostawia Zagrożenie aktywne i rozpatruje normalne konsekwencje przegranej walki.** Zagrożenie, jego znacznik i aktywne efekty nie znikają po przegranej.
31. **Po pierwszej porażce danej metody jej konsekwencja porażki staje się jawna dla wszystkich graczy.** Ukryte ryzyko pozostaje tajemnicą tylko do chwili, gdy zostanie po raz pierwszy rzeczywiście ujawnione podczas nieudanej próby tej metody.
32. **Każde Zagrożenie posiada własną regułę rozmieszczenia wynikającą z jego fabuły i charakteru.** Karta może wskazywać konkretny typ terenu, obiekt, lokację, region lub inną zasadę wyboru heksu zamiast korzystać z jednego wspólnego sposobu losowania dla wszystkich problemów.
33. **Karta Zagrożenia może posiadać własną regułę miejsca awaryjnego.** Jeśli nie istnieje legalne miejsce spełniające warunek podstawowy, gra próbuje zastosować zapisany na tej karcie fallback, np. „kopalnia żelaza, a jeśli jej nie ma — dowolna kopalnia”.
34. **Jeśli nie da się spełnić ani podstawowej, ani awaryjnej reguły rozmieszczenia, Wydarzenie nie wchodzi do gry.** Karta trafia na stos odrzuconych, a gra dobiera kolejne Wydarzenie z tej samej talii i tego samego Poziomu Świata.
35. **Kilka różnych Zagrożeń może jednocześnie znajdować się na tym samym heksie.** Jeżeli reguły rozmieszczenia kilku aktywnych kart legalnie wskazują to samo miejsce, ich znaczniki i problemy współistnieją na jednym heksie.
36. **Pełną nagrodę za rozwiązanie Zagrożenia otrzymuje bohater, który faktycznie je rozwiązał.** Nie ma znaczenia, który bohater wcześniej wykonał akcję „Zbadaj problem”; samo odkrycie metod nie daje udziału w późniejszej nagrodzie.
37. **Nie ma limitu liczby aktywnych Zagrożeń.** Świat może posiadać dowolną liczbę nierozwiązanych problemów jednocześnie; kolejne Zagrożenia nie zastępują ani nie usuwają wcześniejszych tylko dlatego, że jest ich dużo.
38. **Efekt Zagrożenia zaczyna działać natychmiast po jego pojawieniu się na mapie.** Nie trzeba najpierw użyć akcji „Zbadaj problem”. Badanie ujawnia metody rozwiązania, ale nie aktywuje samego wpływu Zagrożenia na świat.
39. **Zagrożenie posiadające fizyczny Znacznik Zagrożenia pozostaje aktywne aż do rozwiązania.** Nie wygasa automatycznie przy następnej Radzie ani po określonej liczbie rund. Krótkotrwałe efekty wygasające z czasem mogą występować jako zwykłe Wydarzenia Świata bez fizycznego Zagrożenia na mapie.
40. **Zmiana Poziomu Świata nie usuwa aktywnych Zagrożeń z wcześniejszych poziomów.** Problem powstały np. na Poziomie Świata 1 pozostaje na mapie po przejściu na Poziom Świata 2 i nadal działa aż do jego rozwiązania.
41. **Aktywne Zagrożenie nie skaluje się dynamicznie po zmianie Poziomu Świata.** Jego DC, przypisani przeciwnicy, nagroda i pozostałe parametry pozostają takie, jakie zostały określone dla tego Zagrożenia w chwili jego wejścia do gry.

## Punkty do działania

- [x] Stworzyć jeden wspólny Znacznik Zagrożenia.
- [x] Umieszczać Znacznik Zagrożenia na heksie.
- [x] Pozwolić Wydarzeniu Świata tworzyć Zagrożenie.
- [x] Każda karta może posiadać własną regułę rozmieszczenia.
- [x] Obsłużyć regułę miejsca awaryjnego.
- [x] Jeśli nie istnieje legalne miejsce podstawowe ani awaryjne — wydarzenie zostaje odrzucone i dobierane jest kolejne z tej samej talii.
- [x] Kliknięcie znacznika pokazuje szczegóły.
- [x] Pokazać nazwę problemu.
- [x] Pokazać opis fabularny.
- [x] Pokazać aktualny efekt.
- [x] Pokazać warunek zakończenia.
- [x] Pokazać dostępną akcję na heksie.
- [x] Wejście na heks nie uruchamia interakcji automatycznie.
- [x] Bohater świadomie wybiera akcję rozwiązania problemu.
- [ ] Ujawnić metody rozwiązania dopiero po użyciu akcji „Zbadaj problem” na heksie Zagrożenia.
- [ ] Pobrać 1 Akcję za użycie „Zbadaj problem”.
- [ ] Zapamiętać stan zbadanego Zagrożenia i utrzymywać odkryte metody jawne do końca problemu.
- [ ] Po zbadaniu udostępnić odkryte metody wszystkim graczom.
- [ ] Pobrać osobną 1 Akcję za rozpoczęcie wybranej metody rozwiązania.
- [ ] Nie wymagać ponownego badania po porażce ani od kolejnego bohatera.
- [ ] Po zbadaniu pokazywać przy metodach statystykę, DC oraz dodatkowe wymagania.
- [ ] Nie ujawniać przed próbą dokładnej konsekwencji porażki ani nagrody za sukces.
- [ ] Umożliwić darmowy podgląd wcześniej odkrytych metod bez zużywania Akcji.
- [x] Obsłużyć kilka metod rozwiązania jednego problemu.
- [ ] Wymagać minimum 2 metod rozwiązania dla każdego Zagrożenia i obsłużyć również 3 lub więcej metod.
- [x] Metody mogą korzystać z różnych statystyk.
- [ ] Obsłużyć dodatkowe wymagania metod, np. Złoto, Towar, Przedmiot albo Pomocnika.
- [ ] Zużywać zasoby wymagane przez metodę już przy rozpoczęciu próby, także przy późniejszej porażce.
- [ ] Metoda „Walka” uruchamia pełny system walki zamiast zwykłego testu statystyki.
- [ ] Po przegranej Walce pozostawić Zagrożenie aktywne i rozpatrzyć normalne konsekwencje przegranej walki.
- [x] Metody mogą mieć różne konsekwencje.
- [ ] Po pierwszej porażce konkretnej metody ujawnić jej konsekwencję wszystkim graczom.
- [x] Nagroda za rozwiązanie jest wspólna dla Zagrożenia i niezależna od skutecznej metody.
- [x] Pełna nagroda trafia do bohatera, który faktycznie rozwiązał Zagrożenie.
- [x] Sukces usuwa problem.
- [x] Sukces usuwa znacznik.
- [x] Sukces wyłącza efekt wydarzenia.
- [x] Po sukcesie karta trafia na stos odrzuconych.
- [x] Porażka pozostawia wydarzenie aktywne.
- [x] Problem po porażce może zostać podjęty ponownie.
- [x] Po porażce blokować temu samemu bohaterowi kolejną próbę do jego następnej tury.
- [ ] Przy kolejnej próbie pozwolić bohaterowi wybrać dowolną inną odkrytą metodę.
- [x] Inny bohater może później podjąć próbę rozwiązania problemu.
- [x] Obsłużyć kilka aktywnych Zagrożeń jednocześnie.
- [ ] Zagwarantować pełną obsługę kilku różnych Zagrożeń na tym samym heksie także w UI.
- [ ] Nie wprowadzać limitu aktywnych Zagrożeń także w warstwie UI — usunąć ograniczenia wyświetlania, które mogłyby ukryć część problemów.
- [ ] Dopilnować, aby efekt Zagrożenia działał natychmiast po jego pojawieniu się, jeszcze przed zbadaniem.
- [ ] Zagwarantować, że Zagrożenia ze znacznikiem nie wygasają przy kolejnej Radzie ani po zmianie Poziomu Świata.
- [ ] Zachować stałe DC, przeciwników, nagrodę i pozostałe parametry już aktywnego Zagrożenia po zmianie Poziomu Świata.
- [x] Znacznik może znajdować się na heksie z innym obiektem.
- [x] Znacznik może pojawić się na heksie zajętym przez bohatera.
- [ ] Zapisywać sposób rozwiązania problemu.
- [x] Dodać wpis do historii Wydarzeń Świata.
- [ ] Przygotować punkt integracji z Kroniką Świata.
- [ ] Stworzyć 3–5 testowych Zagrożeń.

## Stan po audycie kodu — 2026-08-11

Istnieją już trzy główne warstwy techniczne modułu:

1. `rg_world/world_event_markers.py` — fizyczne znaczniki, reguły rozmieszczenia, fallback, podgląd i synchronizacja znacznika z aktywnym wydarzeniem.
2. `rg_engine/world_problems.py` — rozpoczęcie próby, koszt Akcji, różne metody rozwiązania, test k20, nagrody, konsekwencje porażki i blokada ponownej próby do następnej tury.
3. `rg_ui/world_state.py` — panel Wydarzeń Świata, lista Problemów, klikany znacznik, akcje na aktualnym heksie oraz ekran wyboru metody rozwiązania.

### Najbliższe rzeczy do wykonania

1. Dodać osobny krok „Zbadaj problem”, kosztujący 1 Akcję i dopiero po świadomym użyciu na właściwym heksie ujawniający metody rozwiązania.
2. Zapamiętywać, że Zagrożenie zostało zbadane, ujawniać jego metody wszystkim graczom i nie wymagać ponownego badania po porażce ani przez kolejnych bohaterów.
3. Rozdzielić koszt badania i koszt próby rozwiązania: każda z tych czynności kosztuje po 1 Akcji.
4. Po zbadaniu pokazywać statystykę, DC i jawne wymagania każdej metody, ale ukrywać dokładną konsekwencję porażki oraz nagrodę do czasu rozpatrzenia próby.
5. Umożliwić bezkosztowy podgląd odkrytych metod.
6. Wymagać co najmniej 2 metod na Zagrożenie, obsługiwać 3 lub więcej oraz dodatkowe wymagania metod.
7. Zużywać wymagane przez metodę zasoby już w chwili rozpoczęcia próby.
8. Dodać możliwość, aby metoda rozwiązania Problemu uruchamiała pełną Walkę, zamiast zawsze być zwykłym testem statystyki, oraz po przegranej zachować Zagrożenie i zastosować standardowe konsekwencje walki.
9. Po pierwszym niepowodzeniu danej metody ujawniać wszystkim graczom jej konsekwencję porażki.
10. Zachować jedną wspólną nagrodę za rozwiązanie Zagrożenia niezależnie od wybranej skutecznej metody i przyznawać ją wyłącznie bohaterowi, który rozwiązał problem.
11. Zagwarantować pełną obsługę kilku różnych Zagrożeń na jednym heksie, również w UI.
12. Usunąć techniczne limity prezentacji aktywnych Problemów w UI tak, aby zasada „brak limitu aktywnych Zagrożeń” była prawdziwa również dla gracza.
13. Dopilnować natychmiastowej aktywacji efektów Zagrożeń oraz ich trwałości między Radami i zmianami Poziomu Świata bez dynamicznego skalowania już aktywnych problemów.
14. Zapisywać w historii nie tylko bohatera, ale również konkretny sposób rozwiązania Problemu.
15. Przygotować neutralny punkt integracji z przyszłą Kroniką Świata.
16. Przenieść „Rozbójników na trakcie” z narzędzia DEV do prawdziwego contentu i przygotować łącznie 3–5 testowych Zagrożeń.

## Pierwszy problem testowy

**Rozbójnicy na trakcie**

Docelowe możliwe drogi:
- Walka — zaatakuj obóz.
- Intryga — zakradnij się i zniszcz zapasy.
- Dyplomacja — spróbuj przekonać lub zmusić grupę do opuszczenia traktu.

Obecna wersja DEV zawiera już drogę Walki jako test statystyki oraz drogę Intrygi. Docelowo droga „Walka” ma uruchamiać właściwy system walki, a karta otrzyma trzecią drogę opartą o Dyplomację.

## Definition of Done

W trakcie normalnej rozgrywki pojawia się Wydarzenie Świata, tworzy fizyczny problem na planszy, problem wpływa na świat, bohater może dotrzeć na odpowiedni heks, świadomie użyć kosztującej 1 Akcję akcji „Zbadaj problem”, ujawnić metody całej grupie, a następnie za kolejną 1 Akcję podjąć wybraną próbę rozwiązania. Raz odkryte metody pozostają jawne do końca Zagrożenia, również po porażce i dla kolejnych bohaterów. Podgląd odkrytych metod jest darmowy, metoda Walki uruchamia pełny system walki, wymagane zasoby są zużywane przy rozpoczęciu próby, a po pierwszym niepowodzeniu konkretnej metody jej konsekwencja staje się jawna. Nagroda za rozwiązanie jest wspólna dla Zagrożenia niezależnie od wybranej drogi i otrzymuje ją bohater, który faktycznie rozwiązał problem. Liczba aktywnych Zagrożeń nie ma limitu, ich efekty działają natychmiast, fizyczne problemy nie wygasają przy Radzie ani zmianie Poziomu Świata i nie skalują się dynamicznie po wejściu do gry. Po sukcesie znacznik oraz efekt prawidłowo znikają.