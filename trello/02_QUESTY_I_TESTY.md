# 02 — Questy i Testy: wspólny silnik

**Status Kanban:** DO ZROBIENIA

## Cel

Stworzyć jeden wspólny system Questów. Każdy przyszły Quest powinien być przede wszystkim zestawem danych, etapów i opcji, a nie osobno programowaną mechaniką.

Podstawowy test:

`k20 + odpowiednia statystyka + bonusy >= poziom trudności`

Statystyki: Walka, Handel, Intryga, Dyplomacja, Kultura, Nauka.

## Punkty do działania

- [ ] Stworzyć jeden wspólny model Questa.
- [ ] Obsłużyć Quest składający się z wielu etapów.
- [ ] Każdy etap może mieć kilka dostępnych opcji.
- [ ] Opcje mogą wykorzystywać różne statystyki.
- [ ] Opcje mogą posiadać różne poziomy trudności.
- [ ] Opcja może kosztować Złoto.
- [ ] Opcja może wymagać Towaru.
- [ ] Opcja może wymagać Przedmiotu.
- [ ] Opcja może wymagać Pomocnika.
- [ ] Opcja może prowadzić do walki.
- [ ] Opcja może prowadzić do następnego etapu.
- [ ] Opcja może prowadzić do alternatywnego etapu.
- [ ] Różne wybory mogą prowadzić do różnych konsekwencji.
- [ ] Obsłużyć sukces.
- [ ] Obsłużyć porażkę.
- [ ] Obsłużyć Nat 1.
- [ ] Obsłużyć Nat 20.
- [ ] Obsłużyć maksymalnie 4 porażki Questa.
- [ ] Obsłużyć ponowną próbę.
- [ ] Ustalić ostateczny koszt Akcji etapu Questa.
- [ ] Ustalić ostateczny koszt ponownej próby.
- [ ] Ustalić wpływ porażek na nagrody.
- [ ] Rozważyć mechanikę „Przygotuj się”.
- [ ] Zapisywać historię przebiegu Questa.
- [ ] Obsłużyć Złoto jako nagrodę.
- [ ] Obsłużyć Punkty Legendy jako nagrodę.
- [ ] Obsłużyć Towary jako nagrodę.
- [ ] Obsłużyć Przedmioty jako nagrodę.
- [ ] Obsłużyć utratę Questa.
- [ ] Obsłużyć porzucenie Questa.
- [ ] Quest może wymagać konkretnej lokacji.
- [ ] Quest może wymagać konkretnego heksu.
- [ ] Quest może tworzyć cel na mapie.
- [ ] Quest może zawierać walkę.
- [ ] Quest może mieć kilka różnych metod ukończenia.
- [ ] Przebudować „Szatańskie siły” na wzorcowy Quest wspólnego systemu.
- [ ] Przygotować kilka prostych Questów testowych.
- [ ] Przygotować punkt integracji z Kroniką Świata.

## Ważna zasada projektowa

Nie tworzyć fałszywego wyboru, np. `Nauka 12` albo `Intryga 14`, jeżeli obie opcje prowadzą dokładnie do tego samego rezultatu.

Różne drogi powinny różnić się przynajmniej jednym elementem: ryzykiem, kosztem, konsekwencją, nagrodą albo dalszym przebiegiem historii.

## Definition of Done

Można stworzyć nowy wieloetapowy Quest z testami, alternatywnymi drogami, walką i nagrodami bez pisania osobnej mechaniki tylko dla tego Questa.