"""
Classes des objets de la simulation (Levy) : Astre (classe abstraite) et AstreFixe (orbite circulaire).

Documentation officielle :
    numpy : https://numpy.org/doc/stable/reference/
    classes abstraites (abc) : https://docs.python.org/3/library/abc.html
    pandas Series.get (lecture d'une ligne du CSV) : https://pandas.pydata.org/docs/reference/api/pandas.Series.get.html
"""
from abc import ABC, abstractmethod
from xml.dom import NoModificationAllowedErr

import numpy as np
import math

#Constante gravitationnelle convertie dans les unités du programme : UA³ / (masse terrestre · jour²) ≈ 8,888e-10
G_SI = 6.67430e-11          # m³ / (kg · s²)
MT_EN_KG = 5.9722e24        # masse terrestre en kg
JOUR_EN_S = 86400.0         # jour en secondes
UA_EN_M = 149597870700.0    # unité astronomique en mètres
G = G_SI * MT_EN_KG * JOUR_EN_S ** 2 / UA_EN_M ** 3


def en_booleen(valeur) -> bool:
    """_summary_

    Args:
        valeur (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        bool: _description_
    """
    #Convertit la valeur « actif » du CSV ou d'un formulaire en booléen.
    #Attention : bool("false") vaut True en Python, d'où cette fonction.
    #np.bool_ : le type booléen de numpy, que pandas donne quand il lit true/false dans le CSV
    #https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.bool
    if isinstance(valeur, (bool, np.bool_)):
        return bool(valeur)
    texte = str(valeur).strip().lower()
    if texte in ("true", "vrai", "oui", "1", "1.0"):
        return True
    if texte in ("false", "faux", "non", "0", "0.0"):
        return False
    raise ValueError(f"« {valeur} » n'est pas une valeur valide pour actif (attendu true ou false)")


class Astre(ABC):
    
    #Classe abstraite commune aux astres fixes et aux projectiles.
    """
    Attributs :
        nom : nom unique de l'objet.
        masse : masse en masses terrestres (Terre = 1), comme dans systeme_solaire.csv.
        couleur : couleur d'affichage dans le graphique matplotlib (ex. "orange" ou "#FDB813").
        taille : taille d'affichage (rayon relatif à celui de la Terre dans le CSV).
        rayon : rayon de collision en UA.
        actif : un objet inactif n'attire pas et n'est pas simulé.
    """

    #Constructeur de la classe Astre
    def __init__(self, nom: str, masse: float, couleur: str, taille: float, rayon: float, actif: bool = True):
        self.nom = nom
        self.couleur = couleur
        self.actif = en_booleen(actif)
        #Les valeurs numériques peuvent venir du CSV ou d'un formulaire : on vérifie leur conversion
        try:
            self.masse = float(masse)
            self.taille = float(taille)
            self.rayon = float(rayon)
        except (TypeError, ValueError):
            raise ValueError(f"Astre « {nom} » : masse, taille et rayon doivent être des nombres") from None
        if self.masse < 0 or self.rayon < 0 or self.taille <= 0:
            raise ValueError(f"Astre « {nom} » : masse et rayon doivent être positifs, taille strictement positive")

    def _tableau_temps(self, temps) -> np.ndarray:
        # convertit une ligne de temps en tableau numpy
        try:
            # ne copie pas si le tableau recu est déjà un array
            return np.asarray(temps, dtype=float).reshape(-1)
        except (TypeError, ValueError):
            #from None permet d'afficher la nouvelle erreur et supprimer l'ancienne erreur
            raise ValueError (f"AstreFixe {self.nom} : les temps doivent etre des nombres de jours") from None

    def positions(self, temps) -> np.ndarray:
        """retourne les positions (x, y) a plusieurs instants d'un coup sans boucle"""
        temps = self._tableau_temps(temps)
        phase = np.radians(self.phase)
        if self.periode > 0:
            theta = 2*np.pi*temps / self.periode + phase
        else:
            theta = np.full(len(temps), phase) #ce qui signifie que l'astre est immobile: l'angle reste la phase
        centre = np.zeros((len(temps), 2)) if self.parent is None else self.parent.positions(temps)
        return centre + self.distance * np.column_stack((np.cos(theta), np.sin(theta)))
    
    def distance_max(self) -> float:
        #retourne la plus grande distance entre l'astre et son centre
        return self.distance

    def points_orbite(self, t: float, nb_points: int = 120) -> np.ndarray:
        #retourne les points de l'orbitre pour la dessiner avec ax.plot
        angles = np.linspace(0, 2 * np.pi, nb_points)
        centre = np.zeros(2) if self.parent is None else self.parent.position(t)
        return centre + self.distance * np.column_stack((np.cos(angles), np.sin(angles)))




    @abstractmethod
    def position(self, t: float) -> np.ndarray:
        #Renvoie la position (x, y) en UA au temps t (jours), tableau numpy de forme (2,).
        pass


