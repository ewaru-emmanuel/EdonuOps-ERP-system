"""
Currency and Exchange Rate Models for Multi-Currency Support
Uses ExchangeRate-API (free, no limits) for live forex data
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app import db

class Currency(db.Model):
    """
    Currency master data with support for all global currencies
    """
    __tablename__ = 'currencies'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True, nullable=False, index=True)  # ISO 4217 code (USD, EUR, etc.)
    name = Column(String(100), nullable=False)  # US Dollar, Euro, etc.
    symbol = Column(String(10), nullable=False)  # $, €, £, etc.
    decimal_places = Column(Integer, default=2)  # Number of decimal places
    is_active = Column(Boolean, default=True)
    is_base_currency = Column(Boolean, default=False)  # Company's base currency
    country = Column(String(100))  # Primary country using this currency
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    exchange_rates_from = relationship("ExchangeRate", foreign_keys="ExchangeRate.from_currency_id", back_populates="from_currency")
    exchange_rates_to = relationship("ExchangeRate", foreign_keys="ExchangeRate.to_currency_id", back_populates="to_currency")
    
    def __repr__(self):
        return f'<Currency {self.code}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'symbol': self.symbol,
            'decimal_places': self.decimal_places,
            'is_active': self.is_active,
            'is_base_currency': self.is_base_currency,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_base_currency(cls):
        """Get the company's base currency"""
        return cls.query.filter_by(is_base_currency=True).first()
    
    @classmethod
    def get_active_currencies(cls):
        """Get all active currencies"""
        return cls.query.filter_by(is_active=True).order_by(cls.code).all()


class ExchangeRate(db.Model):
    """
    Exchange rates between currencies with historical tracking
    Sourced from ExchangeRate-API
    """
    __tablename__ = 'exchange_rates'
    
    id = Column(Integer, primary_key=True)
    from_currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    to_currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    rate = Column(Float, nullable=False)  # Exchange rate (1 from_currency = rate * to_currency)
    inverse_rate = Column(Float, nullable=False)  # Inverse rate for quick lookups
    date = Column(DateTime, nullable=False, index=True)  # Rate effective date
    source = Column(String(50), default='ExchangeRate-API')  # Data source
    is_current = Column(Boolean, default=True, index=True)  # Latest rate flag
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    from_currency = relationship("Currency", foreign_keys=[from_currency_id], back_populates="exchange_rates_from")
    to_currency = relationship("Currency", foreign_keys=[to_currency_id], back_populates="exchange_rates_to")
    
    # Ensure unique current rates per currency pair
    __table_args__ = (
        UniqueConstraint('from_currency_id', 'to_currency_id', 'is_current', 
                        name='unique_current_rate_per_pair'),
    )
    
    def __repr__(self):
        return f'<ExchangeRate {self.from_currency.code}->{self.to_currency.code}: {self.rate}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_currency_code': self.from_currency.code,
            'to_currency_code': self.to_currency.code,
            'from_currency_name': self.from_currency.name,
            'to_currency_name': self.to_currency.name,
            'rate': self.rate,
            'inverse_rate': self.inverse_rate,
            'date': self.date.isoformat() if self.date else None,
            'source': self.source,
            'is_current': self.is_current,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_current_rate(cls, from_currency_code, to_currency_code):
        """Get current exchange rate between two currencies"""
        return cls.query.join(
            Currency, cls.from_currency_id == Currency.id
        ).join(
            Currency.query.filter_by(code=to_currency_code).subquery(), 
            cls.to_currency_id == Currency.id
        ).filter(
            Currency.code == from_currency_code,
            cls.is_current == True
        ).first()
    
    @classmethod
    def get_historical_rates(cls, from_currency_code, to_currency_code, days=30):
        """Get historical exchange rates for a currency pair"""
        from sqlalchemy import desc
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        return cls.query.join(
            Currency, cls.from_currency_id == Currency.id
        ).join(
            Currency.query.filter_by(code=to_currency_code).subquery(), 
            cls.to_currency_id == Currency.id
        ).filter(
            Currency.code == from_currency_code,
            cls.date >= cutoff_date
        ).order_by(desc(cls.date)).all()


class CurrencyConversion(db.Model):
    """
    Track currency conversions for audit trails
    """
    __tablename__ = 'currency_conversions'
    
    id = Column(Integer, primary_key=True)
    from_currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    to_currency_id = Column(Integer, ForeignKey('currencies.id'), nullable=False)
    original_amount = Column(Float, nullable=False)
    converted_amount = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    conversion_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reference_type = Column(String(50))  # 'account', 'transaction', 'report', etc.
    reference_id = Column(Integer)  # ID of related record
    notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    from_currency = relationship("Currency", foreign_keys=[from_currency_id])
    to_currency = relationship("Currency", foreign_keys=[to_currency_id])
    
    def __repr__(self):
        return f'<Conversion {self.original_amount} {self.from_currency.code} -> {self.converted_amount} {self.to_currency.code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_currency_code': self.from_currency.code,
            'to_currency_code': self.to_currency.code,
            'original_amount': self.original_amount,
            'converted_amount': self.converted_amount,
            'exchange_rate': self.exchange_rate,
            'conversion_date': self.conversion_date.isoformat() if self.conversion_date else None,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
