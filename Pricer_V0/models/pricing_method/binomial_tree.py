
#binomial_tree.py

import math
import numpy as np

class BinomialTreePricer:
    @staticmethod
    def price_vanilla_american(S, K, T, r, sigma, q=0, option_type="call", steps=500, american=False): 
        dt = T / steps
        u = math.exp(sigma * math.sqrt(dt))
        d = 1 / u
        p = (math.exp((r - q) * dt) - d) / (u - d)

        if not (0 <= p <= 1):
            raise ValueError(f"Probabilité neutre au risque invalide : p={p}")

        prices = np.zeros((steps + 1, steps + 1))
        prices[0, 0] = S

        for i in range(1, steps + 1):
            prices[i, 0] = prices[i-1, 0] * u
            for j in range(1, i + 1):
                prices[i, j] = prices[i-1, j-1] * d

        option_values = np.zeros((steps + 1, steps + 1))
        for j in range(steps + 1):
            if option_type == "call":
                option_values[steps, j] = max(0, prices[steps, j] - K)
            elif option_type == "put":
                option_values[steps, j] = max(0, K - prices[steps, j])

        for i in range(steps - 1, -1, -1):
            for j in range(i + 1):
                continuation_value = math.exp(-r * dt) * (p * option_values[i+1, j] + (1 - p) * option_values[i+1, j+1])
                if option_type == "call":
                    intrinsic_value = max(0, prices[i, j] - K)
                else:  # put
                    intrinsic_value = max(0, K - prices[i, j])

                if american:
                    option_values[i, j] = max(continuation_value, intrinsic_value)
                else:
                    option_values[i, j] = continuation_value

        return option_values[0, 0]

    @staticmethod
    def price_barrier_binomial(
        type_option, spot, strike, maturity, rate, volatility, dividend_yield,
        barrier_level, barrier_type, rebate=0.0,
        steps=200):

        # Initialisation des paramètres de l'arbre binomial
        dt = maturity / steps
        u = np.exp(volatility * np.sqrt(dt))  # Facteur de hausse
        d = 1 / u                             # Facteur de baisse
        p = (np.exp((rate - dividend_yield) * dt) - d) / (u - d)  # Probabilité neutre au risque
        
        # Initialisation des matrices pour les prix du sous-jacent et les payoffs
        prices = np.zeros((steps + 1, steps + 1))
        prices[0, 0] = spot

        for i in range(1, steps + 1):
            for j in range(i + 1):
                prices[j, i] = spot * (u ** (i - j)) * (d ** j)

        # Calcul des payoffs à maturité (vanilla)
        payoffs = np.zeros(steps + 1)
        if "call" in type_option:
            payoffs = np.maximum(prices[:, steps] - strike, 0.0)
        else:
            payoffs = np.maximum(strike - prices[:, steps], 0.0)

        # Backward induction en tenant compte de la barrière
        for i in range(steps - 1, -1, -1):
            for j in range(i + 1):
                # Actualisation des payoffs
                payoffs[j] = np.exp(-rate * dt) * (p * payoffs[j] + (1 - p) * payoffs[j + 1])

                # Condition de barrière (knock-in / knock-out)
                if "up" in barrier_type and prices[j, i] >= barrier_level:
                    if "in" in barrier_type:
                        payoffs[j] = payoffs[j]  # Knock-in : conserver le payoff
                    else:
                        payoffs[j] = rebate     # Knock-out : appliquer le rebate
                elif "down" in barrier_type and prices[j, i] <= barrier_level:
                    if "in" in barrier_type:
                        payoffs[j] = payoffs[j]  # Knock-in : conserver le payoff
                    else:
                        payoffs[j] = rebate     # Knock-out : appliquer le rebate

        # Retourner le prix de l'option
        return payoffs[0]

    @staticmethod
    def price_autocall(spot, strike, maturity, rate, volatility, dividend_yield,
                       coupon, barrier, protection_barrier,
                       type_autocall='athena', frequency_per_year= "'semi-annual'", steps=500, memory_feature=True):
  
        dt = maturity / steps
        u = np.exp(volatility * np.sqrt(dt))
        d = 1 / u
        p = (np.exp((rate - dividend_yield) * dt) - d) / (u - d)

        # Construction de l'arbre des prix
        prices = np.zeros((steps + 1, steps + 1))
        for i in range(steps + 1):
            for j in range(i + 1):
                prices[j, i] = spot * (u ** (i - j)) * (d ** j)

        # Initialisation des payoffs et mémoire des coupons
        payoffs = np.zeros(steps + 1)
        coupon_memory = [0] * (steps + 1) if memory_feature else None

        # Calcul des dates d'observation
        observation_dates = BinomialTreePricer.calculate_observation_dates(maturity, frequency_per_year, dt, steps)
        
        # Backward induction
        for i in range(steps, -1, -1):
            t = i * dt
            discount_factor = np.exp(-rate * t)  # Calculé une seule fois par étape
            df_step = np.exp(-rate * dt)  # Facteur d'actualisation pour une étape

            if i == steps:  # Échéance finale
                for j in range(i + 1):
                    payoffs[j] = prices[j, i] / spot if prices[j, i] < protection_barrier else 1.0
                continue

            new_payoffs = np.zeros(i + 1)
            new_coupon_memory = [0] * (i + 1) if memory_feature else None

            for j in range(i + 1):
                continuation = df_step * (p * payoffs[j] + (1 - p) * payoffs[j + 1])
                
                if i in observation_dates:
                    current_coupon_mem = coupon_memory[j] if memory_feature else None
                    payoff_val, new_coupon = BinomialTreePricer.calculate_payoff(
                        prices[j, i], continuation, coupon, barrier, discount_factor,
                        type_autocall, memory_feature, current_coupon_mem
                    )
                    new_payoffs[j] = payoff_val
                    if memory_feature:
                        new_coupon_memory[j] = new_coupon
                else:
                    new_payoffs[j] = continuation
                    if memory_feature:
                        new_coupon_memory[j] = p * coupon_memory[j] + (1 - p) * coupon_memory[j + 1]

            payoffs = new_payoffs
            if memory_feature:
                coupon_memory = new_coupon_memory

        return payoffs[0]

    @staticmethod
    def calculate_observation_dates(maturity, frequency, dt, steps):

        frequency_map = {
            'annual': 1,
            'semi-annual': 2,
            'quarterly': 4,
            'monthly': 12
        }

        if frequency not in frequency_map:
            raise ValueError("Invalid frequency. Choose from 'annual', 'semi-annual', 'quarterly', 'monthly'.")

        num_observations = int(maturity * frequency_map[frequency])
        observation_dates = np.linspace(0, maturity, num_observations + 1)[1:]
        obs_indices = [min(steps, int(round(t / dt + 1e-8))) for t in observation_dates]

        return sorted(set(obs_indices))

    @staticmethod
    def calculate_payoff(price, continuation, coupon, barrier, discount_factor, type_autocall, memory_feature, current_coupon_mem):
        if price >= barrier:
            if memory_feature and type_autocall == 'phenix':
                total = (1 + current_coupon_mem + coupon)
                return total * discount_factor, 0  # Reset mémoire après paiement
            else:
                return (1 + coupon) * discount_factor, None
        else:
            if memory_feature:
                return continuation, current_coupon_mem + coupon
            else:
                return continuation, None
