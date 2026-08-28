# Rise & Glory — AKCEPTACJE QUESTÓW 1–23

Data przeglądu: 2026-08-28

Ten plik zapisuje decyzje zaakceptowane podczas końcowego przeglądu Questów 1–23. Wartości poniżej są finalnymi ustaleniami projektowymi i przy implementacji zastępują wcześniejsze wpisy `DO USTALENIA` w `QUESTY_FINAL.md`.

## Zasada Miejsc tworzonych przez Questy

Quest może w wyniku konkretnego zakończenia utworzyć trwałe **Miejsce na mapie**. `qXX_result` jest wystarczającą informacją o tym, czy Miejsce powstało — nie tworzymy dodatkowej flagi tylko po to, aby potwierdzić jego istnienie. Funkcje Miejsc (akcje, handel, produkcja, leczenie, badania, nowe Questy itd.) będą projektowane osobno w dokumentacji Miejsc i później implementowane w kodzie.

---

# Q1 — Dzwon między nami

**Status:** zaakceptowany.

**Tablica Ogłoszeń**
- Wystawca: Wójt Elarin.
- Treść: od kilku nocy mieszkańców Elarin budzi bicie starego dzwonu dobiegające z opuszczonego cmentarza. Kaplica od lat stoi pusta, a mimo to dzwon odzywa się po zmroku. Poszukiwany jest ktoś, kto zbada sprawę i sprawi, aby mieszkańcy ponownie mogli zaznać spokojnego snu. Osoba, która rozwiąże problem, otrzyma zapłatę od wsi.
- Wskazówka nagrody: Złoto, ekwipunek lub wyjątkowa nagroda.

**Nagrody:**
- A — Uciszony dzwon: 7 Złota, losowy Hełm, +2 Legendy.
- B — Dzwon Trolfa: 9 Złota, 4 Wytrychy, Krótki Miecz, +1 Legenda.
- C — Tajemnica Eldana: 11 Złota, Towarzysz Bran, +1 Legenda. Bran: +1 do dowolnego rzutu, maksymalnie 2 razy na rundę Gracza.
- D — Wygnanie Eldana: 14 Złota, losowy Hełm, losowy Pierścień, +2 Legendy.

---

# Q2 — Pomocnik kata

**Status:** zaakceptowany.

**Tablica:** Kat Garran szuka pomocnika do przygotowania i przeprowadzenia egzekucji ośmiu skazańców. Ogłoszenie nie zdradza sprawy Orena ani Mardeka.

**Nagrody:**
- A — Ręce kata: 15 Złota, +2 Legendy, zwykły przedmiot związany z Garranem / Topór kata.
- B — Ósmy skazaniec: 7 Złota, +3 Legendy, wdzięczność Orena wynikająca z `q02_result`.
- C — Brudny kompromis: 20 Złota, +1 Legenda.

---

# Q3 — Ostatni spichlerz

**Status:** zaakceptowany.

**Tablica:** wystawca Klasztor w Thalwen. Słabe zbiory, napięcie wokół klasztornego spichlerza, mieszkańcy żądają wydania zapasów, klasztor szuka kogoś, kto opanuje sytuację przed rozlewem krwi.

**Nagrody:**
- A — Zamknięte bramy: 14 Złota, +1 Legenda, 2× Jedzenie.
- B — Podzielony chleb: 8 Złota, +2 Legendy, 3× Jedzenie.
- C — Chleb zabrany siłą: 5 Złota, +1 Legenda, 5× Jedzenie.

---

# Q4 — Żelazo pod sianem

**Status:** zaakceptowany.

**Tablica:** wystawca Straż Vargard. W Norven znaleziono ukryty skład starej i nowej broni; władze chcą ustalić pochodzenie arsenału i sprawdzić, czy wieś przygotowuje działania zbrojne.

**Nagrody:**
- A — Rozbrojona wieś: 13 Złota, +1 Legenda, losowa zwykła Broń.
- B — Straż Norven: 7 Złota, +2 Legendy, losowy rzadki Pierścień; trwały skutek: Norven posiada legalną Straż.
- C — Broń w cieniu: 5 Złota, +1 Legenda, losowa rzadka Broń.

