import pydantic
import enum
import pandas as pd


class User(pydantic.BaseModel):
    class ThingsboardRole(enum.Enum):
        ADMIN = "admin"
        USER = "user"

    class GrafanaRole(enum.Enum):
        ADMIN = "admin"
        EDITOR = "editor"
        VIEWER = "viewer"

    username: str
    email: str
    user_group: list[str]
    thingsboard_role: ThingsboardRole
    grafana_role: GrafanaRole

    class Config:
        use_enum_values = True


user = User(
    username="username",
    email="upchh@example.com",
    user_group=["admin"],
    thingsboard_role=User.ThingsboardRole.ADMIN,
    grafana_role=User.GrafanaRole.ADMIN,
)


user_df = pd.DataFrame.from_dict(user.dict(), orient="columns")
print(user_df)
print(user_df)
