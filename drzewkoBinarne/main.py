# biblioteka do wczytywania danych
from openpyxl import load_workbook

# ladowanie danych z excela
wb = load_workbook('../testowy.xlsx')
arkusz = wb.active