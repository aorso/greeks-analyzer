

# plot_pricing.py

import numpy as np
import plotly.graph_objects as go
import copy

from option_models.asian_option import AsianOption
from option_models.vanilla_option import VanillaOption



class OptionGraph:
    def __init__(self, option, price_method, payoff_formula = None, expected_payoff = None):
        self.option = option
        self.price_method = price_method
        self.payoff_formula = payoff_formula
        self.expected_payoff = expected_payoff
        self.strike = option.strike




    def generate_spot_prices(self, factor=0.5):
        spot_min = self.strike * (1 - factor)
        spot_max = self.strike * (1 + factor)
        return np.linspace(spot_min, spot_max, 100)

    def generate_strike_prices(self, factor=0.5):
        strike_min = self.option.spot * (1 - factor)
        strike_max = self.option.spot * (1 + factor)
        return np.linspace(strike_min, strike_max, 100)

    def create_payoff_graph_vs_spot(self):
        option_copy = copy.deepcopy(self.option)  # Copie unique au début
        spot_prices = self.generate_spot_prices(factor=1.0)
        payoff_values = []





        for spot in spot_prices:
            option_copy.spot = spot  # Modification uniquement sur la copie
            payoff = self.payoff_formula(option_copy)
            payoff_values.append(payoff)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=spot_prices,
            y=payoff_values,
            mode='lines',
            name='Payoff vs Spot'
        ))

        fig.update_layout(
            title=f'{type(self.option).__name__} Payoff vs Spot Price (Strike: {self.strike})',
            xaxis_title='Spot Price',
            yaxis_title='Payoff',
            template='plotly_dark'
        )
        
        return fig

    def create_payoff_graph_vs_maturity(self, min_maturity=1, max_maturity=24, steps=100):
        option_copy = copy.deepcopy(self.option)  # Copie unique au début
        maturities = np.linspace(min_maturity, max_maturity, steps)
        payoff_values = []

        print("Le nombre de steps est :", steps)

        for maturity in maturities:
            option_copy.maturity = maturity  # Mise à jour de la maturité dans l'option
            payoff = option_copy.expected_payoff()  # Calcul du payoff avec la formule définie
            payoff_values.append(payoff)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=maturities,
            y=payoff_values,
            mode='lines',
            name='Payoff vs Maturity'
        ))

        fig.update_layout(
            title=f'{type(self.option).__name__} Payoff vs Maturity (Strike: {self.strike})',
            xaxis_title='Maturity (Months)',
            yaxis_title='Payoff',
            template='plotly_dark'
        )
        
        return fig

    def create_payoff_graph_vs_volatility(self, min_vol=0.05, max_vol=0.5, steps=100):
        option_copy = copy.deepcopy(self.option)  # Copie unique au début
        volatilities = np.linspace(min_vol, max_vol, steps)
        payoff_values = []

        print("Le nombre de steps est :", steps)

        for vol in volatilities:
            option_copy.volatility = vol  # Mise à jour de la volatilité dans l'option
            payoff = self.payoff_formula(option_copy)  # Calcul du payoff avec la formule définie
            payoff_values.append(payoff)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=volatilities,
            y=payoff_values,
            mode='lines',
            name='Payoff vs Volatility'
        ))

        fig.update_layout(
            title=f'{type(self.option).__name__} Payoff vs Volatility (Strike: {self.strike})',
            xaxis_title='Volatility',
            yaxis_title='Payoff',
            template='plotly_dark'
        )
        
        return fig

    def create_expected_payoff_vs_maturity(self, min_maturity=1, max_maturity=24, steps=100):
        """Crée un graphique du payoff attendu (expected payoff) pour une option digitale en fonction de la maturité."""
        option_copy = copy.deepcopy(self.option)  # Copie unique de l'option originale
        maturities = np.linspace(min_maturity, max_maturity, steps)
        expected_payoff_values = []

        for maturity in maturities:
            option_copy.maturity = maturity  # Mise à jour de la maturité dans l'instance de l'option
            expected_payoff = self.expected_payoff(option_copy)  # Utilisation de la méthode expected_payoff()
            expected_payoff_values.append(expected_payoff)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=maturities,
            y=expected_payoff_values,
            mode='lines',
            name='Expected Payoff vs Maturity'
        ))

        # Forcer l'affichage de l'axe Y avec une échelle adaptée
        fig.update_layout(
            title=f'{type(self.option).__name__} Expected Payoff vs Maturity (Strike: {self.strike})',
            xaxis_title='Maturity (Months)',
            yaxis_title='Expected Payoff',
            yaxis=dict(range=[min(expected_payoff_values) * 0.9, max(expected_payoff_values) * 1.1]),  # Ajustement automatique de l'échelle
            template='plotly_dark'
        )

        return fig

    




    def create_premium_graph_vs_spot(self):
        option_copy = copy.deepcopy(self.option)  # Copie unique au début
        spot_prices = self.generate_spot_prices(factor=1.0)
        premium_values = []

        for spot in spot_prices:
            option_copy.spot = spot  # Modification uniquement sur la copie
            premium = self.price_method(option_copy)  # Calcul du premium
            premium_values.append(premium)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=spot_prices,
            y=premium_values,
            mode='lines',
            name='Premium vs Spot'
        ))

        fig.update_layout(
            title=f'{type(self.option).__name__} Premium vs Spot Price (Strike: {self.strike})',
            xaxis_title='Spot Price',
            yaxis_title='Premium (Option Price)',
            template='plotly_dark'
        )
        
        return fig

    def create_premium_graph_vs_volatility(self, min_vol=0.05, max_vol=0.3, steps=100):
        """Crée un graphique du premium en fonction de la volatilité."""
        option_copy = copy.deepcopy(self.option)  # Copie unique au début
        volatilities = np.linspace(min_vol, max_vol, steps)
        premium_values = []

        for vol in volatilities:
            option_copy.volatility = vol  # Modification uniquement sur la copie
            premium = self.price_method(option_copy)  # Calcul du premium
            premium_values.append(premium)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=volatilities,
            y=premium_values,
            mode='lines',
            name='Premium vs Volatility'
        ))

        fig.update_layout(
            title=f'{type(self.option).__name__} Premium vs Volatility (Strike: {self.option.strike}, Spot: {self.option.spot})',
            xaxis_title='Volatility',
            yaxis_title='Premium (Option Price)',
            template='plotly_dark'
        )
        
        return fig

    def create_premium_graph_vs_maturity(self, min_maturity=1, max_maturity=24, steps=100):
        """Crée un graphique du premium (prix de l'option) en fonction de la maturité."""
        option_copy = copy.deepcopy(self.option)  # Copie unique au début
        maturities = np.linspace(min_maturity, max_maturity, steps)
        premium_values = []

        for maturity in maturities:
            option_copy.maturity = maturity  # Mise à jour de la maturité dans l'instance de l'option
            premium = self.price_method(option_copy)  # Calcul du premium avec la méthode de pricing
            premium_values.append(premium)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=maturities,
            y=premium_values,
            mode='lines',
            name='Premium vs Maturity'
        ))

        fig.update_layout(
            title=f'{type(self.option).__name__} Premium vs Maturity (Strike: {self.option.strike}, Spot: {self.option.spot})',
            xaxis_title='Maturity (Months)',
            yaxis_title='Premium (Option Price)',
            template='plotly_dark'
        )
        
        return fig
    
    def create_premium_3d_graph_spot_vol(self, min_spot_factor=0.5, max_spot_factor=1.5, 
                                     min_vol=0.05, max_vol=0.3, spot_steps=50, vol_steps=50):
        """Crée un graphique 3D du prix de l'option en fonction du Spot et de la Volatilité."""
        option_copy = copy.deepcopy(self.option)  # Copie unique de l'option originale

        # Génération des valeurs pour Spot et Volatility
        spot_prices = np.linspace(self.option.strike * min_spot_factor, self.option.strike * max_spot_factor, spot_steps)
        volatilities = np.linspace(min_vol, max_vol, vol_steps)

        # Création d'une grille pour le graphique 3D
        spot_grid, vol_grid = np.meshgrid(spot_prices, volatilities)
        premium_values = np.zeros_like(spot_grid)

        # Calcul du prix de l'option pour chaque couple (Spot, Volatility)
        for i in range(spot_grid.shape[0]):
            for j in range(spot_grid.shape[1]):
                option_copy.spot = spot_grid[i, j]  # Mise à jour du Spot
                option_copy.volatility = vol_grid[i, j]  # Mise à jour de la Volatilité
                premium_values[i, j] = self.price_method(option_copy)  # Calcul du prix

        # Création du graphique 3D avec Plotly
        fig = go.Figure(data=[go.Surface(z=premium_values, x=spot_grid, y=vol_grid, colorscale='Viridis')])

        fig.update_layout(
            title=f'{type(self.option).__name__} Price vs Spot & Volatility',
            scene=dict(
                xaxis_title='Spot Price',
                yaxis_title='Volatility',
                zaxis_title='Premium (Option Price)'
            ),
            template='plotly_dark'
        )

        return fig

