# -*- coding: utf-8 -*-
# Code Python Projet Mécanique
# Programmé par : HASSANE HAIDAR, AXEL BLIN, MILHARO CLEMENT, JOHAN FILLAT

from itertools import *
from math import *
from matplotlib.pyplot import *
from numpy import *
from scipy.integrate import odeint

# Les masses sont en kg, les vitesses et accélérations en m/s,
# les distances et hauteurs en m.
# Les masses seront notées m, les hauteurs H, les distances D,
# les accélérations acc, U est le coefficient de frottement dynamique.
# Les longueurs L et largeurs l, alpha représente l'angle d'inclinaison de la pente.

donnees = {
    "U": 0.1,
    "Cz": 0.3,
    "Dpente": 31,
    "Dlooping": 12*pi,
    "Rlooping": 6,
    "Dravin": 9,
    "Dfinale": 10,
    "Hravin": 1,
    "Hpente": 2,
    "alpha": 4*pi/180,
    "v0": 0,
    "y0": 0,
    "tinitial_pente": 0,
    "pas": 0.1,
    "g": 9.81,
    "rho": 1.225,
}

Accessoires = {
    "booster": {"accSup": 1.3},
    "ailerons": {"mAilerons": 30, "CzSup": 1.1},
    "jupe": {"mJupe": 15, "CxRed": 0.95}
}

listeVoitures = [
    {"nom": "Dodge Charger R/T", "m": 1760, "acc": 5.1, "L": 5.28, "l": 1.95, "h": 1.35, "Cx": 0.38},
    {"nom": "Toyota Supra Mark IV", "m": 1615, "acc": 5, "L": 4.21, "l": 1.81, "h": 1.27, "Cx": 0.29},
    {"nom": "Chevrolet Yenko Camaro", "m": 1498, "acc": 5.3, "L": 4.72, "l": 1.88, "h": 1.30, "Cx": 0.35},
    {"nom": "Mazda RX-7 FD", "m": 1385, "acc": 5.2, "L": 4.3, "l": 1.75, "h": 1.23, "Cx": 0.28},
    {"nom": "Nissan Skyline GTR-R34", "m": 1540, "acc": 5.8, "L": 4.6, "l": 1.79, "h": 1.36, "Cx": 0.34},
    {"nom": "Mitsubishi Lancer Evolution VII", "m": 1600, "acc": 5, "L": 4.51, "l": 1.81, "h": 1.48, "Cx": 0.28},
]


# FONCTION OPTIONNELLE POUR DÉTERMINER LA VITESSE MINIMALE À FRANCHIR LE RAVIN  #

def vitesse_min_ravin(voiture, S, donnees, pas_increment=0.5):
    """
    consiste en une répétition de l'étape du ravin jusqu'à obtenir les bonnes valeurs de distance ,hauteurs et vitesses
    """
    # Récupération des paramètres
    Dr = donnees["Dravin"]
    Hr = donnees["Hravin"]
    g = donnees["g"]
    
    # On part d'une petite vitesse, et on teste
    v_test = 1.0  
    test = False

    while not test:#test les vitesse jusqu'à ce que le ravin soit passé
        # Conditions initiales : on suppose qu'on démarre à x=0, y=Hr (ou 1m, etc.)
        # pour simuler le saut
        ref_entree = [0, Hr, v_test, 0]  
        temps_test = linspace(0, 10, 1000)
        
        sol = odeint(ravin, ref_entree, temps_test, args=(voiture, S, donnees))
        
        x_test = sol[:, 0]
        y_test = sol[:, 1]
        
        # Vérifier si on a franchi Dravin (x >= Dr) et en restant au-dessus du "sol"
        # Si y < 0 (ou proche de zéro),c'est raté.
        # On regarde le premier instant avec x >= Dr
        # et on vérifie si y > 0 (ou un peu plus que -Hravin).
        
        for i in range(len(x_test)):
            if x_test[i] >= Dr:
                # On a franchi la distance du ravin
                if y_test[i] >= 0:
                    test = True
                break
        
        if not test:
            v_test += pas_increment

    return v_test


# ÉQUATION DIFFÉRENTIELLE POUR LA PENTE                                        

