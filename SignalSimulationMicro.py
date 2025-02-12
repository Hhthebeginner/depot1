from matplotlib.pyplot import *
import sounddevice as sd
import numpy as np
from soundfile import read
import time
import scipy.integrate as sp
# --- Fonctions de conversion ---

def import_song(nomfichier):       # Définition de la fonction qui importe le nom du fichier son
    """
    Lit le fichier son et retourne (Fe, data)
    """
    data, fq_e = read(nomfichier + ".wav")
    return fq_e, data         # Retour des valeurs de fréquence d'échantillonage et des valeurs data

def verif_message(message):# Définition de la fonction qui vérifie la taille du message
    if 5 <= len(message) <= 10:    #Verification si la longueur du message est comprise entre 5 et 10 inclus
        return True
    else:
        raise ValueError("Erreur : message de mauvaise taille (doit contenir entre 5 et 10 caractères)")

def convertir_ascii(message):# Définition de la fonction qui convertit le message en ASCII
    """
    Convertit un message texte en une liste de codes ASCII.
    """
    return [ord(c) for c in message]               # Fonction ord qui converti des caratère en leurs valeur ASCII

def convertir_binaire(codes, nb_bits=7):# Définition de la fonction qui convertit les codes en binaire
    """
    Convertit une liste de codes (ASCII ou entiers) en une séquence de bits (0 et 1)
    sur nb_bits bits. Par défaut, nb_bits=7 (pour le texte).
    Pour le son, il faudra appeler avec nb_bits=8.
    """
    bits = []
    for code in codes:
        b = format(code, f'0{nb_bits}b')  # représentation sur nb_bits bits
        bits.extend([int(bit) for bit in b])    # bits étend sa liste pour chaque bit mais en tant qu'entier
    return bits

def convertir_decimal(message_binaire, nb_bits=7):# Définition de la fonction qui convertit le binaire en décimal
    """
    Regroupe la liste de bits en paquets de nb_bits bits et les convertit en nombre décimal.
    """
    decimals = []
    for i in range(0, len(message_binaire), nb_bits):
        grp = message_binaire[i:i+nb_bits]
        nv_decimal = ''.join(str(bit) for bit in grp)   # convertit en chaîne de caractères
   
        decimals.append(int(nv_decimal, 2))
    return decimals

def convertir_caractere(message_decimal):   # Définition de la fonction qui convertit le décimal en caractère
    """
    Convertit une liste de nombres décimaux en une liste de caractères.
    """
    return [chr(c) for c in message_decimal]    #Fonction retourne chaque décimal en caratère

def convertir_anal(signal):# Définition de la fonction qui convertit le signal en analogique
    """
    Convertit des valeurs quantifiées (0 à 255) en signal analogique dans l'intervalle [-1, 1].
    Par exemple, 0 -> -1 et 255 -> 1.
    """
    return [(c - 127.5) / 127.5 for c in signal]

def convertir_quantifie(data):# Définition de la fonction qui quantifie les données
    """
    Convertit le signal audio (supposé avoir des valeurs entre -1 et 1)
    en valeurs entières entre 0 et 255.
    """
    return [int(round(((c + 1) / 2) * 255)) for c in data]  #   on effectue un calcul transformant toutes les valeurs décimales en entier. Pour c=1 on a le max à 255 et pour c=-1 on a le min : 0

# --- Paramètres globaux ---
Fe =10000                           # Fréquence d'échantillonnage pour la modulation/démodulation


baud = 600                          # Débit binaire (bits par seconde)
Ns = int(round(Fe / baud))          # Nombre d'échantillons par bit

# --- Modulation 1--

def modul_Ask(message):# Définition de la fonction qui module le message en ASK
    """
    Modulation ASK.
    On suppose que 'message' est une liste de bits (0 ou 1).
    """
    nbits = len(message)  # Nombre de bits initial qui correspond au nombre d'éléments du message de base ( entre 5 et 10 )
    N = nbits * Ns        # N correspond au nouveau nombre de bits après produit par 'Ns' bits
    # Duplique chaque bit sur Ns échantillons (bien que l'on n'utilise pas M_duplique par la suite)
    M_duplique = np.repeat(message, Ns)
   
    # Vecteur temps
    t = np.linspace(0, N / Fe, N)
   
    # Porteuse
    Ap = 1                      
    Fp = 2100                    
    Porteuse = Ap * np.sin(2 * np.pi * Fp * t)    # Formule de la porteuse
   
    # Modulation : on insère la porteuse pour un bit correspondant à 1, et zéro pour un 0
    ASK = np.zeros(N)
    for i, bit in enumerate(message):
        if bit == 1:
            ASK[i * Ns:(i + 1) * Ns] = Porteuse[i * Ns:(i + 1) * Ns]
        else:
            ASK[i * Ns:(i + 1) * Ns] = 0  # ou reste à 0
    return ASK, Fp, nbits, Fe

