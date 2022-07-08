############################################################################
# AUTHORS: Pedro Margolles & David Soto
# EMAIL: pmargolles@bcbl.eu, dsoto@bcbl.eu
# COPYRIGHT: Copyright (C) 2021-2022, pyDecNef
# URL: https://pedromargolles.github.io/pyDecNef/
# INSTITUTION: Basque Center on Cognition, Brain and Language (BCBL), Spain
# LICENCE: GNU General Public License v3.0
############################################################################

#############################################################################################
# DESCRIPTION
#############################################################################################

# Here are indicated class objects instantiated in main.py which are then shared across all framework modules
# as global variables to facilitate processing in threads and returning results, and sychronization between modules

server = None # Corresponding class in modules/config/connection_config.py
timeseries = None # Corresponding class in modules/classes/classes.py
new_trial = None # Corresponding class in modules/classes/classes.py
watcher = None # Corresponding class in modules/classes/classes.py
listener = None # Corresponding class in modules/config/listener.py
logger = None # Corresponding class in modules/classes/classes.py
new_vol = None # Corresponding class in modules/classes/classes.py