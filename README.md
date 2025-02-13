# Option Pricer - WIP 🚧

Ce dépôt GitHub contient un projet **en cours de développement**, destiné à devenir un **Pricer d'options** complet avec une interface interactive en **Streamlit**. Le but est d’offrir un outil pour :

- **Pricer différents types d'options** : options vanilles (européennes et américaines), options exotiques (barrières, asiatiques, lookback), ainsi que des produits structurés comme les autocalls.
- **Visualiser les Grecs** associés (Delta, Gamma, Vega, Theta, Rho) grâce à **des graphiques interactifs**.
- **Explorer les stratégies d'options** : call spread, put spread, straddle, butterfly, etc.

### ⚠️ État Actuel du Projet
Pour l'instant, ce dépôt est surtout une **base de code en construction**. L'application Streamlit n'est pas encore finalisée, mais elle intégrera prochainement :
- Une interface complète pour ajuster les paramètres (prix, volatilité, taux d'intérêt) et observer l'impact sur le pricing et les Grecs.
- Des outils d’analyse graphique interactifs.
- Une optimisation des méthodes de pricing Monte Carlo pour accélérer les calculs.

### 🚀 Tester le Pricer

Si vous souhaitez tester le pricer, vous pouvez facilement le faire en suivant ces étapes :  
1. **Téléchargez le projet** 
2. **Activez l'environnement virtuel** (si nécessaire) et assurez-vous d'avoir installé les dépendances  
3. **Lancez le fichier de test** `test (price and greek).ipynb` :  
- Ouvrez le fichier dans un notebook Jupyter.  
- **Renseignez vos propres valeurs** (prix de l’actif, volatilité, taux d’intérêt, maturité, etc.).  
- Exécutez les cellules pour obtenir les résultats du pricing et des Grecs.



### 📂 Structure du Code
. ├── models 

│ ├── option_models # Modèles pour les options (Vanilla, Barrier, Asian, etc.) 

│ ├── greek_method # Méthodes pour le calcul des Grecs 

│ ├── pricing_method # Méthodes de pricing (Black-Scholes, Monte Carlo, arbres binomiaux) 

│ └── plot_tools # Visualisation avec Plotly et Streamlit 

├── strategy_tools # Analyse de stratégies d'options (straddle, strangle, butterfly, etc.) 

└── test # Notebooks de test

### Prochaines Étapes
- **Finaliser l'interface Streamlit.**
- **Optimiser les calculs Monte Carlo.**
- **Ajouter plus de stratégies d'options.**

### ❗ Note Importante
Ce dépôt est pour l’instant une version **non finalisée**, mise en ligne temporairement en attendant l’intégration complète des fonctionnalités. 

Merci de votre compréhension !
