
from runner import RunnerBase

class Runner(RunnerBase):

    def __init__(self,generalInfo,name,logger,**config):
        RunnerBase.__init__(self,generalInfo,name,logger)
    
    def _getTableColumns(self):
        columns = {
                "tvoc":"INT",
                "delta_tvoc":"INT",
                "pm2_5": "INT",
                "delta_pm2_5": "INT",
                "humidity": "DOUBLE",
                "delta_humidity": "DOUBLE",
                "cnt0_3": "INT",
                "delta_cnt0_3": "INT",
                "measuretime": "INT",
                "sound": "DOUBLE",
                "delta_sound":"DOUBLE",
                "temperature":"DOUBLE",
                "delta_temperature":"DOUBLE",
                "cnt0_5": "INT",
                "delta_cnt0_5": "INT",
                "performance": "DOUBLE",
                "co": "DOUBLE",
                "delta_co": "DOUBLE",
                "humidity_abs": "DOUBLE",
                "delta_humidity_abs": "DOUBLE",
                "co2": "DOUBLE",
                "delta_co2": "DOUBLE",
                "uptime": "INT",
                "so2": "DOUBLE",
                "delta_so2": "DOUBLE",
                "cnt2_5": "INT",
                "delta_cnt2_5": "INT",
                "o3": "DOUBLE",
                "delta_o3": "DOUBLE",
                "cnt10": "INT",
                "delta_cnt10": "INT",
                "no2": "DOUBLE",
                "delta_no2": "DOUBLE",
                "cnt5": "INT",
                "delta_cnt5": "INT",
                "time": "TIMESTAMP",
                "h2s": "DOUBLE",
                "delta_h2s": "DOUBLE",
                "TypPS": "DOUBLE",
                "pressure": "DOUBLE",
                "delta_pressure": "DOUBLE",
                "sound_max": "DOUBLE",
                "delta_sound_max": "DOUBLE",
                "pm1": "INT",
                "delta_pm1":"INT",
                "oxygen": "DOUBLE",
                "delta_oxygen": "DOUBLE",
                "cnt1": "INT",
                "delta_cnt1": "INT",
                "dewpt": "DOUBLE",
                "delta_dewpt": "DOUBLE",
                "pm10": "INT",
                "delta_pm10": "INT",
                "health": "INT"}

        return columns

    def _on_Execution(self):
        while not self.recivedHaltSignal:
            pass
