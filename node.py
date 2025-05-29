import math

class Node:
    """Clase que representa un nodo en un grafo con coordenadas"""
    def __init__(self, name, coordx, coordy):
        """Inicializa un nodo con nombre y coordenadas x,y"""
        self.name = name
        self.coordx = coordx
        self.coordy = coordy
        self.neighbors = []

def AddNeighbor(n1, n2):
    """Añade n2 como vecino de n1 si no lo es ya"""
    if n2 in n1.neighbors:
        return False
    else:
        n1.neighbors.append(n2)
        return True

def Distance(n1, n2):
    """Calcula la distancia euclidiana entre dos nodos"""
    return math.sqrt((n1.coordx - n2.coordx) ** 2 + (n1.coordy - n2.coordy) ** 2)