---

# Q5 — Ogród umarłego

**Status:** zaakceptowany.

**Tablica:** wystawca Straż Eryndor. Przy drodze odnaleziono ciało, wokół którego po śmierci zaczęły wyrastać kwiaty na wcześniej jałowej ziemi. Straż chce zbadać zjawisko i jego zagrożenie.

**Nagrody:**
- A — Ostatnie kwiaty: 10 Złota, +1 Legenda, **3 różne materiały**.
- B — Ogród powraca: 6 Złota, +2 Legendy, losowy rzadki Amulet; tworzy trwałe Miejsce **Stary Ogród**.
- C — Cena nasienia: 18 Złota, +1 Legenda, 1 losowy rzadki materiał.

---

# Q6 — Za zamkniętą bramą

**Status:** zaakceptowany.

**Tablica:** wystawca Rada Lirion. Jedna z dzielnic objęta kwarantanną z powodu gwałtownej gorączki i ciemnych plam; liczba chorych rośnie, a rada szuka kogoś do ustalenia źródła choroby i zatrzymania epidemii.

**Nagrody:**
- A — Żelazny kordon: 14 Złota, +1 Legenda, Towarzysz **Lekkomyślny znachor** — leczenie kosztuje 2 Złota mniej; 2× losowa para Butów.
- B — Lazaret Lirion: 8 Złota, +2 Legendy, losowy rzadki Amulet; tworzy trwałe Miejsce **Lazaret Lirion**.
- C — Otwarte bramy: 18 Złota, +1 Legenda, losowy rzadki Pierścień, 1 losowy rzadki materiał.

---

# Q7 — Ziarno za murami

**Status:** zaakceptowany.

**Tablica:** wystawca Rada Valdren. Po słabych zbiorach wprowadzono czasowy zakaz wywozu zboża; przy bramie zatrzymano kupieckie wozy, których właściciel twierdzi, że kupił towar legalnie przed zakazem.

**Nagrody:**
- A — Zboże zostaje: 14 Złota, +1 Legenda, 3× Jedzenie, losowa zwykła Zbroja.
- B — Otwarty handel: 9 Złota, +2 Legendy, losowy rzadki Pierścień, 3 różne materiały.
- C — Nocny transport: 20 Złota, +1 Legenda, losowa rzadka Broń, 2 Wytrychy.

---

# Q8 — Martwy pokład

**Status:** zaakceptowany.

**Tablica:** wystawca Zarządca portu Eryndor. Do portu przydryfowała Srebrna Mewa bez załogi; na pokładzie są ślady choroby i nietknięty ładunek. Należy zbadać statek i odnaleźć załogę.

**Nagrody:**
- A — Ogień na wodzie: 13 Złota, +1 Legenda, 2 losowe materiały, losowa rzadka Zbroja.
- B — Srebrna Mewa wraca: 8 Złota, +2 Legendy, losowa rzadka Zbroja, losowa zwykła Broń; **Srebrna Mewa pozostaje aktywnym statkiem/Miejscem świata**.
- C — Cena ciszy: 22 Złota, +1 Legenda, losowy rzadki Amulet, losowa zwykła Broń.

---

# Q9 — Ostatnia woda

**Status:** zaakceptowany.

**Tablica:** wystawca Starszyzna Elarin. Spór trzech gospodarstw o wodę, przegrodzony kanał, wysychające pola i rosnące ryzyko przemocy.

**Nagrody:**
- A — Dawne koryto: 10 Złota, **+3 Legendy**, 3 różne materiały.
- B — Trzy kanały: koszt 4 Drewna, 4 Kamienia, 2 Żelaza; nagroda 7 Złota, +2 Legendy, losowy rzadki Pierścień; tworzy trwałe Miejsce **Folwark w Elarin**.
- C — Woda dla bogatszych: 19 Złota, +1 Legenda, losowa zwykła Broń, 2× Jedzenie.

