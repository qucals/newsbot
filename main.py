import logging

from newsbot import bot


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    bot_ = bot.Bot()

    bot_.start()
    # bot_.stop()
