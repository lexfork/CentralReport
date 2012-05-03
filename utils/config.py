# CentralReport - Indev version
# Project by Charles-Emmanuel CAMUS - Avril 2012

__author__ = 'che'

from collectors.Collector import Collector
import ConfigParser, os, uuid

class ConfigGetter:

    config = ConfigParser.ConfigParser()
    uuid = ""
    config_enable_check_memory = True
    config_enable_check_cpu = True
    config_enable_check_loadaverage = True
    config_server_addr = ""

    config_webserver_enable = True
    config_webserver_interface = '0.0.0.0'
    config_webserver_port = 8080

    def __init__(self):

        if Collector.isMac():
            # On est sur Mac. Test du repertoire
            if os.path.isdir("/etc/cr") != True:
                # Creation du dossier
                os.mkdir("/etc/cr")

            ConfigGetter.chemin = "/etc/cr/"
            print("Mac config")
        else:
            # On est sur un systeme Linux

            if os.path.isdir("/etc/cr") != True:
                # Creation du dossier
                os.mkdir("/etc/cr")
            ConfigGetter.chemin = "/etc/cr/"
            print("Linux config")


        # Fichier de utils existe ?
        config = ConfigParser.ConfigParser()
        if os.path.isfile(ConfigGetter.chemin +'centralreport.cfg'):
            print('Fichier de conf : Existant. Lecture.')
        else:
            print('Fichier de conf : Inexistant. Creation.')

            # On ecrit le fichier de conf
            config.add_section('General')
            config.set('General', 'uuid', uuid.uuid1())
            config.add_section('Network')
            config.set('Network', 'enable_check_cpu', True)
            config.set('Network', 'enable_check_memory', True)
            config.set('Network', 'enable_check_loadaverage', True)
            config.set("Network", 'server_addr', 'localhost:8888')
            config.add_section('Webserver')
            config.set("Webserver", 'enable', True)
            config.set("Webserver", 'interface', '0.0.0.0')
            config.set("Webserver", 'port', '8080')


            config.write(open(ConfigGetter.chemin +'centralreport.cfg','w'))

        # Lecture du fichier de utils
        config.read(ConfigGetter.chemin +'centralreport.cfg')

        ConfigGetter.uuid = config.get('General', 'uuid')
        ConfigGetter.config_enable_check_memory = config.getboolean("Network","enable_check_memory")
        ConfigGetter.config_enable_check_cpu = config.getboolean("Network","enable_check_cpu")
        ConfigGetter.config_enable_check_loadaverage = config.getboolean("Network","enable_check_loadaverage")
        ConfigGetter.config_server_addr = config.get("Network",'server_addr')
        ConfigGetter.config_webserver_enable = config.getboolean("Webserver","enable")
        ConfigGetter.config_webserver_interface = config.get("Webserver","interface")
        ConfigGetter.config_webserver_port = config.getint("Webserver","port")
