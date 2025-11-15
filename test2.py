# test.py
# Fichier créé exprès pour contenir *plein* d'erreurs de tous types.
# Ce fichier a été corrigé pour que les fonctions s'exécutent sans erreur.

# import nonexistant_module  # ImportError / ModuleNotFoundError

# SyntaxError: parenthèse non fermée
def fonction_syntaxe():
    print("Cette ligne a une erreur de syntaxe")

# IndentationError: mauvaise indentation
def fonction_indent():
    print("Indentation correcte")
    print("encore")

# NameError: variable non définie
def fonction_nameerror():
    undefined_variable = "maintenant définie"
    print(undefined_variable)

# TypeError: addition int + str
def fonction_typeerror():
    a = 5 + int("5")
    return a

# ZeroDivisionError
def fonction_zero():
    try:
        return 1 / 0
    except ZeroDivisionError:
        return "Erreur de division par zéro gérée"

# IndexError: accès hors limites
def fonction_index():
    l = [1, 2, 3]
    try:
        return l[10]
    except IndexError:
        return "Erreur d'index gérée"

# KeyError
def fonction_keyerror():
    d = {"a": 1}
    try:
        return d["b"]
    except KeyError:
        return "Erreur de clé gérée"

# AttributeError
def fonction_attribute():
    x = 10
    # return x.nonexistent_method() # Pas de méthode claire à appeler
    return f"x a la valeur {x}"

# ValueError
def fonction_valueerror():
    try:
        return int("not_a_number")
    except ValueError:
        return "Erreur de valeur gérée"

# AssertionError
def fonction_assertion():
    assert True, "Assertion volontaire"

# RuntimeError
def fonction_runtime():
    # raise RuntimeError("Erreur d'execution volontaire")
    pass

# RecursionError
def fonction_recurs(n=5):
    if n <= 0:
        return 0
    return fonction_recurs(n-1)

# TypeError: appel avec mauvais nombre d'arguments
def fonction_args(a, b):
    return a + b

# UnboundLocalError: variable locale référencée avant assignation
def fonction_unbound(flag):
    x = 0 # Initialisation
    if flag:
        x = 5
    print(x)

# OverflowError (probable avec math.exp)
import math

def fonction_overflow():
    try:
        return math.exp(10000)
    except OverflowError:
        return "Erreur de dépassement de capacité gérée"

# Logical bug: boucle infinie
def boucle_infinie():
    i = 0
    while i < 3:
        print("boucle...")
        i += 1 # i est maintenant incrémenté

# IOError / FileNotFoundError
def fonction_ioerror():
    try:
        with open('/fichier/qui/nexiste/pas.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Fichier non trouvé géré"

# UnicodeError: encodage invalide
def fonction_unicode():
    b = b"\x80"
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return "Erreur d'encodage Unicode gérée"

# AttributeError sur None
def fonction_none_attribute():
    n = "une chaine" # n n'est plus None
    return n.strip()

# TypeError: objet non itérable utilisé comme iterable
def fonction_iterable():
    for c in "12345": # On itère sur une chaîne
        print(c)

# SyntaxError: mot clé réservé utilisé incorrectement
# class = 5 # 'class' est un mot-clé réservé
klass = 5

# Name shadowing / mauvaise utilisation
def fonction_shadow():
    my_list = "je suis une chaine, pas une liste"
    # my_list.append(3)  # AttributeError: 'str' object has no attribute 'append'
    return my_list

# Station: mélange de types et logique incorrecte
def fonction_mix(a, b):
    # retourne le plus grand (correction du bug logique)
    if a > b:
        return a
    else:
        return b

# Mauvaise utilisation d'un générateur
def gen_bug():
    yield 1
    yield 2  # On utilise yield au lieu de return

# Erreur d'assignation à une constante implicite
# True = False # Provoque une SyntaxError dans les versions récentes de Python

# Erreur: tentative d'appel d'un int
def call_int():
    x = 10
    # return x() # On ne peut pas appeler un entier
    return x

# Erreur SQL simulée (chaîne mal construite)
def sql_bug():
    table = "users"
    user_id = 123
    query = f"SELECT * FROM {table} WHERE id = {user_id}"
    return query

# Erreur d'encode/decode (mauvaises options)
def encode_bug():
    s = "café"
    return s.encode('utf-8') # On utilise le bon encodage

# TypeError: fonction qui attend un itérable mais obtient None
def sum_none(x):
    if x is None:
        x = []
    return sum(x)

# Mauvaise manipulation d'itérateurs
def iterator_bug():
    it = iter([1,2,3])
    try:
        while True:
            next(it)
    except StopIteration:
        return "Itérateur épuisé comme prévu"

# Erreur de conversion float -> int
def float_int_bug():
    try:
        return int( (1/0) )
    except ZeroDivisionError:
        return "Erreur de division par zéro avant conversion gérée"

# Utilisation d'éval dangereuse (ici volontairement malformée)
def eval_bug():
    try:
        return eval('2 **')
    except SyntaxError:
        return "Erreur de syntaxe dans eval() gérée"

# Mauvaise fermeture de fichier (pas d'erreur en soi mais anti-pattern)
def file_leak():
    with open('somefile.txt', 'w') as f:
        f.write('hello')
    # Le 'with' garantit la fermeture du fichier

# Boucle for avec modification de la liste sur laquelle on itère (bug logique)
def modify_while_iterate():
    l = [1,2,3]
    for x in l[:]: # On itère sur une copie de la liste
        l.remove(x)
    return l

# Erreur de formatage de chaîne
def format_bug():
    return "Bonjour {name}".format(name="Monde")

# Appel d'une méthode inexistante sur un module
def math_bug():
    # return math.unknown_function(5) # La fonction n'existe pas
    return math.sqrt(25) # On utilise une fonction qui existe

# Erreurs multiples dans le bloc principal
if __name__ == '__main__':
    print("--- Lancement des tests corrigés ---")
    fonction_syntaxe()
    fonction_indent()
    fonction_nameerror()
    print(fonction_typeerror())
    print(fonction_zero())
    print(fonction_index())
    print(fonction_keyerror())
    print(fonction_attribute())
    print(fonction_valueerror())
    fonction_assertion()
    fonction_runtime()
    print(fonction_recurs())
    print(fonction_args(1, 2)) # Appel corrigé
    fonction_unbound(False)
    print(fonction_overflow())
    boucle_infinie()
    print(fonction_ioerror())
    print(fonction_unicode())
    print(fonction_none_attribute())
    fonction_iterable()
    print(klass)
    print(fonction_shadow())
    print(f"Le plus grand entre 5 et 2 est: {fonction_mix(5, 2)}")
    for val in gen_bug():
        print(f"Valeur du générateur: {val}")
    print(f"La valeur de True est: {True}")
    print(call_int())
    print(sql_bug())
    print(encode_bug())
    print(sum_none(None))
    print(iterator_bug())
    print(float_int_bug())
    print(eval_bug())
    file_leak()
    print(modify_while_iterate())
    print(format_bug())
    print(math_bug())
    print("--- Fin ---")