def modul_FSK(message):# Définition de la fonction qui module le message en FSK
    """
    Modulation FSK.
    On suppose que 'message' est une liste de bits (0 ou 1).
    """
    nbits = len(message)
    N = nbits * Ns
    M_duplique = np.repeat(message, Ns)
   
    # Vecteur temps
    t = np.linspace(0, N / Fe, N)
    t1 = np.linspace(0, Ns / Fe, Ns)
   
    # Définition des porteuses pour 1 et 0
    A1 = 1  # pour le bit 1                          
    A2 = 1  # pour le bit 0
    fp1 = 2000  # fréquence pour 1
    fp2 = 2200  # fréquence pour 0
   
    P1 = A1 * np.sin(2 * np.pi * fp1 * t1)  # Porteuse pour 1  
    P2 = A2 * np.sin(2 * np.pi * fp2 * t1)  # Porteuse pour 0
   
    FSK = np.zeros(len(M_duplique))
    for i, bit in enumerate(message):
        if bit == 1:
            FSK[i * Ns:(i + 1) * Ns] = P1       # Si le bit=1 on  prend P1
        else:
            FSK[i * Ns:(i + 1) * Ns] = P2       # Si le bit=0 on prend P2
    return FSK, fp1, fp2, nbits, Fe

def filtre_ASK(fp, data_sortie):
    frequence = sp.fft.fft(data_sortie)
    frequence_filtre = []
    for i in frequence:
        if fp - 50 < i < fp + 50:
            frequence_filtre.append(i)
    ASK_filtre = sp.fft.ifft(frequence_filtre)
    return ASK_filtre

def filtre_FSK(fp1, fp2, data_sortie):
    frequence = sp.fft.fft(data_sortie)
    frequence_filtre = []
    for i in frequence:
        if fp1 - 50 < i < fp1 + 50 and fp2 - 50 < i < fp2 + 50:
            frequence_filtre.append(i)

    FSK_filtre = sp.fft.ifft(frequence_filtre)
    return FSK_filtre

def demod_ASK(signal, Fe, Nbits, fp1):# Définition de la fonction qui démodule le signal ASK
    Ns_local = int(round(Fe / baud))
    N_attendu = Nbits * Ns_local
    # Ajustement de la longueur du signal
    if len(signal) > N_attendu:                 # Condition si la longueur du signal est supérieure à N_attendu
        signal = signal[:N_attendu]
    elif len(signal) < N_attendu:
        signal = np.pad(signal, (0, N_attendu - len(signal)), mode='constant')  # Si condition validée on ajoute N_attendu-len(signal) 0 à la fin du signal
    N = N_attendu

    t = np.linspace(0, N / Fe, N)
    S = np.sin(2 * np.pi * fp1 * t)

    ASK_demod = signal * S

    Message_demodule_ASK = []
    for i in range(0, N, Ns_local):
        morceau = ASK_demod[i:i + Ns_local]
        integ = np.trapezoid(morceau)  # Utilisation de np.traperoid qui est plus poussé que trapz
        if integ > 0:
            Message_demodule_ASK.append(1)      # Transformation du signal en binaire 1 si l'intégrale est positive
        else:
            Message_demodule_ASK.append(0)      # Transformation du signal en bianire 0 si l'intégrale est négative
   
    return Message_demodule_ASK

def demod_FSK(signal, Fe, Nbits, fp1, fp2):# Définition de la fonction qui démodule le signal FSK
    Ns_local = int(round(Fe / baud))      
    N_attendu = Nbits * Ns_local
    if len(signal) > N_attendu:
        signal = signal[:N_attendu]
    elif len(signal) < N_attendu:
        signal = np.pad(signal, (0, N_attendu - len(signal)), mode='constant')       # Si condition validée on ajoute N_attendu-len(signal) 0 à la fin du signal
    N = N_attendu

    t = np.linspace(0, N / Fe, N)
    t1 = np.linspace(0, Ns_local / Fe, Ns_local)
    S1 = np.sin(2 * np.pi * fp1 * t1)
    S2 = np.sin(2 * np.pi * fp2 * t1)
   
    num_segments = int(N / Ns_local)
    S1_tile = np.tile(S1, num_segments)
    S2_tile = np.tile(S2, num_segments)
   
    P1 = signal * S1_tile
    P2 = signal * S2_tile

    y1 = []
    y2 = []
    for i in range(0, N, Ns_local):
        y1.append(np.trapezoid(P1[i:i + Ns_local]))     # Calcul d'intégrale pour chaque segment du signal pour P1
        y2.append(np.trapezoid(P2[i:i + Ns_local]))     # Calcul d'intégrale pour chaque segment du signal pour P2
   
    message_demodule_FSK = []
    for j in range(len(y1)):
        if abs(y1[j]) > abs(y2[j]):                     # Si l'intégrale de P1 est supérieure à celle de P2, le message prend 1 sinon 0
            message_demodule_FSK.append(1)
        else:
            message_demodule_FSK.append(0)
   
    return message_demodule_FSK