def  pente(y, t, voiture, S, donnees):
    v = y[0]  # vitesse
    x = y[1]  # position
    alpha = donnees["alpha"]
    m = voiture["m"]
    g = donnees["g"]

    # Réaction normale
    N = m * g * cos(alpha)
    # Frottement sol
    f_sol = donnees["U"] * N
    # Résistance de l'air
    f_air = 0.5 * voiture["Cx"] * donnees["rho"] * S * (v**2)
    # Force motrice
    fMotrice = voiture["acc"] * m
    # Projection du poids
    px = m * g * sin(alpha)
    
    sommeForces = fMotrice + px - (f_sol + f_air)
    a = sommeForces / m

    return [a, v]


# ÉQUATION DIFFÉRENTIELLE POUR LE LOOPING
def looping(y, t, voiture, S, donnees):
    """
    y = [theta, theta_v]
    """
    theta = y[0]
    theta_v = y[1]
    
    g = donnees["g"]
    R = donnees["Rlooping"]
    m = voiture["m"]
    U = donnees["U"]

    pUr = cos(theta)*m*g
    pUo = sin(theta)*m*g
    # Réaction normale
    N = m*R*(theta_v**2) + pUr
    # Frottement
    fsol = N*U
    # Force motrice
    fMotrice = voiture["acc"] * m
    # Résistance de l'air
    fAir = 0.5 * voiture["Cx"] * donnees["rho"] * S * (R*theta_v)**2

    sommeForces = fMotrice - pUo - (fsol + fAir)
    a = sommeForces / (m*R)
    return [theta_v, a]


# ÉQUATION DIFFÉRENTIELLE POUR LE RAVIN           

def ravin(U, t, voiture, S, donnees):
    x = U[0]   # Position horizontale
    y = U[1]   # Position verticale
    vx = U[2]  # Vitesse horizontale
    vy = U[3]  # Vitesse verticale

    T = voiture["Cx"] * S
    P = donnees["Cz"] * S
    rho = donnees["rho"]
    m = voiture["m"]
    g = donnees["g"]

    # Norme de la vitesse
    v_norm = sqrt(vx**2 + vy**2)
    
    #  trainée
    ax = -(rho/(2*m)) * v_norm * (T*vx + P*vy)
    ay = -(rho/(2*m)) * v_norm * (T*vy - P*vx) - g

    return [vx, vy, ax, ay]


# ÉQUATION DIFFÉRENTIELLE POUR LE PLAT   

def plat(z, t, voiture, S, donnees):
    v = z[0]  # Vitesse
    x = z[1]  # Position
    
    m = voiture["m"]
    g = donnees["g"]
    N = m * g  # Réaction normale
    f_sol = donnees["U"] * N
    f_air = 0.5 * voiture["Cx"] * donnees["rho"] * S * v**2
    fMotrice = voiture["acc"] * m

    sommeForces = fMotrice - (f_sol + f_air)
    a = sommeForces / m
    return [a, v]

