"""
SQLite database writer for data storage.

This module provides database storage using SQLAlchemy ORM with support
for batch inserts and foreign key constraints.
"""

import json
import logging
from datetime import date as date_type
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import create_engine, Column, String, Integer, Float, Date, Boolean, JSON, Text, ForeignKey, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


# ===== Database Models =====

class User(Base):
    """User profile table."""
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True)
    name = Column(String)
    persona = Column(String)
    annual_income = Column(Float)
    characteristics = Column(JSON)  # Stores dict as JSON

    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    """Account table."""
    __tablename__ = 'accounts'

    account_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    type = Column(String)
    subtype = Column(String)
    iso_currency_code = Column(String, default="USD")
    holder_category = Column(String, default="personal")

    # Balance fields (flattened from nested balances object)
    balance_current = Column(Float)
    balance_available = Column(Float, nullable=True)
    balance_limit = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class Transaction(Base):
    """Transaction table."""
    __tablename__ = 'transactions'

    transaction_id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey('accounts.account_id'))
    date = Column(Date)
    amount = Column(Float)
    merchant_name = Column(String, nullable=True)
    merchant_entity_id = Column(String, nullable=True)
    payment_channel = Column(String)
    personal_finance_category = Column(String)
    pending = Column(Boolean, default=False)

    # Relationships
    account = relationship("Account", back_populates="transactions")


class Liability(Base):
    """Liability table (supports credit cards, student loans, mortgages)."""
    __tablename__ = 'liabilities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, ForeignKey('accounts.account_id'))
    liability_type = Column(String)  # 'credit_card', 'student_loan', 'mortgage'

    # Common fields
    interest_rate = Column(Float, nullable=True)
    next_payment_due_date = Column(Date, nullable=True)

    # Credit card specific fields
    aprs = Column(JSON, nullable=True)  # List of APRs
    minimum_payment_amount = Column(Float, nullable=True)
    last_payment_amount = Column(Float, nullable=True)
    last_statement_balance = Column(Float, nullable=True)
    is_overdue = Column(Boolean, nullable=True)


class PersonaAssignmentRecord(Base):
    """
    Persona assignment records with complete audit trail.

    Stores persona assignments per user per time window with full decision
    history including all qualifying personas, match evidence, and prioritization logic.
    """
    __tablename__ = 'persona_assignments'

    assignment_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    time_window = Column(String, nullable=False)  # "30d" or "180d"
    assigned_persona_id = Column(String, nullable=False)  # Persona ID or "unclassified"
    assigned_at = Column(DateTime, nullable=False)
    priority = Column(Integer, nullable=True)  # None for unclassified
    qualifying_personas = Column(JSON, nullable=False)  # List[str] of persona IDs
    match_evidence = Column(JSON, nullable=False)  # Dict[str, Dict] with evidence per persona
    prioritization_reason = Column(Text, nullable=False)
    signal_id = Column(String, nullable=True)  # Future: link to behavioral_signals table

    # Performance index for common queries
    __table_args__ = (
        Index('idx_assignments_user_window', 'user_id', 'time_window'),
    )


