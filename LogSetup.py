from logging import Logger, Formatter, FileHandler, StreamHandler, getLogger, DEBUG, ERROR
from sys import stdout

def CreateLogger(name:str) -> Logger:
    logger: Logger = getLogger(name)
    format: Formatter = Formatter(
        "%(asctime)s | %(name)s.%(threadName)s | %(levelname)s | %(message)s",
        datefmt="%d %b %y %H:%M:%S"
    )
    logger.setLevel(DEBUG)

    # File Handler
    fileHandler: FileHandler = FileHandler('BR.log')
    fileHandler.setLevel(DEBUG)
    fileHandler.setFormatter(format)
    logger.addHandler(fileHandler)

    # Stream Handler (Console)
    streamHandler: StreamHandler = StreamHandler(stdout)
    streamHandler.setLevel(ERROR)
    streamHandler.setFormatter(format)
    logger.addHandler(streamHandler)

    return logger