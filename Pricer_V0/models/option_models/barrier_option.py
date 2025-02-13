# barrier_option.py

from option_models.exotic_option import ExoticOption
from pricing_method.monte_carlo import MonteCarloPricer
from pricing_method.binomial_tree import BinomialTreePricer
from greek_method.binomial_tree_greek import BinomialTreeGreek

class BarrierOption(ExoticOption):
    def __init__(self, barrier_level, barrier_type, rebate=0, **kwargs):

        super().__init__(exotic_type='barrier', **kwargs)
        
        if barrier_type not in ['up-and-in', 'up-and-out', 'down-and-in', 'down-and-out']:
            raise ValueError("Le type de barrière doit être 'up-and-in', 'up-and-out', 'down-and-in' ou 'down-and-out'.")

        self.barrier_level = barrier_level
        self.barrier_type = barrier_type
        self.rebate = rebate

    def price(self, num_paths=100000, time_steps=100):
        return MonteCarloPricer.price_barrier(
            type_option=self.type_option,
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.volatility,
            dividend_yield=self.dividend_yield,
            barrier_level=self.barrier_level,
            barrier_type=self.barrier_type,
            rebate=self.rebate,
            num_paths=num_paths,
            time_steps=time_steps
        )
    
    def price2(self, steps=500):
        return BinomialTreePricer.price_barrier_binomial(
            type_option=self.type_option,
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.volatility,
            dividend_yield=self.dividend_yield,
            barrier_level=self.barrier_level,
            barrier_type=self.barrier_type,
            rebate=self.rebate,
            steps= steps        )

    
    def greek(self, steps=500):
        return BinomialTreeGreek.binomial_barrier_greeks(
            S=self.spot,
            K=self.strike,
            T=self.maturity,
            r=self.rate,
            sigma=self.volatility,
            q=self.dividend_yield,
            option_type=self.type_option,
            barrier_level=self.barrier_level,
            barrier_type=self.barrier_type,
            rebate=self.rebate,
            steps=steps
        )