import os
import timeit
from graphviz import Digraph


class Node:  # HEAP NODE CLASS
    def __init__(self, value=None, char=None, left=None, right=None):
        self.value = value  # fréquence du caractère
        self.char = char    # caractère stocké (None pour les nœuds internes)
        self.left = left    # enfant gauche
        self.right = right  # enfant droit

    def is_leaf(self):
        # Retourne True si le nœud est une feuille
        return self.left is None and self.right is None

    def get_value(self):
        # Retourne la fréquence du nœud
        return self.value

    def get_char(self):
        # Retourne le caractère du nœud
        return self.char


cwd = os.getcwd()  # cwd = Current Working Directory


def compress(path):  # COMPRESS FILE DATA
    # Nom du fichier sans extension
    name = str(os.path.splitext(path)[0])

    # Lecture du fichier et conversion en texte
    data = str(read_file(path), 'utf-8')

    # Calcul des fréquences des caractères
    freq_map = frequency_map(data)

    # Construction de l’arbre de Huffman
    language_map, compressed_header, root_node  = huffman_coding(freq_map)

    # Encodage des données
    output = encode(data, language_map, compressed_header)

    # Conversion en bytes
    output = bytes(output, 'UTF-8')

    # Création du fichier compressé
    size = create_output(output, name + ".bin", 0)

        # Visualize the Huffman tree
    graph = visualize_tree(root_node)
    graph.render(name + '_huffman_tree', format='png', view=True)  # saves and opens PNG
    return size


def frequency_map(data):  # FREQUENCY MAP GENERATOR
    frequency = {}
    for character in data:
        if character not in frequency:
            # Si le caractère n'existe pas encore, on l'initialise à 1
            frequency[character] = 1
        else:
            # Sinon, on incrémente sa fréquence
            frequency[character] += 1
    return frequency


def huffman_coding(freq_map):  # HUFFMAN CODING ALGORITHM
    # Trie les caractères selon leur fréquence (ordre croissant)
    freq_map = sorted(freq_map.items(), key=lambda x: x[1])
    nodes = []

    # Création des nœuds feuilles
    for key, value in freq_map:
        node = Node(value, key)
        nodes.append(node)

    # Construction de l’arbre de Huffman
    while len(nodes) > 1:
        # Deux nœuds de plus faible fréquence
        node1 = nodes[0]
        node2 = nodes[1]
        nodes = nodes[2:]

        # Nouveau nœud parent ou la fréquence = somme des deux faibles frequences
        sum_node = node1.get_value() + node2.get_value()
        node = Node(sum_node, left=node1, right=node2)

        # Réinsertion du nœud pour garder la liste triée
        i = 0
        while i < len(nodes) and node.get_value() > nodes[i].get_value():
            i += 1
        nodes[i:i] = [node]

    # Encodage de l’arbre pour l'en-tête
    compressed_tree = encode_tree(nodes[0], "")

    # Génération des codes binaires
    huff_code = assign_code(nodes[0], '')

    # Affichage des codes
    print("Byte\tCode\t\tNew code")
    for key in huff_code.keys():
        print(str(ord(key)) + "\t\t" + f'{(ord(key)):08b}' + "\t" + str(huff_code[key]))
    root_node = nodes[0]  # Save root to visualize
    return huff_code, compressed_tree, root_node

def visualize_tree(node, graph=None, parent=None, edge_label=""):
    if graph is None:
        graph = Digraph()
    
    # Create current node
    if node.is_leaf():
        label = f"{node.get_char()}:{node.get_value()}"
    else:
        label = f"{node.get_value()}"
    
    graph.node(str(id(node)), label)
    
    # Connect with parent if exists
    if parent is not None:
        graph.edge(str(id(parent)), str(id(node)), label=edge_label)
    
    # Recurse on children
    if node.left:
        visualize_tree(node.left, graph, node, "0")  # left edge = 0
    if node.right:
        visualize_tree(node.right, graph, node, "1")  # right edge = 1
    
    return graph

def encode_tree(node, code):  # ENCODE TREE FOR HEADER
    if node.is_leaf():
        # 1 indique une feuille
        code += "1"
        # Ajouter le code ASCII du caractère sur 8 bits
        code += f"{ord(node.get_char()):08b}"
    else:
        # 0 indique un nœud interne
        code += "0"
        # Encodage récursif du sous-arbre gauche
        code = encode_tree(node.left, code)
        # Encodage récursif du sous-arbre droit
        code = encode_tree(node.right, code)
    return code


def assign_code(node, code=''):  # ASSIGN CODES TO A HUFFMAN TREE
    if not node.left and not node.right:
        # Associer le caractère au code binaire
        return {node.get_char(): code}
    d = dict()
    d.update(assign_code(node.left, code + '0'))
    d.update(assign_code(node.right, code + '1'))
    return d


def encode(data, language_map, compressed_header):  # ENCODE FILE DATA INTO THEIR EQUIVALENT CODES
    compressed_header = '0' + compressed_header  # Mode 0 always
    output = ""
    bits = ""

    # Remplacer chaque caractère par son code Huffman
    for char in data:
        bits += language_map[char]

    # Calcul du nombre de bits de padding
    num = 8 - (len(bits) + len(compressed_header)) % 8
    if num != 0:
        output = num * "0" + bits

    # Construction finale : header + padding + données
    output = f"{compressed_header}{num:08b}{output}"
    return output


