# monte_carlo_greek.py
import numpy as np
from pricing_method.monte_carlo import MonteCarloPricer

class MonteCarloGreek:
    def __init__(self, option):
        self.option = option

    @staticmethod
    def montecarlo_asian_greeks(type_option, spot, strike, maturity, rate, volatility, dividend_yield, average_type, observation_frequency, num_paths=100_000, time_steps=100, seed=None):
        S_paths, W_shocks = MonteCarloPricer.simulate_gbm_euler(
            S=spot, T=maturity, r=rate, sigma=volatility, q=dividend_yield,
            num_paths=num_paths, time_steps=time_steps, seed=seed
        )
        
        dt = maturity / time_steps
        discount_factor = np.exp(-rate * maturity)

        if observation_frequency == 'daily':
            num_obs = round(maturity * 365)
        elif observation_frequency == 'weekly':
            num_obs = round(maturity * 52)
        elif observation_frequency == 'monthly':
            num_obs = round(maturity * 12)
        else:
            raise ValueError("La fréquence doit être 'daily', 'weekly', ou 'monthly'.")
        num_obs = min(num_obs, time_steps)
        obs_indices = np.linspace(0, time_steps, num_obs, endpoint=False, dtype=int)
        observed_prices = S_paths[:, obs_indices]

        if average_type == "arithmetic":
            avg_values = np.mean(observed_prices, axis=1)
        else:  # "geometric"
            avg_values = np.exp(np.mean(np.log(observed_prices), axis=1))

        intrinsic_payoff = np.maximum(avg_values - strike, 0.0) if type_option == "call" else np.maximum(strike - avg_values, 0.0)
        payoff = discount_factor * intrinsic_payoff

        partial_avg = (
            np.sum(observed_prices / spot, axis=1) / observed_prices.shape[1]
            if average_type == "arithmetic" else avg_values / spot
        )
        indicator_itm = (intrinsic_payoff > 0).astype(float)
        delta_samples = discount_factor * indicator_itm * (partial_avg if type_option == "call" else -partial_avg)
        delta = np.mean(delta_samples)

        sum_W = np.sum(W_shocks, axis=1)
        vega_samples = payoff * (sum_W / volatility - volatility * maturity)
        vega = np.mean(vega_samples)

        theta_score = ((sum_W * (rate - dividend_yield - 0.5 * volatility**2) / volatility**2) - (rate * maturity / volatility))
        theta_samples = payoff * theta_score
        theta = -np.mean(theta_samples)

        rho_samples = payoff * maturity
        rho = np.mean(rho_samples)

        gamma_samples = -discount_factor * indicator_itm * (avg_values / (spot ** 2))
        gamma = np.mean(gamma_samples)

        return {
            "Delta": float(delta),
            "Gamma": float(gamma),
            "Vega": float(vega),
            "Theta": float(theta),
            "Rho": float(rho),
        }

    @staticmethod
    def montecarlo_lookback_greeks(type_option, spot, strike, maturity, rate, volatility, dividend_yield, strike_type, num_paths=100_000, time_steps=100, seed=None):
        """ Calcule les grecques pour une option lookback en utilisant Monte Carlo """
        # 1) Simulation des trajectoires et chocs brownien
        S_paths, dW = MonteCarloPricer.simulate_gbm_euler(
            S=spot, T=maturity, r=rate, sigma=volatility, q=dividend_yield,
            num_paths=num_paths, time_steps=time_steps, seed=seed
        )

        # Préparation des constantes
        dt = maturity / time_steps
        discount = np.exp(-rate * maturity)

        # 2) Calcul de l'extrême (min/max) selon le type d'option
        if strike_type == 'floating':
            observed_extreme = np.min(S_paths, axis=1) if type_option == 'call' else np.max(S_paths, axis=1)
            strike = observed_extreme
        else:
            strike = strike

        # 3) Calcul du payoff
        payoff_intrinsic = np.maximum(S_paths[:, -1] - strike, 0.0) if type_option == 'call' else np.maximum(strike - S_paths[:, -1], 0.0)
        payoff = discount * payoff_intrinsic

        # 4) Delta (Pathwise)
        delta_pathwise = discount * ((S_paths[:, -1] > strike).astype(float) * (S_paths[:, -1] / spot))
        Delta = np.mean(delta_pathwise)

        # 5) Vega (Likelihood Ratio)
        normalized_sum_dW = np.sum(dW, axis=1) / np.sqrt(time_steps)
        likelihood_vega = (normalized_sum_dW / volatility) - volatility * maturity
        Vega = np.mean(payoff * likelihood_vega)

        # 6) Theta (Likelihood Ratio)
        theta_score = np.where(volatility > 1e-6, (normalized_sum_dW * (rate - dividend_yield - 0.5 * volatility**2) / volatility**2) - (rate * maturity / volatility), 0.0)
        Theta = -np.mean(payoff * theta_score)

        # 7) Rho (Pathwise)
        rho_samples = payoff * maturity
        Rho = np.mean(rho_samples)

        # 8) Gamma (Pathwise)
        gamma_pathwise = -discount * ((payoff_intrinsic / (spot ** 2)) * (spot > 1e-6))
        Gamma = np.mean(gamma_pathwise)

        return {
            "Delta": float(Delta),
            "Gamma": float(Gamma),
            "Vega": float(Vega),
            "Theta": float(Theta),
            "Rho": float(Rho),
        }
