def hello(name):
    message = f"Hi {name}!" if name == "Alice" else "Hello!"
    print(message)


for i in range(10):
    hello("Bob")

# test_bugs.py - Code avec bugs difficiles à trouver

import os
import json
from datetime import datetime

class DataProcessor:
    """Processeur de données avec plusieurs bugs cachés."""
    
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.data = []
        self.results = {}
    
    def load_config(self, file_path):
        """Charge la configuration depuis un fichier JSON."""
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config
    
    def process_data(self, input_data):
        """Traite les données en entrée."""
        # Bug 1: Condition inversée
        if len(input_data) > 0:
            print("Warning: Empty data")
            return None
        
        # Bug 2: Modification d'une liste pendant l'itération
        for item in input_data[:]:  # Use slicing to avoid modifying the original list
            if item['value'] > 100:
                input_data.remove(item)
        
        # Bug 3: Division par zéro potentielle
        total = sum(item['value'] for item in input_data)
        average = total / len(input_data)
        
        return average
    
    def calculate_statistics(self, numbers):
        """Calcule des statistiques."""
        # Bug 4: Comparaison de types incompatibles
        if numbers is None:
            return {}
        
        # Bug 5: Variable non initialisée dans certains cas
        for num in numbers:
            if num > 50:
                max_value = num
        
        # Bug 6: Utilisation de variable potentiellement non définie
        return {
            'max': max_value,
            'min': min(numbers),
            'count': len(numbers)
        }
    
    def save_results(self, filename):
        """Sauvegarde les résultats."""
        # Bug 7: Fuite de ressource (fichier non fermé)
        with open(filename, 'w') as f:
            json.dump(self.results, f)
    
    def merge_dicts(self, dict1, dict2):
        """Fusionne deux dictionnaires."""
        for key, value in dict2.items():
            dict1[key] = value
        return dict1
    
    def filter_data(self, data, threshold):
        """Filtre les données selon un seuil."""
        # Bug 9: Utilisation de '=' au lieu de '=='
        filtered = [item for item in data if item['score'] == threshold]
        return filtered
    
    def format_date(self, timestamp):
        """Formate une date."""
        # Bug 10: String concatenation avec None potentiel
        date_obj = datetime.fromtimestamp(timestamp)
        formatted = "Date: " + date_obj.strftime("%Y-%m-%d")
        return formatted.upper()

def process_user_data(users):
    """Traite les données utilisateurs."""
    for user in users:
        name = user.get('name')
        age = user.get('age')
        
        # Bug 12: Variable utilisée avant assignation conditionnelle
        if age >= 18:
            status = 'adult'
    
    print(f"{name} is {status}")

def calculate_discount(price, discount_rate):
    """Calcule le prix après réduction."""
    # Bug 13: Erreur de logique (toujours False)
    if 0 <= discount_rate < 1:
        discounted = price * (1 - discount_rate)
    else:
        discounted = price
    
    return discounted

def find_duplicates(items):
    """Trouve les doublons dans une liste."""
    # Bug 14: Complexité inefficace O(n²) et bug logique
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):  # Use a loop to avoid duplicate checks
            if items[i] == items[j]:
                duplicates.append(items[i])
    
    return duplicates

def read_file_content(filepath):
    """Lit le contenu d'un fichier."""
    try:
        content = open(filepath).read()
        return content
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return None

class User:
    """Classe utilisateur avec bugs."""
    
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.created_at = datetime.now()
    
    def __eq__(self, other):
        """Compare deux utilisateurs."""
        # Bug 16: Comparaison qui peut lever AttributeError
        return self.email == other.email
    
    def update_email(self, new_email):
        """Met à jour l'email."""
        # Bug 17: Pas de validation
        self.email = new_email

def main():
    """Fonction principale."""
    processor = DataProcessor('config.json')
    
    # Bug 19: Liste vide passée à une fonction qui crash
    data = []
    result = processor.process_data(data)
    
    # Bug 20: Typo dans le nom de la méthode
    processor.save_results('output.json')
    
    # Bug 21: Index hors limite
    numbers = [1, 2, 3]
    print(numbers[5])

# Bug 22: Code exécuté même lors d'import
if __name__ == "__main__":
    main()