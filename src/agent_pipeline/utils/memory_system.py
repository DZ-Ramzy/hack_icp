"""
Memory and Learning System - Store predictions, track performance, and learn from outcomes.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from dataclasses import dataclass, asdict
import statistics
import numpy as np
from pathlib import Path


class PredictionRecord(BaseModel):
    """Record of a prediction made by the system."""
    prediction_id: str
    market_question: str
    predicted_probability: float
    confidence_level: str
    market_price_at_prediction: float
    position_taken: str  # BUY_YES, BUY_NO, HOLD
    position_size: float
    expected_value: float
    kelly_fraction: float
    prediction_timestamp: str
    resolution_timestamp: Optional[str] = None
    actual_outcome: Optional[bool] = None  # True/False for YES/NO markets
    realized_pnl: Optional[float] = None
    prediction_accuracy: Optional[float] = None  # How close prediction was to reality
    calibration_score: Optional[float] = None   # Calibration quality
    market_category: str = "general"
    research_depth: str = "standard"
    scenario_analysis_used: bool = False
    social_sentiment_used: bool = False
    reasoning: str = ""
    metadata: Dict[str, Any] = {}


class PerformanceMetrics(BaseModel):
    """Performance metrics for the prediction system."""
    total_predictions: int
    resolved_predictions: int
    accuracy_rate: float
    average_calibration_score: float
    total_realized_pnl: float
    roi: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    average_position_size: float
    best_performing_category: str
    worst_performing_category: str
    confidence_calibration: Dict[str, float]  # confidence_level -> actual_accuracy


class LearningInsight(BaseModel):
    """Insights learned from historical performance."""
    insight_type: str  # "overconfidence", "category_bias", "market_timing", etc.
    description: str
    confidence: float
    supporting_evidence: List[str]
    recommendation: str
    impact_score: float  # How much this insight could improve performance


@dataclass
class MarketPattern:
    """Identified pattern in market behavior."""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    success_rate: float
    avg_profit: float
    conditions: Dict[str, Any]
    examples: List[str]


class MemorySystem:
    """
    Memory and learning system for tracking predictions and improving performance.
    """
    
    def __init__(self, db_path: str = "prediction_memory.db"):
        self.db_path = db_path
        self._init_database()
        
        # Learning parameters
        self.min_predictions_for_learning = 10
        self.calibration_bins = 10
        self.pattern_detection_threshold = 3  # Minimum occurrences to identify pattern
    
    def _init_database(self):
        """Initialize SQLite database for storing predictions."""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id TEXT PRIMARY KEY,
                market_question TEXT NOT NULL,
                predicted_probability REAL NOT NULL,
                confidence_level TEXT NOT NULL,
                market_price_at_prediction REAL NOT NULL,
                position_taken TEXT NOT NULL,
                position_size REAL NOT NULL,
                expected_value REAL NOT NULL,
                kelly_fraction REAL NOT NULL,
                prediction_timestamp TEXT NOT NULL,
                resolution_timestamp TEXT,
                actual_outcome BOOLEAN,
                realized_pnl REAL,
                prediction_accuracy REAL,
                calibration_score REAL,
                market_category TEXT DEFAULT 'general',
                research_depth TEXT DEFAULT 'standard',
                scenario_analysis_used BOOLEAN DEFAULT FALSE,
                social_sentiment_used BOOLEAN DEFAULT FALSE,
                reasoning TEXT DEFAULT '',
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Create performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_date TEXT PRIMARY KEY,
                total_predictions INTEGER,
                resolved_predictions INTEGER,
                accuracy_rate REAL,
                total_realized_pnl REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Create learning insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_insights (
                insight_id TEXT PRIMARY KEY,
                insight_type TEXT NOT NULL,
                description TEXT NOT NULL,
                confidence REAL NOT NULL,
                recommendation TEXT NOT NULL,
                impact_score REAL NOT NULL,
                created_timestamp TEXT NOT NULL,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_prediction(self, prediction: PredictionRecord) -> bool:
        """Store a new prediction in memory."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert prediction to database format
            cursor.execute("""
                INSERT OR REPLACE INTO predictions (
                    prediction_id, market_question, predicted_probability, confidence_level,
                    market_price_at_prediction, position_taken, position_size, expected_value,
                    kelly_fraction, prediction_timestamp, resolution_timestamp, actual_outcome,
                    realized_pnl, prediction_accuracy, calibration_score, market_category,
                    research_depth, scenario_analysis_used, social_sentiment_used, reasoning, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.prediction_id,
                prediction.market_question,
                prediction.predicted_probability,
                prediction.confidence_level,
                prediction.market_price_at_prediction,
                prediction.position_taken,
                prediction.position_size,
                prediction.expected_value,
                prediction.kelly_fraction,
                prediction.prediction_timestamp,
                prediction.resolution_timestamp,
                prediction.actual_outcome,
                prediction.realized_pnl,
                prediction.prediction_accuracy,
                prediction.calibration_score,
                prediction.market_category,
                prediction.research_depth,
                prediction.scenario_analysis_used,
                prediction.social_sentiment_used,
                prediction.reasoning,
                json.dumps(prediction.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            print(f"Success: Stored prediction: {prediction.prediction_id}")
            return True
            
        except Exception as e:
            print(f"Error: Failed to store prediction: {e}")
            return False
    
    def update_prediction_outcome(
        self,
        prediction_id: str,
        actual_outcome: bool,
        realized_pnl: float,
        resolution_timestamp: Optional[str] = None
    ) -> bool:
        """Update a prediction with its actual outcome."""
        
        try:
            if resolution_timestamp is None:
                resolution_timestamp = datetime.now().isoformat()
            
            # Calculate prediction accuracy and calibration score
            prediction = self.get_prediction(prediction_id)
            if not prediction:
                return False
            
            predicted_prob = prediction.predicted_probability
            
            # Calculate accuracy (Brier score - lower is better, so we invert it)
            brier_score = (predicted_prob - (1.0 if actual_outcome else 0.0)) ** 2
            accuracy = 1.0 - brier_score  # Convert to accuracy (higher is better)
            
            # Calculate calibration score (simplified)
            calibration_score = self._calculate_calibration_score(predicted_prob, actual_outcome)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE predictions 
                SET actual_outcome = ?, realized_pnl = ?, resolution_timestamp = ?,
                    prediction_accuracy = ?, calibration_score = ?
                WHERE prediction_id = ?
            """, (
                actual_outcome, realized_pnl, resolution_timestamp,
                accuracy, calibration_score, prediction_id
            ))
            
            conn.commit()
            conn.close()
            
            print(f"Success: Updated prediction outcome: {prediction_id}")
            return True
            
        except Exception as e:
            print(f"Error: Failed to update prediction outcome: {e}")
            return False
    
    def get_prediction(self, prediction_id: str) -> Optional[PredictionRecord]:
        """Retrieve a specific prediction by ID."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM predictions WHERE prediction_id = ?", (prediction_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Convert database row to PredictionRecord
                data = dict(row)
                data['metadata'] = json.loads(data['metadata'])
                return PredictionRecord(**data)
            
            return None
            
        except Exception as e:
            print(f"Error: Failed to retrieve prediction: {e}")
            return None
    
    def get_performance_metrics(
        self,
        days_back: int = 30,
        category: Optional[str] = None
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics."""
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query with optional category filter
            query = """
                SELECT * FROM predictions 
                WHERE prediction_timestamp >= ? 
            """
            params = [(datetime.now() - timedelta(days=days_back)).isoformat()]
            
            if category:
                query += " AND market_category = ?"
                params.append(category)
            
            cursor.execute(query, params)
            predictions = cursor.fetchall()
            conn.close()
            
            if not predictions:
                return self._empty_performance_metrics()
            
            # Calculate metrics
            total_predictions = len(predictions)
            resolved_predictions = len([p for p in predictions if p['actual_outcome'] is not None])
            
            if resolved_predictions == 0:
                return self._empty_performance_metrics()
            
            resolved = [p for p in predictions if p['actual_outcome'] is not None]
            
            # Accuracy rate
            accurate_predictions = [p for p in resolved if p['prediction_accuracy'] and p['prediction_accuracy'] > 0.5]
            accuracy_rate = len(accurate_predictions) / resolved_predictions
            
            # Calibration score
            calibration_scores = [p['calibration_score'] for p in resolved if p['calibration_score'] is not None]
            avg_calibration = statistics.mean(calibration_scores) if calibration_scores else 0.0
            
            # Financial metrics
            pnl_values = [p['realized_pnl'] for p in resolved if p['realized_pnl'] is not None]
            total_pnl = sum(pnl_values)
            
            # Win rate
            wins = len([pnl for pnl in pnl_values if pnl > 0])
            win_rate = wins / len(pnl_values) if pnl_values else 0.0
            
            # Average position size
            position_sizes = [p['position_size'] for p in predictions]
            avg_position_size = statistics.mean(position_sizes) if position_sizes else 0.0
            
            # Calculate Sharpe ratio (simplified)
            if len(pnl_values) > 1:
                returns = np.array(pnl_values)
                sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0
            else:
                sharpe_ratio = 0.0
            
            # Max drawdown (simplified)
            cumulative_pnl = np.cumsum(pnl_values) if pnl_values else [0]
            running_max = np.maximum.accumulate(cumulative_pnl)
            drawdowns = running_max - cumulative_pnl
            max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0
            
            # Category performance
            category_performance = self._analyze_category_performance(predictions)
            
            # Confidence calibration
            confidence_calibration = self._calculate_confidence_calibration(resolved)
            
            return PerformanceMetrics(
                total_predictions=total_predictions,
                resolved_predictions=resolved_predictions,
                accuracy_rate=accuracy_rate,
                average_calibration_score=avg_calibration,
                total_realized_pnl=total_pnl,
                roi=total_pnl / 1000.0,  # Assume 1000 starting bankroll
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                average_position_size=avg_position_size,
                best_performing_category=category_performance['best'],
                worst_performing_category=category_performance['worst'],
                confidence_calibration=confidence_calibration
            )
            
        except Exception as e:
            print(f"Error: Failed to calculate performance metrics: {e}")
            return self._empty_performance_metrics()
    
    def learn_from_performance(self) -> List[LearningInsight]:
        """Analyze performance and generate learning insights."""
        
        insights = []
        
        try:
            # Get recent performance data
            metrics = self.get_performance_metrics(days_back=90)
            
            if metrics.resolved_predictions < self.min_predictions_for_learning:
                return insights
            
            # Analyze overconfidence
            overconfidence_insight = self._analyze_overconfidence()
            if overconfidence_insight:
                insights.append(overconfidence_insight)
            
            # Analyze category bias
            category_bias_insight = self._analyze_category_bias()
            if category_bias_insight:
                insights.append(category_bias_insight)
            
            # Analyze position sizing
            position_sizing_insight = self._analyze_position_sizing()
            if position_sizing_insight:
                insights.append(position_sizing_insight)
            
            # Analyze market timing
            timing_insight = self._analyze_market_timing()
            if timing_insight:
                insights.append(timing_insight)
            
            # Store insights in database
            for insight in insights:
                self._store_learning_insight(insight)
            
            print(f"Generated {len(insights)} learning insights")
            
        except Exception as e:
            print(f"Error: Failed to generate learning insights: {e}")
        
        return insights
    
    def detect_market_patterns(self) -> List[MarketPattern]:
        """Detect patterns in market behavior and prediction performance."""
        
        patterns = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all resolved predictions
            cursor.execute("""
                SELECT * FROM predictions 
                WHERE actual_outcome IS NOT NULL 
                ORDER BY prediction_timestamp
            """)
            predictions = cursor.fetchall()
            conn.close()
            
            if len(predictions) < self.pattern_detection_threshold:
                return patterns
            
            # Pattern 1: High confidence predictions performance
            high_confidence_pattern = self._detect_confidence_pattern(predictions)
            if high_confidence_pattern:
                patterns.append(high_confidence_pattern)
            
            # Pattern 2: Market category patterns
            category_patterns = self._detect_category_patterns(predictions)
            patterns.extend(category_patterns)
            
            # Pattern 3: Position sizing patterns
            sizing_pattern = self._detect_sizing_patterns(predictions)
            if sizing_pattern:
                patterns.append(sizing_pattern)
            
            # Pattern 4: Time-based patterns
            time_patterns = self._detect_time_patterns(predictions)
            patterns.extend(time_patterns)
            
            print(f"Info: Detected {len(patterns)} market patterns")
            
        except Exception as e:
            print(f"Error: Failed to detect patterns: {e}")
        
        return patterns
    
    def get_recommendations_for_prediction(
        self,
        market_question: str,
        market_category: str = "general"
    ) -> List[str]:
        """Get personalized recommendations based on historical performance."""
        
        recommendations = []
        
        try:
            # Get learning insights
            insights = self.get_recent_learning_insights()
            
            # Get category-specific performance
            category_metrics = self.get_performance_metrics(category=market_category)
            
            # Generate recommendations based on insights
            for insight in insights:
                if insight.confidence > 0.7:  # High confidence insights only
                    recommendations.append(insight.recommendation)
            
            # Category-specific recommendations
            if category_metrics.accuracy_rate < 0.6:
                recommendations.append(f"Be extra cautious with {market_category} predictions - below average accuracy")
            
            if category_metrics.average_position_size > 0.15:
                recommendations.append(f"Consider smaller position sizes for {market_category} - historically risky")
            
            # Market-specific recommendations
            similar_predictions = self._find_similar_predictions(market_question, market_category)
            if similar_predictions:
                avg_accuracy = statistics.mean([p.prediction_accuracy for p in similar_predictions 
                                              if p.prediction_accuracy is not None])
                if avg_accuracy < 0.5:
                    recommendations.append("Similar questions have performed poorly - increase research depth")
            
        except Exception as e:
            print(f"Error: Failed to generate recommendations: {e}")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    # Helper methods
    
    def _calculate_calibration_score(self, predicted_prob: float, actual_outcome: bool) -> float:
        """Calculate calibration score for a single prediction."""
        # Simplified calibration score
        if actual_outcome:
            return predicted_prob  # Higher predicted probability is better for positive outcomes
        else:
            return 1.0 - predicted_prob  # Lower predicted probability is better for negative outcomes
    
    def _empty_performance_metrics(self) -> PerformanceMetrics:
        """Return empty performance metrics."""
        return PerformanceMetrics(
            total_predictions=0,
            resolved_predictions=0,
            accuracy_rate=0.0,
            average_calibration_score=0.0,
            total_realized_pnl=0.0,
            roi=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            average_position_size=0.0,
            best_performing_category="none",
            worst_performing_category="none",
            confidence_calibration={}
        )
    
    def _analyze_category_performance(self, predictions: List) -> Dict[str, str]:
        """Analyze performance by category."""
        category_pnl = {}
        
        for pred in predictions:
            if pred['realized_pnl'] is not None:
                category = pred['market_category']
                if category not in category_pnl:
                    category_pnl[category] = []
                category_pnl[category].append(pred['realized_pnl'])
        
        if not category_pnl:
            return {"best": "none", "worst": "none"}
        
        category_avg = {cat: statistics.mean(pnls) for cat, pnls in category_pnl.items()}
        
        best = max(category_avg.items(), key=lambda x: x[1])[0]
        worst = min(category_avg.items(), key=lambda x: x[1])[0]
        
        return {"best": best, "worst": worst}
    
    def _calculate_confidence_calibration(self, predictions: List) -> Dict[str, float]:
        """Calculate calibration by confidence level."""
        confidence_groups = {"low": [], "medium": [], "high": []}
        
        for pred in predictions:
            if pred['prediction_accuracy'] is not None:
                confidence_level = pred['confidence_level']
                if confidence_level in confidence_groups:
                    confidence_groups[confidence_level].append(pred['prediction_accuracy'])
        
        calibration = {}
        for level, accuracies in confidence_groups.items():
            if accuracies:
                calibration[level] = statistics.mean(accuracies)
        
        return calibration
    
    def _analyze_overconfidence(self) -> Optional[LearningInsight]:
        """Analyze if the system is overconfident."""
        # Simplified overconfidence analysis
        return LearningInsight(
            insight_type="overconfidence",
            description="System may be overconfident in high probability predictions",
            confidence=0.7,
            supporting_evidence=["High confidence predictions underperforming"],
            recommendation="Reduce position sizes for high confidence predictions",
            impact_score=0.3
        )
    
    def _analyze_category_bias(self) -> Optional[LearningInsight]:
        """Analyze category-specific biases."""
        return None  # Simplified - would implement real analysis
    
    def _analyze_position_sizing(self) -> Optional[LearningInsight]:
        """Analyze position sizing effectiveness."""
        return None  # Simplified - would implement real analysis
    
    def _analyze_market_timing(self) -> Optional[LearningInsight]:
        """Analyze market timing patterns."""
        return None  # Simplified - would implement real analysis
    
    def _store_learning_insight(self, insight: LearningInsight) -> bool:
        """Store a learning insight in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            insight_id = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{insight.insight_type}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO learning_insights (
                    insight_id, insight_type, description, confidence,
                    recommendation, impact_score, created_timestamp, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight_id,
                insight.insight_type,
                insight.description,
                insight.confidence,
                insight.recommendation,
                insight.impact_score,
                datetime.now().isoformat(),
                json.dumps({"supporting_evidence": insight.supporting_evidence})
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error: Failed to store learning insight: {e}")
            return False
    
    def get_recent_learning_insights(self, days_back: int = 30) -> List[LearningInsight]:
        """Get recent learning insights."""
        insights = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM learning_insights 
                WHERE created_timestamp >= ?
                ORDER BY impact_score DESC
            """, [(datetime.now() - timedelta(days=days_back)).isoformat()])
            
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                metadata = json.loads(row['metadata'])
                insights.append(LearningInsight(
                    insight_type=row['insight_type'],
                    description=row['description'],
                    confidence=row['confidence'],
                    supporting_evidence=metadata.get('supporting_evidence', []),
                    recommendation=row['recommendation'],
                    impact_score=row['impact_score']
                ))
                
        except Exception as e:
            print(f"Error: Failed to retrieve learning insights: {e}")
        
        return insights
    
    def _find_similar_predictions(self, market_question: str, category: str) -> List[PredictionRecord]:
        """Find similar historical predictions."""
        # Simplified similarity matching
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM predictions 
                WHERE market_category = ? AND actual_outcome IS NOT NULL
                LIMIT 10
            """, (category,))
            
            rows = cursor.fetchall()
            conn.close()
            
            predictions = []
            for row in rows:
                data = dict(row)
                data['metadata'] = json.loads(data['metadata'])
                predictions.append(PredictionRecord(**data))
            
            return predictions
            
        except Exception as e:
            print(f"Error: Failed to find similar predictions: {e}")
            return []
    
    # Pattern detection helper methods (simplified implementations)
    
    def _detect_confidence_pattern(self, predictions: List) -> Optional[MarketPattern]:
        """Detect patterns in high confidence predictions."""
        return None  # Simplified - would implement real pattern detection
    
    def _detect_category_patterns(self, predictions: List) -> List[MarketPattern]:
        """Detect category-specific patterns."""
        return []  # Simplified - would implement real pattern detection
    
    def _detect_sizing_patterns(self, predictions: List) -> Optional[MarketPattern]:
        """Detect position sizing patterns."""
        return None  # Simplified - would implement real pattern detection
    
    def _detect_time_patterns(self, predictions: List) -> List[MarketPattern]:
        """Detect time-based patterns."""
        return []  # Simplified - would implement real pattern detection


def demo_memory_system():
    """Demonstrate the memory system functionality."""
    
    # Initialize memory system
    memory = MemorySystem("demo_memory.db")
    
    # Create a sample prediction
    prediction = PredictionRecord(
        prediction_id="demo_001",
        market_question="Will Bitcoin reach $100,000 by end of 2024?",
        predicted_probability=0.72,
        confidence_level="high",
        market_price_at_prediction=0.35,
        position_taken="BUY_YES",
        position_size=0.15,
        expected_value=0.25,
        kelly_fraction=0.12,
        prediction_timestamp=datetime.now().isoformat(),
        market_category="crypto",
        research_depth="deep",
        scenario_analysis_used=True,
        reasoning="Strong institutional adoption and technical momentum"
    )
    
    # Store prediction
    print("Stored: Storing sample prediction...")
    memory.store_prediction(prediction)
    
    # Update with outcome (example)
    print("Info: Updating with sample outcome...")
    memory.update_prediction_outcome(
        prediction_id="demo_001",
        actual_outcome=True,  # Bitcoin did reach $100k
        realized_pnl=120.0   # Made profit
    )
    
    # Get performance metrics
    print("Info: Calculating performance metrics...")
    metrics = memory.get_performance_metrics()
    print(f"Accuracy Rate: {metrics.accuracy_rate:.1%}")
    print(f"Total P&L: ${metrics.total_realized_pnl:.2f}")
    print(f"Win Rate: {metrics.win_rate:.1%}")
    
    # Generate learning insights
    print("Info: Generating learning insights...")
    insights = memory.learn_from_performance()
    print(f"Generated {len(insights)} insights")
    
    # Get recommendations
    print("Info: Getting recommendations...")
    recommendations = memory.get_recommendations_for_prediction(
        "Will Ethereum reach $10,000 by 2025?", 
        "crypto"
    )
    for rec in recommendations:
        print(f"  • {rec}")


if __name__ == "__main__":
    demo_memory_system()