---

# Q10 — Fałszywy król

**Status:** zaakceptowany.

**Tablica:** wystawca Mennica Lirion. W mieście pojawia się seria bardzo dobrych fałszywych monet, część po wypłatach z miejskiego skarbca.

**Nagrody:**
- A — Dwóch fałszerzy: 14 Złota, +2 Legendy, losowy zwykły Pierścień, 3 różne materiały.
- B — Fałszerz mennicy: 9 Złota, +3 Legendy, losowy rzadki Amulet; Daven pracuje dla Mennicy Lirion.
- C — Ostatnia fałszywa moneta: 24 Złota, +1 Legenda, losowa rzadka Broń, 2 Wytrychy.

---

# Q11 — Dzwony na trwogę

**Status:** zaakceptowany.

**Tablica:** wystawca Starszyzna Thalwen. Zwiadowcy ostrzegają o uzbrojonej grupie; wieś jest słaba, a w starej wieży wisi dzwon o zapomnianym znaczeniu.

**Nagrody:**
- A — Dzwony odpowiedziały: 9 Złota, +3 Legendy, losowy rzadki Hełm; trwały skutek świata: przywrócona **Sieć Dzwonów Alarmowych**.
- B — Cena ataku / Cena krwi: 14 Złota, +2 Legendy, losowy zwykły Pancerz, 3 różne materiały.
- C — Zasadzka na Harkela / Krew przed świtem: 12 Złota, +2 Legendy, losowa rzadka Broń, 2 Wytrychy.

---

# Q12 — Prawo gościny

**Status:** zaakceptowany.

**Tablica:** wystawca Straż Lirion. W gospodzie Pod Białym Jeleniem znaleziono czterech martwych podróżnych ułożonych według nieznanego rytuału.

**Nagrody:**
- A — Ostatni goście: 11 Złota, +3 Legendy, losowy rzadki Amulet, 3 różne materiały.
- B — Pierwszy stół: 7 Złota, +2 Legendy, losowy rzadki Pierścień; tworzy trwałe Miejsce/funkcję **Pierwszy Stół w gospodzie Pod Białym Jeleniem**.
- C — Zapomniany zwyczaj: 20 Złota, +1 Legenda, losowa zwykła Broń, 2 Wytrychy.

---

# Q13 — Złodziej złodzieja

**Status:** zaakceptowany.

**Tablica:** kontakt przez półświatek. Dyskretne zlecenie odzyskania ładunku przejętego przez Czarne Psy. Ogłoszenie nie zdradza pierwotnych właścicieli łupu.

**Nagrody:**
- A — Honor między złodziejami: 17 Złota, +1 Legenda, losowa zwykła Broń, 2 Wytrychy.
- B — To, co skradzione: 8 Złota, +3 Legendy, losowy rzadki Pancerz, 3 różne materiały.
- C — Trzeci złodziej: 23 Złota, +1 Legenda, losowa rzadka Broń, losowy rzadki Pierścień.

---

# Q14 — Pogrzeb przy drodze

**Status:** zaakceptowany.

**Tablica:** wystawca Zarządca ziem przy Artium. Obcy podróżni przygotowują pochówek przy trakcie, właściciel ziemi protestuje, a przybysze powołują się na stare prawo drogi.

**Nagrody:**
- A — Kamień przy drodze: 8 Złota, +3 Legendy, losowy rzadki Amulet, specjalny status **Świadek Drogi**.
- B — Dwa pożegnania: 12 Złota, +2 Legendy, losowy rzadki Pierścień, 3 różne materiały.
- C — Droga bez końca: 16 Złota, +1 Legenda, losowa zwykła Broń, 2 Wytrychy.

---

# Q15 — Świeca, która nie gaśnie

**Status:** zaakceptowany.

**Tablica:** wystawca Kupiec Nerin. Niezwykła świeca po Alrenie Vossie nie gaśnie i zachowuje się inaczej niż zwykły ogień; potrzeba osoby obeznanej z alchemią lub wynalazkami.

