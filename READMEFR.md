# Outil de Filigranage et Combinaison de Documents PDF

Cet outil applique automatiquement des filigranes aux fichiers PDF provenant de plusieurs dossiers (représentant différentes personnes) et les combine en un seul document principal avec une page de titre, une table des matières, des signets et des pages de séparation pour une navigation facile.

## Fonctionnalités

- 🔒 **Filigranage** : Ajoute des filigranes personnalisables à tous les fichiers PDF
- 📑 **Combinaison Intelligente** : Combine tous les PDF en un seul document
- 📋 **Table des Matières** : Générée automatiquement avec des liens cliquables
- 🔖 **Signets** : Signets PDF pour une navigation facile
- 🏷️ **Pages de Séparation** : Séparation claire entre les documents de différentes personnes
- ⚙️ **Configuration** : Configuration JSON optionnelle pour l'ordre personnalisé et les alias
- 🔄 **Adaptation Automatique** : Le texte du filigrane s'adapte automatiquement à la largeur de la page

## Installation

### Windows (PowerShell)
```powershell
.\setup_environment.ps1
```

### Windows (Invite de Commandes)
```cmd
setup_environment.bat
```

### Linux/macOS (Bash)
```bash
./setup_environment.sh
```

Ces scripts vont :
1. Créer un environnement virtuel Python
2. Installer les dépendances requises (reportlab, PyPDF2, PyCryptodome)
3. Configurer l'environnement pour une utilisation immédiate

## Structure du Dossier d'Entrée

Créez votre dossier d'entrée avec la structure suivante :

```
VotreDossierDEntree/
├── Personne1/
│   ├── Document1.pdf
│   ├── Document2.pdf
│   └── ...
├── Personne2/
│   ├── Document1.pdf
│   ├── Document2.pdf
│   └── ...
├── Personne3/
│   └── ...
└── generation.json (optionnel)
```

### Notes Importantes :
- Chaque sous-dossier représente une personne
- Les fichiers PDF doivent suivre la convention de nommage : `TypeDocument-AutresInfos.pdf`
- La partie avant le premier `-` sera utilisée comme nom du document dans la table des matières
- Les underscores (`_`) dans les noms de documents seront remplacés par des espaces

### Exemples de Nommage de Documents :
- `CNI-Jean.pdf` → "CNI"
- `RIB-CompteBancaire.pdf` → "RIB"
- `Contrat_Travail-2024.pdf` → "Contrat Travail"

## Configuration Optionnelle (generation.json)

Créez un fichier `generation.json` dans votre dossier d'entrée pour personnaliser :

```json
{
    "Personne1": {
        "alias": "Jean DUPONT",
        "order": 1
    },
    "Personne2": {
        "alias": "Jeanne MARTIN", 
        "order": 2
    },
    "Personne3": {
        "alias": "Pierre BERNARD",
        "order": 3
    }
}
```

### Options de Configuration :
- **`alias`** : Nom d'affichage pour la personne (affiché dans la table des matières et les signets)
- **`order`** : Ordre de traitement (nombres plus bas = traités en premier)

Sans configuration, les dossiers sont traités par ordre alphabétique en utilisant les noms de dossiers.

## Utilisation

### Utilisation de Base
```bash
python generate_loc_file.py -s ./DossierEntree
```

### Avec Filigrane Personnalisé
```bash
python generate_loc_file.py -s ./DossierEntree -w "CONFIDENTIEL - DEMANDE DE LOCATION"
```

### Avec Titre Personnalisé
```bash
python generate_loc_file.py -s ./DossierEntree -t "Documents Location Famille Dupont"
```

### Exemple Complet
```bash
python generate_loc_file.py -s ./DocsLocation -w "RESERVE POUR LOCATION APPARTEMENT" -t "Dossier Complet de Location - Famille Dupont"
```

### Options de Ligne de Commande

| Option | Court | Description | Défaut |
|--------|-------|-------------|---------|
| `--source` | `-s` | Chemin du dossier d'entrée | **Requis** |
| `--watermark` | `-w` | Texte du filigrane | "DOCUMENT RESERVE A LA LOCATION" |
| `--title` | `-t` | Titre du document | "Dossier de Location" |

## Sortie

L'outil génère un seul fichier PDF nommé d'après votre titre (ex: `Documents_Location_Famille_Dupont.pdf`) contenant :

1. **Page de Titre** - Affiche le titre du document et la date de génération
2. **Table des Matières** - Liens cliquables vers toutes les sections
3. **Pages de Séparation** - Une par personne avec "NomPersonne - Documents"
4. **Documents** - Tous les PDF filigranés organisés par personne (par ordre alphabétique dans chaque personne)

### Fonctionnalités de Navigation :
- **Table des Matières Cliquable** : Cliquez sur n'importe quelle entrée pour aller à cette page
- **Signets PDF** : Utilisez le panneau de signets de votre lecteur PDF
- **Pages de Séparation** : Pauses visuelles entre les documents de différentes personnes

## Dépannage

### Problèmes Courants :

1. **"Aucun fichier PDF trouvé"**
   - Vérifiez que les fichiers PDF sont dans des sous-dossiers, pas dans le dossier racine d'entrée
   - Assurez-vous que les fichiers ont l'extension `.pdf`

2. **"PyCryptodome requis"**
   - Certains PDF chiffrés nécessitent un déchiffrement supplémentaire
   - Essayez avec des versions non chiffrées des PDF

3. **Texte de filigrane trop grand**
   - L'outil réduit automatiquement la taille de la police
   - Un texte très long peut être tronqué avec "..."

4. **Mauvais ordre de traitement**
   - Vérifiez la syntaxe de votre fichier `generation.json`
   - Assurez-vous que les noms de dossiers correspondent exactement (sensible à la casse)

### Dossiers Exclus :
Les dossiers suivants sont automatiquement exclus du traitement :
- `Dossier Location`
- `protected_files`
- `temp_watermarked`

## Prérequis

- Python 3.7+
- reportlab
- PyPDF2
- PyCryptodome

## Licence

Licence MIT

Copyright (c) 2025

La permission est accordée, gratuitement, à toute personne obtenant une copie
de ce logiciel et des fichiers de documentation associés (le "Logiciel"), de traiter
le Logiciel sans restriction, y compris sans limitation les droits
d'utiliser, copier, modifier, fusionner, publier, distribuer, sous-licencier et/ou vendre
des copies du Logiciel, et de permettre aux personnes à qui le Logiciel est
fourni de le faire, sous réserve des conditions suivantes :

L'avis de copyright ci-dessus et cet avis de permission doivent être inclus dans toutes
les copies ou parties substantielles du Logiciel.

LE LOGICIEL EST FOURNI "EN L'ÉTAT", SANS GARANTIE D'AUCUNE SORTE, EXPRESSE OU
IMPLICITE, Y COMPRIS MAIS SANS S'Y LIMITER LES GARANTIES DE QUALITÉ MARCHANDE,
D'ADÉQUATION À UN USAGE PARTICULIER ET DE NON-CONTREFAÇON. EN AUCUN CAS LES
AUTEURS OU DÉTENTEURS DU COPYRIGHT NE POURRONT ÊTRE TENUS RESPONSABLES DE TOUTE RÉCLAMATION,
DOMMAGES OU AUTRE RESPONSABILITÉ, QUE CE SOIT DANS UNE ACTION DE CONTRAT, DE DÉLIT OU AUTRE,
DÉCOULANT DE, OU EN RELATION AVEC LE LOGICIEL OU L'UTILISATION OU D'AUTRES DEALINGS DANS LE
LOGICIEL.