#BOUCLE SUR CHAQUE VOITURE #
#DEBUT DE LA COURSE#
for voiture in listeVoitures:
    # Surface frontale (approx. l*h)
    S = voiture['l'] * voiture["h"]

   
    #  Résolution de l'équation différentielle sur la pente
   

    v0 = 0
    x0 = 0
    y_init_pente = [v0, x0]
    t_pente = linspace(0, 10, 2500)

    # On résout
    sortie_pente = odeint(pente, y_init_pente, t_pente, args=(voiture, S, donnees))

    vitesse_pente = sortie_pente[:, 0]
    position_pente = sortie_pente[:, 1]

    indice_fin_pente = -1
    vitesseFinPente = 0.0
    tempsFinPente = 0.0

    for i in range(len(position_pente)):
        if position_pente[i] >= donnees["Dpente"]:
            vitesseFinPente = vitesse_pente[i]
            tempsFinPente = t_pente[i]
            indice_fin_pente = i
            print(voiture['nom'] ,":")
            print("Vitesse à la fin de la pente =",  round(vitesseFinPente, 3),
                  "m/s soit", round(vitesseFinPente * 3.6),"km/h")
            print("Temps correspondant =", round(tempsFinPente, 3),"secondes\n")
            break

    # Graphique vitesse sur la pente
    plot(t_pente[:indice_fin_pente], vitesse_pente[:indice_fin_pente],
         label="Vitesse v(t)", color="blue")
    xlabel("temps(s)")
    ylabel("Vitesse (m/s)")
    title(f"Évolution de la vitesse sur la pente - {voiture['nom']}")
    legend()
    grid()
    tight_layout()
    show()

    
    #  Vérification de la vitesse minimale pour le looping
    
    v_min_theorique = sqrt(5 * donnees["g"] * donnees["Rlooping"]) 
    vitesse_test = v_min_theorique
    tolerance = 0.01
    vteta0 = [0, vitesse_test / donnees["Rlooping"]]
    temps_test_loop = linspace(0, 5, 1000)
    vteta = odeint( looping, vteta0, temps_test_loop, args=(voiture, S, donnees))
    Rn = max(donnees["g"] * cos(vteta[:, 0]) + donnees["Rlooping"] * vteta[:, 1]**2)

    if Rn < 0:  # Décrochage
        vitesse_test += tolerance
        
        continue

    print("La vitesse minimale d'entréepour le looping est =", round(vitesse_test, 3), "m/s")
    
    
    #Parcours du looping si la vitesse en sortie de pente est suffisante
    
    if vitesseFinPente > vitesse_test:
        theta0 = 1*np.pi/180
        Vanglloop = vitesseFinPente / donnees["Rlooping"]
        S_init_loop = [theta0, Vanglloop]
        t_loop = linspace(0, 5, 1000)

        resultLooping = odeint (looping, S_init_loop, t_loop, args=(voiture, S, donnees))
        pos_loop = resultLooping[:,0]
        vit_loop = resultLooping[:,1]
        
        vitesse_sommet_insuffisante = False
        v_min_sommet = sqrt(donnees["Rlooping"] * donnees["g"])

        indice_fin_loop = -1
        for i in range(len(pos_loop)):
            distance_parcourue = donnees["Rlooping"] * pos_loop[i]
            # Sommet => pi*R environ
            if abs(distance_parcourue - pi * donnees["Rlooping"]) < 1e-2:
                vitesse_sommet = vit_loop[i] * donnees["Rlooping"]
                # Test de la condition
                if vitesse_sommet < v_min_sommet:
                    print(voiture['nom']," :")
                    print("Impossible de réaliser le looping : vitesse au sommet insuffisante.\n")
                    vitesse_sommet_insuffisante = True
                    break
            
            if distance_parcourue >= donnees["Dlooping"] and not vitesse_sommet_insuffisante:
                vitesseLoopingFinale = vit_loop[i] * donnees["Rlooping"]
                positionLoopingFinale = distance_parcourue
                tempsLoopingFinale = t_loop[i]
                indice_fin_loop = i
                print(voiture['nom'] ,":")
                print("Position à la fin du looping =", round(positionLoopingFinale, 3),"m")
                print("Vitesse à la fin du looping =", round(vitesseLoopingFinale, 3) ,"m/s")
                print("Temps pour terminer le looping =", round(tempsLoopingFinale, 3),"secondes\n")
                break

        # Graphique de la vitesse dans le looping
        if indice_fin_loop > 0:
            t_looping = t_loop[:indice_fin_loop]
            v_looping = vit_loop[:indice_fin_loop] * donnees["Rlooping"]
            
            figure(figsize=(10, 6))
            plot(t_looping, v_looping, label="Vitesse linéaire (m/s)", color="blue")
            xlabel("Temps (s)")
            ylabel("Vitesse (m/s)")
            title("Évolution de la vitesse linéaire dans le looping")
            legend()
            grid()
            show()
            
      
        # Traversée du ravin s'il y a une vitesse de sortie du looping
      
            
            #  calcule  de la vitesse minimale pour franchir le ravin
            v_min_ravin_calculee = vitesse_min_ravin(voiture, S, donnees, pas_increment=0.5)
            print(f"Vitesse minimale nécessaire pour franchir le ravin (approx) = {v_min_ravin_calculee:.2f} m/s")
            
            if vitesseLoopingFinale >= v_min_ravin_calculee:
                # On simule le ravin avec la vitesse horizontale = vitesseLoopingFinale
                x0_ravin = 0
                y0_ravin = 1  # on suppose 1m de haut (ou Hravin)
                vx0_ravin = vitesseLoopingFinale
                vy0_ravin = 0  # ou petit saut
                ref_entree_ravin = [x0_ravin, y0_ravin, vx0_ravin, vy0_ravin]
                
                t_ravin = linspace(0, 5, 10000)
                resultRavin = odeint(ravin, ref_entree_ravin, t_ravin, args=(voiture, S, donnees))

                x_ravin = resultRavin[:, 0]
                y_ravin = resultRavin[:, 1]
                vx_ravin = resultRavin[:, 2]
                vy_ravin = resultRavin[:, 3]

                indice_fin_ravin = -1
                for i in range(len(x_ravin)):
                    # Condition : la voiture atterrit à Dravin ~ 9m + retombe à y=~0
                    if abs(x_ravin[i] - donnees["Dravin"]) <= 0.09 and abs(y_ravin[i]) <= 0.09:
                        indice_fin_ravin = i
                        tFinRavin = t_ravin[i]
                        vx_Finravin = vx_ravin[i]
                        vy_Finravin = vy_ravin[i]
                        print("Vitesse en x de fin de ravin =", round(vx_Finravin, 3),"m/s")
                        print("Vitesse en y de fin de ravin =", round(vy_Finravin, 3),"m/s")
                        print("Temps de fin du ravin =", round(tFinRavin, 3),"s")
                        print(voiture['nom']," :")
                        break

                # Tracé de la trajectoire dans le ravin
                if indice_fin_ravin > 0:
                    figure(figsize=(10, 6))
                    plot(x_ravin[:indice_fin_ravin], y_ravin[:indice_fin_ravin],
                         label="Trajectoire dans le ravin", color="blue")
                    xlabel("Position horizontale x (m)")
                    ylabel("Position verticale y (m)")
                    title(f"Trajectoire dans le ravin - {voiture['nom']}")
                    legend()
                    show()
                    
               
                #  Parcours sur le plat
              
                if indice_fin_ravin > 0:
                    z0_plat = [vx_Finravin, 0]
                    t_plat = linspace(0, 11, 5000)
                    finCircuit = odeint(plat, z0_plat, t_plat, args=(voiture, S, donnees))

                    vitesse_finale = finCircuit[:, 0]
                    position_finale = finCircuit[:, 1]

                    indice_finale_plat = -1
                    for i in range(len(position_finale)):
                        if position_finale[i] >= donnees["Dfinale"]:
                            v_fin = vitesse_finale[i]
                            x_fin = position_finale[i]
                            t_fin = t_plat[i]
                            indice_finale_plat = i
                            print("Vitesse finale sur le plat =", round(v_fin, 3),"m/s")
                            print("Position atteinte =", round(x_fin, 3),"m")
                            print("Temps total sur le plat =", round(t_fin, 3), "secondes")
                            break

                    # Graphique sur le plat
                    if indice_finale_plat > 0:
                        figure(figsize=(10, 6))
                        plot(t_plat[:indice_finale_plat], vitesse_finale[:indice_finale_plat],
                             label="Vitesse v(t) sur le plat (m/s)", color="orange")
                        xlabel("Temps (s)")
                        ylabel("Vitesse (m/s)")
                        title(f"Évolution sur le plat - {voiture['nom']}")
                        legend()
                        grid()
                        show()
                        
                    # Temps total
                    if indice_finale_plat > 0:
                        temps_total = tempsFinPente + tempsLoopingFinale + tFinRavin + t_plat[indice_finale_plat]
                        print("Temps total final pour le circuit =", round(temps_total, 3), "secondes\n")
            else:
                print(voiture['nom'], ": La vitesse de sortie du looping est insuffisante pour franchir le ravin.\n")
    else:
        print(voiture['nom'], ": Vitesse en fin de pente trop faible pour entamer le looping.\n")
