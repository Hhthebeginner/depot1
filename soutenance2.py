

import itertools  # Importation du module itertools pour générer des combinaisons d'accessoires
import math  # Importation du module math pour les fonctions mathématiques
import matplotlib  # Importation du module matplotlib pour les graphiques
import matplotlib.pyplot as plt  # Importation de pyplot pour faciliter la création de graphiques
import numpy as np  # Importation de numpy pour les calculs numériques et les tableaux
from scipy.integrate import odeint  # Importation de odeint pour résoudre les équations différentielles

# Constantes et données
donnees = {
    "U": 0.1,  # Coefficient de frottement dynamique (frottement au sol)
    "Cz": 0.3,  # Coefficient de portance (aérodynamique)
    "d_pente": 31,  # Distance de la pente en mètres
    "d_looping": 12 * math.pi,  # Longueur du looping (circonférence) en mètres
    "r_looping": 6,  # Rayon du looping en mètres
    "d_ravin": 9,  # Distance du ravin en mètres
    "d_finale": 10,  # Distance finale sur le plat en mètres
    "h_ravin": 1,  # Hauteur du ravin en mètres
    "h_pente": 2,  # Hauteur de la pente en mètres
    "alpha": 4 * math.pi / 180,  # Angle d'inclinaison de la pente en radians (4 degrés)
    "g": 9.81,  # Accélération due à la gravité en m/s²
    "rho": 1.225,  # Densité de l'air en kg/m³
}

# Dictionnaire des accessoires avec leurs effets respectifs
accessoires_dict = {
    "booster": {"acc_sup": 1.3},  # Booster : Accélération supplémentaire lors du looping et du plat
    "ailerons": {"masse": 30, "Cz_sup": 1.1},  # Ailerons : Masse supplémentaire et coefficient de portance augmenté
    "jupe": {"masse": 15, "Cx_reduction": 0.95}  # Jupe : Masse supplémentaire et coefficient de traînée réduit
}

# Liste des voitures avec leurs caractéristiques
voitures = [
    {"nom": "Dodge Charger R/T", "masse": 1760, "acceleration": 5.1, "longueur": 5.28, "largeur": 1.95, "hauteur": 1.35, "cx": 0.38},
    {"nom": "Toyota Supra Mark IV", "masse": 1615, "acceleration": 5, "longueur": 4.21, "largeur": 1.81, "hauteur": 1.27, "cx": 0.29},
    {"nom": "Chevrolet Yenko Camaro", "masse": 1498, "acceleration": 5.3, "longueur": 4.72, "largeur": 1.88, "hauteur": 1.30, "cx": 0.35},
    {"nom": "Mazda RX-7 FD", "masse": 1385, "acceleration": 5.2, "longueur": 4.3, "largeur": 1.75, "hauteur": 1.23, "cx": 0.28},
    {"nom": "Nissan Skyline GTR-R34", "masse": 1540, "acceleration": 5.8, "longueur": 4.6, "largeur": 1.79, "hauteur": 1.36, "cx": 0.34},
    {"nom": "Mitsubishi Lancer Evolution VII", "masse": 1600, "acceleration": 5, "longueur": 4.51, "largeur": 1.81, "hauteur": 1.48, "cx": 0.28},
]

# Fonction pour générer toutes les combinaisons d'accessoires possibles
def generer_combinaisons_accessoires():
    accessoires = ['jupe', 'booster', 'ailerons']  # Liste des accessoires disponibles
    combinaisons = []  # Liste pour stocker toutes les combinaisons
    for i in range(len(accessoires) + 1):  # Boucle sur le nombre d'accessoires (0 à 3)
        for combinaison in itertools.combinations(accessoires, i):  # Génère les combinaisons de taille i
            combinaisons.append(combinaison)  # Ajoute la combinaison à la liste
    return combinaisons  # Retourne toutes les combinaisons possibles

