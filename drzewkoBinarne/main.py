# biblioteka do wczytywania danych
from openpyxl import load_workbook
# biblioteka do liczenia logarytmu
from math import log


# ladowanie danych z excela
wb = load_workbook('../testowy.xlsx')
arkusz = wb.active

# 'tablica' z danymi
tablica = {}

# zmienne pomocnicze
var = None
ilo_wierszy = 10  # ilosc wierszy w arkuszu
ilo_kolumn = 14  # ilosc kolumn w arkuszu
atrybut = arkusz.cell(1, 1).value  # pierwszy atrybut w arkuszu

# wczytanie danych do tablicy wiersz po wierszu z arkusza
# gdzie w pierwszej kolumnie sa przeslanki
# w drugiej kolumnie sa atrybuty
# a w kolumnach od 3 do 103 (?) sa przypadki
for nr_wiersza in range(1, ilo_wierszy+1):
    # wczytanie przeslanki
    if arkusz.cell(nr_wiersza, 1).value != var:
        atrybut = arkusz.cell(nr_wiersza, 1).value
        tablica[atrybut] = {}

    # wczytanie atrybutu
    tablica[atrybut][arkusz.cell(nr_wiersza, 2).value] = []

    # wczytanie przypadkow dla atrybutu (czyli '0' oraz '1')
    for wiersz in arkusz.iter_rows(min_row=nr_wiersza, min_col=3, max_row=nr_wiersza, max_col=ilo_kolumn):
        for przypadek in wiersz:
            tablica[atrybut][arkusz.cell(nr_wiersza, 2).value].append(przypadek.value)


# testowe wypisanie tablicy
def wypisz(tab):
    for p in tab:
        print(p, ": ")
        for a in tab[p]:
            print("     ", a, ": ", end=" ")
            print(tab[p][a])


# szukana przeslanka
szukana = 'reklama'


# liczenie entropi 'I'
# *tab - nasza 'tablica' z danymi
# szuk - szukana przeslanka
# n - liczba kolumn z przypadkami
def entropia(tab, szuk, n):
    tab_ni = {}  # slownik z ilosciami przypadkow dla danego atrybutu
    # zliczanie ilosci przypadkow
    for atr in tab[szuk]:
        tab_ni[atr] = sum(tab[szuk][atr])
    # liczenie entropi 'I'
    entr = 0
    for atr in tab_ni:
        entr -= (tab_ni[atr] / n) * log(tab_ni[atr]/n, 2)
    print('Entropia = ', entr)


entropia(tablica, szukana, ilo_kolumn-2)
