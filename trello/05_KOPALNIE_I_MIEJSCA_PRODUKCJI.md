# 05 — Kopalnie i Miejsca Produkcji

**Status Kanban:** BACKLOG

## Cel

Fizycznie umieścić źródła zasobów w świecie.

Tworzymy wspólny typ obiektu: **Miejsce Produkcji**.

Pierwszym implementowanym typem będzie **Kopalnia**. W przyszłości system może obsługiwać również Tartak, Kamieniołom, Gospodarstwo, Łowisko i inne miejsca produkcji. Nie implementujemy wszystkich typów od razu.

## Oficjalna lista 10 materiałów

W Rise & Glory obowiązuje zamknięta podstawowa lista 10 materiałów przechowywanych na planszetce bohatera:

1. **Żelazo** — broń, pancerze i narzędzia.
2. **Drewno** — łuki, tarcze, budowa i naprawy.
3. **Skóra** — lekkie zbroje, pasy, sakwy i rękawice.
4. **Srebro** — przedmioty przeciw potworom i klątwom, amulety oraz specjalna broń.
5. **Tkanina** — szaty, kaptury oraz wyposażenie Kultury i Dyplomacji.
6. **Klejnoty** — biżuteria, przedmioty wartościowe, amulety i bardziej zaawansowane receptury.
7. **Kamień** — budowle, fortyfikacje, naprawy i infrastruktura.
8. **Mroczna Stal** — rzadki materiał do potężnego, niebezpiecznego lub późnego ekwipunku.
9. **Proch** — materiały wybuchowe, specjalne narzędzia i późniejsze technologie.
10. **Odłamek Upadku** — specjalny materiał związany bezpośrednio z postępującym upadkiem świata.

### Odłamek Upadku

**Odłamek Upadku** jest charakterystycznym materiałem Rise & Glory. Jego dostępność rośnie wraz z pogarszaniem się stanu świata.

- **Poziom Świata 1:** praktycznie nie występuje; może pojawić się tylko jako wyjątkowa zapowiedź przyszłych wydarzeń.
- **Poziom Świata 2:** zaczyna pojawiać się przy pierwszych anomaliach, skażonych ruinach i wydarzeniach związanych z rozpadem świata.
- **Poziom Świata 3:** można zdobywać go częściej z potężniejszych przeciwników, skażonych miejsc i ważniejszych Questów.
- **Poziom Świata 4:** świat jest już mocno przesiąknięty skutkami Upadku, więc materiał staje się wyraźnie łatwiejszy do znalezienia.

Odłamek Upadku nie jest zwykłym materiałem do podstawowego craftingu. Ma służyć przede wszystkim do wyjątkowych zastosowań: tworzenia lub wzmacniania **Mrocznej Stali**, przeklętego i potężnego ekwipunku, specjalnych rytuałów, aktywowania lub naprawiania starożytnych artefaktów, otwierania niedostępnych wcześniej możliwości oraz mechanik związanych z końcową fazą gry.

Założenie projektowe: **im bardziej świat upada, tym większy dostęp gracze otrzymują do potężnych materiałów i ryzykownych możliwości**. Upadek świata jest więc jednocześnie zagrożeniem i źródłem nowych sposobów budowania siły bohatera.

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