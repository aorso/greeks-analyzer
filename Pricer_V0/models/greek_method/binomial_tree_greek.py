# binomial_tree_greek.py
import math
import numpy as np
from pricing_method.binomial_tree import BinomialTreePricer
from concurrent.futures import ThreadPoolExecutor


class BinomialTreeGreek:
    def __init__(self, option):
        self.option = option
    @staticmethod
    def binomial_american_greeks(S, K, T, r, sigma, q, option_type, steps=100, dS_rel=0.01, dSigma_rel=0.01, dR_rel=0.01, dT=1/365):

        params = {"spot": S, "strike": K, "maturity": T, "rate": r, "volatility": sigma, "dividend_yield": q}

        price_0 = BinomialTreePricer.price_vanilla_american(S, K, T, r, sigma, q, option_type, steps, american=True)

        def bumped_price(param_name, bump):
            original_value = params[param_name]
            params[param_name] = original_value + bump
            bumped_price = BinomialTreePricer.price_vanilla_american(
                params["spot"], params["strike"], params["maturity"], params["rate"], params["volatility"],
                params["dividend_yield"], option_type, steps, american=True
            )
            params[param_name] = original_value  # Rétablir la valeur d'origine
            return bumped_price

        
        dS = S * dS_rel
        delta = (bumped_price("spot", dS) - bumped_price("spot", -dS)) / (2 * dS)
        gamma = (bumped_price("spot", dS) - 2 * price_0 + bumped_price("spot", -dS)) / (dS ** 2)

        dSigma = sigma * dSigma_rel
        vega = (bumped_price("volatility", dSigma) - price_0) / dSigma

        dR = r * dR_rel
        rho = (bumped_price("rate", dR) - price_0) / dR

        price_T_down = bumped_price("maturity", -dT)
        theta = (price_T_down - price_0) / (-dT)

        return {
            "Delta": float(delta),
            "Gamma": float(gamma), 
            "Vega": float(vega),
            "Theta": float(theta),
            "Rho": float(rho),
        }



    @staticmethod
    def binomial_barrier_greeks(S, K, T, r, sigma, q, option_type, barrier_level, barrier_type, rebate=0, steps=100, dS_rel=0.01, dSigma_rel=0.01, dR_rel=0.01, dT=1/365):
    
        params = {
            "spot": S,
            "strike": K,
            "maturity": T,
            "rate": r,
            "volatility": sigma,
            "dividend_yield": q,
            "barrier_level": barrier_level,
            "barrier_type": barrier_type,
            "rebate": rebate
        }


        price_0 = BinomialTreePricer.price_barrier_binomial(option_type, S, K, T, r, sigma, q, barrier_level, barrier_type, rebate, steps)
        
        def bumped_price(param_name, bump):
            """ Calcule le prix après avoir modifié un paramètre donné """
            original_value = params[param_name]
            params[param_name] = original_value + bump
            bumped_price = BinomialTreePricer.price_barrier_binomial(
                option_type,
                params["spot"], params["strike"], params["maturity"], params["rate"],
                params["volatility"], params["dividend_yield"],
                params["barrier_level"], params["barrier_type"], params["rebate"],
                steps
            )
            params[param_name] = original_value  # Restaurer la valeur originale
            return bumped_price

        # Calcul des grecques
        dS = S * dS_rel
        delta = (bumped_price("spot", dS) - bumped_price("spot", -dS)) / (2 * dS)
        gamma = (bumped_price("spot", dS) - 2 * price_0 + bumped_price("spot", -dS)) / (dS ** 2)
        
        dSigma = sigma * dSigma_rel
        vega = (bumped_price("volatility", dSigma) - price_0) / dSigma
        
        dR = r * dR_rel
        rho = (bumped_price("rate", dR) - price_0) / dR
        
        price_T_down = bumped_price("maturity", -dT)
        theta = (price_T_down - price_0) / (-dT)

        # Retourner les grecques
        return {
            "Delta": float(delta),
            "Gamma": float(gamma),
            "Vega": float(vega),
            "Theta": float(theta),
            "Rho": float(rho),
        }


    @staticmethod
    def binomial_autocall_greeks(spot, strike, maturity, rate, volatility, dividend_yield,
                                  coupon, barrier, protection_barrier, type_autocall='athena',
                                  frequency_per_year='semi-annual', steps=500, memory_feature=True):
  
        # Configuration des perturbations
        dt = maturity / steps if steps > 0 and maturity > 0 else 0.0
        h_spot = max(0.05 * spot, 1e-4)  # 5% du spot minimum
        h_vol = min(max(0.01 * volatility, 1e-4), 0.2 * volatility)  # Limité à 20% de la volatilité
        h_rate = 1e-4

        # Ajustement dynamique pour Theta
        theta_maturity = max(1e-5, maturity - 1/365)
        theta_steps = int(theta_maturity / dt) if dt > 0 else steps

        # Fonction de pricing générique
        def generate_scenario(_spot=spot, _maturity=maturity, _rate=rate, _volatility=volatility, _steps=steps):
            return BinomialTreePricer.price_autocall(
                spot=_spot,
                strike=strike,
                maturity=_maturity,
                rate=_rate,
                volatility=max(0.0001, _volatility),
                dividend_yield=dividend_yield,
                coupon=coupon,
                barrier=barrier,
                protection_barrier=protection_barrier,
                type_autocall=type_autocall,
                frequency_per_year=frequency_per_year,
                steps=_steps,
                memory_feature=memory_feature
            )

        # Calcul parallèle des scénarios
        with ThreadPoolExecutor() as executor:
            futures = {
                'base': executor.submit(generate_scenario),
                'up_spot': executor.submit(generate_scenario, _spot=spot + h_spot),
                'down_spot': executor.submit(generate_scenario, _spot=spot - h_spot),
                'vol_up': executor.submit(generate_scenario, _volatility=volatility + h_vol),
                'rate_up': executor.submit(generate_scenario, _rate=rate + h_rate),
                'theta': executor.submit(generate_scenario, _maturity=theta_maturity, _steps=theta_steps)
            }
            results = {k: f.result() for k, f in futures.items()}

        # Extraction des résultats
        price = results['base']
        price_up = results['up_spot']
        price_down = results['down_spot']
        price_vol_up = results['vol_up']
        price_rate_up = results['rate_up']
        price_theta = results['theta']

        # Calcul des grecques avec contrôles
        delta = (price_up - price_down) / (2 * h_spot) if h_spot != 0 else 0.0
        gamma = (price_up - 2 * price + price_down) / (h_spot ** 2) if h_spot != 0 else 0.0
        vega = (price_vol_up - price) / h_vol if h_vol != 0 and volatility > 0.01 else 0.0
        rho = (price_rate_up - price) / h_rate if h_rate != 0 else 0.0
        theta = (price_theta - price) / (1/365) * -1 if maturity > 1/365 else 0.0

        return {
            "Delta": float(delta),
            "Gamma": float(gamma),
            "Vega": float(vega),
            "Theta": float(theta),
            "Rho": float(rho)
        }