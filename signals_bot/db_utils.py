from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Wallets
import loggs_handler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL='postgresql://virtuum_owner:npg_A2rhO4MTipyW@ep-ancient-dew-a5zf8onm-pooler.us-east-2.aws.neon.tech/virtuum?sslmode=require'


class DB:
    def __init__(self):
        self.db_url = DATABASE_URL
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

    def update_user_data(self, username, data):
        session = self._connect_db()
        if session:
            try:
                user = session.query(User).filter(User.telegram_username == str(username)).first()
                if user:
                    user.telegram_id = data
                    session.commit()
                    loggs_handler.system_log.info(f"User data updated. User ID: {user.telegram_username}")
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while updating user: {e}')
            finally:
                session.close()

    def change_user_status(self, username, status):
        session = self._connect_db()
        if session:
            try:
                user = session.query(User).filter(User.telegram_username == str(username)).first()
                if user:
                    user.status = status
                    session.commit()
                    loggs_handler.system_log.info(f"User status changed to {status} User ID: {user.telegram_username}")
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while updating user: {e}')
            finally:
                session.close()

    def update_payment_method(self, username, payment_type):
        session = self._connect_db()
        if session:
            try:
                user = session.query(User).filter(User.telegram_username == str(username)).first()
                if user:
                    user.payment_type = payment_type
                    session.commit()
                    loggs_handler.system_log.info(f"User payment type changed to {payment_type} User ID: {user.telegram_username}")
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

    def check_user(self, username):
        session = self._connect_db()
        if session:
            try:
                user = session.query(User).filter(User.telegram_username == str(username)).first()
                print(user.trial)
                print(user.paid)
                if not (user.trial or user.paid):
                    return False
                else:
                    return True
            except Exception as e:
                loggs_handler.error_logs_logger.error(f'Error while fetching user: {e}')
                return False




    def get_all_active_users(self):

        """Get Active Users"""

        session = self._connect_db()
        active_users = []
        if session:
            users = session.query(User).all()
            for user in users:
                if user.paid or user.trial:
                    active_users.append(user.telegram_id)
                    print(active_users)
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

    active_users = db.get_all_active_users()
    print(active_users)