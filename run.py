from multiprocessing import Process
from signals_bot.main import main
from core import check_expirations
import asyncio
import time


def run_welcome_bot():
    print("Welcome bot running...")
    asyncio.run(main())

def run_signal_receiver():
    print("Signal receiver running...")
    Process(target=main).start()
    asyncio.run(main())


def run_check_expirations():
    print("Check expirations running...")
    while True:
        check_expirations.check_if_expired()
        time.sleep(3600)

def run_all():
    p1 = Process(target=run_welcome_bot)
    p2 = Process(target=run_signal_receiver)
    p3 = Process(target=run_check_expirations)

    p1.start()
    p2.start()
    p3.start()


    p1.join()
    p2.join()
    p3.join()


if __name__ == "__main__":
    run_all()