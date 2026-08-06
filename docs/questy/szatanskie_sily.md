# Quest: Szatańskie siły

## Dane główne

- **ID:** `klatwa_katakumb_0`
- **Nazwa:** Szatańskie siły
- **Talia:** Talia Nauki
- **Poziom świata:** 1
- **Dostępność poziomowa:** dostępny od poziomu świata 1 również na wszystkich późniejszych poziomach
- **Rodzaj:** zwykły quest z Talii Nauki
- **Dostępny w:** wyłącznie na tablicy ogłoszeń Zamku Artium
- **Sposób pojawiania się:** zawsze znajduje się na tablicy ogłoszeń w Artium od początku rozgrywki
- **Miejsce rozpoczęcia i wykonania:** Zamek Artium
- **Liczba kopii:** 1
- **Można sprzedać:** tak
- **Można wymienić:** tak
- **Można porzucić:** tak
- **Quest wspólny:** nie
- **Liczba etapów:** 3
- **Struktura:** złożony, liniowy quest z alternatywnymi testami
- **Koszt pobrania:** 0 akcji
- **Koszt rozpoczęcia questa:** 0 akcji po dotarciu do Zamku Artium
- **Koszt wykonania każdego etapu lub ponowienia testu:** 1 akcja
- **Grafika główna i rozwinięć:** `uczony w katakumbach.png`
- **Ikona:** do przygotowania
- **Znacznik mapy:** niewymagany w pierwszej wersji, ponieważ quest jest pobierany i wykonywany w Artium

## Sposób uruchamiania w interfejsie

1. Gracz musi dotrzeć do Zamku Artium.
2. Na tablicy ogłoszeń w Artium zawsze dostępna jest karta „Szatańskie siły”.
3. Po pobraniu karta trafia do aktywnych questów bohatera.
4. Questa nie wykonuje się bezpośrednio z planszetki bohatera.
5. Podczas pobytu w Artium w ekranie zamku pojawia się osobna zakładka **„Quest: Szatańskie siły”**.
6. Po wejściu do zakładki wysuwa się pozioma karta zadania zawierająca grafikę, tekst aktualnego etapu, dostępne warianty testu, próg, koszt oraz przycisk wykonania.
7. Kliknięcie wybranego wariantu testu kosztuje 1 akcję i wykonuje automatyczny rzut k20.
8. Po opuszczeniu Artium postęp zostaje zachowany, ale kolejnego etapu nie można wykonywać poza Zamkiem Artium.

## Tekst na tablicę ogłoszeń

> Śmiałek, który odegna światła i inne dziwy, hojnie zostanie wynagrodzony.

## Tekst karty głównej

Docierasz do Zamku Artium. Strażnicy nie zatrzymują cię, ponieważ widzą za twoim pasem zwinięte ogłoszenie zdjęte z tablicy.

> „Mamy nadzieję, że znajdziesz sposób, by odegnać monstrum z kaplicy zamkowej. Wyje i mieni się głęboko pod ziemią, spać nie daje, a nawet garnizon, który tu stacjonuje, źle walczy i nieszczęścia na niego spływają. Resztę usłyszysz od kapitana.”

## Zasady porażek i nagród

- Każdy nieudany test dodaje **1 znacznik porażki** do głównej karty questa.
- Zwykła porażka daje karę **+1 do progu następnego testu** w tym queście.
- Kara +1 nie kumuluje się. Kolejna zwykła porażka nadal oznacza najwyżej +1 do następnego testu.
- Kara zostaje zużyta po wykonaniu następnego testu, niezależnie od jego wyniku.
- Naturalne 1 daje zamiast tego karę **+2 do progu następnego testu**. Kara naturalnej 1 nie łączy się z karą +1 ze zwykłej porażki.
- Znaczniki porażki pomniejszają wyłącznie końcową nagrodę w złocie.
- Krótki miecz, paczki suszonego mięsa i Punkty Legendy nigdy nie są pomniejszane przez znaczniki porażki, o ile quest zostanie ukończony.
- Złoto po ukończeniu questa:
  - 0 znaczników: 8 złota,
  - 1 znacznik: 6 złota,
  - 2 znaczniki: 4 złota,
  - 3 znaczniki: 2 złota,
  - 4 znaczniki: quest przegrany, bez nagrody.
