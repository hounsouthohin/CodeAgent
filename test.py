# test_bugs.py - Code avec 22 bugs difficiles à trouver (corrigé)

import json
import re
from datetime import datetime

class DataProcessor:
    """Processeur de données avec plusieurs bugs cachés."""
    
    def __init__(self, config_file):
        try:
            self.config = self.load_config(config_file)
        except FileNotFoundError:
            self.config = {}
        self.data = []
        self.results = {}
    
    def load_config(self, file_path):
        """Charge la configuration depuis un fichier JSON."""
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config
    
    def process_data(self, input_data):
        """Traite les données en entrée."""
        # Bug 1: Corrigé - Vérifier si la liste est vide
        if not input_data:
            print("Warning: Empty data")
            return None
        
        # Bug 2: Corrigé - Itérer sur une copie de la liste
        for item in input_data[:]:
            if item.get('value', 0) > 100:
                input_data.remove(item)
        
        # Bug 3: Corrigé - Éviter la division par zéro
        if not input_data:
            return 0
        total = sum(item['value'] for item in input_data)
        average = total / len(input_data)
        
        return average
    
    def calculate_statistics(self, numbers):
        """Calcule des statistiques."""
        # Bug 4: Corrigé - Utiliser 'is None' pour la comparaison
        if numbers is None or not numbers:
            return {}
        
        # Bug 5 & 6: Corrigé - Initialiser max_value
        max_value = numbers[0]
        for num in numbers:
            if num > max_value:
                max_value = num
        
        return {
            'max': max_value,
            'min': min(numbers),
            'count': len(numbers)
        }
    
    def save_results(self, filename):
        """Sauvegarde les résultats."""
        # Bug 7: Corrigé - Utiliser 'with' pour la gestion du fichier
        with open(filename, 'w') as f:
            json.dump(self.results, f)
    
    def merge_dicts(self, dict1, dict2):
        """Fusionne deux dictionnaires."""
        # Bug 8: Corrigé - Ne pas modifier le dictionnaire original
        merged = dict1.copy()
        merged.update(dict2)
        return merged
    
    def filter_data(self, data, threshold):
        """Filtre les données selon un seuil."""
        # Bug 9: Corrigé - Utiliser '==' pour la comparaison
        filtered = [item for item in data if item.get('score') == threshold]
        return filtered
    
    def format_date(self, timestamp):
        """Formate une date."""
        # Bug 10: Corrigé - Gestion de timestamp potentiellement None
        if timestamp is None:
            return "Date: UNKNOWN"
        date_obj = datetime.fromtimestamp(timestamp)
        return f"Date: {date_obj.strftime('%Y-%m-%d')}".upper()

def process_user_data(users):
    """Traite les données utilisateurs."""
    # Bug 11 & 12: Corrigé - Indentation et variable non initialisée
    for user in users:
        name = user.get('name', 'Unknown')
        age = user.get('age')
        
        status = 'minor'
        if age is not None and age >= 18:
            status = 'adult'
        
        print(f"{name} is {status}")

def calculate_discount(price, discount_rate):
    """Calcule le prix après réduction."""
    # Bug 13: Corrigé - Logique de la condition
    if 0 < discount_rate < 1:
        discounted = price * (1 - discount_rate)
    else:
        discounted = price
    
    return discounted

def find_duplicates(items):
    """Trouve les doublons dans une liste."""
    # Bug 14: Corrigé - Algorithme efficace pour trouver les doublons
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)

def read_file_content(filepath):
    """Lit le contenu d'un fichier."""
    # Bug 15: Corrigé - Gestion des erreurs de fichier
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Error: File not found."
    except IOError:
        return "Error: Could not read file."

class User:
    """Classe utilisateur avec bugs."""
    
    def __init__(self, name, email):
        self.name = name
        if self.validate_email(email):
            self.email = email
        else:
            raise ValueError("Invalid email format")
        self.created_at = datetime.now()

    @staticmethod
    def validate_email(email):
        """Valide le format de l'email."""
        # Bug 17: Corrigé - Ajout de la validation d'email
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return True
        return False

    def __eq__(self, other):
        """Compare deux utilisateurs."""
        # Bug 16: Corrigé - Vérifier le type de 'other'
        if not isinstance(other, User):
            return NotImplemented
        return self.email == other.email
    
    def update_email(self, new_email):
        """Met à jour l'email."""
        if self.validate_email(new_email):
            self.email = new_email
        else:
            print("Error: Invalid email format.")

def main():
    """Fonction principale."""
    # Création d'un fichier de config pour le test
    with open('config.json', 'w') as f:
        json.dump({'setting': 'value'}, f)

    # Bug 18: Corrigé - Utilisation correcte de la classe
    processor = DataProcessor('config.json')
    
    # Bug 19: Corrigé - La fonction gère maintenant les listes vides
    data = []
    result = processor.process_data(data)
    print(f"Processing empty data result: {result}")

    data_with_values = [{'value': 10}, {'value': 150}, {'value': 20}]
    result = processor.process_data(data_with_values)
    print(f"Processing data with values result: {result}")


    # Bug 20: Corrigé - Typo dans le nom de la méthode
    processor.results = {'final': result}
    processor.save_results('output.json')
    
    # Bug 21: Corrigé - Accès à un index valide
    numbers = [1, 2, 3, 60, 70]
    print(f"Statistics: {processor.calculate_statistics(numbers)}")
    print(f"Number at index 2: {numbers[2]}")

    # Test des autres fonctions
    users = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 17}]
    process_user_data(users)

    print(f"Discounted price: {calculate_discount(100, 0.1)}")
    
    duplicates = find_duplicates([1, 2, 3, 2, 4, 5, 4, 6])
    print(f"Duplicates: {duplicates}")

    print(read_file_content('README.md'))

    user1 = User("Test", "test@example.com")
    user2 = User("Test2", "test2@example.com")
    print(f"Users are equal: {user1 == user2}")


# Bug 22: Corrigé - Exécution contrôlée
if __name__ == "__main__":
    main()