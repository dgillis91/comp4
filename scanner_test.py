from scanner import Scanner
from readers import FileReader
from fsa import initialize_scanner


scan = initialize_scanner(None)
while True:
    tk = next(scan)
    print(tk)
    if tk.payload == 'eof':
        break
