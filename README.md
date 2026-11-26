# AstroLab : Simulateur de projectiles dans l'espace

*Par Demba Cissé, Liam Feller, Marc-Antoine Gauthier et Levy Loïk Enok Koutoua dans le cadre du cours de Développement d'Applications dans un Environnement Graphique*

Une application graphique permettant de simuler des mouvements de projectile dans l’espace selon diverses conditions. L’application est destinée aux étudiants et professeurs du domaine de la physique de l’espace et de l’astronomie. Par la simulation, elle aide à comprendre et visualiser les mécanismes des mouvements de projectiles météoriques selon la gravité d’astres environnants, tout en offrant une flexibilité dans le positionnement d’astres.

## Installation et Lancement

Prérequis : Python 3.10 ou plus récent.

```bash
git clone https://github.com/Enok01/ProjetGroupe.git
cd ProjetGroupe
pip install -r requirements.txt
python -m src.main
```

> Le programme se lance depuis la racine du dépôt : tous les imports passent par `src.` (ex. `from src.astre import AstreFixe`).

## Nouveautés

- **Orbites elliptiques** (lois de Kepler) : la classe `AstreElliptique` place le Soleil à un foyer de l'ellipse. Le fichier `donnees/systeme_solaire_elliptique.csv` utilise les éléments képlériens de la NASA (JPL, « Approximate Positions of the Planets » : https://ssd.jpl.nasa.gov/planets/approx_pos.html). Deux colonnes facultatives s'ajoutent au CSV : `excentricite` (0 = cercle) et `perihelie` (degrés) ; un ancien fichier sans elles reste valide.
- **Légende** des couleurs de chaque astre dans la vue.
- **Graphiques** de la position (x, y, distance au centre) et de l'accélération du projectile en fonction du temps.
- **Corrections** : le panneau Projectile affiche la position, la vitesse et la cible au temps t ; cocher ou décocher un objet recalcule aussitôt la trajectoire ; un projectile lancé au jour T ne vit plus T jours de trop.

## Organisation du code

Chaque fichier a un responsable ; pour modifier le fichier d'un autre membre, on le lui demande ou on passe par une pull request qu'il relit.


## Notions élémentaires de physique

- **Astres fixes** : chaque astre tourne en cercle autour du centre (0, 0) qui est le soleil, ou autour de son `parent` pour la lune (Demba implémente la fonctionnalité en extra). Sa position est donnée directement par une formule, sans intégration :
  θ(t) = 2π·t / T + φ, puis r(t) = d · (cos θ, sin θ).
  Les astres ne s'attirent pas entre eux.
- **Projectiles** : seuls les projectiles subissent la gravité de tous les astres **actifs** (loi de Newton) :
  a = Σᵢ G·Mᵢ·(rᵢ − r) / ‖rᵢ − r‖³.
  Leur trajectoire est calculée pas à pas (méthode de Verlet a confirmer).
- **Fin d'un projectile** : collision quand sa distance à un astre est inférieure au rayon de cet astre, ou expiration quand il dépasse sa durée de vie.

Unités utilisées dans tout le programme :

| Grandeur           | Unité                                           |
|--------------------|-------------------------------------------------|
| Distance, position | UA (unité astronomique)                         |
| Temps              | jour                                            |
| Masse              | masse terrestre (Terre = 1)                     |
| Vitesse            | UA / jour                                       |
| G                  | ≈ 8,888 × 10⁻¹⁰ UA³ / (masse terrestre · jour²) |

## Format du fichier CSV  

Un seul fichier décrit les astres et les projectiles ; la colonne `type` indique lequel, et les colonnes qui ne s'appliquent pas restent vides.


## Méthode de travail Git

- `main` : version stable, qui démarre fonctione.
- `dev` : intégration du travail terminé de tous.
- Une branche par tâche, créée à partir de `dev`, puis fusionnée dans `dev` par pull request relue par un ou plusieurs membres.