# --- Décodage Manchester et NRZI ---

def decodage_manchester(message_demodule):# Définition de la fonction qui décode le message en Manchester
    """
    Décodage Manchester : on prend le second bit de chaque paire.
    """
    return [int(message_demodule[i + 1]) for i in range(0, len(message_demodule), 2)]

def decodage_nrzi(message_demodule):# Définition de la fonction qui décode le message en NRZI
    return [1 if message_demodule[0] == 1 else 0] + [                               # Si le premier bit est 1, le premier bit du message décodé est 1 sinon 0
        1 if message_demodule[i] != message_demodule[i - 1] else 0                  # Pour chaque bit, si le bit est 1 on inverse le niveau, sinon on garde le même niveau
        for i in range(1, len(message_demodule))                                    # Ceci pour chaque bit du tableau
    ]

def ouverture_fichier(nomfichier):# Définition de la fonction qui ouvre le fichier
    with open(nomfichier + ".txt", "r") as text:        # Ouverture du fichier en mode lecture avec .txt en extension de base
        nbits = int(text.readline().strip())
        Fe = int(text.readline().strip())
        fp1 = int(text.readline().strip())
        fp2 = int(text.readline().strip())
        signal = np.loadtxt(text)
    return signal, nbits, Fe, fp1, fp2

def sauvegarde_fichier(nomfichier, trame, signal):# Définition de la fonction qui sauvegarde le fichier
    with open(nomfichier + ".txt", "w") as text:
        text.writelines(trame)
        for valeur in signal:
            text.write(f"{valeur}\n")             # Ecriture de chaque valeur du signal dans le fichier chacune à la ligne

def play_sound(signal, Fe):# Définition de la fonction qui joue le son
    sd.play(signal, Fe)
    sd.wait()

# --- Choix de la modulation ou sauvegarde/lecture ---
def choix(message):
    print("Choisissez le type de modulation que vous voulez faire")
    choix_mod = int(input("""Votre choix:
    1. ASK
    2. FSK
    """))
    choix_tr = int(input("""Votre choix:
    1. Sauvegarder dans un fichier
    2. Jouer le son directement
    """))
    if choix_mod == 1:                                                  # Si le choix de la modulation est ASK on effectue la modulation ASK
        mod_signal, fp1, nbits, Fe = modul_Ask(message)
        trame = [f"{nbits}\n", f"{Fe}\n", f"{fp1}\n",f"{0}\n"]
        if choix_tr == 1:                                               # Ensuite dans ASK on demande le type de transmission, si 1 on sauvegarde le fichier
            sauvegarde_fichier("ASK", trame, mod_signal)
        elif choix_tr == 2:                                             #  Si 2 on joue le son directement
            mod_trame, fp1, nbits, Fe = modul_Ask([format(nbits,'07b'), format(Fe,'16b'), format(fp1,'12b'), format(0,'12b')])
            # play_sound(mod_trame, Fe)
            # time.sleep(1)
            play_sound(mod_signal, Fe)
    elif choix_mod == 2:                                                # Même chose que ASK pour FSK
        mod_signal, fp1, fp2, nbits, Fe = modul_FSK(message)
        trame = [f"{nbits}\n", f"{Fe}\n", f"{fp1}\n", f"{fp2}\n"]
        if choix_tr == 1:
            sauvegarde_fichier("FSK", trame, mod_signal)
        elif choix_tr == 2:
            play_sound(mod_signal, Fe)
    else:
        print("Erreur de saisie dans le choix de la modulation")
        choix(message)

def codage_manchester(tab_binaire):# Définition de la fonction qui code le message en Manchester
                # Codage Manchester : pour chaque bit, 0 -> (1,0) et 1 -> (0,1)
    message_codemans = []
    for bit in tab_binaire:
        if bit == 0:
            message_codemans.extend([1, 0])
        elif bit == 1:
            message_codemans.extend([0, 1])
    return message_codemans

def codage_NRZI(message):# Définition de la fonction qui code le message en NRZI
    """
    # Encodage NRZI : on part d'un niveau initial égal à 0.
    Pour chaque bit, si le bit est 1 on inverse le niveau, sinon on le conserve.
    """
    e = [1 if message[0] == 1 else 0]    
    for i in range(1, len(message)):
        if message[i] == 1:
            e.append(1 - e[i - 1])       # Niveau inversé
        else:
            e.append(e[i - 1])           # Niveau conser
    return e

