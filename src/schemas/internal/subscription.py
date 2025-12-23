from enum import Enum


class SubscriptionPlan(str, Enum):
    FREE = 'free'
    PREMIUM = 'premium'
    PRO = 'pro'
