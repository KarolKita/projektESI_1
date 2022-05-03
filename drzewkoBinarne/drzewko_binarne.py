# klasa stworzona do tworzenia drzewka, zawierajaca
# korzen oraz galezie drzewka nazwane 'tak' oraz 'nie'
class Drzewko:
    def __init__(self, korzen):
        self.korzen = korzen
        self.przeslanka = None
        self.tak = None
        self.nie = None
        self.tab_tak = None
        self.tab_nie = None

    def chodzenie(self):
        # wyswietlenie korzenia
        print(self.korzen)

        # wyswietlenie wezla 'tak'
        if isinstance(self.tak, Drzewko):
            self.tak.chodzenie()
        else:
            print(self.tak, end='')

        print('          ', end='')

        # wyswietlenie wezla 'nie'
        if isinstance(self.nie, Drzewko):
            self.nie.chodzenie()
        else:
            print(self.nie)

    def __str__(self):
        return "%s: { tak: %s, nie: %s}" % (self.korzen, self.tak, self.nie)
