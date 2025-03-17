from .models import User, Wallets
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import loggs_handler
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class DB:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _connect_db(self):
        try:
            User.metadata.create_all(self.engine)
            session = self.SessionLocal()
            return session
        except Exception as e:
            loggs_handler.error_logs_logger.error(f'Error while connecting to db: {e}')
            return None

    def add_new_user(self, user_data):
        session = self._connect_db()
        if session:
            try:
                if user_data['status'] == "payed":
                    trial_start = None
                    trial_end = None
                    expiry_date = datetime.utcnow() + timedelta(days=30)
                else:
                    trial_start = datetime.utcnow()
                    trial_end = datetime.utcnow() + timedelta(days=7)
                    expiry_date = None

                new_user = User(
                    user_id=user_data['user_id'],
                    status=user_data['status'],
                    trial_start=trial_start,
                    trial_end=trial_end,
                    expiry_date=expiry_date,
                    payment_type=user_data['payment_type']
                )

                session.add(new_user)
                session.commit()
                loggs_handler.system_log.info(f"New user created. User ID: {user_data['user_id']}")
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while storing data: {e}')
                session.rollback()
            finally:
                session.close()

    def change_user_status(self, user_id, status):
        session = self._connect_db()
        try:
            user = session.query(User).filter(User.user_id == str(user_id)).one()
            user.status = status
            session.commit()
            loggs_handler.system_log.info(f"User status changed to {status} User ID: {user.user_id}")
        except Exception as e:
            loggs_handler.error_logs_logger.error(f'Error while updating user: {e}')

    def update_payment_method(self, user_id, payment_type):
        session = self._connect_db()
        try:
            user = session.query(User).filter(User.user_id == str(user_id)).one()
            user.payment_type = payment_type
            session.commit()
            loggs_handler.system_log.info(f"User payment type changed to {payment_type} User ID: {user.user_id}")
        except Exception as e:
            loggs_handler.error_logs_logger.error(f'Error while updating user payment type: {e}')

    def add_wallet(self, new_wallet):
        session = self._connect_db()
        try:
            new_wallet = Wallets(
                wallet_address=new_wallet['wallet_address'],
                wallet_network=new_wallet['wallet_network'],
            )
            session.add(new_wallet)
            session.commit()
        except Exception as e:
            loggs_handler.error_logs_logger.error(f'Error while saving wallet: {e}')

    def get_wallet_address(self, crypto_type):
        """ Fetch the wallet address for a given cryptocurrency type (TRC20, ERC20, Solana, Bitcoin). """
        session = self._connect_db()
        try:
            wallet = session.query(Wallets).filter(Wallets.wallet_network == crypto_type).first()
            return wallet.wallet_address if wallet else None
        except Exception as e:
            loggs_handler.error_logs_logger.error(f'Error while fetching wallet address: {e}')
            return None
        finally:
            session.close()


if __name__ == "__main__":
    user_data = {
        "user_id": 1234,
        "status": "payed",
        "payment_type": 'crypto',
    }

    wallet_data = {
        "wallet_address": '1KZh7uzKTHjZHt9q7Z6ikpeAJ6Fv98VVhe',
        "wallet_network": "Bitcoin",
    }

    db = DB()
    # db.add_new_user(user_data)
    # db.change_user_status(user_data['user_id'], 'inactive')
    # db.add_wallet(wallet_data)

    # Test wallet retrieval
    crypto_type = "Bitcoin"
    wallet_address = db.get_wallet_address(crypto_type)
    print(f"Wallet address for {crypto_type}: {wallet_address}")