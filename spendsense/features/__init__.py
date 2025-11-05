"""
Behavioral signal detection and feature engineering module.

This module provides utilities for analyzing user financial data to detect
behavioral patterns including subscriptions, savings, credit utilization,
and income stability.
"""

from spendsense.features.time_windows import TimeWindowCalculator
from spendsense.features.subscription_detector import SubscriptionDetector, SubscriptionMetrics, DetectedSubscription
from spendsense.features.savings_detector import SavingsDetector, SavingsMetrics
from spendsense.features.credit_detector import CreditDetector, CreditMetrics, PerCardUtilization
from spendsense.features.income_detector import IncomeDetector, IncomeMetrics
from spendsense.features.behavioral_summary import BehavioralSummaryGenerator, BehavioralSummary

__all__ = [
    'TimeWindowCalculator',
    'SubscriptionDetector',
    'SubscriptionMetrics',
    'DetectedSubscription',
    'SavingsDetector',
    'SavingsMetrics',
    'CreditDetector',
    'CreditMetrics',
    'PerCardUtilization',
    'IncomeDetector',
    'IncomeMetrics',
    'BehavioralSummaryGenerator',
    'BehavioralSummary'
]
