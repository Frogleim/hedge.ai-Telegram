from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import User, Wallets
from . import loggs_handler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

class DB:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _connect_db(self):
        try:
            # Ensure the tables are created in the database
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
                # Use .first() to avoid exception if no user is found
                user = session.query(User).filter(User.telegram_id == str(user_data['telegram_id'])).first()
                if user:
                    return False  # User already exists

                if user_data['status'] == "payed":
                    trial_start = None
                    trial_end = None
                    expiry_date = datetime.utcnow() + timedelta(days=30)
                else:
                    trial_start = datetime.utcnow()
                    trial_end = datetime.utcnow() + timedelta(days=1)
                    expiry_date = None

                new_user = User(
                    telegram_id=user_data['telegram_id'],
                    telegram_username=user_data['telegram_username'],
                    status=user_data['status'],
                    trial_start=trial_start,
                    trial_end=trial_end,
                    expiry_date=expiry_date,
                    payment_type=user_data['payment_type']
                )

                session.add(new_user)
                session.commit()
                loggs_handler.system_log.info(f"New user created. User ID: {user_data['telegram_id']}")
                return True
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while storing data: {e}')
                session.rollback()
            finally:
                session.close()

    def change_user_status(self, user_id, status):
        session = self._connect_db()
        if session:
            try:
                user = session.query(User).filter(User.telegram_id == str(user_id)).first()
                if user:
                    user.status = status
                    session.commit()
                    loggs_handler.system_log.info(f"User status changed to {status} User ID: {user.telegram_id}")
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while updating user: {e}')
            finally:
                session.close()

    def update_payment_method(self, user_id, payment_type):
        session = self._connect_db()
        if session:
            try:
                user = session.query(User).filter(User.telegram_id == str(user_id)).first()
                if user:
                    user.payment_type = payment_type
                    session.commit()
                    loggs_handler.system_log.info(f"User payment type changed to {payment_type} User ID: {user.telegram_id}")
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while updating user payment type: {e}')
            finally:
                session.close()

    def add_wallet(self, new_wallet):
        session = self._connect_db()
        if session:
            try:
                wallet = Wallets(
                    wallet_address=new_wallet['wallet_address'],
                    wallet_network=new_wallet['wallet_network'],
                )
                session.add(wallet)
                session.commit()
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while saving wallet: {e}')
            finally:
                session.close()

    def get_wallet_address(self, crypto_type):
        """ Fetch the wallet address for a given cryptocurrency type (TRC20, ERC20, Solana, Bitcoin). """
        session = self._connect_db()
        if session:
            try:
                wallet = session.query(Wallets).filter(Wallets.wallet_network == crypto_type).first()
                return wallet.wallet_address if wallet else None
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while fetching wallet address: {e}')
                return None
            finally:
                session.close()

    def check_user(self, telegram_id):
        session = self._connect_db()
        if session:
            try:
                user = session.query(User).filter(User.telegram_id == str(telegram_id)).first()
                expire_date = user.expiry_date
                trial_end = user.trial_end
                if expire_date and trial_end and expire_date > datetime.utcnow() and trial_end > datetime.utcnow():
                    new_status = "expired"
                    db.change_user_status(telegram_id, new_status)
                    return False

                if user.status == "paid" or user.status == 'trial':
                    return True
                else:
                    return False
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while fetching user: {e}')
                pass


    def get_all_active_users(self):

        """Get Active Users"""

        session = self._connect_db()
        active_users = []

        if session:
            users = session.query(User).all()
            for user in users:
                if user.status == "payed" or user.status == "trial":
                    active_users.append(user.telegram_id)
            return active_users


if __name__ == "__main__":
    user_data = {
        "telegram_id": 1234,
        "telegram_username": "frogleim",
        "status": 'trial',
        'payment_type': "not payed",
    }

    wallet_data = {
        "wallet_address": '1KZh7uzKTHjZHt9q7Z6ikpeAJ6Fv98VVhe',
        "wallet_network": "Bitcoin",
    }

    db = DB()
    # db.add_new_user(user_data)
    # db.change_user_status(user_data['user_id'], 'inactive')
    # db.add_wallet(wallet_data)

    # # Test wallet retrieval
    # crypto_type = "Bitcoin"
    # wallet_address = db.get_wallet_address(crypto_type)
    # print(f"Wallet address for {crypto_type}: {wallet_address}")
    active_users = db.get_all_active_users()
    print(active_users)