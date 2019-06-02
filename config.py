import configparser
config = configparser.ConfigParser()
config.read('config.ini')
if config["DEFAULT"]["DEV"]:
    config = config['DEV']
else:
    config = config['PROD']