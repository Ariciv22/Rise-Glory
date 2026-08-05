# Assety premium kostki k20

Silnik działa bez dodatkowych obrazów i używa proceduralnej kostki Rise & Glory.

Finalne rendery PNG można dodać bez zmiany kodu:

```text
Grafiki/kostka_k20/
├── roll/
│   ├── 0001.png
│   ├── 0002.png
│   └── ...
├── final/
│   ├── 01.png
│   ├── 02.png
│   └── 20.png
└── settle/
    ├── 01/final.png
    ├── 02/final.png
    └── 20/final.png
```

## Zasady

- Pliki muszą mieć przezroczyste tło.
- Wszystkie klatki powinny mieć identyczny rozmiar i punkt środka.
- `roll/` zawiera wspólne klatki szybkiego turlania.
- `final/XX.png` albo `settle/XX/final.png` przedstawia końcową pozycję wyniku `XX`.
- Każda finalna kostka musi mieć poprawną numerację 1–20 bez powtórzeń.
- Gdy assetu brakuje, gra automatycznie używa proceduralnego renderera.