# --- Programme principal ---

requete = int(input("""Voulez-vous envoyer ou recevoir un message ?
1. Envoyer
2. Recevoir
"""))
                                        # Début du programme
if requete == 1:                                                                # Première condition au niveau de la tâche à effectuer  
    print("Vous avez choisi d'envoyer un message")                              # Si 1 : Configuration d'envoie d'un signal/message
    TypeMessage = input("Quel type de message voulez-vous envoyer ? (son/texte) : ").strip()
    if TypeMessage == "son":                                                    # Condition 1.2) Type de message à envoyer
        nomfichier = input("Quel est le nom du fichier que vous voulez importer (sans extension) : ").strip()   # Nom du fichier à importer
        Fe, data = import_song(nomfichier)
        # Convertir le signal de [-1, 1] en valeurs entières entre 0 et 255
        data_quant = convertir_quantifie(data)
        # Pour le son, on utilise 8 bits
        conv2 = convertir_binaire(data_quant, nb_bits=8)
        man = int(input("""L'information est-elle confidentielle ?
                        1. OUI
                        2. NON
                        """))
        if man == 1:
            message_code1 = codage_manchester(conv2)
            message_code2 = codage_NRZI(message_code1)
        else:
            message_code2 = codage_NRZI(conv2)
        choix(message_code2)
    elif TypeMessage == "texte":
        print("Vous ne pouvez envoyer qu'entre 5 et 10 caractères")
        message = input("Veuillez saisir votre message : ")
        if verif_message(message):
            message_ascii = convertir_ascii(message)
            message_binaire = convertir_binaire(message_ascii, nb_bits=7)
            message_code1 = codage_manchester(message_binaire)
            message_code2 = codage_NRZI(message_code1)
            choix(message_code2)
    else:
        print("Erreur de saisie")
       
elif requete == 2:
    print("Vous avez choisi de recevoir un message")
    TypeMessage = input("Quel type de message voulez-vous recevoir ? (son/texte) : ").strip()
    if TypeMessage == "son":
        choixmod = int(input("""Quel type de modulation avez-vous utilisé ?
                            1. ASK
                            2. FSK
                            """))
        choix_tr = int(input("""Votre choix:
                            1. Lire un fichier sauvgardé
                            2. Ecouter le son directement
                            """))
        if choix_tr == 1:
            signal, nbits, Fe, fp1, fp2 = ouverture_fichier("ASK" if choixmod == 1 else "FSK")
        elif choix_tr == 2:
            signal = sd.rec(3*Fe, fq_e=Fe, channels=1)
        if choixmod == 1:
            m_demod = demod_ASK(signal, Fe, nbits, fp1)
        elif choixmod == 2:
            m_demod = demod_FSK(signal, Fe, nbits, fp1, fp2)
        if int(input("L'information était-elle confidentielle ? (1. OUI/2. NON) : ")) == 1:
            de_nrzi = decodage_nrzi(m_demod)
            de_code = decodage_manchester(de_nrzi)
        else:
            de_code = decodage_nrzi(m_demod)
        # Pour le son, on regroupe par 8 bits
        de_decimal = convertir_decimal(de_code, nb_bits=8)
        de_message = convertir_anal(de_decimal)
        play_sound(de_message, Fe)
 
    elif TypeMessage == "texte":
        choixmod = int(input("""Quel type de modulation avez-vous utilisé ?
                            1. ASK
                            2. FSK
                            """))
        choix_tr = int(input("""Votre choix:                    
                            1. Lire un fichier sauvgardé
                            2. Ecouter le son directement
                            """))
        if choix_tr == 1:
            signal, nbits, Fe, fp1, fp2 = ouverture_fichier("ASK" if choixmod == 1 else "FSK")
        elif choix_tr == 2:
            signal = sd.rec(1*Fe, samplerate=Fe, channels=1)
        if choixmod == 1:
            m_demod = demod_ASK(signal, 10000, 38, 2100) if choix_tr == 2 else demod_ASK(signal, Fe, nbits, fp1)
            if choix_tr == 2:
                time.sleep(0.5)
                signal = sd.rec(1*Fe, samplerate=Fe, channels=1)
                m_demod = demod_ASK(signal, Fe, nbits, fp1)
        elif choixmod == 2:
            m_demod = demod_FSK(signal, Fe, nbits, fp1, fp2)
        de_nrzi = decodage_nrzi(m_demod)
        de_manchester = decodage_manchester(de_nrzi)
        de_decimal = convertir_decimal(de_manchester, nb_bits=7)
        de_message = convertir_caractere(de_decimal)
        message = ''.join(de_message)
        print("Message reçu :", message)



