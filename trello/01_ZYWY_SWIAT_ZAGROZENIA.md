# 01 — Żywy Świat: Zagrożenia i problemy na mapie

**Status Kanban:** DO ZROBIENIA

## Cel

Wydarzenia Świata mają rzeczywiście zmieniać planszę. Część wydarzeń tworzy fizyczne problemy na mapie, które pozostają aktywne do czasu rozwiązania przez bohatera.

## Główny flow

Wydarzenie Świata → pojawia się problem → Znacznik Zagrożenia trafia na mapę → zaczyna działać efekt → bohater dociera na heks → wybiera sposób rozwiązania → sukces albo porażka → po sukcesie problem znika → efekt przestaje działać → wydarzenie zostaje zakończone → Kronika zapisuje wydarzenie.

## Punkty do działania

- [ ] Stworzyć jeden wspólny Znacznik Zagrożenia.
- [ ] Umieszczać Znacznik Zagrożenia na heksie.
- [ ] Pozwolić Wydarzeniu Świata tworzyć Zagrożenie.
- [ ] Każda karta może posiadać własną regułę rozmieszczenia.
- [ ] Obsłużyć regułę miejsca awaryjnego.
- [ ] Jeśli nie istnieje legalne miejsce podstawowe ani awaryjne — wydarzenie zostaje odrzucone.
- [ ] Kliknięcie znacznika pokazuje szczegóły.
- [ ] Pokazać nazwę problemu.
- [ ] Pokazać opis fabularny.
- [ ] Pokazać aktualny efekt.
- [ ] Pokazać warunek zakończenia.
- [ ] Pokazać dostępną akcję na heksie.
- [ ] Wejście na heks nie uruchamia interakcji automatycznie.
- [ ] Bohater świadomie wybiera akcję rozwiązania problemu.
- [ ] Obsłużyć kilka metod rozwiązania jednego problemu.
- [ ] Metody mogą korzystać z różnych statystyk.
- [ ] Metody mogą prowadzić do walki.
- [ ] Metody mogą mieć różne konsekwencje.
- [ ] Sukces usuwa problem.
- [ ] Sukces usuwa znacznik.
- [ ] Sukces wyłącza efekt wydarzenia.
- [ ] Po sukcesie karta trafia na stos odrzuconych.
- [ ] Porażka pozostawia wydarzenie aktywne.
- [ ] Problem po porażce może zostać podjęty ponownie.
- [ ] Inny bohater może później podjąć próbę rozwiązania problemu.
- [ ] Obsłużyć kilka aktywnych Zagrożeń jednocześnie.
- [ ] Nie wprowadzać limitu aktywnych Zagrożeń.
- [ ] Znacznik może znajdować się na heksie z innym obiektem.
- [ ] Znacznik może pojawić się na heksie zajętym przez bohatera.
- [ ] Zapisywać sposób rozwiązania problemu.
- [ ] Dodać wpis do historii Wydarzeń Świata.
- [ ] Przygotować punkt integracji z Kroniką Świata.
- [ ] Stworzyć 3–5 testowych Zagrożeń.

## Pierwszy problem testowy

**Rozbójnicy na trakcie**

Możliwe drogi:
- Walka — zaatakuj obóz.
- Intryga — zakradnij się i zniszcz zapasy.
- Dyplomacja — spróbuj przekonać lub zmusić grupę do opuszczenia traktu.

## Definition of Done

W trakcie normalnej rozgrywki pojawia się Wydarzenie Świata, tworzy fizyczny problem na planszy, problem wpływa na świat, bohater może dotrzeć na odpowiedni heks i rozwiązać go, a po sukcesie znacznik oraz efekt prawidłowo znikają.