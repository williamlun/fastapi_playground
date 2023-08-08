from loguru import logger
from pyG3 import G3, ViewType

# Create a G3 object
server = G3(
    host="172.16.12.181",
    port=82,
    username="gbuser",
    password="Atalces!1",
    version=3.8,
    expire_min=3,
    MAX_RETRIES=3,
    timeout=5,
)


def get_historical_point_list():
    _ = server.get_history_list(api_output=True, view=ViewType.COLLECTION_TABLE)
    return _


def get_historical_data(point_list_response):
    _ = []
    for i in point_list_response:
        _.append(
            server.get_history_data(
                i,
                time_from="2022-01-19T00:00:00Z",
                time_to="2022-01-20T00:00:00Z",
                api_output=True,
                view=ViewType.COLLECTION_TABLE,
            )
        )
    return _


def get_realtime_data(point_list_response):
    _ = []
    for i in point_list_response:
        _.append(
            server.get_value(
                i,
                valueOnly=False,
            )
        )
    return _


def get_values(point_list):
    _ = []
    for i in point_list:
        _.append(
            server.get_values(
                i,
                api_output=True,
            )
        )
    return _


if __name__ == "__main__":
    h_pl = get_historical_point_list()
    sources = h_pl["payload"][:10]
    ids = [i["Id"] for i in sources]

    point_list_historcal = [
        "/ENC_CH1/BLEEDOFF_SYSTEM$2fFLOW_RATE",
    ]
    point_list_realtime = [
        "Drivers/NiagaraNetwork/ENC_SC_01/points/DDC_B2_01/PAU_B2_01/CHW_Valve_Ctrl_Fb",
        "Drivers/NiagaraNetwork/ENC_SC_01/points/DDC_B2_01/PAU_B2_01/Normal_Fault_St",
        "Drivers/NiagaraNetwork/ENC_SC_01/points/DDC_B2_02/PAU_B2_02/SA_Temp",
        "Drivers/NiagaraNetwork/ENC_SC_01/points/DDC_B2_03/PAU_B2_03/Fan_Speed_St",
    ]
    historical_data = get_historical_data(point_list_historcal)
    logger.info(historical_data)

    # realtime_data = get_realtime_data(point_list_realtime)
    # logger.info(realtime_data)
    # value_data = get_values(point_list_realtime)
    # logger.info(value_data)
    # logger.info("Done")
