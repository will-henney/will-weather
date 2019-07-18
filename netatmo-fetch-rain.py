import sys
sys.path.append("/Users/will/Source/netatmo")
import netatmo

def fetch_rain():
    """
        retrieve measures from rain station and append them to csv files
    """
    ws = netatmo.WeatherStation(netatmo.DEFAULT_RC_FILE)
    if not ws.get_data():
        return
    station = ws.station_by_name()
    rainmodule = station['modules'][1]
    print("module_id    : {}".format(rainmodule['_id']))
    print("module_name  : {}".format(rainmodule['module_name']))
    print("data_type    : {}".format(rainmodule['data_type']))

    data_type = ["Rain"]
    netatmo.dl_csv(ws, "netatmo_rain.csv",
                   station['_id'], rainmodule['_id'],
                   data_type, rainmodule['dashboard_data']['time_utc'])


if __name__ == "__main__":
    fetch_rain()
