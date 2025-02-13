
# black_scholes.py

import numpy as np
from scipy.stats import norm
from option_models.option import Option

class BlackScholesPricer:
    def __init__(self, option: Option):
        self.option = option

    def price(S, K, T, r, sigma, q, option_type):
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == "call":
            price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == "put":
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
        return price
        


    def implied_volatility(self, market_price: float, tol=1e-6, max_iter=200):
        S = self.option.spot
        K = self.option.strike
        T = self.option.maturity
        r = self.option.rate

        # Fixer des limites raisonnables pour la volatilité implicite
        sigma_min = 0.001  # 0.1% de volatilité minimale
        sigma_max = 5.0    # 500% de volatilité maximale
        sigma = 0.2        # Volatilité initiale (20%)

        for i in range(max_iter):
            # Calcul du prix avec la volatilité actuelle
            self.option.volatility = sigma
            price = self.price()

            # Calcul de la différence (erreur)
            diff = price - market_price

            # Si l'erreur est suffisamment petite, retourner la volatilité
            if abs(diff) < tol:
                return sigma

            # Calcul de Vega
            vega = self.calculate_greeks()["Vega"]

            # Si Vega est trop faible, basculer sur la méthode de dichotomie
            if abs(vega) < tol:
                return self._implied_volatility_bisection(market_price, sigma_min, sigma_max, tol, max_iter)

            # Mise à jour de sigma avec Newton-Raphson
            sigma -= diff / vega

            # S'assurer que sigma reste dans les limites définies
            sigma = max(sigma_min, min(sigma, sigma_max))

        # Si la convergence échoue avec Newton-Raphson, basculer sur la dichotomie
        return self._implied_volatility_bisection(market_price, sigma_min, sigma_max, tol, max_iter)

    def _implied_volatility_bisection(self, market_price: float, sigma_min: float, sigma_max: float, tol: float, max_iter: int):
        for i in range(max_iter):
            sigma_mid = (sigma_min + sigma_max) / 2
            self.option.volatility = sigma_mid
            price = self.price()

            # Calcul de l'erreur
            diff = price - market_price

            # Si l'erreur est suffisamment petite, retourner la volatilité
            if abs(diff) < tol:
                return sigma_mid

            # Mise à jour des bornes
            if price < market_price:
                sigma_min = sigma_mid
            else:
                sigma_max = sigma_mid

        # Retourne la volatilité moyenne si la convergence n'est pas parfaite
        return (sigma_min + sigma_max) / 2


    def price_with_iv(self, implied_volatility: float):
        self.option.volatility = implied_volatility
        return self.price()