def crea_documento(nome, contenuto):
    with open(f"{nome}.txt", "w") as f:
        f.write(contenuto)
    return f"File {nome}.txt creato."