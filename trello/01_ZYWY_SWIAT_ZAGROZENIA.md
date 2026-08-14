# 01 — Żywy Świat: Zagrożenia i problemy na mapie

**Status Kanban:** W TRAKCIE

## Cel

Wydarzenia Świata mają rzeczywiście zmieniać planszę. Część wydarzeń tworzy fizyczne problemy na mapie, które pozostają aktywne do czasu rozwiązania przez bohatera.

## Główny flow

Wydarzenie Świata → pojawia się problem → Znacznik Zagrożenia trafia na mapę → zaczyna działać efekt → bohater dociera na heks → wybiera sposób rozwiązania → sukces albo porażka → po sukcesie problem znika → efekt przestaje działać → wydarzenie zostaje zakończone → Kronika zapisuje wydarzenie.

## Zatwierdzone zasady projektowe

1. **Każde Zagrożenie zawsze posiada co najmniej 1 aktywny negatywny efekt.** Efekt działa tak długo, jak długo Zagrożenie pozostaje aktywne, chyba że sama karta wyraźnie określa dodatkową regułę.
2. **Zasięg efektu jest definiowany indywidualnie przez każde Zagrożenie.** Efekt może być globalny, regionalny albo lokalny. Nie wszystkie Zagrożenia muszą oddziaływać na cały świat.
3. **Jedno Zagrożenie może posiadać kilka aktywnych efektów jednocześnie.** Nie ma obowiązku stosowania więcej niż jednego efektu — minimum pozostaje 1. Liczba efektów wynika z projektu konkretnego Zagrożenia.
4. **Zagrożenia nie eskalują automatycznie wraz z upływem czasu.** Efekty Zagrożenia pozostają niezmienne aż do jego rozwiązania lub innego zakończenia określonego przez kartę; samo pozostawienie problemu na mapie przez kolejne rundy lub Rady nie zwiększa jego siły ani nie dodaje nowych efektów.
5. **Efekty kilku aktywnych Zagrożeń mogą się kumulować.** Jeżeli dwa lub więcej Zagrożeń modyfikuje tę samą wartość lub zasadę, ich efekty sumują się, o ile konkretna karta wyraźnie nie stanowi inaczej. Przykład: dwa aktywne efekty `-1 Złoto` do sprzedaży Towarów dają łącznie `-2 Złoto`.
6. **Skumulowane efekty Zagrożeń mogą całkowicie wyłączyć daną możliwość.** Nie stosujemy automatycznego minimum `1`, jeśli kilka negatywnych efektów sprowadzi daną wartość lub możliwość do zera. Jeżeli np. cena sprzedaży Towaru zostanie obniżona do `0 Złota`, sprzedaż tego Towaru jest niedostępna tak długo, jak długo utrzymuje się efekt powodujący ten stan.
7. **Pojedyncze Zagrożenie może bezpośrednio całkowicie zablokować konkretną mechanikę, obiekt lub miejsce.** Nie musi do tego dochodzić przez kumulowanie kilku modyfikatorów. Jeżeli wynika to z treści karty, Zagrożenie może np. zablokować wydobycie w kopalni, korzystanie z określonej funkcji lokacji albo przejście przez wskazany heks. Blokada trwa tak długo, jak określa karta, najczęściej do rozwiązania Zagrożenia.

## Punkty do działania

- [x] Stworzyć jeden wspólny Znacznik Zagrożenia.
- [x] Umieszczać Znacznik Zagrożenia na heksie.
- [x] Pozwolić Wydarzeniu Świata tworzyć Zagrożenie.
- [x] Każda karta może posiadać własną regułę rozmieszczenia.
- [x] Obsłużyć regułę miejsca awaryjnego.
- [x] Jeśli nie istnieje legalne miejsce podstawowe ani awaryjne — wydarzenie zostaje odrzucone.
- [x] Kliknięcie znacznika pokazuje szczegóły.
- [x] Pokazać nazwę problemu.
- [x] Pokazać opis fabularny.
- [x] Pokazać aktualny efekt.
- [x] Pokazać warunek zakończenia.
- [x] Pokazać dostępną akcję na heksie.
- [x] Wejście na heks nie uruchamia interakcji automatycznie.
- [x] Bohater świadomie wybiera akcję rozwiązania problemu.
- [x] Obsłużyć kilka metod rozwiązania jednego problemu.
- [x] Metody mogą korzystać z różnych statystyk.
- [ ] Metody mogą prowadzić do walki.
- [x] Metody mogą mieć różne konsekwencje.
- [x] Sukces usuwa problem.
- [x] Sukces usuwa znacznik.
- [x] Sukces wyłącza efekt wydarzenia.
- [x] Po sukcesie karta trafia na stos odrzuconych.
- [x] Porażka pozostawia wydarzenie aktywne.
- [x] Problem po porażce może zostać podjęty ponownie.
- [x] Inny bohater może później podjąć próbę rozwiązania problemu.
- [x] Obsłużyć kilka aktywnych Zagrożeń jednocześnie.
- [ ] Nie wprowadzać limitu aktywnych Zagrożeń także w warstwie UI — usunąć ograniczenia wyświetlania, które mogłyby ukryć część problemów.
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

1. Dodać możliwość, aby metoda rozwiązania Problemu uruchamiała prawdziwą Walkę, zamiast zawsze być zwykłym testem statystyki.
2. Usunąć techniczne limity prezentacji aktywnych Problemów w UI tak, aby zasada „brak limitu aktywnych Zagrożeń” była prawdziwa również dla gracza.
3. Zapisywać w historii nie tylko bohatera, ale również konkretny sposób rozwiązania Problemu.
4. Przygotować neutralny punkt integracji z przyszłą Kroniką Świata.
5. Przenieść „Rozbójników na trakcie” z narzędzia DEV do prawdziwego contentu i przygotować łącznie 3–5 testowych Zagrożeń.

## Pierwszy problem testowy

**Rozbójnicy na trakcie**

Docelowe możliwe drogi:
- Walka — zaatakuj obóz.
- Intryga — zakradnij się i zniszcz zapasy.
- Dyplomacja — spróbuj przekonać lub zmusić grupę do opuszczenia traktu.

Obecna wersja DEV zawiera już drogę Walki jako test statystyki oraz drogę Intrygi. Docelowo droga „Walka” ma uruchamiać właściwy system walki, a karta otrzyma trzecią drogę opartą o Dyplomację.

## Definition of Done

W trakcie normalnej rozgrywki pojawia się Wydarzenie Świata, tworzy fizyczny problem na planszy, problem wpływa na świat, bohater może dotrzeć na odpowiedni heks i rozwiązać go, a po sukcesie znacznik oraz efekt prawidłowo znikają.