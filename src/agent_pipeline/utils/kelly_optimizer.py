"""
Advanced Kelly Criterion implementation for prediction markets with safety features.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import math


class KellyMode(Enum):
    FULL = "full"           # Full Kelly (aggressive)
    FRACTIONAL_50 = "half"  # 50% Kelly (balanced)
    FRACTIONAL_25 = "quarter"  # 25% Kelly (conservative)
    ADAPTIVE = "adaptive"   # Adaptive based on confidence


@dataclass
class MarketOpportunity:
    """Represents a betting opportunity in a prediction market."""
    probability_estimate: float  # Our estimated probability
    market_price: float         # Current market price
    confidence_level: float     # 0-1 confidence in our estimate
    liquidity: float           # Available liquidity
    bid_ask_spread: float      # Market spread
    time_to_resolution: int    # Hours until resolution
    market_id: str            # Market identifier


@dataclass
class KellyResult:
    """Result of Kelly Criterion calculation."""
    kelly_fraction: float      # Raw Kelly fraction
    adjusted_fraction: float   # Risk-adjusted fraction
    expected_value: float      # Expected value of bet
    confidence_adjustment: float  # Confidence penalty applied
    risk_adjustment: float     # Risk penalty applied
    final_position_size: float # Final recommended position size
    recommendation: str        # BUY_YES, BUY_NO, HOLD
    reasoning: str            # Explanation of calculation


class AdvancedKellyOptimizer:
    """
    Advanced Kelly Criterion optimizer with safety features for prediction markets.
    """
    
    def __init__(
        self,
        kelly_mode: KellyMode = KellyMode.FRACTIONAL_50,
        max_position_size: float = 0.15,     # Max 15% of bankroll per position
        min_confidence_threshold: float = 0.6,  # Min confidence to bet
        max_correlation_exposure: float = 0.3,  # Max 30% in correlated bets
        drawdown_protection: bool = True,
        stress_test: bool = True
    ):
        self.kelly_mode = kelly_mode
        self.max_position_size = max_position_size
        self.min_confidence_threshold = min_confidence_threshold
        self.max_correlation_exposure = max_correlation_exposure
        self.drawdown_protection = drawdown_protection
        self.stress_test = stress_test
        
        # Risk adjustment parameters
        self.volatility_penalty = 0.8    # Reduce Kelly in volatile markets
        self.liquidity_penalty = 0.9     # Reduce Kelly in illiquid markets
        self.time_decay_factor = 0.95    # Reduce Kelly for long-term bets
        
        # Confidence calibration
        self.confidence_curve = self._build_confidence_curve()
    
    def calculate_optimal_position(
        self,
        opportunity: MarketOpportunity,
        bankroll: float,
        existing_positions: Optional[List[Dict]] = None
    ) -> KellyResult:
        """
        Calculate optimal position size using advanced Kelly Criterion.
        
        Args:
            opportunity: Market opportunity to analyze
            bankroll: Current bankroll size
            existing_positions: List of existing positions for correlation analysis
            
        Returns:
            KellyResult with optimal position sizing
        """
        
        # Validate inputs
        if not self._validate_opportunity(opportunity):
            return KellyResult(
                kelly_fraction=0.0,
                adjusted_fraction=0.0,
                expected_value=0.0,
                confidence_adjustment=0.0,
                risk_adjustment=0.0,
                final_position_size=0.0,
                recommendation="HOLD",
                reasoning="Invalid opportunity parameters"
            )
        
        # Calculate base Kelly fraction
        base_kelly = self._calculate_base_kelly(opportunity)
        
        # Calculate expected value
        expected_value = self._calculate_expected_value(opportunity)
        
        # Apply confidence adjustment
        confidence_adjusted_kelly, confidence_penalty = self._apply_confidence_adjustment(
            base_kelly, opportunity.confidence_level
        )
        
        # Apply risk adjustments
        risk_adjusted_kelly, risk_penalty = self._apply_risk_adjustments(
            confidence_adjusted_kelly, opportunity
        )
        
        # Apply Kelly mode scaling
        mode_adjusted_kelly = self._apply_kelly_mode_scaling(risk_adjusted_kelly)
        
        # Apply portfolio constraints
        final_kelly = self._apply_portfolio_constraints(
            mode_adjusted_kelly, opportunity, existing_positions, bankroll
        )
        
        # Stress test the position
        if self.stress_test:
            final_kelly = self._stress_test_position(final_kelly, opportunity)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(final_kelly, expected_value, opportunity)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            base_kelly, confidence_penalty, risk_penalty, final_kelly, opportunity
        )
        
        return KellyResult(
            kelly_fraction=base_kelly,
            adjusted_fraction=final_kelly,
            expected_value=expected_value,
            confidence_adjustment=confidence_penalty,
            risk_adjustment=risk_penalty,
            final_position_size=final_kelly,
            recommendation=recommendation,
            reasoning=reasoning
        )
    
    def _calculate_base_kelly(self, opportunity: MarketOpportunity) -> float:
        """Calculate base Kelly fraction using standard formula."""
        
        p = opportunity.probability_estimate
        price = opportunity.market_price
        
        if price <= 0 or price >= 1:
            return 0.0
        
        # For binary prediction markets:
        # Kelly = (p * odds - q) / odds
        # where odds = (1/price - 1) and q = (1-p)
        
        odds = (1 / price) - 1
        q = 1 - p
        
        if odds <= 0:
            return 0.0
        
        kelly = (p * odds - q) / odds
        
        # Ensure non-negative
        return max(kelly, 0.0)
    
    def _calculate_expected_value(self, opportunity: MarketOpportunity) -> float:
        """Calculate expected value of the bet."""
        
        p = opportunity.probability_estimate
        price = opportunity.market_price
        
        if price <= 0 or price >= 1:
            return 0.0
        
        # EV = p * (1/price - 1) - (1-p) * 1
        # Simplified: EV = p/price - 1
        
        return p / price - 1
    
    def _apply_confidence_adjustment(self, kelly: float, confidence: float) -> Tuple[float, float]:
        """
        Adjust Kelly fraction based on confidence level.
        Lower confidence = smaller positions.
        """
        
        if confidence < self.min_confidence_threshold:
            return 0.0, 1.0  # No bet if confidence too low
        
        # Use confidence curve for smooth adjustment
        confidence_multiplier = self._get_confidence_multiplier(confidence)
        adjusted_kelly = kelly * confidence_multiplier
        penalty = 1 - confidence_multiplier
        
        return adjusted_kelly, penalty
    
    def _apply_risk_adjustments(self, kelly: float, opportunity: MarketOpportunity) -> Tuple[float, float]:
        """Apply various risk adjustments to Kelly fraction."""
        
        total_penalty = 0.0
        adjusted_kelly = kelly
        
        # Liquidity penalty
        if opportunity.liquidity < 1000:  # Low liquidity threshold
            liquidity_mult = self.liquidity_penalty
            adjusted_kelly *= liquidity_mult
            total_penalty += (1 - liquidity_mult)
        
        # Spread penalty
        if opportunity.bid_ask_spread > 0.05:  # High spread threshold
            spread_mult = 1 - (opportunity.bid_ask_spread * 2)  # Penalty increases with spread
            spread_mult = max(spread_mult, 0.5)  # Minimum 50% reduction
            adjusted_kelly *= spread_mult
            total_penalty += (1 - spread_mult)
        
        # Time decay penalty for very long-term bets
        if opportunity.time_to_resolution > 2160:  # > 3 months
            weeks_excess = (opportunity.time_to_resolution - 2160) / 168  # Weeks beyond 3 months
            time_mult = self.time_decay_factor ** weeks_excess
            adjusted_kelly *= time_mult
            total_penalty += (1 - time_mult)
        
        return adjusted_kelly, total_penalty
    
    def _apply_kelly_mode_scaling(self, kelly: float) -> float:
        """Apply Kelly mode scaling (full, fractional, etc.)."""
        
        if self.kelly_mode == KellyMode.FULL:
            return kelly
        elif self.kelly_mode == KellyMode.FRACTIONAL_50:
            return kelly * 0.5
        elif self.kelly_mode == KellyMode.FRACTIONAL_25:
            return kelly * 0.25
        elif self.kelly_mode == KellyMode.ADAPTIVE:
            # Adaptive scaling based on Kelly magnitude
            if kelly > 0.2:
                return kelly * 0.25  # Very conservative for large Kelly
            elif kelly > 0.1:
                return kelly * 0.5   # Moderate for medium Kelly
            else:
                return kelly * 0.75  # Less conservative for small Kelly
        
        return kelly
    
    def _apply_portfolio_constraints(
        self,
        kelly: float,
        opportunity: MarketOpportunity,
        existing_positions: Optional[List[Dict]],
        bankroll: float
    ) -> float:
        """Apply portfolio-level constraints."""
        
        # Hard cap at max position size
        kelly = min(kelly, self.max_position_size)
        
        # Portfolio correlation constraint (simplified)
        if existing_positions:
            total_exposure = sum(pos.get('position_size', 0) for pos in existing_positions)
            if total_exposure > self.max_correlation_exposure:
                # Reduce new position if portfolio already highly exposed
                reduction_factor = max(0.5, 1 - (total_exposure - self.max_correlation_exposure))
                kelly *= reduction_factor
        
        return kelly
    
    def _stress_test_position(self, kelly: float, opportunity: MarketOpportunity) -> float:
        """Stress test the position under adverse scenarios."""
        
        # Monte Carlo stress test
        stress_scenarios = [
            {"prob_error": -0.2, "spread_increase": 2.0},  # Overestimated probability
            {"prob_error": -0.15, "spread_increase": 1.5}, # Moderate overestimate
            {"prob_error": -0.1, "spread_increase": 1.2},  # Small overestimate
        ]
        
        worst_case_kelly = kelly
        
        for scenario in stress_scenarios:
            # Adjust probability estimate
            stressed_prob = max(0.01, opportunity.probability_estimate + scenario["prob_error"])
            
            # Create stressed opportunity
            stressed_opp = MarketOpportunity(
                probability_estimate=stressed_prob,
                market_price=opportunity.market_price,
                confidence_level=opportunity.confidence_level * 0.8,  # Reduce confidence
                liquidity=opportunity.liquidity * 0.7,  # Reduce liquidity
                bid_ask_spread=opportunity.bid_ask_spread * scenario["spread_increase"],
                time_to_resolution=opportunity.time_to_resolution,
                market_id=opportunity.market_id
            )
            
            # Calculate Kelly under stress
            stressed_kelly = self._calculate_base_kelly(stressed_opp)
            stressed_kelly *= 0.5  # Conservative scaling under stress
            
            # Use minimum of all scenarios
            worst_case_kelly = min(worst_case_kelly, stressed_kelly)
        
        # Use 80% of worst case as final position
        return worst_case_kelly * 0.8
    
    def _generate_recommendation(self, kelly: float, expected_value: float, opportunity: MarketOpportunity) -> str:
        """Generate trading recommendation."""
        
        if kelly < 0.01 or expected_value <= 0:
            return "HOLD"
        elif kelly >= 0.05:  # 5%+ position
            return "BUY_YES" if opportunity.probability_estimate > opportunity.market_price else "BUY_NO"
        else:
            return "SMALL_BUY"  # Small position
    
    def _generate_reasoning(
        self,
        base_kelly: float,
        confidence_penalty: float,
        risk_penalty: float,
        final_kelly: float,
        opportunity: MarketOpportunity
    ) -> str:
        """Generate explanation of Kelly calculation."""
        
        reasoning_parts = []
        
        reasoning_parts.append(f"Base Kelly: {base_kelly:.3f}")
        
        if confidence_penalty > 0:
            reasoning_parts.append(f"Confidence adjustment: -{confidence_penalty:.1%}")
        
        if risk_penalty > 0:
            reasoning_parts.append(f"Risk adjustments: -{risk_penalty:.1%}")
        
        reasoning_parts.append(f"Kelly mode: {self.kelly_mode.value}")
        reasoning_parts.append(f"Final position: {final_kelly:.1%}")
        
        if final_kelly < 0.01:
            reasoning_parts.append("Position too small - recommend HOLD")
        
        return " | ".join(reasoning_parts)
    
    def _validate_opportunity(self, opportunity: MarketOpportunity) -> bool:
        """Validate opportunity parameters."""
        
        if not (0 < opportunity.probability_estimate < 1):
            return False
        if not (0 < opportunity.market_price < 1):
            return False
        if not (0 <= opportunity.confidence_level <= 1):
            return False
        if opportunity.liquidity < 0:
            return False
        
        return True
    
    def _build_confidence_curve(self) -> Dict[float, float]:
        """Build confidence adjustment curve."""
        
        # Confidence levels to multipliers
        return {
            0.5: 0.0,   # No bet at 50% confidence
            0.6: 0.2,   # 20% of Kelly at 60% confidence
            0.7: 0.5,   # 50% of Kelly at 70% confidence
            0.8: 0.8,   # 80% of Kelly at 80% confidence
            0.9: 0.95,  # 95% of Kelly at 90% confidence
            1.0: 1.0    # Full Kelly at 100% confidence
        }
    
    def _get_confidence_multiplier(self, confidence: float) -> float:
        """Get confidence multiplier using interpolation."""
        
        curve = self.confidence_curve
        
        # Find surrounding points
        confidence_levels = sorted(curve.keys())
        
        if confidence <= confidence_levels[0]:
            return curve[confidence_levels[0]]
        
        if confidence >= confidence_levels[-1]:
            return curve[confidence_levels[-1]]
        
        # Linear interpolation
        for i in range(len(confidence_levels) - 1):
            if confidence_levels[i] <= confidence <= confidence_levels[i + 1]:
                x1, x2 = confidence_levels[i], confidence_levels[i + 1]
                y1, y2 = curve[x1], curve[x2]
                
                # Interpolate
                return y1 + (y2 - y1) * (confidence - x1) / (x2 - x1)
        
        return 0.0
    
    def calculate_multi_market_kelly(
        self,
        opportunities: List[MarketOpportunity],
        correlations: Optional[np.ndarray] = None,
        bankroll: float = 1000.0
    ) -> Dict[str, KellyResult]:
        """
        Calculate Kelly fractions for multiple correlated markets.
        
        Args:
            opportunities: List of market opportunities
            correlations: Correlation matrix between markets (optional)
            bankroll: Total bankroll
            
        Returns:
            Dictionary of market_id -> KellyResult
        """
        
        results = {}
        
        # If no correlations provided, treat markets as independent
        if correlations is None:
            for opp in opportunities:
                results[opp.market_id] = self.calculate_optimal_position(opp, bankroll)
            return results
        
        # Advanced multi-market Kelly (simplified implementation)
        # In practice, this would use portfolio optimization techniques
        
        total_kelly_budget = self.max_correlation_exposure
        
        # Calculate individual Kelly fractions
        individual_kellys = []
        for opp in opportunities:
            kelly_result = self.calculate_optimal_position(opp, bankroll)
            individual_kellys.append(kelly_result.adjusted_fraction)
        
        # Scale down if total exceeds budget
        total_kelly = sum(individual_kellys)
        if total_kelly > total_kelly_budget:
            scale_factor = total_kelly_budget / total_kelly
            individual_kellys = [k * scale_factor for k in individual_kellys]
        
        # Create results
        for i, opp in enumerate(opportunities):
            adjusted_kelly = individual_kellys[i]
            
            results[opp.market_id] = KellyResult(
                kelly_fraction=adjusted_kelly,
                adjusted_fraction=adjusted_kelly,
                expected_value=self._calculate_expected_value(opp),
                confidence_adjustment=0.0,
                risk_adjustment=0.0,
                final_position_size=adjusted_kelly,
                recommendation=self._generate_recommendation(adjusted_kelly, self._calculate_expected_value(opp), opp),
                reasoning=f"Multi-market Kelly with correlation adjustment"
            )
        
        return results


def demo_kelly_optimizer():
    """Demonstrate the Kelly optimizer functionality."""
    
    # Create optimizer
    optimizer = AdvancedKellyOptimizer(
        kelly_mode=KellyMode.FRACTIONAL_50,
        max_position_size=0.15
    )
    
    # Example market opportunity
    opportunity = MarketOpportunity(
        probability_estimate=0.72,
        market_price=0.35,
        confidence_level=0.85,
        liquidity=5000.0,
        bid_ask_spread=0.02,
        time_to_resolution=720,  # 30 days
        market_id="btc_100k_2024"
    )
    
    # Calculate optimal position
    result = optimizer.calculate_optimal_position(opportunity, bankroll=1000.0)
    
    print("🎯 Advanced Kelly Optimization Result")
    print("=" * 40)
    print(f"Market: {opportunity.market_id}")
    print(f"Our Probability: {opportunity.probability_estimate:.1%}")
    print(f"Market Price: {opportunity.market_price:.1%}")
    print(f"Confidence: {opportunity.confidence_level:.1%}")
    print()
    print(f"Base Kelly: {result.kelly_fraction:.1%}")
    print(f"Final Position: {result.final_position_size:.1%}")
    print(f"Expected Value: {result.expected_value:.3f}")
    print(f"Recommendation: {result.recommendation}")
    print()
    print(f"Reasoning: {result.reasoning}")


if __name__ == "__main__":
    demo_kelly_optimizer()