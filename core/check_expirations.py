import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User  # Assuming this is where your SQLAlchemy model is defined
from dotenv import load_dotenv

load_dotenv()

# Setup your database connection
DATABASE_URL = os.getenv('DATABASE_URL')  # Replace with your actual database URL
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def check_if_expired():
    # Create a session to query the database
    session = Session()

    current = datetime.now()
    print("Checking expirations...")
    users = session.query(User).all()

    for user in users:
        if user.expiry_date:
            expiry_timestamp = user.expiry_date.timestamp()  # Convert to float

        if user.trial_end:
            trial_timestamp = user.trial_end.timestamp()  # Convert to float

        current_timestamp = datetime.now().timestamp()

        # Compare using float values
        if user.expiry_date and expiry_timestamp < current_timestamp:
            if user.status != "expired":
                user.status = "expired"
                session.commit()

        if user.trial_end and trial_timestamp < current_timestamp:
            if user.status != "expired":
                user.status = "expired"
                session.commit()  # Save the changes to the database
    print("Done")
    session.close()  # Always close the session when done

if __name__ == "__main__":
    import time

    while True:
        check_if_expired()
        time.sleep(24 * 3600)  # Wait for 24 hours before running again