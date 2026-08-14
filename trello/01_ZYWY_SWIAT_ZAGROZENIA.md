# 01 — Żywy Świat: Zagrożenia i problemy na mapie

**Status Kanban:** W TRAKCIE  
**Status projektu zasad:** ZAMKNIĘTY — gotowe do implementacji

## Cel

Wydarzenia Świata mają rzeczywiście zmieniać planszę. Część wydarzeń tworzy fizyczne problemy na mapie, które pozostają aktywne do czasu rozwiązania przez bohatera.

## Główny flow

Wydarzenie Świata → pojawia się problem → Znacznik Zagrożenia trafia na mapę → efekt zaczyna działać natychmiast → bohater dociera na heks → wybiera „Zbadaj problem” → płaci 1 Akcję → bez testu poznaje dostępne sposoby rozwiązania **dla swojego bohatera** → wybiera sposób rozwiązania → płaci 1 Akcję za całą próbę rozwiązania → sukces albo porażka → po sukcesie problem, znacznik, efekty i blokady znikają natychmiast → wydarzenie zostaje zakończone → historia zapisuje bohatera, metodę i nagrodę → Kronika Świata zapisuje krótki wpis fabularny.

## Zatwierdzone zasady projektowe

1. **Każde Zagrożenie zawsze posiada co najmniej 1 aktywny negatywny efekt.** Efekt działa tak długo, jak długo Zagrożenie pozostaje aktywne, chyba że sama karta wyraźnie określa dodatkową regułę.
2. **Zasięg efektu jest definiowany indywidualnie przez każde Zagrożenie.** Efekt może być globalny, regionalny albo lokalny.
3. **Jedno Zagrożenie może posiadać kilka aktywnych efektów jednocześnie.** Minimum pozostaje 1; liczba efektów wynika z projektu konkretnego Zagrożenia.
4. **Zagrożenia nie eskalują automatycznie wraz z upływem czasu.** Samo pozostawienie problemu przez kolejne rundy lub Rady nie zwiększa jego siły ani nie dodaje nowych efektów.
5. **Efekty kilku aktywnych Zagrożeń mogą się kumulować.** Jeżeli kilka Zagrożeń modyfikuje tę samą wartość lub zasadę, ich efekty sumują się, o ile konkretna karta nie stanowi inaczej.
6. **Skumulowane efekty mogą całkowicie wyłączyć daną możliwość.** Nie stosujemy automatycznego minimum `1`; np. cena sprzedaży sprowadzona do `0 Złota` oznacza niedostępność sprzedaży.
7. **Pojedyncze Zagrożenie może bezpośrednio całkowicie zablokować konkretną mechanikę, obiekt lub miejsce.** Nie wymaga to kumulowania kilku modyfikatorów.
8. **Istnienie, nazwa, lokalizacja i aktywne efekty każdego Zagrożenia są jawne dla wszystkich graczy.** Ukryte są natomiast informacje wymagające osobistego zbadania problemu.
9. **Sposoby rozwiązania Zagrożenia nie są jawne zdalnie.** Samo dotarcie na heks również ich automatycznie nie ujawnia.
10. **Aby poznać sposoby rozwiązania Zagrożenia, bohater znajdujący się na jego heksie musi świadomie kliknąć „Zbadaj problem”.**
11. **„Zbadaj problem” kosztuje 1 Akcję.**
12. **Po zbadaniu Zagrożenia poznane metody pozostają odkryte dla tego bohatera aż do zakończenia danego Zagrożenia.** Nie trzeba ponownie badać go w kolejnych turach tym samym bohaterem.
13. **Stan zbadania jest przypisany do konkretnego bohatera.** Zbadanie Zagrożenia przez jednego bohatera nie ujawnia metod pozostałym bohaterom. To ustalenie zastępuje wcześniejszy wariant globalnego udostępniania metod.
14. **Podjęcie konkretnej próby rozwiązania po zbadaniu kosztuje dodatkowo 1 Akcję.** Badanie i próba rozwiązania są dwiema osobnymi czynnościami.
15. **Porażka nie powoduje ponownego ukrycia metod dla bohatera, który wcześniej zbadał problem.**
16. **Inny bohater musi sam użyć „Zbadaj problem”, zanim uzyska dostęp do metod rozwiązania.** Nie korzysta automatycznie z wiedzy bohatera, który zbadał Zagrożenie wcześniej.
17. **Po zbadaniu przy każdej metodzie ujawniana jest używana statystyka oraz poziom trudności DC.**
18. **Konsekwencja porażki nie jest pokazywana przed pierwszym ujawnieniem jej w praktyce.**
19. **Dokładna nagroda za sukces nie jest pokazywana przed rozwiązaniem Zagrożenia.**
20. **Każde Zagrożenie posiada co najmniej 2 różne metody rozwiązania i może posiadać 3 lub więcej metod.**
21. **Metoda może mieć dodatkowe wymagania poza statystyką.** Może wymagać np. Złota, Towaru, konkretnego Przedmiotu albo Pomocnika.
22. **Po zbadaniu dodatkowe wymagania metod są jawne dla bohatera, który zbadał Zagrożenie.**
23. **Metoda typu „Walka” uruchamia pełną walkę.** Nie jest zastępowana pojedynczym testem statystyki Walka.
24. **Różne metody tego samego Zagrożenia mogą mieć różne konsekwencje porażki.**
25. **Różne metody nie zmieniają nagrody za sukces.** Zagrożenie posiada jedną wspólną nagrodę niezależnie od skutecznej drogi rozwiązania.
26. **Podgląd wcześniej odkrytych metod jest darmowy dla bohatera, który zbadał problem.** 1 Akcja jest pobierana dopiero przy rozpoczęciu próby rozwiązania.
27. **Po nieudanej próbie ten sam bohater może ponownie podjąć to Zagrożenie dopiero w swojej następnej turze.**
28. **Przy kolejnej próbie bohater może wybrać inną odkrytą metodę.**
29. **Koszty zużywane przez metodę są pobierane w momencie rozpoczęcia próby i przepadają również przy porażce.**
30. **Porażka w metodzie „Walka” pozostawia Zagrożenie aktywne i rozpatruje normalne konsekwencje przegranej walki.**
31. **Po pierwszej porażce danej metody jej konsekwencja zostaje odkryta w stanie Zagrożenia.** Bohaterowie, którzy mają już zbadane to Zagrożenie lub zbadają je później, widzą poznaną konsekwencję; bohater bez własnego zbadania nadal nie może zdalnie podejrzeć metod.
32. **Każde Zagrożenie posiada własną regułę rozmieszczenia wynikającą z jego fabuły i charakteru.** Może wskazywać teren, obiekt, lokację, region albo inną zasadę wyboru heksu.
33. **Karta Zagrożenia może posiadać własną regułę miejsca awaryjnego.**
34. **Jeśli nie da się spełnić ani podstawowej, ani awaryjnej reguły rozmieszczenia, Wydarzenie nie wchodzi do gry.** Karta trafia na stos odrzuconych, a gra dobiera kolejne Wydarzenie z tej samej talii i Poziomu Świata.
35. **Kilka różnych Zagrożeń może jednocześnie znajdować się na tym samym heksie.**
36. **Pełną nagrodę otrzymuje bohater, który faktycznie rozwiązał Zagrożenie.** Samo wcześniejsze zbadanie problemu nie daje udziału w nagrodzie.
37. **Nie ma limitu liczby aktywnych Zagrożeń.**
38. **Efekt Zagrożenia zaczyna działać natychmiast po jego pojawieniu się na mapie.** Badanie nie aktywuje efektu, tylko ujawnia metody bohaterowi.
39. **Zagrożenie posiadające fizyczny Znacznik Zagrożenia pozostaje aktywne aż do rozwiązania.** Nie wygasa automatycznie przy następnej Radzie ani po określonej liczbie rund.
40. **Zmiana Poziomu Świata nie usuwa aktywnych Zagrożeń z wcześniejszych poziomów.**
41. **Aktywne Zagrożenie nie skaluje się dynamicznie po zmianie Poziomu Świata.** DC, przeciwnicy, nagroda i inne parametry pozostają takie, jakie zostały określone przy wejściu problemu do gry.
42. **Jedno Wydarzenie Świata może utworzyć maksymalnie jeden Znacznik Zagrożenia.**
43. **Jeżeli na jednym heksie znajduje się kilka Zagrożeń, każde posiada osobną akcję interakcji.**
44. **Pojawienie się Zagrożenia na heksie zajętym przez bohatera nie uruchamia automatycznie żadnej interakcji.**
45. **Jeżeli Zagrożenie blokuje wejście lub przejście przez heks, bohater znajdujący się już na tym heksie może z niego wyjść.** Po opuszczeniu nie może ponownie wejść tak długo, jak trwa blokada.
46. **Po rozwiązaniu Zagrożenia historia zapisuje bohatera, skuteczną metodę oraz otrzymaną nagrodę.**
47. **„Zbadaj problem” zawsze kończy się powodzeniem i nie wymaga testu.** Bohater płaci 1 Akcję i automatycznie odkrywa metody oraz informacje jawne po zbadaniu.
48. **Bohater może przeznaczyć ostatnią Akcję w turze na „Zbadaj problem” i odłożyć próbę rozwiązania na później.**
49. **Po zbadaniu bohater może opuścić heks bez utraty zdobytej wiedzy.** Informacje pozostają odkryte dla tego bohatera do końca danego Zagrożenia.
50. **Koszt 1 Akcji za rozpoczęcie metody obejmuje całą pojedynczą próbę rozwiązania.** Obejmuje test, wynik i wszystkie konsekwencje tej próby.
51. **Jeżeli metodą jest pełna Walka, 1 Akcja obejmuje całą walkę aż do zwycięstwa albo porażki.** Liczba rund walki nie zwiększa kosztu Akcji.
52. **Po użyciu „Zbadaj problem” bohater może od razu w tej samej turze rozpocząć próbę rozwiązania, jeśli posiada jeszcze co najmniej 1 Akcję.**
53. **Po udanym rozwiązaniu bohater zachowuje niewykorzystane Akcje i normalnie kontynuuje turę.**
54. **Bohater może w jednej turze wejść w interakcję z kilkoma Zagrożeniami na tym samym heksie, jeśli ma wystarczającą liczbę Akcji.**
55. **Blokada Zagrożenia dotyczy wyłącznie mechaniki, obiektu, miejsca lub funkcji wskazanej przez kartę.** Nie wyłącza automatycznie innych niezależnych interakcji na tym samym heksie.
56. **Opuszczenie heksu, na którym bohater znajdował się już w chwili powstania blokady, kosztuje normalny koszt ruchu.** Dodatkowa kara istnieje tylko wtedy, gdy karta wyraźnie ją określa.
57. **Metoda rozwiązania może korzystać z dowolnej z sześciu statystyk bohatera:** Walka, Handel, Intryga, Dyplomacja, Kultura albo Nauka.
58. **Nie każda metoda musi wymagać rzutu.** Metoda może zakończyć się automatycznym sukcesem po spełnieniu wszystkich warunków i opłaceniu kosztów.
59. **„Wymaga” i „zużywa” są dwoma różnymi pojęciami.** Element wymagany tylko do posiadania pozostaje u bohatera; element oznaczony jako koszt zostaje zużyty.
60. **Jedna metoda może posiadać kilka wymagań jednocześnie.**
61. **Zagrożenie rozwiązuje wyłącznie aktywny bohater wykonujący swoją turę.** Inni bohaterowie nie dokładają statystyk, przedmiotów ani premii, dopóki osobny moduł wspólnej wyprawy/Towarzysza nie wprowadzi takiej możliwości.
62. **Zwykłe metody oparte na statystyce korzystają z normalnego systemu testów gry.** Rzut jest rozpatrywany jako `k20 + statystyka + legalne bonusy` przeciwko DC metody.
63. **W teście Zagrożenia można użyć maksymalnie 1 Pomocnika**, zgodnie z ogólną zasadą testów.
64. **Metoda bez rzutu rozwiązuje Zagrożenie automatycznie po opłaceniu 1 Akcji oraz spełnieniu i rozliczeniu wszystkich jej wymagań i kosztów.**
65. **Metoda, której bohater aktualnie nie może wykonać, pozostaje widoczna po zbadaniu, ale jest wyszarzona i pokazuje brakujące wymagania.**
66. **Wyposażony przedmiot normalnie spełnia wymaganie typu „posiadaj”.** Nie trzeba zdejmować go z bohatera tylko po to, aby użyć metody.
67. **Po sukcesie wszystkie efekty i blokady danego Zagrożenia znikają natychmiast**, zanim bohater wykona kolejną pozostałą Akcję.
68. **Porażka domyślnie nie osłabia Zagrożenia.** Nie obniża DC, HP przeciwników ani innych parametrów, chyba że konkretna karta wyraźnie posiada taką specjalną zasadę.
69. **Nieudanych prób nie zapisujemy w głównej historii Wydarzeń ani w Kronice Świata.** Historia i Kronika zapisują przede wszystkim ostateczne rozwiązanie problemu; stan samego Zagrożenia może pamiętać techniczne informacje potrzebne do dalszej rozgrywki, np. ujawnioną konsekwencję porażki.
70. **Status „Niezbadane / Zbadane” oraz zdalny podgląd metod są osobne dla każdego bohatera.** Tylko bohater, który sam użył „Zbadaj problem” na danym Zagrożeniu, może później zdalnie podejrzeć jego odkryte metody, DC, wymagania i poznane konsekwencje porażek. Dla pozostałych bohaterów problem nadal ma status „Niezbadane”, mimo że jego istnienie, lokalizacja i aktywne efekty są publiczne.
71. **Każde ostatecznie rozwiązane Zagrożenie automatycznie trafia do Kroniki Świata.** Wpis jest krótki i fabularny: co się wydarzyło, kto rozwiązał problem i jaką metodą. Kronika nie pokazuje technicznych danych takich jak DC.

