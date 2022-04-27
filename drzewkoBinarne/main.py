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


# liczenie entropi 'I' dla warunku j
# tab - 'tablica' z danymi
# szuk - szukana przeslanka
# n - liczba kolumn z przypadkami (0,1)
def entropia(tab, szuk, n):
    tab_ni = {}  # slownik z ilosciami przypadkow dla danego atrybutu
    # zliczanie ilosci przypadkow dla atrybutu
    for atr in tab[szuk]:
        tab_ni[atr] = sum(tab[szuk][atr])
    # liczenie entropi 'I'
    entr = 0
    for atr in tab_ni:
        entr -= (tab_ni[atr] / n) * log(tab_ni[atr]/n, 2)
    return entr


# liczenie entopi potwierdzajacych i zatwierdzajacych warunek j
# tab - 'tablica' z danymi
# szuk - szukana przeslanka
# n - liczba kolumn z przypadkami (0,1)
def entr_potw_zaprz(tab, szuk, przes, war):
    n = len(tab[przes][war])  # liczba przypadkow
    nr = 0  # numer kolumny sprawdzanego przypadku
    # tworzenie slownika do przechowywania ilosci przypadkow potwierdzajacych i zaprzeczajacych warunek j
    tab_ni = {}
    for atr in tab[szuk]:
        tab_ni[atr] = {"n+": 0, "n-": 0}

    # zliczanie ilosci przypadkow dla warunku war
    # w tej petli bedziemy chodzic po przypadkach dla warunku war
    # gdzie p_w to przypadek w nr-kolumnie
    for p_w in tab[przes][war]:
        # w tej sprawdzamy przypadki dla atrybutow z konkluzji w nr-kolumnie
        for atr in tab[szuk]:
            # szukamy atrybutow dla ktorych wartosc przypadku jest rowna '1'
            if tab[szuk][atr][nr] == 1:
                if p_w == 1:
                    # zwiekszamy ilosc elementow potwierdzajacych warunek
                    tab_ni[atr]['n+'] += 1
                else:
                    # zwiekszamy ilosc elementow zaprzeczających warunek
                    tab_ni[atr]['n-'] += 1

        nr += 1  # zwiekszamy numer kolumny

    # liczenie entropi potwierdzajacych oraz zaprzeczajacych warunek
    n_potw = sum(tab[przes][war])  # laczna ilosc elementow potwierdzajacych warunek
    n_zaprz = n - n_potw  # laczna ilosc elementow zaprzeczajacych warunek
    entr_potw = 0  # entropia po potwierdzniu warunku
    entr_zaprz = 0  # entropia po zaprzeczeniu warunku

    for atr in tab[szuk]:
        # liczenie entropi po potwierdzeniu warunku
        if tab_ni[atr]['n+'] > 0:
            entr_potw -= (tab_ni[atr]['n+'] / n_potw) * log((tab_ni[atr]['n+'] / n_potw), 2)
        # liczenie entropi po zaprzeczeniu warunku
        if tab_ni[atr]['n-'] > 0:
            entr_zaprz -= (tab_ni[atr]['n-'] / n_zaprz) * log((tab_ni[atr]['n-'] / n_zaprz), 2)

    return (n_potw / n) * entr_potw + (n_zaprz / n) * entr_zaprz


# funkcja zwracajaca atrybut z nawieksza laczna entropia
# tab - 'tablica' z danymi
# szuk - szukana przeslanka
# ilo_k - ilosc kolumn w tabeli
def max_laczna_entropia(tab, szuk, ilo_k):
    entr_maks = -1  # najwieksza laczna entropia
    atr_maks = ''  # atrybut z najwieksza entropia

    # wartosc entropi
    entr = entropia(tab, szuk, ilo_k)

    # liczenie lacznej wartosci entropi
    for przes in tab:
        if przes != szuk:
            for atr in tab[przes]:
                # szukanie atrybutu z najwieksza wartoscia lacznej entropi
                if entr_maks < (entr - entr_potw_zaprz(tab, szuk, przes, atr)):
                    entr_maks = entr - entr_potw_zaprz(tab, szuk, przes, atr)
                    atr_maks = atr

    return atr_maks


# funkcja dzielaca tabele
# tab 'tablica' z danymi
# przes_p przeslanka dla ktore atrybut posiada najwieksza laczna entropie
# atr_p atrybut na podstawie ktorego dzielimy tabele
def podzial_tab(tab, przes_p, atr_p):
    tab_tak = {}  # tablica z danymi potwierdzajacymi warunek
    tab_nie = {}  # tablica z danymi zaprzeczajacymi warunek

    # wczytywanie przeslanek i atrybutow do tabel
    for przes in tab:
        tab_tak[przes] = {}
        tab_nie[przes] = {}
        for atr in tab[przes]:
            tab_tak[przes][atr] = []
            tab_nie[przes][atr] = []

    nr_kol = 0  # numer kolumny

    # wczytanie przypadkow do tablic
    for przyp_p in tab[przes_p][atr_p]:
        for przes in tab:
            for atr in tab[przes]:
                if przyp_p == 1:
                    # tablica z elementami potwierdzajacymi
                    tab_tak[przes][atr].append(tab[przes][atr][nr_kol])
                else:
                    # tablica z elementami zaprzeczajacymi
                    tab_nie[przes][atr].append(tab[przes][atr][nr_kol])
        nr_kol += 1  # zwiekszanie numeru kolumny

    return tab_tak, tab_nie


# funkcja sprawdzajaca czy jedna z szukanych konkluzji posiada same '1'
# tab - 'tablica' z danymi
# szuk - szukana przeslanka
def sprawdz(tab, szuk):
    for atr in tab[szuk]:
        if len(tab[szuk][atr]) == sum(tab[szuk][atr]):
            return 1
