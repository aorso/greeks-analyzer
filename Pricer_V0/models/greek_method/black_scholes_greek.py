
# black_scholes_greek.py

import numpy as np
from scipy.stats import norm
from option_models.option import Option

class BlackScholesGreek:
    def __init__(self, option: Option):
        self.option = option

    @staticmethod
    def bs_greeks(S, K, T, r, sigma, q, option_type):
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        # Delta
        if option_type == "call":
            delta = np.exp(-q * T) * norm.cdf(d1)
        elif option_type == "put":
            delta = np.exp(-q * T) * (norm.cdf(d1) - 1)

        # Gamma (indépendant du type d'option)
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T)) * np.exp(-q * T)

        # Vega (indépendant du type d'option)
        vega = S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)

        # Theta
        if option_type == "call":
            theta = (-S * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                     - r * K * np.exp(-r * T) * norm.cdf(d2)
                     + q * S * np.exp(-q * T) * norm.cdf(d1))
        elif option_type == "put":
            theta = (-S * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                     + r * K * np.exp(-r * T) * norm.cdf(-d2)
                     - q * S * np.exp(-q * T) * norm.cdf(-d1))

        # Rho
        if option_type == "call":
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == "put":
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

        return {
        "Delta": float(delta),
        "Gamma": float(gamma), 
        "Vega": float(vega),
        "Theta": float(theta),
        "Rho": float(rho),
    }


class QuantoGreek:
    @staticmethod
    def bs_greeks_quanto(S, K, T, r, sigma, q, fx_rate_volatility, fx_correlation, option_type):

        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        # Delta
        if option_type == "call":
            delta = np.exp(-q * T) * norm.cdf(d1)
        elif option_type == "put":
            delta = np.exp(-q * T) * (norm.cdf(d1) - 1)

        # Gamma
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T)) * np.exp(-q * T)

        # Vega
        vega = S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)

        # Theta
        if option_type == "call":
            theta = (-S * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                     - r * K * np.exp(-r * T) * norm.cdf(d2)
                     + q * S * np.exp(-q * T) * norm.cdf(d1))
        elif option_type == "put":
            theta = (-S * np.exp(-q * T) * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                     + r * K * np.exp(-r * T) * norm.cdf(-d2)
                     - q * S * np.exp(-q * T) * norm.cdf(-d1))

        # Rho
        if option_type == "call":
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == "put":
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

        # Cross-Gamma
        cross_gamma = -fx_correlation * S * fx_rate_volatility * sigma / (sigma**2)

        # Vanna
        vanna = S * np.sqrt(T) * (1 - fx_correlation)

        # Charm
        charm = -S * sigma * np.sqrt(T) * 0.5

        # Dual Delta
        dual_delta = -np.exp(-r * T) * norm.cdf(-d2)

        # Lambda (Elasticité)
        lambda_value = (S / (S * np.exp(-q * T) * norm.cdf(d1))) * delta if delta != 0 else 0

        return {
            "Delta": float(delta),
            "Gamma": float(gamma),
            "Vega": float(vega),
            "Theta": float(theta),
            "Rho": float(rho),
            "Cross-Gamma": float(cross_gamma),
            "Vanna": float(vanna),
            "Charm": float(charm),
            "Dual Delta": float(dual_delta),
            "Lambda": float(lambda_value)
        }
    


class DigitGreek:
    @staticmethod
    def bs_greeks_digit(S, K, T, r, sigma, q, cash_payout, type_option, barrier=None, barrier_type=None):

        d2 = (np.log(S / K) + (r - q - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        pdf_d2 = norm.pdf(d2)
        
        # Prix de base sans barrière
        base_price = cash_payout * np.exp(-r * T)

        # Delta
        delta = (base_price / (S * sigma * np.sqrt(T))) * pdf_d2

        # Gamma
        gamma = (-delta / S) * (d2 / (S * sigma * np.sqrt(T)) + 1)

        # Vega
        vega = -base_price * pdf_d2 * d2 / sigma

        # Theta
        theta = -base_price * pdf_d2 * (d2 / (2 * T) + r)

        # Rho
        rho = -cash_payout * T * np.exp(-r * T) * norm.cdf(d2) if type_option == "call" else \
              cash_payout * T * np.exp(-r * T) * norm.cdf(-d2)

        # Gestion des barrières (prix = 0 si la barrière est franchie)
        if barrier:
            if (barrier_type == "up" and S >= barrier) or (barrier_type == "down" and S <= barrier):
                delta = gamma = vega = theta = rho = 0.0

        return {
            "Delta": float(delta),
            "Gamma": float(gamma),
            "Vega": float(vega),
            "Theta": float(theta),
            "Rho": float(rho)
        }