**Nagrody:**
- A — Ostatni płomień: 12 Złota, +2 Legendy, 3 różne materiały, losowy zwykły Amulet.
- B — Ogień Alrena: 8 Złota, +3 Legendy, losowy rzadki Pierścień, unikalny przedmiot/technologia **Lampa Alrena**.
- C — Cena wynalazku: 24 Złota, +1 Legenda, losowa rzadka Broń, 2 różne materiały.

---

# Q16 — Fałszywy bohater

**Status:** zaakceptowany.

**Tablica:** wystawca Starszyzna Norven. Garrik wraca z głową bestii, ale tej samej nocy następuje kolejny atak i znika pasterz. Ogłoszenie nie zdradza, że Garrik kłamie.

**Nagrody:**
- A — Bohater za drugim razem: 12 Złota, +3 Legendy, losowa rzadka Broń, 3 różne materiały.
- B — Prawdziwy łowca / Prawdziwy bohater: 16 Złota, +2 Legendy, losowa rzadka Zbroja, trofeum z bestii.
- C — Cena sławy / Legenda za złoto: 22 Złota, +1 Legenda, losowy rzadki Pierścień, losowa zwykła Broń.

---

# Q17 — Miód wiedźmy

**Status:** zaakceptowany.

**Tablica:** wystawca Pszczelarz Radan. Ule dają czerwony, dziwny miód; pszczoły latają głęboko w las. Radan podejrzewa trucie pasieki.

**Nagrody:**
- A — Spalony wrzos / Zwyczajny miód: 14 Złota, +1 Legenda, losowa rzadka Broń, 3 różne materiały.
- B — Czerwony miód: 9 Złota, +3 Legendy, losowy rzadki Amulet; tworzy trwałe Miejsce **Pasieka Czerwonego Miodu**.
- C — Klątwa na sprzedaż / Tani ul: 23 Złota, +1 Legenda, losowy rzadki Pierścień, losowa zwykła Broń.

---

# Q18 — Trzy filiżanki

**Status:** zaakceptowany.

**Tablica:** wystawca Olan. Stary kupiec szuka osoby znającej dawne prawo kupieckie, aby rozstrzygnąć niedokończoną umowę sprzed dwudziestu lat.

**Nagrody:**
- A — Trzecia filiżanka: 12 Złota, +3 Legendy, losowy rzadki Pierścień, 3 różne materiały.
- B — Nowy rachunek: 15 Złota, +2 Legendy, losowa zwykła Broń, losowy zwykły Amulet.
- C — Czwarty przy stole: 24 Złota, +1 Legenda, losowy rzadki Amulet, unikalny przedmiot **Kontrakt Dłużny**.

---

# Q19 — Samotny grób

**Status:** zaakceptowany.

**Tablica:** wystawca Strażnik traktu z Artium. Przy drodze pojawił się świeży grób z nazwiskiem żyjącego podróżnego i dzisiejszą datą śmierci; wokół mogiły rosną czarne korzenie.

**Nagrody:**
- A — Imię umarłego / Imię skreślone: 10 Złota, +2 Legendy, losowy rzadki Amulet, 3 różne materiały.
- B — Korzenie pod ziemią / Grób bez imienia: 8 Złota, +3 Legendy, losowy rzadki Pierścień, unikalny materiał **Próbka Czarnego Korzenia**.
- C — Pusty dół: 16 Złota, +2 Legendy, losowa rzadka Broń, losowa rzadka Zbroja; każda nieudana próba Walki w tej ścieżce dodatkowo +1 Rana.

---

# Q20 — Kamień szczęścia

**Status:** zaakceptowany.

**Tablica:** wystawcy Kupcy z targu w Valdren. Beldo sprzedaje kamienie obiecujące siedem dni szczęścia; mieszkańcy wydają na nie oszczędności.