## Punkty do działania

### Już istnieje / częściowo działa

- [x] Wspólny Znacznik Zagrożenia.
- [x] Umieszczanie znacznika na heksie.
- [x] Wydarzenia mogą tworzyć fizyczny problem.
- [x] Własne reguły rozmieszczenia i fallback.
- [x] Odrzucenie wydarzenia, gdy nie istnieje legalne miejsce podstawowe ani awaryjne.
- [x] Kliknięcie znacznika pokazuje podstawowe szczegóły.
- [x] Wejście na heks nie uruchamia interakcji automatycznie.
- [x] Obsługa kilku metod rozwiązania w silniku.
- [x] Różne statystyki i konsekwencje porażki są wspierane na poziomie podstawowym.
- [x] Sukces usuwa problem, znacznik i aktywne Wydarzenie.
- [x] Porażka pozostawia problem aktywny i umożliwia późniejszą ponowną próbę.
- [x] Kilka Zagrożeń może być aktywnych jednocześnie.
- [x] Znacznik może współistnieć z innym obiektem oraz bohaterem.
- [x] Istnieje historia Wydarzeń Świata.

### Do implementacji według zamkniętych zasad

- [ ] Dodać osobny, zawsze skuteczny krok „Zbadaj problem” za 1 Akcję.
- [ ] Zapisywać stan zbadania **per bohater + Zagrożenie**, a nie globalnie.
- [ ] Pozwalać wyłącznie bohaterowi, który sam zbadał problem, zdalnie podglądać odkryte metody.
- [ ] Inny bohater musi samodzielnie wydać 1 Akcję na „Zbadaj problem”.
- [ ] Po zbadaniu pokazywać statystykę, DC, wymagania oraz stan dostępności metody.
- [ ] Niedostępne metody wyszarzać i wskazywać brakujące wymagania.
- [ ] Ukrywać nagrodę do sukcesu i konsekwencję porażki do jej pierwszego ujawnienia.
- [ ] Po ujawnieniu konsekwencji przechowywać tę wiedzę w stanie Zagrożenia, ale pokazywać ją zdalnie tylko bohaterom, którzy sami zbadali problem.
- [ ] Rozdzielić 1 Akcję badania od osobnej 1 Akcji za całą próbę rozwiązania.
- [ ] Pozwolić badać ostatnią Akcją oraz rozwiązywać od razu, jeśli bohater ma kolejną Akcję.
- [ ] Po sukcesie nie kończyć tury i natychmiast usuwać wszystkie efekty/blokady problemu.
- [ ] Wymagać minimum 2 metod na Zagrożenie i obsłużyć 3 lub więcej bez limitu UI do trzech przycisków.
- [ ] Obsłużyć wszystkie 6 statystyk, zwykłe testy k20, maksymalnie 1 Pomocnika i legalne bonusy.
- [ ] Obsłużyć metody bez rzutu z automatycznym sukcesem po spełnieniu warunków.
- [ ] Rozróżnić „wymaga” od „zużywa”, w tym kilka wymagań naraz i wyposażone przedmioty jako legalne wymagania typu „posiadaj”.
- [ ] Zużywać koszty metody przy rozpoczęciu próby również przy późniejszej porażce.
- [ ] Metoda „Walka” ma uruchamiać pełny system walki w ramach jednej Akcji.
- [ ] Po przegranej Walce pozostawić Zagrożenie aktywne i zastosować standardowe konsekwencje walki.
- [ ] Porażka nie może domyślnie osłabiać parametrów Zagrożenia.
- [ ] Po porażce blokować temu samemu bohaterowi kolejną próbę do jego następnej tury, ale później pozwalać wybrać inną metodę.
- [ ] Do czasu modułu wspólnej wyprawy/Towarzysza nie pozwalać innym bohaterom dokładać statystyk, przedmiotów ani premii do próby.
- [ ] Zagwarantować pełną obsługę kilku różnych Zagrożeń na jednym heksie z osobną akcją dla każdego problemu.
- [ ] Usunąć techniczne limity prezentacji aktywnych Zagrożeń w UI.
- [ ] Dopilnować natychmiastowej aktywacji efektów po pojawieniu się problemu.
- [ ] Zagrożenia ze znacznikiem nie mogą wygasać przy Radzie ani zmianie Poziomu Świata.
- [ ] Zachować stałe parametry już aktywnego Zagrożenia po zmianie Poziomu Świata.
- [ ] Blokować wyłącznie element wskazany przez kartę; bohater już stojący na zablokowanym heksie może wyjść za normalny koszt ruchu.
- [ ] Po sukcesie zapisać w historii bohatera, skuteczną metodę i nagrodę.
- [ ] Nie zapisywać nieudanych prób w głównej historii ani Kronice.
- [ ] Przygotować punkt integracji z Kroniką Świata i automatyczny krótki wpis fabularny po rozwiązaniu.
- [ ] Przenieść „Rozbójników na trakcie” z DEV do prawdziwego contentu.
- [ ] Przygotować łącznie 3–5 testowych Zagrożeń.