- Czwarty znacznik natychmiast przegrywa quest. Jeżeli czwarty znacznik zostałby dodany przez porażkę finałowego testu, walka z kultystą nie rozpoczyna się.
- Naturalne 20 rozpatruje się według ogólnych zasad questów.
- Ukończenie questa zapewnia zawsze **2 Punkty Legendy**, niezależnie od liczby znaczników porażki.

## Nagroda za ukończenie

- **8 złota** przed pomniejszeniem za znaczniki porażki,
- **2 Punkty Legendy**,
- **Krótki miecz** zapewniający obecnie zapisany bonus **+1 do Walki**,
- **3 paczki suszonego mięsa**.

Krótki miecz trafia do plecaka. Nie jest automatycznie zakładany i nie zastępuje obecnej broni bohatera.

---

# Rozwinięcie 1

## Dane

- **ID:** `klatwa_katakumb_1`
- **Nazwa:** Szatańskie siły
- **Miejsce:** Zamek Artium
- **Koszt:** 1 akcja
- **Warunek:** bohater przebywa w Zamku Artium
- **Można ponowić:** tak

## Tekst fabularny

Lampa doskonale oświetla drogę przez zawiłe i długie korytarze, gdzie cienie padają niczym długie sylwetki. Kroczysz niepewnie, lecz intuicja i mapa podpowiadają, że obrałeś właściwy kierunek. Po długiej wędrówce objawia się przed tobą ołtarzyk pokryty runami. Rozmyślasz nad kolejnym krokiem, szukając klucza do rozwiązania.

## Wybór testu

Gracz wybiera jedną z trzech możliwości:

1. **Nauka 11 — „Przeszukaj bezpiecznie bibliotekę”.**
2. **Intryga 14 — „Dotykasz ołtarza i kreślisz palcem po czerwonych znakach”.**
3. **Kultura 13 — „Wykonaj podstawowy obrzęd”.** Ten test można rozpocząć tylko po zużyciu **2 skór**. Gracz musi posiadać obie skóry przed rozpoczęciem testu; zostają odrzucone po wybraniu tej możliwości.

W pierwszej wersji skóry nie są dodawane do sklepu ani wyposażenia startowego. Wariant Kultury pozostaje niedostępny, dopóki gracz nie posiada 2 skór zdobytych z innego źródła.

## Sukces

Przejdź do rozwinięcia `klatwa_katakumb_2`.

## Porażka

- Dodaj 1 znacznik porażki.
- Ustaw karę +1 do progu następnego testu w tym queście. Kara nie kumuluje się.
- Przy naturalnej 1 ustaw zamiast tego karę +2.
- Etap można ponowić, ponownie płacąc 1 akcję.

---

# Rozwinięcie 2

## Dane

- **ID:** `klatwa_katakumb_2`
- **Nazwa:** Szatańskie siły
- **Miejsce:** Zamek Artium, katakumby
- **Koszt:** 1 akcja
- **Warunek:** bohater przebywa w Zamku Artium i ukończył rozwinięcie 1
- **Można ponowić:** tak

## Tekst fabularny

Po dłuższych oględzinach i odkurzeniu wielu ksiąg z pradawnej biblioteki łączysz fakty. Dawny kult pozostawił po sobie miejsce rytualne, na którym mordowano dzieci. Czas rozproszyć panującą tu magię i oczyścić miejsce z grzechu.

## Wybór testu

Gracz wybiera jedną z trzech możliwości:

1. **Nauka 13 — „Wypowiedz słowa rozdziału o końcu rytuału”.**
2. **Intryga 15 — „Zabierz księgę i przekonaj kapitana, że klątwa została uciszona”.**
3. **Kultura 14 — „Przeczytaj rozdział o mocach nadprzyrodzonych”.**

## Sukces

Przejdź do rozwinięcia `klatwa_katakumb_3`.

## Porażka