# Fonction pour simuler le parcours pour une voiture et une combinaison d'accessoires donnée
def simuler_parcours(voiture, accessoires, donnees, accessoires_dict):
    # Appliquer les effets des accessoires
    masse_totale = voiture['masse']  # Masse initiale de la voiture
    coeff_trainee = voiture['cx']  # Coefficient de traînée initial
    coeff_portance = donnees["Cz"]  # Coefficient de portance initial
    acceleration_base = voiture['acceleration']  # Accélération de base de la voiture

    # Indicateurs d'application des accessoires
    a_jupe = 'jupe' in accessoires  # Vérifie si la jupe est ajoutée
    a_booster = 'booster' in accessoires  # Vérifie si le booster est ajouté
    a_ailerons = 'ailerons' in accessoires  # Vérifie si les ailerons sont ajoutés

    # Appliquer les effets de la jupe
    if a_jupe:
        masse_totale += accessoires_dict['jupe']['masse']  # Ajoute la masse de la jupe à la masse totale
        coeff_trainee *= accessoires_dict['jupe']['Cx_reduction']  # Réduit le coefficient de traînée

    # Appliquer les effets des ailerons
    if a_ailerons:
        masse_totale += accessoires_dict['ailerons']['masse']  # Ajoute la masse des ailerons à la masse totale
        coeff_portance *= accessoires_dict['ailerons']['Cz_sup']  # Augmente le coefficient de portance

    # Fonction interne pour obtenir l'accélération basée sur la section et les accessoires
    def obtenir_acceleration(section, acc_base):
        if section in ['looping', 'plat'] and a_booster:  # Si on est dans le looping ou le plat et que le booster est ajouté
            return acc_base + accessoires_dict['booster']['acc_sup']  # Ajoute l'accélération supplémentaire
        return acc_base  # Sinon, retourne l'accélération de base

    # Initialiser le temps total du parcours
    temps_total = 0

    # Dictionnaire pour stocker les données détaillées par phase (pente, looping, ravin, plat)
    donnees_phase = {}

    # ----------- Simulation de la Pente -----------
    surface_pente = voiture['largeur'] * voiture["hauteur"]  # Calcul de la surface frontale de la voiture (en m²)
    vitesse_initiale_pente = 0  # Vitesse initiale au début de la pente (en m/s)
    position_initiale_pente = 0  # Position initiale au début de la pente (en m)
    etat_initial_pente = [vitesse_initiale_pente, position_initiale_pente]  # État initial [vitesse, position]
    t_pente = np.linspace(0, 20, 2500)  # Intervalle de temps pour la simulation de la pente (20 secondes, 2500 points)

    # Définition de l'équation différentielle pour la pente
    def equation_pente(y, t, acc_pente, coeff_pente):
        vitesse, position = y  # Extraction de la vitesse et de la position actuelles
        N = masse_totale * donnees["g"] * math.cos(donnees["alpha"])  # Calcul de la réaction normale
        f_frottement = donnees["U"] * N  # Calcul de la force de frottement au sol
        f_air = 0.5 * coeff_pente * donnees["rho"] * surface_pente * vitesse**2  # Calcul de la résistance de l'air
        f_motrice = acc_pente * masse_totale  # Calcul de la force motrice (accélération * masse)
        composante_poids = masse_totale * donnees["g"] * math.sin(donnees["alpha"])  # Composante du poids parallèle à la pente
        somme_forces = f_motrice + composante_poids - (f_frottement + f_air)  # Somme des forces agissant sur la voiture
        acceleration = somme_forces / masse_totale  # Accélération (F = m*a => a = F/m)
        return [acceleration, vitesse]  # Retourne les dérivées [dv/dt, dx/dt]

    acc_pente = obtenir_acceleration('pente', acceleration_base)  # Obtient l'accélération pour la pente
    sortie_pente = odeint(equation_pente, etat_initial_pente, t_pente, args=(acc_pente, coeff_trainee))  # Résout les équations différentielles pour la pente
    vitesse_pente = sortie_pente[:, 0]  # Extraction des vitesses obtenues de la simulation
    position_pente = sortie_pente[:, 1]  # Extraction des positions obtenues de la simulation

    # Détermination de la fin de la pente
    fin_pente_indices = np.where(position_pente >= donnees["d_pente"])[0]  # Trouve les indices où la position atteint ou dépasse d_pente
    if len(fin_pente_indices) == 0:
        # Si la voiture n'a pas atteint la fin de la pente, la simulation échoue
        return None
    fin_pente = fin_pente_indices[0]  # Premier indice où la condition est remplie
    temps_pente = t_pente[fin_pente]  # Temps correspondant à la fin de la pente
    vitesse_pente_fin = vitesse_pente[fin_pente]  # Vitesse à la fin de la pente
    position_pente_fin = position_pente[fin_pente]  # Position à la fin de la pente
    temps_total += temps_pente  # Ajoute le temps de la pente au temps total

    # Stocker les données de la pente pour le tracé
    donnees_phase['pente_vitesse'] = {
        "temps": t_pente[:fin_pente],  # Temps jusqu'à la fin de la pente
        "vitesse": vitesse_pente[:fin_pente]  # Vitesse jusqu'à la fin de la pente
    }
    donnees_phase['pente_position'] = {
        "temps": t_pente[:fin_pente],  # Temps jusqu'à la fin de la pente
        "position": position_pente[:fin_pente]  # Position jusqu'à la fin de la pente
    }

    # ----------- Simulation du Looping -----------
    theta_initial = 1 * math.pi / 180  # Position angulaire initiale en radians (1 degré)
    vitesse_angulaire_initiale = vitesse_pente_fin / donnees["r_looping"]  # Vitesse angulaire initiale (v = r*omega => omega = v/r)
    etat_initial_looping = [theta_initial, vitesse_angulaire_initiale]  # État initial [theta, omega]
    t_looping = np.linspace(0, 5, 1000)  # Intervalle de temps pour la simulation du looping (5 secondes, 1000 points)

    # Définition de l'équation différentielle pour le looping
    def equation_looping(vtheta, t, acc_loop, coeff_portance_loop):
        theta, vitesse_angulaire = vtheta  # Extraction de la position angulaire et de la vitesse angulaire
        N = masse_totale * (donnees["g"] * math.cos(theta) + donnees["r_looping"] * vitesse_angulaire**2)  # Réaction normale au sommet du looping
        f_frottement = donnees["U"] * N  # Force de frottement au sol dans le looping
        f_air = 0.5 * coeff_trainee * donnees["rho"] * (voiture['largeur'] * voiture['hauteur']) * (donnees["r_looping"] * vitesse_angulaire)**2  # Traînée aérodynamique
        f_motrice = acc_loop * masse_totale  # Force motrice (accélération * masse)
        composante_poids = math.sin(theta) * masse_totale * donnees["g"]  # Composante du poids perpendiculaire au mouvement dans le looping
        somme_forces = f_motrice - composante_poids - (f_frottement + f_air)  # Somme des forces agissant sur la voiture dans le looping
        acceleration_angulaire = somme_forces / (masse_totale * donnees["r_looping"])  # Accélération angulaire (alpha = F/(m*r))
        return [vitesse_angulaire, acceleration_angulaire]  # Retourne les dérivées [dtheta/dt, domega/dt]

    acc_looping = obtenir_acceleration('looping', acceleration_base)  # Obtient l'accélération pour le looping
    sortie_looping = odeint(equation_looping, etat_initial_looping, t_looping, args=(acc_looping, coeff_portance))  # Résout les équations différentielles pour le looping
    theta_looping = sortie_looping[:, 0]  # Extraction des positions angulaires obtenues de la simulation
    vitesse_angulaire_looping = sortie_looping[:, 1]  # Extraction des vitesses angulaires obtenues de la simulation

    # Calcul de la vitesse linéaire dans le looping
    vitesse_lineaire_looping = donnees["r_looping"] * vitesse_angulaire_looping  # v = r * omega

    # Vérifier si le looping est possible (réaction normale positive tout au long du looping)
    Reac_normale = donnees["g"] * np.cos(theta_looping) + donnees["r_looping"] * vitesse_angulaire_looping**2  # Calcul de la réaction normale
    if np.max(Reac_normale) < 0:
        # Si la réaction normale maximale est négative, le looping est impossible
        return None

    # Détermination de la fin du looping
    fin_looping_indices = np.where(theta_looping >= donnees["d_looping"] / donnees["r_looping"])[0]  # Trouve les indices où theta atteint d_looping / r_looping
    if len(fin_looping_indices) == 0:
        # Si la voiture n'a pas complété le looping, la simulation échoue
        return None
    fin_looping = fin_looping_indices[0]  # Premier indice où la condition est remplie
    temps_looping = t_looping[fin_looping]  # Temps correspondant à la fin du looping
    vitesse_lineaire_looping_fin = vitesse_lineaire_looping[fin_looping]  # Vitesse linéaire à la fin du looping
    position_looping_fin = theta_looping[fin_looping] * donnees["r_looping"]  # Position finale en mètres après le looping
    temps_total += temps_looping  # Ajoute le temps du looping au temps total

    # Calcul du périmètre parcouru en fonction de l'angle theta
    perimetre_looping = donnees["r_looping"] * theta_looping  # Périmètre = rayon * angle

    # Stocker les données du looping pour le tracé
    donnees_phase['looping_vlineaire'] = {
        "temps": t_looping[:fin_looping],  # Temps jusqu'à la fin du looping
        "v_lineaire": vitesse_lineaire_looping[:fin_looping]  # Vitesse linéaire jusqu'à la fin du looping
    }
    donnees_phase['looping_perimetre'] = {
        "theta": theta_looping[:fin_looping],  # Angle theta jusqu'à la fin du looping
        "perimetre": perimetre_looping[:fin_looping]  # Périmètre parcouru jusqu'à la fin du looping
    }

    # ----------- Simulation du Ravin (Ravine) -----------
    # Définition de l'équation différentielle pour le ravin
    def equation_ravin(etat, t, coeff_trainee_ravin, coeff_portance_ravin, surface_ravin, masse):
        x, y, vx, vy = etat  # Décomposition de l'état en position et vitesse horizontales et verticales
        vitesse = math.sqrt(vx**2 + vy**2) or 1e-6  # Calcul de la vitesse totale, évite division par zéro
        ax = (-donnees["rho"] / (2 * masse)) * vitesse * (coeff_trainee_ravin * vx + coeff_portance_ravin * vy)  # Accélération horizontale
        ay = (-donnees["rho"] / (2 * masse)) * vitesse * (coeff_trainee_ravin * vy - coeff_portance_ravin * vx) - donnees["g"]  # Accélération verticale
        return [vx, vy, ax, ay]  # Retourne les dérivées [dx/dt, dy/dt, dvx/dt, dvy/dt]

    # Définir la surface frontale pour le ravin (A = largeur * hauteur)
    surface_ravin = voiture['largeur'] * voiture['hauteur']  # Surface frontale de la voiture pour le ravin
    coeff_trainee_ravin = coeff_trainee if 'jupe' in accessoires else 1  # Coefficient de traînée horizontale, réduit si jupe
    coeff_portance_ravin = coeff_portance  # Coefficient de portance verticale

    # Initialiser les conditions pour le ravin
    etat_initial_ravin = [0, 1, vitesse_lineaire_looping_fin, 0]  # Conditions initiales [x0, y0, vx0, vy0]
    t_ravin = np.linspace(0, 10, 5000)  # Intervalle de temps pour la simulation du ravin (10 secondes, 5000 points)

    # Appeler odeint pour résoudre les équations différentielles du ravin
    sortie_ravin = odeint(equation_ravin, etat_initial_ravin, t_ravin, args=(coeff_trainee_ravin, coeff_portance_ravin, surface_ravin, masse_totale))
    x_ravin = sortie_ravin[:, 0]  # Extraction des positions horizontales
    y_ravin = sortie_ravin[:, 1]  # Extraction des positions verticales
    vx_ravin = sortie_ravin[:, 2]  # Extraction des vitesses horizontales
    vy_ravin = sortie_ravin[:, 3]  # Extraction des vitesses verticales

    # Détermination de la fin du ravin
    condition_ravin = (np.abs(x_ravin - donnees["d_ravin"]) <= 0.09) & (np.abs(y_ravin) <= 0.09)  # Condition pour terminer le ravin
    indices_ravin = np.where(condition_ravin)[0]  # Trouve les indices où la condition est remplie
    if len(indices_ravin) == 0:
        # Si la voiture n'a pas complété le ravin, la simulation échoue
        return None
    fin_ravin = indices_ravin[0]  # Premier indice où la condition est remplie
    temps_ravin = t_ravin[fin_ravin]  # Temps correspondant à la fin du ravin
    vx_fin_ravin = vx_ravin[fin_ravin]  # Vitesse horizontale à la fin du ravin
    vy_fin_ravin = vy_ravin[fin_ravin]  # Vitesse verticale à la fin du ravin
    temps_total += temps_ravin  # Ajoute le temps du ravin au temps total

    # Stocker les données du ravin pour le tracé
    donnees_phase['ravin_vitesse'] = {
        "temps": t_ravin[:fin_ravin],  # Temps jusqu'à la fin du ravin
        "vx": vx_ravin[:fin_ravin],  # Vitesse horizontale jusqu'à la fin du ravin
        "vy": vy_ravin[:fin_ravin]  # Vitesse verticale jusqu'à la fin du ravin
    }
    donnees_phase['ravin_trajectoire'] = {
        "x": x_ravin[:fin_ravin],  # Position horizontale jusqu'à la fin du ravin
        "y": y_ravin[:fin_ravin]  # Position verticale jusqu'à la fin du ravin
    }

    # ----------- Simulation du Plat -----------
    surface_plat = voiture['largeur'] * voiture["hauteur"]  # Surface frontale de la voiture pour le plat
    etat_initial_plat = [vx_fin_ravin, 0]  # Conditions initiales [vitesse, position]
    t_plat = np.linspace(0, 11, 5000)  # Intervalle de temps pour la simulation du plat (11 secondes, 5000 points)

    # Définition de l'équation différentielle pour le plat
    def equation_plat(etat, t, acc_plat, coeff_plat):
        vitesse, position = etat  # Extraction de la vitesse et de la position actuelles
        f_frottement = donnees["U"] * masse_totale * donnees["g"]  # Calcul de la force de frottement au sol
        f_air = 0.5 * coeff_plat * donnees["rho"] * surface_plat * vitesse**2  # Calcul de la résistance de l'air
        f_motrice = acc_plat * masse_totale  # Calcul de la force motrice (accélération * masse)
        acceleration = (f_motrice - (f_frottement + f_air)) / masse_totale  # Accélération nette
        return [acceleration, vitesse]  # Retourne les dérivées [dv/dt, dx/dt]

    acc_plat = obtenir_acceleration('plat', acceleration_base)  # Obtient l'accélération pour le plat
    sortie_plat = odeint(equation_plat, etat_initial_plat, t_plat, args=(acc_plat, coeff_trainee))  # Résout les équations différentielles pour le plat
    vitesse_plat = sortie_plat[:, 0]  # Extraction des vitesses obtenues de la simulation
    position_plat = sortie_plat[:, 1]  # Extraction des positions obtenues de la simulation

    # Détermination de la fin du plat
    fin_plat_indices = np.where(position_plat >= donnees["d_finale"])[0]  # Trouve les indices où la position atteint ou dépasse d_finale
    if len(fin_plat_indices) == 0:
        # Si la voiture n'a pas atteint la fin du plat, la simulation échoue
        return None
    fin_plat = fin_plat_indices[0]  # Premier indice où la condition est remplie
    temps_plat = t_plat[fin_plat]  # Temps correspondant à la fin du plat
    vitesse_plat_fin = vitesse_plat[fin_plat]  # Vitesse à la fin du plat
    position_plat_fin = position_plat[fin_plat]  # Position à la fin du plat
    temps_total += temps_plat  # Ajoute le temps du plat au temps total

    # Stocker les données du plat pour le tracé
    donnees_phase['plat_vitesse'] = {
        "temps": t_plat[:fin_plat],  # Temps jusqu'à la fin du plat
        "vitesse": vitesse_plat[:fin_plat]  # Vitesse jusqu'à la fin du plat
    }
    donnees_phase['plat_position'] = {
        "temps": t_plat[:fin_plat],  # Temps jusqu'à la fin du plat
        "position": position_plat[:fin_plat]  # Position jusqu'à la fin du plat
    }

    # Collecter les métriques de performance
    performance = {
        "accessoires": accessoires,  # Liste des accessoires utilisés
        "temps_total": temps_total,  # Temps total pour le parcours
        "vitesse_fin": vitesse_plat_fin,  # Vitesse finale sur le plat
        "position_fin": position_plat_fin,  # Position finale sur le plat
        "temps_a_31m": temps_pente,  # Temps pour atteindre 31m sur la pente
        "vitesse_a_31m": vitesse_pente_fin,  # Vitesse à 31m sur la pente
        "temps_looping_finale": temps_looping,  # Temps pour terminer le looping
        "vitesse_looping_finale": vitesse_lineaire_looping_fin,  # Vitesse linéaire à la fin du looping
        "t_fin_ravin": temps_ravin,  # Temps à la fin du ravin
        "vx_fin_ravin": vx_fin_ravin,  # Vitesse horizontale à la fin du ravin
        "vy_fin_ravin": vy_fin_ravin,  # Vitesse verticale à la fin du ravin
        "temps_fin": temps_plat,  # Temps à la fin du plat
        "donnees_phase": donnees_phase  # Dictionnaire contenant les données détaillées par phase
    }

    return performance  # Retourne les métriques de performance de la simulation