## Stan po audycie kodu — 2026-08-11

Istnieją już trzy główne warstwy techniczne modułu:

1. `rg_world/world_event_markers.py` — fizyczne znaczniki, reguły rozmieszczenia, fallback, podgląd i synchronizacja znacznika z aktywnym wydarzeniem.
2. `rg_engine/world_problems.py` — obecne rozpoczęcie próby, koszt Akcji, różne metody, test k20, nagrody, konsekwencje porażki i blokada ponownej próby do następnej tury.
3. `rg_ui/world_state.py` — panel Wydarzeń Świata, lista Problemów, klikany znacznik, akcje na aktualnym heksie i ekran wyboru metody.

Obecny kod **nie realizuje jeszcze finalnego dwustopniowego modelu** `Zbadaj problem → Rozwiąż problem` ani osobistego stanu wiedzy per bohater. To jest najważniejsza zmiana architektoniczna do wdrożenia.

## Kolejność implementacji

1. Stan wiedzy `hero_id + event_id`: niezbadane / zbadane oraz zdalny podgląd tylko dla odkrywcy.
2. Osobna akcja „Zbadaj problem” za 1 Akcję bez testu.
3. Przebudowa sesji rozwiązania: osobne 1 Akcja za próbę, wymagania, dostępność metod i ujawnianie informacji.
4. Metody testowe: wszystkie 6 statystyk, Pomocnik, kilka wymagań, `wymaga` vs `zużywa`, metody automatyczne.
5. Integracja pełnej Walki.
6. Efekty i blokady Zagrożeń oraz natychmiastowe ich usuwanie po sukcesie.
7. UI bez limitów liczby Zagrożeń/metod, kilka Zagrożeń na jednym heksie i osobiste statusy „Niezbadane / Zbadane”.
8. Historia rozwiązania i integracja z Kroniką Świata.
9. Przeniesienie „Rozbójników na trakcie” do contentu i przygotowanie 3–5 Zagrożeń testowych.