class AstreFixe(Astre):
    #Astre en orbite circulaire autour du centre (0, 0) ou autour de son parent (lune).
    """
    Attributs :
        distance : rayon de l'orbite en UA (0 = immobile au centre, comme le Soleil).
        periode : période de révolution en jours (0 = immobile).
        phase : angle de l'astre à t = 0, en degrés (comme dans systeme_solaire.csv).
        parent : astre autour duquel il tourne, ou None pour le centre.
    """

    #Constructeur de la classe AstreFixe
    def __init__(self, nom: str, masse: float, couleur: str, taille: float, rayon: float, actif: bool = True,
                 distance: float = 0.0, periode: float = 0.0, phase: float = 0.0, parent=None):
        """_summary_

        Args:
            nom (str): _description_
            masse (float): _description_
            couleur (str): _description_
            taille (float): _description_
            rayon (float): _description_
            actif (bool, optional): _description_. Defaults to True.
            distance (float, optional): _description_. Defaults to 0.0.
            periode (float, optional): _description_. Defaults to 0.0.
            phase (float, optional): _description_. Defaults to 0.0.
            parent (_type_, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        super().__init__(nom, masse, couleur, taille, rayon, actif)
        try:
            self.distance = float(distance)
            self.periode = float(periode)
            self.phase = float(phase)
        except (TypeError, ValueError):
            raise ValueError(f"AstreFixe « {nom} » : distance, période et phase doivent être des nombres") from None
        if self.distance < 0 or self.periode < 0:
            raise ValueError(f"AstreFixe « {nom} » : distance et période doivent être positives")
        if parent is self:
            raise ValueError(f"AstreFixe « {nom} » ne peut pas être son propre parent")
        self.parent = parent

    def _temps(self, t) -> float:
        #Convertit le temps en nombre de jours, avec un message clair si t n'est pas un nombre.
        try:
            return float(t)
        except (TypeError, ValueError):
            raise ValueError(f"AstreFixe « {self.nom} » : le temps doit être un nombre de jours, reçu {t!r}") from None

    def _angle(self, t: float) -> float:
        #Angle en radians au temps t : theta = 2*pi*t/T + phase (l'angle reste égal à la phase si T = 0).
        #La phase est donnée en degrés, on la convertit en radians pour cos et sin.
        t = self._temps(t)
        #np.radians convertit des degrés en radians : https://numpy.org/doc/stable/reference/generated/numpy.radians.html
        #np.pi vaut 3.14159... : https://numpy.org/doc/stable/reference/constants.html
        phase = np.radians(self.phase)
        if self.periode > 0:
            return 2 * np.pi * t / self.periode + phase
        return phase

    def position(self, t: float) -> np.ndarray:
        #Position r(t) = centre + d * (cos(theta), sin(theta)), le centre étant (0, 0) ou le parent.
        theta = self._angle(t)
        centre = np.zeros(2) if self.parent is None else self.parent.position(t)
        #np.array crée le vecteur [x, y] ; np.cos et np.sin prennent un angle en radians
        #https://numpy.org/doc/stable/reference/generated/numpy.array.html
        #https://numpy.org/doc/stable/reference/generated/numpy.cos.html
        return centre + self.distance * np.array([np.cos(theta), np.sin(theta)])

    @classmethod
    def depuis_ligne(cls, ligne):
        #Crée un AstreFixe à partir d'une ligne du CSV (dictionnaire ou ligne pandas).
        #Les cases vides valent la valeur par défaut ; le parent (lune) est relié ensuite par le chargeur CSV.
        try:
            nom = str(ligne["nom"]).strip()
        except (KeyError, TypeError):
            raise ValueError("Ligne CSV invalide : la colonne « nom » est manquante") from None

        def nombre(cle, defaut=0.0):
            #ligne.get(cle, defaut) : la valeur de la colonne, ou defaut si la colonne n'existe pas
            #(marche pour un dictionnaire et pour une ligne pandas) : https://pandas.pydata.org/docs/reference/api/pandas.Series.get.html
            valeur = ligne.get(cle, defaut)
            if valeur is None or str(valeur).strip() == "":
                return defaut
            try:
                valeur = float(valeur)
            except (TypeError, ValueError):
                raise ValueError(f"Astre « {nom} », colonne « {cle} » : « {valeur} » n'est pas un nombre") from None 
            return defaut if np.isnan(valeur) else valeur
    
        valeurs = dict(
            nom=nom,
            masse=nombre("masse"),
            couleur=str(ligne.get("couleur") or "#FFFFFF").strip(),
            taille=nombre("taille", 5.0),
            rayon=nombre("rayon"),
            actif=en_booleen(ligne.get("actif", True)),
            distance=nombre("distance"),
            periode=nombre("periode"),
            phase=nombre("phase"),
        )
        # Colonnes facultatives : une excentricité non nulle donne une orbite elliptique.
        # != 0 (et pas > 0) : une excentricité négative arrive dans AstreElliptique, qui la refuse avec un message clair.
        excentricite = nombre("excentricite")
        if excentricite != 0:
            return AstreElliptique(**valeurs, excentricite=excentricite, perihelie=nombre("perihelie"))
        return cls(**valeurs)


class AstreElliptique(AstreFixe):

    ITERATIONS_KEPLER = 15 # cette valeur représente un nombre fixe d'itérations de Newton

    def __init__(self, nom: str, masse: float, couleur: str, taille: float, rayon: float, actif: bool = True, distance: float = 0.0,
                 periode: float = 0.0, phase: float = 0.0, parent = None, excentricite: float = 0.0, perihelie: float = 0.0):
                 
                 super().__init__(nom, masse, couleur, taille, rayon, actif, distance, periode, phase, parent)
                 
                 try:
                    self.excentricite = float(excentricite)
                    self.perihelie = float(perihelie)
                except (TypeError, ValueError):
                    raise ValueError(f"AstreElliptique « {nom} » : excentricité et périhélie doivent être des nombres") from None

                    # not (0 <= e < 1) refuse NaN, car toute comparaison avec NaN est fausse
                    if not 0 <= self.excentricite < 1:
                        raise ValueError(f"AstreElliptique {nom} : l'excentricité doit être entre 0 (inclus) et 1 (exclu), "
                        f"recu {self.excentricite}")

    def _anomalie_excentrique(self, _anomalie_moyenne: np.ndarray) -> np.ndarray:
        """
        Résout l'équation de Kepler E - e·sin(E) = M par la méthode de Newton.

        Il n'existe pas de formule directe pour E : on part d'une estimation et on la corrige
        ITERATIONS_KEPLER fois. Le dénominateur 1 - e·cos(E) vaut au moins 1 - e > 0 : jamais de division par zéro.

        :param anomalie_moyenne: Tableau des M, en radians
        :return: Tableau des E, en radians
        """

        e = self.excentricite
        # Depart E = M ou E = pi
        for _ in range(self.ITERATIONS_KEPLER):
            E -= (E - e * np.sin(E) - anomalie_moyenne) / (1 - e * np.cos(E))
        return E

    # https://fr.wikipedia.org/wiki/%C3%89quation_de_Kepler
    def _dans_le_plan(self, E: np.ndarray) -> np.ndarray:
        """
        Position par rapport au foyer pour des anomalies excentriques E, tournée de l'angle du périhélie.

        :param E: Tableau des anomalies excentriques, en radians
        :return: Tableau numpy de forme (n, 2)

        """
        a, e = self.distance, sefl.excentricite
        x = a * (np.cos(E) - e)  # On decale le foyer par rapport au centre de l'ellipse
        y = a * np.sqrt(1 - e * e) * np.sin(E)   # b = a·√(1 - e²) : le demi-petit axe
        w = np.radians(self.perihelie)
        # Rotation d'angle w : (x cos w - y sin w, x sin w + y cos w)
        return np.column_stack((x * np.cos(w) - y * np.sin(w), x * np.sin(w) + y * np.cos(w)))

    def positions(self, temps) -> np.ndarray:
        """Positions à plusieurs instants ; même rôle que AstreFixe.positions. Complexité O(n)."""
        temps = self._tableau_temps(temps)
        if self.periode > 0:
            anomalie_moyenne = np.radians(self.phase) + 2 * np.pi * temps / self.periode
        else:
            anomalie_moyenne = np.full(len(temps), np.radians(self.phase))
        centre = np.zeros((len(temps), 2)) if self.parent is None else self.parent.positions(temps)
        return centre + self._dans_le_plan(self._anomalie_excentrique(anomalie_moyenne))

    def position(self, t: float) -> np.ndarray:
        """
        Position au temps t. Même calcul que positions, mais sur de simples nombres avec le module math :
        physique.py l'appelle des centaines de milliers de fois, et numpy est lent sur un seul nombre
        (environ 200 µs par appel avec des tableaux, quelques µs avec math).
        """
        t = self._temps(t)
        e, a = self.excentricite, self.distance
        M = math.radians(self.phase) + (2 * math.pi * t / self.periode if self.periode > 0 else 0.0)
        E = M if e < 0.8 else math.pi
        for _ in range(self.ITERATIONS_KEPLER):
            E -= (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
        x = a * (math.cos(E) - e)
        y = a * math.sqrt(1 - e * e) * math.sin(E)
        w = math.radians(self.perihelie)
        point = np.array([x * math.cos(w) - y * math.sin(w), x * math.sin(w) + y * math.cos(w)])
        return point if self.parent is None else self.parent.position(t) + point

    def distance_max(self) -> float:
        L'aphélie, le point le plus loin du foyer : a·(1 + e).
        return self.distance * (1 + self.excentricite)

    def points_orbite(self, t: float, nb_points: int = 120) -> np.ndarray:
        Points de l'ellipse complète, pour la dessiner.
        centre = np.zeros(2) if self.parent is None else self.parent.position(t)
        return centre + self._dans_le_plan(np.linspace(0, 2 * np.pi, nb_points))
                