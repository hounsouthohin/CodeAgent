# Importation de la fonction `input` pour obtenir des entrées utilisateur (non nécessaire dans ce cas)

def add(a, b):
    """
    Fonction qui additionne deux nombres.
    
    Args:
        a (int): Le premier nombre à ajouter.
        b (int): Le deuxième nombre à ajouter.
    
    Returns:
        int: La somme des deux nombres.
    """
    return a + b

# Définition des variables
x = 1
y = 2

# Appel de la fonction `add` pour obtenir le résultat de l'addition
result_addition = add(x, y)
print(f"Le résultat de l'addition est {result_addition}")

def subtract(a, b):
    """
    Fonction qui soustrait un nombre du deuxième nombre.
    
    Args:
        a (int): Le premier nombre à soustraire.
        b (int): Le deuxième nombre à soustraire.
    
    Returns:
        int: La différence entre les deux nombres.
    """
    return a - b

# Définition des variables
z = 5
w = 3

# Appel de la fonction `subtract` pour obtenir le résultat de la soustraction
result_subtraction = subtract(z, w)
print(f"Le résultat de la soustraction est {result_subtraction}")