## Pierwszy problem testowy

**Rozbójnicy na trakcie**

Docelowe możliwe drogi:
- Walka — zaatakuj obóz.
- Intryga — zakradnij się i zniszcz zapasy.
- Dyplomacja — spróbuj przekonać lub zmusić grupę do opuszczenia traktu.

Obecna wersja DEV zawiera drogę Walki jako zwykły test statystyki oraz drogę Intrygi. Docelowo Walka ma uruchamiać pełny system walki, a karta ma otrzymać trzecią drogę opartą o Dyplomację.

## Definition of Done

W normalnej rozgrywce Wydarzenie Świata może utworzyć fizyczne Zagrożenie, którego efekt działa natychmiast i pozostaje aktywny aż do rozwiązania. Każdy bohater osobno może dotrzeć na właściwy heks i za 1 Akcję bez testu użyć „Zbadaj problem”. Tylko ten bohater uzyskuje status „Zbadane” i może później zdalnie podglądać metody, DC, wymagania oraz już poznane konsekwencje porażek. Następnie za kolejną 1 Akcję może podjąć pełną próbę rozwiązania — zwykły test, metodę automatyczną albo pełną Walkę. Sukces natychmiast usuwa problem, znacznik, efekty i blokady, przyznaje wspólną nagrodę rozwiązującemu bohaterowi, pozwala kontynuować turę i zapisuje rozwiązanie w historii oraz Kronice Świata. Porażka pozostawia Zagrożenie bez domyślnego osłabienia i nie trafia do głównej historii ani Kroniki.