# Fonction principale pour évaluer toutes les voitures et combinaisons d'accessoires
def evaluer_toutes_voitures(voitures, donnees, accessoires_dict):
    combinaisons_accessoires = generer_combinaisons_accessoires()  # Génère toutes les combinaisons possibles d'accessoires
    meilleures_performances = []  # Liste pour stocker les meilleures performances de chaque voiture

    for voiture in voitures:
        print(f"\n--- Test de {voiture['nom']} ---")  # Affiche le nom de la voiture en cours de test
        meilleure_performance = None  # Initialise la meilleure performance pour la voiture

        for combinaison in combinaisons_accessoires:
            performance = simuler_parcours(voiture, combinaison, donnees, accessoires_dict)  # Simule le parcours avec la combinaison d'accessoires
            if performance is None:
                continue  # Ignore si la simulation a échoué (voiture ne peut pas compléter le parcours)

            # Mettre à jour la meilleure performance basée sur le temps_total (le plus court est le meilleur)
            if (meilleure_performance is None) or (performance["temps_total"] < meilleure_performance["temps_total"]):
                meilleure_performance = performance  # Met à jour si la performance actuelle est meilleure

        if meilleure_performance:
            meilleures_performances.append({
                "voiture": voiture['nom'],  # Nom de la voiture
                "accessoires": meilleure_performance["accessoires"],  # Accessoires optimaux
                "temps_total": meilleure_performance["temps_total"],  # Temps total pour le parcours
                "vitesse_fin": meilleure_performance["vitesse_fin"],  # Vitesse finale sur le plat
                "position_fin": meilleure_performance["position_fin"],  # Position finale sur le plat
                "donnees_phase": meilleure_performance["donnees_phase"]  # Données détaillées par phase
            })
            print(f"Accessoires Optimaux : {meilleure_performance['accessoires']}")  # Affiche les accessoires optimaux pour cette voiture
            print(f"Temps Total : {meilleure_performance['temps_total']:.3f} secondes")  # Affiche le temps total
            print(f"Vitesse Finale : {meilleure_performance['vitesse_fin']:.3f} m/s")  # Affiche la vitesse finale
            print(f"Position Finale : {meilleure_performance['position_fin']:.3f} m")  # Affiche la position finale
        else:
            print("Aucune combinaison d'accessoires valide trouvée pour cette voiture.")  # Message si aucune combinaison ne fonctionne

    # Comparer toutes les performances pour trouver la meilleure voiture
    if not meilleures_performances:
        print("Aucune performance enregistrée.")  # Message si aucune performance n'a été enregistrée
        return

    # Trouver la voiture avec le temps total le plus court
    meilleure_voiture = min(meilleures_performances, key=lambda x: x["temps_total"])
    print("\n=== Meilleure Performance Globale ===")
    print(f"Voiture : {meilleure_voiture['voiture']}")  # Affiche le nom de la meilleure voiture
    print(f"Accessoires : {meilleure_voiture['accessoires']}")  # Affiche les accessoires optimaux
    print(f"Temps Total : {meilleure_voiture['temps_total']:.3f} secondes")  # Affiche le temps total
    print(f"Vitesse Finale : {meilleure_voiture['vitesse_fin']:.3f} m/s")  # Affiche la vitesse finale
    print(f"Position Finale : {meilleure_voiture['position_fin']:.3f} m")  # Affiche la position finale

    # Tracer les métriques de performance pour la meilleure voiture
    tracer_performance_meilleure_voiture(meilleure_voiture)  # Appelle la fonction de tracé

