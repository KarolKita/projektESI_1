# biblioteka do wczytywania danych
from openpyxl import load_workbook
# biblioteka do liczenia logarytmu
from math import log
# biblioteka sluzaca do graficznego przdstawienia drzewa
import tkinter as tk
# wlasna biblioteka zawierajaca klase implementujaca drzewko binarne
from drzewko_binarne import Drzewko


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
def entropia(tab, szuk):
    tab_ni = {}  # slownik z ilosciami przypadkow dla danego atrybutu
    n = len(tab['mieszka']['wieś'])  # ilosc kolumn z przypadkami
    # zliczanie ilosci przypadkow dla atrybutu
    for atr in tab[szuk]:
        tab_ni[atr] = sum(tab[szuk][atr])
    # liczenie entropi 'I'
    entr = 0
    for atr in tab_ni:
        if tab_ni[atr] > 0:
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
def max_laczna_entropia(tab, szuk):
    entr_maks = -1  # najwieksza laczna entropia
    atr_maks = ''  # atrybut z najwieksza entropia
    przes_maks = ''  # przeslanka dla ktorej atrybut ma najwieksza laczna entropie

    # wartosc entropi
    entr = entropia(tab, szuk)

    # liczenie lacznej wartosci entropi
    for przes in tab:
        if przes != szuk:
            for atr in tab[przes]:
                # szukanie atrybutu z najwieksza wartoscia lacznej entropi
                if entr_maks < (entr - entr_potw_zaprz(tab, szuk, przes, atr)):
                    entr_maks = entr - entr_potw_zaprz(tab, szuk, przes, atr)
                    atr_maks = atr
                    przes_maks = przes

    return atr_maks, przes_maks


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


# funkcja zwraca konkluzje z samymi '1' w przypadkach
def zwroc_konkluzje(tab, szuk):
    for atr in tab[szuk]:
        if len(tab[szuk][atr]) == sum(tab[szuk][atr]):
            return atr


# tworzenie korzenia
atr_temp, przes_temp = max_laczna_entropia(tablica, szukana)
drzewo = Drzewko(atr_temp)
drzewo.przeslanka = przes_temp


# funkcja tworzaca drzewo
# korz - to obiekt klasy Drzewko
# tab - 'tablica' z danymi
# szuk - szukana przeslanka
def tworz_drzewo(korz, tab, szuk):
    # podzial tabeli
    korz.tab_tak, korz.tab_nie = podzial_tab(tab, korz.przeslanka, korz.korzen)

    # tworzenie kolejnych galezi drzewa
    # galezie z 'tak'
    if sprawdz(korz.tab_tak, szuk) == 1:
        korz.tak = zwroc_konkluzje(korz.tab_tak, szuk)
    else:
        temp_t = max_laczna_entropia(korz.tab_tak, szuk)
        korz.tak = Drzewko(temp_t[0])
        korz.tak.przeslanka = temp_t[1]
        tworz_drzewo(korz.tak, korz.tab_tak, szuk)
    # galezie z 'nie'
    if sprawdz(korz.tab_nie, szuk) == 1:
        korz.nie = zwroc_konkluzje(korz.tab_nie, szuk)
    else:
        temp_n = max_laczna_entropia(korz.tab_nie, szuk)
        korz.nie = Drzewko(temp_n[0])
        korz.nie.przeslanka = temp_n[1]
        tworz_drzewo(korz.nie, korz.tab_nie, szuk)

    return korz


# tworzenie drzewa
tworz_drzewo(drzewo, tablica, szukana)

# lista zawierajaca dane do rysowania drzewa
dane = []


# tworzenie danych potrzebnych do graficznego przedstawienia drzewa,
# funkcja zwraca liste zawierajaca listy z nazwami etykiet oraz wspolrzednymi 'x' i 'y'
def dane_do_rysowania(korz, d, x, y):
    # dane korzenia
    d.append([korz.korzen, x, y])

    # dane wezla 'tak'
    if isinstance(korz.tak, Drzewko):
        dane_do_rysowania(korz.tak, d, x - 100, y + 75)
    else:
        d.append([korz.tak, x - 100, y + 75])

    # dane wezla 'nie'
    if isinstance(korz.nie, Drzewko):
        dane_do_rysowania(korz.nie, d, x + 100, y + 75)
    else:
        d.append([korz.nie, x + 100, y + 75])

    return d


# tworzenie danych
dane_do_rysowania(drzewo, dane, 495, 0)

# graficzne przedstawienie drzewa
# tworzenie okna
okno = tk.Tk()

# dodanie tytulu i rozmiarow okna
okno.title("Drzewko decyzyjne")
okno.geometry("1200x600")

# pakiet uzywany do rysowania lini
canvas = tk.Canvas(okno, width=1200, height=600)
canvas.pack()

# tworzenie graficzne drzewka
for etykieta in dane:
    # tworzenie etykiet
    tk.Label(master=okno,
             text=etykieta[0],
             font=20,
             width=10,
             borderwidth=2,
             relief="solid").place(x=etykieta[1], y=etykieta[2])

    # tworzenie lini
    if etykieta[0] == 'Telewizja' or etykieta[0] == 'Internet' or etykieta[0] == 'Prasa':
        continue
    else:
        # wspolrzedne startowe
        x_start = etykieta[1] + 50
        y_start = etykieta[2] + 20
        # rysowanie lini
        canvas.create_line(x_start, y_start, x_start-100, y_start+60, fill="green", width=3)
        canvas.create_line(x_start, y_start, x_start+100, y_start+60, fill="red", width=3)

    # tworzenie etykiet 'tak' i 'nie'
    tk.Label(master=okno, text='TAK', font=5).place(x=x_start - 70, y=y_start + 20)
    tk.Label(master=okno, text='NIE', font=5).place(x=x_start + 40, y=y_start + 20)

okno.mainloop()