- Dodaj 1 znacznik porażki.
- Ustaw karę +1 do progu następnego testu w tym queście. Kara nie kumuluje się.
- Przy naturalnej 1 ustaw zamiast tego karę +2.
- Etap można ponowić, ponownie płacąc 1 akcję.

---

# Rozwinięcie 3

## Dane

- **ID:** `klatwa_katakumb_3`
- **Nazwa:** Szatańskie siły
- **Miejsce:** Zamek Artium, katakumby
- **Koszt:** 1 akcja
- **Warunek:** bohater przebywa w Zamku Artium i ukończył rozwinięcie 2
- **Etap finałowy:** tak

## Tekst fabularny

Przeczytane wersy mienią się na kartach księgi. Masz wrażenie, że zaraz zostaną oderwane od stronic — i rzeczywiście tak się dzieje. Słowa i litery splatają się w jedno zaklęcie, które uspokaja demoniczny ołtarz ofiarny. Pozostaje tylko pytanie: co teraz powiesz kapitanowi?

## Wybór testu

Gracz wybiera jedną z dwóch możliwości:

1. **Nauka 10 — „Zamknij księgę i zniszcz ją na dziedzińcu zamku przed kapitanem”.**
2. **Intryga 13 — „Przekonaj kapitana, że klątwa została uciszona, a księga przepadła wraz z zamkniętym rytuałem”.**

## Sukces

Quest zostaje ukończony. Kapitan mówi:

> „Niesłychane! Udało ci się opanować magię spod kaplicy zamkowej? Nie wierzyłem do końca w twoje możliwości, ale zawiodła mnie własna intuicja. Masz tutaj trochę prowiantu, obiecane złoto i ten scyzoryk — krótki miecz — na drogę!”

Gracz otrzymuje końcową nagrodę pomniejszoną wyłącznie w części złotej zgodnie z liczbą znaczników porażki.

## Porażka

- Dodaj 1 znacznik porażki za nieudany test.
- Jeśli jest to czwarty znacznik, quest zostaje natychmiast przegrany i walka się nie rozpoczyna.
- Przy maksymalnie 3 znacznikach klątwa księgi pochłania jednego ze strażników. Strażnik wpada w amok i rzuca się na bohatera z zakrwawionymi rękami pradawnych ofiar.
- Rozpoczyna się walka z przeciwnikiem **Odkryty kultysta**.
- Jeśli bohater wygra walkę, quest zostaje ukończony z wszystkimi zgromadzonymi znacznikami porażki.
- Jeśli bohater przegra walkę, quest zostaje przegrany i nie przyznaje żadnej nagrody.

## Przeciwnik finałowy — Odkryty kultysta

- **Nazwa:** Odkryty kultysta
- **Bazowe HP:** 4
- **Skalowanie HP:** przeciwnik otrzymuje dodatkowe HP zgodnie z aktualnym poziomem świata
- **Klasa Pancerza:** 11
- **Premia do ataku:** +0
- **Obrażenia:** 1 Rana po udanym trafieniu
- **Ucieczka:** niedozwolona
- **Osobna nagroda za walkę:** brak; zwycięstwo pozwala ukończyć quest

Skalowanie całkowitego HP kultysty:

- poziom świata 1: 6 HP,
- poziom świata 2: 8 HP,
- poziom świata 3: 10 HP,
- poziom świata 4: 12 HP.

## Tymczasowe zasady walki dla pierwszej wersji

- Bohater bez broni zadaje po trafieniu **1 obrażenie HP** przeciwnikowi.
- Broń z premią **+1 do obrażeń** zwiększa obrażenia pojedynczego trafienia do **2 HP**.
- Naturalne 20 podczas ataku rozpatruje dwa trafienia zgodnie z ogólnymi zasadami walki.
- Bohater bez zbroi ma KP 10.
- Zwykła zbroja zapewnia pełne KP 12.
- Odkryty kultysta zadaje bohaterowi 1 Ranę po udanym trafieniu.
- Z walki nie można uciec.

Statystyki przeciwnika i zasady są gotowe do wykorzystania przy tworzeniu pierwszego modułu walki.