# Fonction pour tracer les performances de la meilleure voiture
def tracer_performance_meilleure_voiture(meilleure_voiture):
    donnees_phase = meilleure_voiture["donnees_phase"]  # Données détaillées par phase (pente, looping, ravin, plat)
    accessoires = meilleure_voiture["accessoires"]  # Accessoires utilisés
    nom_voiture = meilleure_voiture["voiture"]  # Nom de la voiture

    # ----------- Tracer la Pente - Vitesse vs Temps -----------
    pente_vitesse = donnees_phase['pente_vitesse']  # Données de vitesse lors de la pente
    plt.figure(figsize=(10, 6))
    plt.plot(pente_vitesse["temps"], pente_vitesse["vitesse"], color="blue", label="Vitesse")
    plt.title("Pente : Vitesse vs Temps")
    plt.xlabel("Temps (s)")
    plt.ylabel("Vitesse (m/s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ----------- Tracer la Pente - Position vs Temps -----------
    pente_position = donnees_phase['pente_position']  # Données de position lors de la pente
    plt.figure(figsize=(10, 6))
    plt.plot(pente_position["temps"], pente_position["position"], color="green", label="Position")
    plt.title("Pente : Position vs Temps")
    plt.xlabel("Temps (s)")
    plt.ylabel("Position (m)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ----------- Tracer le Looping - Vitesse Linéaire vs Temps -----------
    looping_vlineaire = donnees_phase['looping_vlineaire']  # Données de vitesse linéaire lors du looping
    plt.figure(figsize=(10, 6))
    plt.plot(looping_vlineaire["temps"], looping_vlineaire["v_lineaire"], color="purple", label="Vitesse Linéaire")
    plt.title("Looping : Vitesse Linéaire vs Temps")
    plt.xlabel("Temps (s)")
    plt.ylabel("Vitesse Linéaire (m/s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ----------- Tracer le Looping - Périmètre vs Angle θ -----------
    looping_perimetre = donnees_phase['looping_perimetre']  # Données du périmètre parcouru en fonction de l'angle theta
    plt.figure(figsize=(10, 6))
    plt.plot(looping_perimetre["theta"], looping_perimetre["perimetre"], color="magenta", label="Périmètre")
    plt.title("Looping : Périmètre vs Angle θ")
    plt.xlabel("Angle θ (rad)")
    plt.ylabel("Périmètre (m)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ----------- Tracer le Ravin - Vitesse Totale vs Temps -----------
    ravin_vitesse = donnees_phase['ravin_vitesse']  # Données de vitesses dans le ravin

    # Calculer la vitesse totale
    vitesse_totale_ravin = np.sqrt(ravin_vitesse["vx"]**2 + ravin_vitesse["vy"]**2)

    plt.figure(figsize=(10, 6))
    plt.plot(ravin_vitesse["temps"], vitesse_totale_ravin, color="orange", label="Vitesse Totale")
    plt.title("Ravin : Vitesse Totale vs Temps")
    plt.xlabel("Temps (s)")
    plt.ylabel("Vitesse Totale (m/s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ----------- Tracer le Ravin - Trajectoire (Y vs X) -----------
    ravin_trajectoire = donnees_phase['ravin_trajectoire']  # Données de trajectoire dans le ravin
    plt.figure(figsize=(10, 6))
    plt.plot(ravin_trajectoire["x"], ravin_trajectoire["y"], color="green", label="Trajectoire")
    plt.title("Ravin : Trajectoire (Y vs X)")
    plt.xlabel("Position Horizontale X (m)")
    plt.ylabel("Position Verticale Y (m)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ----------- Tracer le Plat - Vitesse vs Temps -----------
    plat_vitesse = donnees_phase['plat_vitesse']  # Données de vitesse sur le plat
    plt.figure(figsize=(10, 6))
    plt.plot(plat_vitesse["temps"], plat_vitesse["vitesse"], color="brown", label="Vitesse")
    plt.title("Plat : Vitesse vs Temps")
    plt.xlabel("Temps (s)")
    plt.ylabel("Vitesse (m/s)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ----------- Tracer le Plat - Position vs Temps -----------
    plat_position = donnees_phase['plat_position']  # Données de position sur le plat
    plt.figure(figsize=(10, 6))
    plt.plot(plat_position["temps"], plat_position["position"], color="cyan", label="Position")
    plt.title("Plat : Position vs Temps")
    plt.xlabel("Temps (s)")
    plt.ylabel("Position (m)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Exécuter l'évaluation
if __name__ == "__main__":
    evaluer_toutes_voitures(voitures, donnees, accessoires_dict)  # Appelle la fonction principale pour évaluer toutes les voitures et combinaisons d'accessoires
