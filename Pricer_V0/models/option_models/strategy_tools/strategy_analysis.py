# strategy_analysis.py
from pricing_method.black_scholes import BlackScholesPricer
from greek_method.black_scholes_greek import BlackScholesGreek

def price_strategy(options):

    total_price = 0
    for option in options:
        price = BlackScholesPricer.price(
            S=option['spot'],
            K=option['strike'],
            T=option['maturity'],
            r=option['rate'],
            sigma=option['volatility'],
            q=option['dividend_yield'],
            option_type=option['type_option']
        )
        total_price += price * option['quantity']
    return total_price


def greeks_strategy(strategy_type, options):

    combined_greeks = {"Delta": 0, "Gamma": 0, "Vega": 0, "Theta": 0, "Rho": 0}
    for option in options:
        greeks = BlackScholesGreek.bs_greeks(
            S=option['spot'],
            K=option['strike'],
            T=option['maturity'],
            r=option['rate'],
            sigma=option['volatility'],
            q=option['dividend_yield'],
            option_type=option['type_option']
        )
        for key in combined_greeks:
            combined_greeks[key] += greeks[key] * option['quantity']
    return combined_greeks
