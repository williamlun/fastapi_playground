import uuid


class TsdbConnector:
    _connector_id = uuid.uuid4()

    def __init__(self, name: str):
        self.name = name

    def use_db_do_stuffs(self):
        print(f"Connector ID: {self._connector_id} is doing stuffs for {self.name}")


if __name__ == "__main__":
    tsdb1 = TsdbConnector("TSDB1")
    tsdb1.use_db_do_stuffs()

    tsdb2 = TsdbConnector("TSDB2")
    tsdb2.use_db_do_stuffs()
