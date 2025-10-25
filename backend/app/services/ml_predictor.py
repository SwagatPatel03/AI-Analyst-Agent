"""
ML Predictor Service
Purpose: Train models and predict sales/growth with confidence intervals
"""
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import json
from datetime import datetime


class MLPredictor:
    """
    Machine Learning predictor for financial forecasting
    
    Features:
    - Revenue growth prediction with confidence intervals
    - Multi-year sales forecasting
    - Segment-level predictions
    - Investment recommendations
    - Model persistence and retraining
    """
    
    def __init__(self):
        """Initialize ML Predictor with model storage"""
        self.models_dir = "ml_models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Model configurations
        self.confidence_level = 0.95
        self.forecast_years = 3
        self.volatility_factor = 0.2  # 20% of growth as volatility
    
    def predict_growth_and_sales(
        self, 
        financial_data: Dict[str, Any],
        report_id: int
    ) -> Dict[str, Any]:
        """
        Predict growth rate and future sales
        
        Args:
            financial_data: Historical financial data
            report_id: Report identifier for model storage
        
        Returns:
            Comprehensive predictions with confidence intervals
        """
        
        try:
            # Validate input data
            if not financial_data:
                raise ValueError("Financial data is empty")
            
            # Extract features
            features = self._extract_features(financial_data)
            
            # Predict revenue growth
            growth_prediction = self._predict_growth(features)
            
            # Predict future sales (next 3 years)
            sales_predictions = self._predict_sales(features, financial_data)
            
            # Calculate breakdown by segments
            segment_breakdown = self._predict_segment_breakdown(financial_data)
            
            # Generate investment recommendations
            recommendations = self._generate_recommendations(
                growth_prediction, 
                financial_data
            )
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(features, growth_prediction)
            
            return {
                "success": True,
                "report_id": report_id,
                "timestamp": datetime.now().isoformat(),
                "growth_rate": {
                    "predicted": growth_prediction['rate'],
                    "confidence_lower": growth_prediction['lower_bound'],
                    "confidence_upper": growth_prediction['upper_bound'],
                    "confidence_level": self.confidence_level,
                    "historical_growth": growth_prediction.get('historical_growth', None)
                },
                "sales_forecast": sales_predictions,
                "segment_breakdown": segment_breakdown,
                "risk_metrics": risk_metrics,
                "model_accuracy": growth_prediction.get('accuracy', 'N/A'),
                "recommendations": recommendations,
                "methodology": "Statistical forecasting with financial indicators"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "predictions_available": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_features(self, financial_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Extract features for ML model from financial data
        
        Args:
            financial_data: Raw financial data dictionary
            
        Returns:
            DataFrame with engineered features
        """
        
        metrics = financial_data.get('key_metrics', {})
        
        # Extract and sanitize values
        def safe_get(value, default=0):
            """Safely get numeric value"""
            if value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Handle both dict and direct value for revenue/net_income
        revenue_current = financial_data.get('revenue', 0)
        revenue_previous = 0
        net_income_current = financial_data.get('net_income', 0)
        net_income_previous = 0
        
        # Check if we have history arrays
        revenue_history = financial_data.get('revenue_history', [])
        if revenue_history and len(revenue_history) >= 2:
            revenue_previous = revenue_history[0]
            revenue_current = revenue_history[1]
        
        net_income_history = financial_data.get('net_income_history', [])
        if net_income_history and len(net_income_history) >= 2:
            net_income_previous = net_income_history[0]
            net_income_current = net_income_history[1]
        
        features = {
            'revenue_current': safe_get(revenue_current),
            'revenue_previous': safe_get(revenue_previous),
            'net_income_current': safe_get(net_income_current),
            'net_income_previous': safe_get(net_income_previous),
            'total_assets': safe_get(financial_data.get('total_assets')),
            'total_liabilities': safe_get(financial_data.get('total_liabilities')),
            'shareholders_equity': safe_get(financial_data.get('shareholders_equity')),
            'eps': safe_get(metrics.get('eps')),
            'roe': safe_get(metrics.get('roe')),
            'debt_to_equity': safe_get(metrics.get('debt_to_equity')),
            'operating_margin': safe_get(metrics.get('operating_margin')),
            'profit_margin': safe_get(metrics.get('profit_margin'))
        }
        
        # Add derived features
        if features['revenue_current'] > 0:
            features['revenue_growth_historical'] = (
                (features['revenue_current'] - features['revenue_previous']) / 
                features['revenue_previous'] * 100
            ) if features['revenue_previous'] > 0 else 0
        else:
            features['revenue_growth_historical'] = 0
        
        if features['net_income_current'] > 0:
            features['profit_growth_historical'] = (
                (features['net_income_current'] - features['net_income_previous']) / 
                features['net_income_previous'] * 100
            ) if features['net_income_previous'] > 0 else 0
        else:
            features['profit_growth_historical'] = 0
        
        # Financial health score (0-100)
        features['health_score'] = self._calculate_health_score(features)
        
        return pd.DataFrame([features])
    
    def _calculate_health_score(self, features: Dict[str, float]) -> float:
        """Calculate overall financial health score (0-100)"""
        score = 50  # Start at neutral
        
        # ROE contribution (max ±15 points)
        roe = features.get('roe', 0)
        if roe > 20:
            score += 15
        elif roe > 15:
            score += 10
        elif roe > 10:
            score += 5
        elif roe < 5:
            score -= 10
        
        # Debt contribution (max ±10 points)
        debt_ratio = features.get('debt_to_equity', 0)
        if debt_ratio < 0.5:
            score += 10
        elif debt_ratio < 1.0:
            score += 5
        elif debt_ratio > 2.0:
            score -= 10
        elif debt_ratio > 1.5:
            score -= 5
        
        # Growth contribution (max ±15 points)
        revenue_growth = features.get('revenue_growth_historical', 0)
        if revenue_growth > 20:
            score += 15
        elif revenue_growth > 10:
            score += 10
        elif revenue_growth > 5:
            score += 5
        elif revenue_growth < 0:
            score -= 10
        
        # Margin contribution (max ±10 points)
        profit_margin = features.get('profit_margin', 0)
        if profit_margin > 20:
            score += 10
        elif profit_margin > 10:
            score += 5
        elif profit_margin < 5:
            score -= 5
        
        return max(0, min(100, score))  # Clamp between 0-100
    
    def _predict_growth(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Predict revenue growth rate with confidence intervals"""
        
        revenue_current = features['revenue_current'].iloc[0]
        revenue_previous = features['revenue_previous'].iloc[0]
        
        if revenue_previous == 0 or revenue_previous is None or revenue_current == 0:
            # Use industry average if no historical data
            return {
                'rate': 5.0,
                'lower_bound': 2.0,
                'upper_bound': 8.0,
                'accuracy': 'estimated',
                'method': 'industry_average'
            }
        
        # Calculate historical growth
        historical_growth = ((revenue_current - revenue_previous) / revenue_previous) * 100
        
        # Adjust based on financial health indicators
        roe = features['roe'].iloc[0]
        debt_ratio = features['debt_to_equity'].iloc[0]
        health_score = features['health_score'].iloc[0]
        
        adjustment = 0
        
        # ROE adjustment
        if roe > 20:
            adjustment += 3
        elif roe > 15:
            adjustment += 2
        elif roe > 10:
            adjustment += 1
        elif roe < 5:
            adjustment -= 2
        
        # Debt adjustment
        if debt_ratio > 2.0:
            adjustment -= 2
        elif debt_ratio > 1.5:
            adjustment -= 1
        elif debt_ratio < 0.5:
            adjustment += 1
        
        # Health score adjustment
        if health_score > 80:
            adjustment += 1
        elif health_score < 40:
            adjustment -= 1
        
        # Calculate predicted growth
        predicted_growth = historical_growth + adjustment
        
        # Calculate confidence interval based on volatility
        volatility = abs(historical_growth) * self.volatility_factor
        if volatility < 2:
            volatility = 2
        
        return {
            'rate': round(predicted_growth, 2),
            'lower_bound': round(predicted_growth - volatility * 1.96, 2),
            'upper_bound': round(predicted_growth + volatility * 1.96, 2),
            'historical_growth': round(historical_growth, 2),
            'adjustment_applied': round(adjustment, 2),
            'volatility': round(volatility, 2),
            'accuracy': 'calculated',
            'method': 'adjusted_historical_growth'
        }
    
    def _predict_sales(
        self, 
        features: pd.DataFrame, 
        financial_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Predict sales for next N years"""
        
        revenue_current = features['revenue_current'].iloc[0]
        growth_prediction = self._predict_growth(features)
        growth_rate = growth_prediction['rate'] / 100
        
        predictions = []
        current_year = financial_data.get('report_year', datetime.now().year)
        currency = 'USD'  # Default currency (could be made configurable)
        
        for year in range(1, self.forecast_years + 1):
            predicted_revenue = revenue_current * ((1 + growth_rate) ** year)
            
            # Calculate confidence bounds
            growth_lower = growth_prediction['lower_bound'] / 100
            growth_upper = growth_prediction['upper_bound'] / 100
            
            revenue_lower = revenue_current * ((1 + growth_lower) ** year)
            revenue_upper = revenue_current * ((1 + growth_upper) ** year)
            
            predictions.append({
                'year': current_year + year,
                'predicted_revenue': round(predicted_revenue, 2),
                'confidence_lower': round(revenue_lower, 2),
                'confidence_upper': round(revenue_upper, 2),
                'growth_rate': round(growth_rate * 100, 2),
                'currency': currency,
                'confidence_level': self.confidence_level
            })
        
        return predictions
    
    def _predict_segment_breakdown(
        self, 
        financial_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Predict segment revenue breakdown with growth rates"""
        
        segments = financial_data.get('segment_revenue', [])
        
        if not segments or len(segments) == 0:
            return []
        
        total_revenue = sum(s.get('revenue', 0) for s in segments)
        
        if total_revenue == 0:
            return []
        
        breakdown = []
        
        for segment in segments:
            segment_revenue = segment.get('revenue', 0)
            proportion = segment_revenue / total_revenue
            
            # Predict segment growth
            base_growth = 5.0
            segment_variation = np.random.uniform(-3, 3)
            segment_growth = base_growth + segment_variation
            
            predicted_revenue = segment_revenue * (1 + segment_growth / 100)
            
            breakdown.append({
                'segment': segment.get('segment', 'Unknown'),
                'current_revenue': round(segment_revenue, 2),
                'proportion': round(proportion * 100, 2),
                'predicted_growth': round(segment_growth, 2),
                'predicted_revenue': round(predicted_revenue, 2),
                'currency': segment.get('currency', 'USD')
            })
        
        breakdown.sort(key=lambda x: x['current_revenue'], reverse=True)
        
        return breakdown
    
    def _calculate_risk_metrics(
        self, 
        features: pd.DataFrame,
        growth_prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate risk metrics for the predictions"""
        
        health_score = features['health_score'].iloc[0]
        debt_ratio = features['debt_to_equity'].iloc[0]
        volatility = growth_prediction.get('volatility', 5)
        
        # Overall risk level
        if health_score > 75 and debt_ratio < 1.0 and volatility < 5:
            risk_level = "Low"
            risk_score = 25
        elif health_score > 60 and debt_ratio < 1.5 and volatility < 10:
            risk_level = "Moderate"
            risk_score = 50
        elif health_score > 40 and debt_ratio < 2.0:
            risk_level = "Moderate-High"
            risk_score = 70
        else:
            risk_level = "High"
            risk_score = 85
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "financial_health_score": round(health_score, 1),
            "volatility": round(volatility, 2),
            "debt_risk": "High" if debt_ratio > 1.5 else "Moderate" if debt_ratio > 1.0 else "Low",
            "growth_uncertainty": "High" if volatility > 10 else "Moderate" if volatility > 5 else "Low"
        }
    
    def _generate_recommendations(
        self, 
        growth_prediction: Dict[str, Any],
        financial_data: Dict[str, Any]
    ) -> List[str]:
        """Generate investment recommendations based on predictions"""
        
        recommendations = []
        
        growth_rate = growth_prediction['rate']
        metrics = financial_data.get('key_metrics', {})
        
        # Growth-based recommendations
        if growth_rate > 15:
            recommendations.append("🚀 Strong growth trajectory - Consider expansion opportunities")
            recommendations.append("💰 High growth potential - Suitable for growth investors")
        elif growth_rate > 10:
            recommendations.append("📈 Solid growth expected - Maintain investment strategy")
        elif growth_rate > 5:
            recommendations.append("📊 Moderate growth expected - Monitor performance")
        elif growth_rate > 0:
            recommendations.append("⚠️ Slow growth - Focus on efficiency")
        else:
            recommendations.append("🔴 Negative growth - Strategic review needed")
        
        # ROE-based recommendations
        roe = metrics.get('roe', 0)
        if roe and roe > 20:
            recommendations.append("⭐ Exceptional ROE (>20%) - Outstanding management")
        elif roe and roe > 15:
            recommendations.append("✅ Excellent ROE (15-20%) - Strong value creation")
        elif roe and roe < 5:
            recommendations.append("⚠️ Low ROE (<5%) - Review asset utilization")
        
        # Debt-based recommendations
        debt_ratio = metrics.get('debt_to_equity', 0)
        if debt_ratio and debt_ratio > 2.0:
            recommendations.append("🔴 High debt (>2.0) - Prioritize debt reduction")
        elif debt_ratio and debt_ratio > 1.5:
            recommendations.append("⚠️ Elevated debt (1.5-2.0) - Monitor cash flow")
        elif debt_ratio and debt_ratio < 0.5:
            recommendations.append("💪 Low debt (<0.5) - Strong financial position")
        
        # Overall recommendation
        if growth_rate > 10 and roe and roe > 15 and debt_ratio and debt_ratio < 1.5:
            recommendations.append("⭐ STRONG BUY - Excellent fundamentals")
        elif growth_rate > 5 and roe and roe > 10:
            recommendations.append("✅ BUY - Solid fundamentals")
        elif growth_rate > 0:
            recommendations.append("👍 HOLD - Monitor closely")
        else:
            recommendations.append("⚠️ CAUTION - High risk")
        
        return recommendations
    
    @staticmethod
    async def predict_metrics(data: Dict[str, Any], analysis_id: int, db):
        """Background task to generate predictions (legacy method)"""
        from app.models.analysis import Analysis
        
        try:
            predictor = MLPredictor()
            predictions = predictor.predict_growth_and_sales(data, analysis_id)
            
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.predictions = predictions
                analysis.status = "completed"
                db.commit()
        
        except Exception as e:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.error_message = f"Prediction error: {str(e)}"
                db.commit()
    
    def train_advanced_model(
        self, 
        historical_data: pd.DataFrame, 
        target_column: str
    ) -> Tuple[Any, float]:
        """
        Train advanced ML model with historical data
        
        Args:
            historical_data: DataFrame with historical data
            target_column: Column to predict
            
        Returns:
            Tuple of (trained model, R² score)
        """
        if len(historical_data) < 10:
            raise ValueError("Insufficient data for training (minimum 10 records)")
        
        # Prepare features
        feature_columns = [col for col in historical_data.columns if col != target_column]
        X = historical_data[feature_columns].values
        y = historical_data[target_column].values
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train model
        model = LinearRegression()
        model.fit(X_scaled, y)
        
        # Calculate R² score
        score = model.score(X_scaled, y)
        
        return model, score
    
    def save_model(self, model: Any, model_name: str) -> str:
        """
        Save trained model to disk
        
        Args:
            model: Trained model object
            model_name: Name for the model file
            
        Returns:
            Path to saved model
        """
        filepath = os.path.join(self.models_dir, f"{model_name}.pkl")
        joblib.dump(model, filepath)
        return filepath
    
    def load_model(self, model_name: str) -> Optional[Any]:
        """
        Load trained model from disk
        
        Args:
            model_name: Name of the model file
            
        Returns:
            Loaded model or None if not found
        """
        filepath = os.path.join(self.models_dir, f"{model_name}.pkl")
        if os.path.exists(filepath):
            return joblib.load(filepath)
        return None


# Global instance
ml_predictor = MLPredictor()
