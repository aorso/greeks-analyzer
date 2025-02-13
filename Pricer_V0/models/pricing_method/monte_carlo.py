

#monte_carlo.py

import numpy as np
import pandas as pd

class MonteCarloPricer:

    @staticmethod
    def simulate_gbm_euler(S, T, r, sigma, q, num_paths, time_steps, seed=None):
        if seed is not None:
            np.random.seed(seed)

        dt = T / time_steps
        # Incréments brownien
        dW = np.random.randn(num_paths, time_steps) * np.sqrt(dt)
        
        # On calcule la somme cumulée des accroissements du log(S)
        log_increments = (r - q - 0.5 * sigma**2) * dt + sigma * dW
        log_S = np.cumsum(log_increments, axis=1) # On fait la somme cumulée sur chaque ligne (axis=1)
        log_S = np.log(S) + log_S  # On ajoute log(S) au début, pour « accrocher » la trajectoire au spot initial
        S_paths = np.exp(log_S) # Maintenant, exp pour repasser en niveau
        
        # Au lieu de partir directement à t=0, on ajoute la colonne initiale S
        S_paths = np.hstack((np.full((num_paths, 1), S), S_paths))
        
        return S_paths, dW

    @staticmethod
    def price_barrier(
        type_option, spot, strike, maturity, rate, volatility, dividend_yield,
        barrier_level, barrier_type, rebate=0.0,
        num_paths=500000, time_steps=200, seed=None):

        # 1) Simulation des trajectoires
        S_paths, _ = MonteCarloPricer.simulate_gbm_euler(
            S=spot, T=maturity, r=rate, sigma=volatility, q=dividend_yield,
            num_paths=num_paths, time_steps=time_steps, seed=seed)
        
        if "up" in barrier_type:
            crossed = np.any(S_paths >= barrier_level, axis=1)
        else:  # "down"
            crossed = np.any(S_paths <= barrier_level, axis=1)
        

        # 2) Vérification du franchissement de la barrière
        final_underlyings = S_paths[:, -1]  # Dernier point de chaque trajectoire simulée

        if "call" in type_option:
            vanilla_payoffs = np.maximum(final_underlyings - strike, 0.0)
        else:  # "put"
            vanilla_payoffs = np.maximum(strike - final_underlyings, 0.0)
  
        # 4) Application de la condition knock-in / knock-out + rebate
        payoffs = vanilla_payoffs.copy() 
        if "in" in barrier_type:
            payoffs[~crossed] = rebate
        else:
            payoffs[crossed] = rebate

        # Actualisation et calcul du prix
        discounted_payoffs = np.exp(-rate * maturity) * payoffs
        price = np.mean(discounted_payoffs)
        return price

    @staticmethod
    def price_asian(
        type_option, spot, strike, maturity, rate, volatility, dividend_yield,
        average_type, observation_frequency, num_paths = 50000, time_steps=200, seed=None
    ):
    
        if maturity > 1.8:
            time_steps = 500
        

        # Simulation des trajectoires du sous-jacent
        S_paths, _  = MonteCarloPricer.simulate_gbm_euler(spot, maturity, rate, volatility, dividend_yield, num_paths, time_steps, seed)

        # Sélection des points d'observation en fonction de la fréquence
        if observation_frequency == 'daily':
            num_observations = round(maturity * 365)
        elif observation_frequency == 'weekly':
            num_observations = round(maturity * 52)
        elif observation_frequency == 'monthly':
            num_observations = round(maturity * 12)
        else:
            raise ValueError("frequency must be 'daily', 'weekly', or 'monthly'.")

        observation_indices = np.linspace(0, time_steps, num_observations, endpoint=False, dtype=int)
        observed_prices = S_paths[:, observation_indices]


        # Calcul de la moyenne selon le type spécifié
        if average_type == "arithmetic":
            averages = np.mean(observed_prices, axis=1)
        elif average_type == "geometric":
            averages = np.exp(np.mean(np.log(observed_prices), axis=1))
        else:
            raise ValueError("average_type must be 'arithmetic' or 'geometric'.")

        # Calcul des payoffs
        if type_option == "call":
            payoffs = np.maximum(averages - strike, 0)
        else:  # put
            payoffs = np.maximum(strike - averages, 0)

        # Actualisation du payoff
        return np.exp(-rate * maturity) * np.mean(payoffs)

    @staticmethod
    def price_lookback(
        type_option, spot, strike, maturity, rate, volatility, dividend_yield,
        strike_type, num_paths=500000, time_steps=200, seed=None
    ):
 
        # Simulation des trajectoires du sous-jacent
        S_paths, _  = MonteCarloPricer.simulate_gbm_euler(spot, maturity, rate, volatility, dividend_yield, num_paths, time_steps, seed)

        # Extraction des valeurs min/max de chaque trajectoire
        min_S = np.min(S_paths, axis=1)
        max_S = np.max(S_paths, axis=1)
        final_S = S_paths[:, -1]

        # Pricing en fonction du type de lookback (strike fixe ou flottant)
        if strike_type == "fixed":
            if type_option == "call":
                payoffs = np.maximum(max_S - strike, 0)
            else:  # Put
                payoffs = np.maximum(strike - min_S, 0)
        elif strike_type == "floating":
            if type_option == "call":
                payoffs = np.maximum(final_S - min_S, 0)
            else:  # Put
                payoffs = np.maximum(max_S - final_S, 0)
        else:
            raise ValueError("strike_type must be 'fixed' or 'floating'.")

        # Actualisation du payoff
        return np.exp(-rate * maturity) * np.mean(payoffs)



