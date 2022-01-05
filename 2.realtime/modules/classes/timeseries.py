from modules.config.exp_config import Exp
from modules.pipelines.preproc_vol_to_timeseries_pipeline import preproc_vol_to_timeseries
import numpy as np

class Timeseries(Exp):
    def __init__(self):
        self.baseline_vols = np.array([])
        self.task_vols = np.array([])
        self.whole_timeseries = np.array([])

    def preproc_vol_2_timeseries(self, vol):
        self._append_vol(vol)
        if vol.type == 'task': # Start preprocessing once baseline time ends
            preprocessed_vol, preproc_vol_to_timeseries_times = preproc_vol_to_timeseries(self.whole_timeseries, self.baseline_vols)
        return preprocessed_vol, preproc_vol_to_timeseries_times

    def _append_vol(self, vol):
        
        # Stack new vol into onto baseline_vols, task_vols or whole_timeseries array
        def vol_to_array(base_array, vol):
            if base_array.shape[0] == 0:
                base_array = vol
            else:
                base_array = np.vstack([base_array, vol])
            return base_array

        if vol.vol_type == 'heatup':
            pass

        elif vol.vol_type == 'baseline':
            self.baseline_vols = vol_to_array(self.baseline_vols, vol.data)
            np.save(str(self.preprocessed_dir) / 'baseline.npy', self.baseline_vols)

            self.whole_timeseries = vol_to_array(self.whole_timeseries, vol.data)
            np.save(str(self.preprocessed_dir) / 'whole_timeseries.npy', self.whole_timeseries)

        elif vol.vol_type == 'task':
            self.task_vols = vol_to_array(self.task_vols, vol.data)
            np.save(str(self.preprocessed_dir) / 'task_vols.npy', self.task_vols)

            self.whole_timeseries = vol_to_array(self.whole_timeseries, vol.data)
            np.save(str(self.preprocessed_dir) / 'whole_timeseries.npy', self.whole_timeseries)

        else:
            self.whole_timeseries = vol_to_array(self.whole_timeseries, vol.data)
            np.save(str(self.preprocessed_dir) / 'whole_timeseries.npy', self.whole_timeseries)
        




    def _detrend_baseline(self):
        
        if self.baseline_vols.shape[0] == self.n_baseline_vols:
            self._detrend_baseline() # Detrend baseline when last baseline vol arrives

        print(f'Detrending baseline...')
        self.detrended_baseline = _detrend(self.baseline_vols, 
                                           inplace = False, 
                                           type = 'linear', 
                                           n_batches = 10)
        np.save(str(self.preprocessed_dir) / 'detrended_baseline.npy', self.detrended_baseline)