from sqlalchemy import Column, DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class CurrencyExchangeRate(Base):
    __tablename__ = "currency_exchange_rates"

    date_key = Column(String(10), primary_key=True)
    recorded_at = Column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    reference_currency = Column(String(3), nullable=False, default="USD")
    rate_usd = Column(Numeric(10, 4), nullable=True)
    rate_eur = Column(Numeric(10, 4), nullable=True)
    rate_jpy = Column(Numeric(10, 4), nullable=True)
    rate_gbp = Column(Numeric(10, 4), nullable=True)
    rate_aud = Column(Numeric(10, 4), nullable=True)
    rate_cad = Column(Numeric(10, 4), nullable=True)
    rate_chf = Column(Numeric(10, 4), nullable=True)
    rate_cny = Column(Numeric(10, 4), nullable=True)
    rate_sek = Column(Numeric(10, 4), nullable=True)
    rate_mxn = Column(Numeric(10, 4), nullable=True)
    rate_nzd = Column(Numeric(10, 4), nullable=True)
    rate_sgd = Column(Numeric(10, 4), nullable=True)
    rate_hkd = Column(Numeric(10, 4), nullable=True)
    rate_nok = Column(Numeric(10, 4), nullable=True)
    rate_krw = Column(Numeric(10, 4), nullable=True)
    rate_try = Column(Numeric(10, 4), nullable=True)
    rate_inr = Column(Numeric(10, 4), nullable=True)
    rate_rub = Column(Numeric(10, 4), nullable=True)
    rate_brl = Column(Numeric(10, 4), nullable=True)
    rate_zar = Column(Numeric(10, 4), nullable=True)
    rate_dkk = Column(Numeric(10, 4), nullable=True)
    rate_pln = Column(Numeric(10, 4), nullable=True)
    rate_twd = Column(Numeric(10, 4), nullable=True)
    rate_thb = Column(Numeric(10, 4), nullable=True)
    rate_myr = Column(Numeric(10, 4), nullable=True)