**Nagrody:**
- A — Zwykły kamień: 12 Złota, +2 Legendy, losowy zwykły Pierścień, 3 różne materiały.
- B — Dobry Los: 8 Złota, +3 Legendy, losowy rzadki Amulet; tworzy trwałe Miejsce/wydarzenie **Jarmark Dobrego Losu w Valdren**.
- C — Szczęście kosztuje: 24 Złota, +1 Legenda, losowy rzadki Pierścień, 2 Wytrychy.

---

# Q21 — Kruk z pierścieniem

**Status:** zaakceptowany z przebudowanym początkiem.

**Tablica:** jubiler Teren prosi o pomoc w odzyskaniu kosztowności po wypadku wozu.

**Natychmiast po przyjęciu Questa:** Teren zaczepia bohatera i wyjaśnia, że widział nietypowego kruka. Ptak był bardziej zachłanny i agresywny wobec błyskotek niż normalne kruki: aktywnie przeszukiwał rzeczy, atakował przy próbie odpędzenia i wybierał złoto oraz kamienie. Teren widział, jak kruk porwał pierścień i odleciał w stronę lasu. Pierwszy etap Questa to **Śladem kruka**.

Nie wyjaśniamy od razu przyczyny nietypowego zachowania ptaka — zostaje furtka fabularna na rozwinięcie.

**Nagrody:**
- A — Uczciwa prowizja: 13 Złota, +3 Legendy, losowy rzadki Pierścień, 3 różne materiały.
- B — Prawo znalazcy: 18 Złota, +2 Legendy, losowy rzadki Amulet, losowa zwykła Broń.
- C — Błyszczące znalezisko: 21 Złota, +1 Legenda, losowy rzadki Pierścień, losowa rzadka Zbroja.

---

# Q22 — Porzucony namiot

**Status:** zaakceptowany.

**Tablica:** wystawca Straż Thalwen. Kilku podróżnych zaginęło na leśnym trakcie; przy drodze odnaleziono opuszczony namiot, świeże jedzenie i wygaszone ognisko, bez ciał ani śladów walki.

**Nagrody:**
- A — Obóz bez dymu: 10 Złota, +3 Legendy, losowy rzadki Amulet, 3 różne materiały.
- B — Łowcy złapani: 15 Złota, +2 Legendy, losowa rzadka Broń, losowa zwykła Zbroja, 2 Wytrychy.
- C — Ciepła kolacja: 25 Złota, +1 Legenda, losowy rzadki Pierścień, losowa rzadka Zbroja.

---

# Q23 — Wędrowny dom

**Status:** zaakceptowany.

**Tablica:** wystawcy podróżni z traktu. Między Norven a Durnhal widywany jest drewniany dom poruszający się na czterech mechanicznych nogach i krążący po tej samej trasie.

**Nagrody:**
- A — Ostatni krok: 14 Złota, +2 Legendy, 5 różnych materiałów, losowa zwykła Broń.
- B — Dom wraca na drogę: 9 Złota, +3 Legendy, losowy rzadki Amulet; tworzy trwałe Miejsce **Wędrowne Laboratorium Mervena**.
- C — Nowa droga: 18 Złota, +2 Legendy, unikalny przedmiot **Miniaturowy Wędrowny Dom**. Usunięto wcześniejszy rzadki Pierścień i rzadką Broń z tej nagrody.

**Miniaturowy Wędrowny Dom — efekt:** raz na rundę Gracza właściciel może natychmiast teleportować swoją postać do **najbliższego Miejsca na mapie**. Jeśli kilka Miejsc znajduje się w tej samej minimalnej odległości, gracz wybiera jedno. Przedmiot nie tworzy nowego Miejsca; korzysta z istniejącego systemu Miejsc.

---

# Stan po przeglądzie

Questy **1–23 zostały zaakceptowane projektowo** w zakresie przedstawionym w rozmowie: nagród, punktów Legendy, wyjątkowych przedmiotów, Towarzyszy, kluczowych trwałych skutków oraz opisanych Tablic Ogłoszeń / zmian fabularnych.

Nie kodować ich automatycznie tylko na podstawie tej akceptacji. Implementacja w `rg_content/quests_final.py` następuje dopiero po osobnym poleceniu właściciela projektu.