class DatabaseWriter:
    """
    Database writer for storing validated data in SQLite.

    Provides batch insert capabilities and manages schema creation.
    """

    def __init__(self, db_path: Path):
        """
        Initialize the database writer.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_tables(self):
        """Create all database tables if they don't exist."""
        Base.metadata.create_all(self.engine)
        self.logger.info("Database tables created/verified")

    def _convert_to_float(self, value: Any) -> float:
        """Convert Decimal or string to float for SQLite storage."""
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return value

    def write_users(self, users: List[Dict[str, Any]]) -> int:
        """
        Write user records to database.

        Args:
            users: List of user dictionaries

        Returns:
            Number of users written
        """
        session = self.Session()
        try:
            for user_data in users:
                user = User(
                    user_id=user_data['user_id'],
                    name=user_data.get('name'),
                    persona=user_data.get('persona'),
                    annual_income=self._convert_to_float(user_data.get('annual_income')),
                    characteristics=user_data.get('characteristics', {})
                )
                session.merge(user)  # Use merge to handle updates

            session.commit()
            self.logger.info(f"Wrote {len(users)} users to database")
            return len(users)
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to write users: {e}")
            raise
        finally:
            session.close()

    def write_accounts(self, accounts: List[Dict[str, Any]]) -> int:
        """
        Write account records to database.

        Args:
            accounts: List of account dictionaries

        Returns:
            Number of accounts written
        """
        session = self.Session()
        try:
            for account_data in accounts:
                # Extract balances
                balances = account_data.get('balances', {})
                if isinstance(balances, dict):
                    balance_current = self._convert_to_float(balances.get('current'))
                    balance_available = self._convert_to_float(balances.get('available'))
                    balance_limit = self._convert_to_float(balances.get('limit'))
                else:
                    # Fallback for flat structure
                    balance_current = self._convert_to_float(account_data.get('initial_balance') or account_data.get('balance_current'))
                    balance_available = self._convert_to_float(account_data.get('balance_available'))
                    balance_limit = self._convert_to_float(account_data.get('limit') or account_data.get('balance_limit'))

                account = Account(
                    account_id=account_data['account_id'],
                    user_id=account_data.get('user_id'),
                    type=account_data.get('type'),
                    subtype=account_data.get('subtype'),
                    iso_currency_code=account_data.get('iso_currency_code', 'USD'),
                    holder_category=account_data.get('holder_category', 'personal'),
                    balance_current=balance_current,
                    balance_available=balance_available,
                    balance_limit=balance_limit
                )
                session.merge(account)

            session.commit()
            self.logger.info(f"Wrote {len(accounts)} accounts to database")
            return len(accounts)
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to write accounts: {e}")
            raise
        finally:
            session.close()

    def write_transactions(self, transactions: List[Dict[str, Any]]) -> int:
        """
        Write transaction records to database.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Number of transactions written
        """
        session = self.Session()
        try:
            for txn_data in transactions:
                # Parse date if string
                txn_date = txn_data.get('date')
                if isinstance(txn_date, str):
                    txn_date = date_type.fromisoformat(txn_date)

                transaction = Transaction(
                    transaction_id=txn_data['transaction_id'],
                    account_id=txn_data['account_id'],
                    date=txn_date,
                    amount=self._convert_to_float(txn_data.get('amount')),
                    merchant_name=txn_data.get('merchant_name'),
                    merchant_entity_id=txn_data.get('merchant_entity_id'),
                    payment_channel=txn_data.get('payment_channel'),
                    personal_finance_category=txn_data.get('personal_finance_category'),
                    pending=txn_data.get('pending', False)
                )
                session.merge(transaction)

            session.commit()
            self.logger.info(f"Wrote {len(transactions)} transactions to database")
            return len(transactions)
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to write transactions: {e}")
            raise
        finally:
            session.close()

    def write_liabilities(self, liabilities: List[Dict[str, Any]]) -> int:
        """
        Write liability records to database.

        Args:
            liabilities: List of liability dictionaries (credit cards, loans)

        Returns:
            Number of liabilities written
        """
        session = self.Session()
        try:
            count = 0
            for liab_data in liabilities:
                # Determine liability type from data structure
                if 'aprs' in liab_data or 'minimum_payment_amount' in liab_data:
                    liability_type = 'credit_card'
                elif 'interest_rate' in liab_data:
                    # Differentiate between student loan and mortgage by account_id or context
                    account_id = liab_data.get('account_id', '')
                    if 'student' in account_id:
                        liability_type = 'student_loan'
                    elif 'mortgage' in account_id:
                        liability_type = 'mortgage'
                    else:
                        liability_type = 'loan'  # Generic
                else:
                    liability_type = 'unknown'

                # Parse date if string
                next_due_date = liab_data.get('next_payment_due_date')
                if isinstance(next_due_date, str):
                    next_due_date = date_type.fromisoformat(next_due_date)

                # Convert APRs list
                aprs = liab_data.get('aprs')
                if aprs and isinstance(aprs, list):
                    aprs = [self._convert_to_float(apr) for apr in aprs]

                liability = Liability(
                    account_id=liab_data.get('account_id'),
                    liability_type=liability_type,
                    interest_rate=self._convert_to_float(liab_data.get('interest_rate')),
                    next_payment_due_date=next_due_date,
                    aprs=aprs,
                    minimum_payment_amount=self._convert_to_float(liab_data.get('minimum_payment_amount')),
                    last_payment_amount=self._convert_to_float(liab_data.get('last_payment_amount')),
                    last_statement_balance=self._convert_to_float(liab_data.get('last_statement_balance')),
                    is_overdue=liab_data.get('is_overdue')
                )
                session.add(liability)
                count += 1

            session.commit()
            self.logger.info(f"Wrote {count} liabilities to database")
            return count
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to write liabilities: {e}")
            raise
        finally:
            session.close()

    def clear_all_data(self):
        """Clear all data from all tables (for testing)."""
        session = self.Session()
        try:
            session.query(Transaction).delete()
            session.query(Liability).delete()
            session.query(Account).delete()
            session.query(User).delete()
            session.commit()
            self.logger.info("Cleared all data from database")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to clear database: {e}")
            raise
        finally:
            session.close()
