from modules.config.exp_config import Exp
import pandas as pd
from collections import defaultdict

class Logger(Exp):
    
    def append_data(self, variables_to_log: list):
        if hasattr(self, 'variables_to_log') == False:
            self.variables_to_log = defaultdict(lambda: None) # Create a dictionary with default None values for any key
        for item in variables_to_log: # Iterate over key:value pairs list
            self.variables_to_log[item[0]] # Create a new key in dictionary using first pair item
            try:
                self.variables_to_log[item[0]] = item[1] # If
            except:
                pass # In case a value for a specific key still does not exist
        if hasattr(self, 'dataframe') == False:
            self.dataframe = pd.DataFrame(columns = [key for key in self.variables_to_log.keys()]) # Create an empty dataframe using defaultdict key names
            self._record_vol_data()
        else:
            self._record_vol_data()

    def _record_vol_data(self):
        self.dataframe = self.dataframe.append(self.variables_to_log, ignore_index = True) # Append new data to dataframe columns
        self.dataframe.to_csv(str(self.logs_dir) + f'/logs.csv')