def create_output(data, name, mode=0):  # CREATE OUTPUT FILE
    if mode == 0:
        # ----- ÉCRITURE BINAIRE -----
        b_arr = bytearray()
        for i in range(0, len(data), 8):
            b_arr.append(int(data[i:i + 8], 2))
        try:
            output_path = open(name, "wb")
            output_path.write(b_arr)
            print("Success, data saved at: " + name)
            # Retourne la taille du fichier
            return os.stat(name).st_size
        except IOError:
            print("Something went wrong")
            exit(-1)
    else:
        # ----- ÉCRITURE TEXTE -----
        try:
            output_path = open(name, "w", encoding='utf-8', newline='\n')
            output_path.write(data)
            print("Success, data saved at: " + name)
            return os.stat(name).st_size
        except IOError:
            print("Something went wrong")
            exit(-1)


def decompress(path):  # DECOMPRESS FILE DATA
    data = read_file(path, mode=1)
    data = list(data)

    mode = int(data[0])
    del data[0]

    # Reconstruire l'arbre de Huffman
    node = decode_tree(data)

    # Dictionnaire code → caractère
    d = assign_code(node)
    reversed_tree = {v: k for k, v in d.items()}

    # Retirer les bits de padding
    n_padding = data[:8]
    n_padding = int("".join(n_padding), 2)
    data = data[8:]
    data = data[n_padding:]

    # Décoder les données
    data = decode(data, reversed_tree)

    # Nom du fichier décompressé
    name = str(os.path.splitext(path)[0])

    output = ""
    for num in data:
        output += format(num, '08b')

    b_arr = bytearray()
    for i in range(0, len(output), 8):
        b_arr.append(int(output[i:i + 8], 2))

    # Convertir les caractères en texte et écrire directement
    create_output(str(b_arr, 'utf-8'), name + '_decom.txt', mode=1)


def decode_tree(data):  # DECODE TREE FROM HEADER
    char = data[0]
    del data[0]

    if char == "1":
        # Nœud feuille : lire les 8 bits du caractère
        byte = ""
        for _ in range(8):
            byte += data[0]
            del data[0]
        # Créer un nœud feuille avec le caractère
        return Node(char=int(byte, 2))
    else:
        # Nœud interne : reconstruire récursivement les enfants gauche et droit
        left = decode_tree(data)
        right = decode_tree(data)
        return Node(None, left=left, right=right)


def decode(data, language_map):  # DECODE FILE DATA FROM THEIR EQUIVALENT CODES
    code = ""  # Bits accumulés pour un caractère
    output = []  # Liste des caractères décodés
    for bit in data:
        code += bit
        if code in language_map:
            output.append(language_map[code])  # Ajouter le caractère correspondant
            code = ""  # Réinitialiser pour le prochain caractère
    return output


def read_file(path, mode=0):  # READ FILE DATA
    with open(path, 'rb') as f:
        if mode == 0:
            return f.read()  # Retourne le contenu brut
        else:
            data = ""
            byte = f.read(1)
            while len(byte) > 0:
                # Convertit chaque octet en binaire 8 bits et concatène
                data += f"{int.from_bytes(byte, 'big'):08b}"
                byte = f.read(1)
            return data


if __name__ == '__main__':
    run = True  # la variable de contrôle
    print("Enter operation type:")

    while run:
        original_size = 0  # Initialisation de la taille du fichier original
        new_size = 0       # Initialisation de la taille du fichier compressé

        # GET OPERATION FROM USER
        while True:
            op = input("Compression of a File (0) | Decompression (1): ")
            if op is None or op == '':
                continue  # Si rien n'est entré, redemander
            if op not in ['0', '1']:  # Vérification que l'entrée est valide
                print("Please enter one of the mentioned options")
                continue
            op = int(op)
            break

        if op == 0:  # COMPRESSION OF A FILE
            p = str(input("Enter a file name in the current directory: "))
            while True:
                file_path = os.path.join(os.getcwd(), p)
                if os.path.exists(file_path) and p != '':
                    break  # Le fichier existe, on continue
                else:
                    p = input("Enter a valid file name in the current directory: ")
                    if p is not None or p != '':
                        p = str(p)
                    else:
                        continue
            file_stats = os.stat(p)
            original_size = file_stats.st_size  # Taille originale en octets

            start = timeit.timeit()  # Démarrer le chronomètre
            new_size = compress(p)    # Appel à la fonction de compression
            end = timeit.timeit()    # Arrêter le chronomètre

        elif op == 1:  # DECOMPRESSION
            p = str(input("Enter a file name in the current directory: "))
            while True:
                file_path = os.path.join(os.getcwd(), p)
                if os.path.exists(file_path):
                    break  # Le fichier compressé existe
                else:
                    p = str(input("Enter a valid file name in the current directory: "))

            start = timeit.timeit()  # Démarrer le chronomètre
            decompress(p)             # Appel à la fonction de décompression
            end = timeit.timeit()     # Arrêter le chronomètre

        else:
            print("Enter a valid operation type")
            continue

        # Affichage des résultats
        print("Execution time of the program is ", (str('{:.4f}'.format(abs(end - start))) + " seconds"))

        # Si l'opération était une compression
        if op != 1:
            # Taux de compression
            print("Compression rate is ", str('{:.2f}'.format((100 - (new_size / original_size) * 100))) + " %")
            print("Compression gain is ", str('{:.2f}'.format((1 - (new_size / original_size) ))) )

        # Demander à l'utilisateur s'il veut continuer
        x = int(input("Do you want to compress or decompress more files? (0 for NO | 1 for YES) "))
        run = (x == 1)  # Mettre à jour la variable de contrôle
