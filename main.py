import logging

from newsbot import bot


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    bot_ = bot.Bot(a_token='2130893067:AAFL3ERuk30SIcbONhAOV0KZW4PLFzR2D1A')

    bot_.start()
    # bot_.stop()
