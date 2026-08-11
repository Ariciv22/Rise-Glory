# 05 — Kopalnie i Miejsca Produkcji

**Status Kanban:** BACKLOG

## Cel

Fizycznie umieścić źródła zasobów w świecie.

Tworzymy wspólny typ obiektu: **Miejsce Produkcji**.

Pierwszym implementowanym typem będzie **Kopalnia**. W przyszłości system może obsługiwać również Tartak, Kamieniołom, Gospodarstwo, Łowisko i inne miejsca produkcji. Nie implementujemy wszystkich typów od razu.

## Punkty do działania

- [ ] Stworzyć wspólny obiekt Miejsce Produkcji.
- [ ] Kopalnia jako pierwszy typ.
- [ ] Znacznik miejsca na mapie.
- [ ] Rozmieszczanie miejsc podczas generowania świata.
- [ ] Kliknięcie miejsca pokazuje informacje.
- [ ] Nazwa miejsca.
- [ ] Typ produkowanego zasobu.
- [ ] Dostępna ilość zasobu.
- [ ] Akcja „Wydobywaj”.
- [ ] Koszt wydobycia w Akcjach.
- [ ] Bohater otrzymuje zasób.
- [ ] Respektować limit Towarów bohatera.
- [ ] Ustalić, czy zasób jest ograniczony.
- [ ] Ustalić mechanikę odnawiania zasobów.
- [ ] Ustalić tempo odnawiania.
- [ ] Zasoby można sprzedawać.
- [ ] Zasoby można wykorzystywać w Questach.
- [ ] Zasoby można wymieniać podczas Rady.
- [ ] Wydarzenia Świata mogą wpływać na produkcję.
- [ ] Zagrożenie może pojawić się na Miejscu Produkcji.
- [ ] Zagrożenie może tymczasowo zablokować miejsce.
- [ ] Po rozwiązaniu Zagrożenia miejsce ponownie działa.
- [ ] Poziom Świata może wpływać na produkcję.
- [ ] Przygotować kilka miejsc testowych.

## Przykładowy flow

Bohater dociera do Kopalni Żelaza → wybiera „Wydobywaj” → wydaje Akcje → otrzymuje Żelazo → wykorzystuje je później w handlu, Queście albo gospodarce.

## Definition of Done

Na mapie znajduje się działająca Kopalnia, bohater może pozyskać zasób, a zasób funkcjonuje później w gospodarce gry.