import internal_schema


def create_keycloak_resource() -> dict[
    internal_schema.ResourceType, list[internal_schema.ImportModel]
]:
    internal_resource: dict[
        internal_schema.ResourceType, list[internal_schema.ImportModel]
    ] = {}
    ## realms
    realm_resource = internal_schema.Realm(enabled=True, name="ataldev")
    internal_resource[internal_schema.ResourceType.REALMS] = [realm_resource]

    ##user group
    usergroup_resources = [
        internal_schema.Group(name="site", path="site"),
        internal_schema.Group(name="BLK_A", path="site/BLK_A"),
        internal_schema.Group(name="BLK_B", path="site/BLK_B"),
        internal_schema.Group(name="101", path="site/BLK_A/101"),
        internal_schema.Group(name="102", path="site/BLK_A/102"),
        internal_schema.Group(name="101", path="site/BLK_B/101"),
        internal_schema.Group(name="102", path="site/BLK_B/102"),
    ]
    internal_resource[internal_schema.ResourceType.USERGROUP] = usergroup_resources

    ##user
    user_resources = [
        internal_schema.User(username="atal_admin", groups=["site"]),
        internal_schema.User(username="site_admin", groups=["site"]),
        internal_schema.User(username="BLK_A_user", groups=["site/BLK_A"]),
        internal_schema.User(username="BLK_B_user", groups=["site/BLK_B"]),
        internal_schema.User(username="A_101_user", groups=["site/BLK_A/101"]),
        internal_schema.User(username="A_102_user", groups=["site/BLK_A/102"]),
        internal_schema.User(username="B_101_user", groups=["site/BLK_B/101"]),
        internal_schema.User(username="B_102_user", groups=["site/BLK_B/102"]),
    ]
    internal_resource[internal_schema.ResourceType.USER] = user_resources

    ##Client
    client_resources = [
        internal_schema.KeyCloakClient(clientId="data-service"),
        internal_schema.KeyCloakClient(clientId="alarm-service"),
        internal_schema.KeyCloakClient(clientId="any-service"),
    ]
    internal_resource[internal_schema.ResourceType.CLIENT] = client_resources

    ##scpoes
    scopes_resources = [
        internal_schema.Scope(name="read"),
        internal_schema.Scope(name="write"),
    ]
    internal_resource[internal_schema.ResourceType.SCPOES] = scopes_resources

    ##policy
    policy_resource = [
        internal_schema.GroupBasePolicy(
            name=group.name + "_permission",
            groups=[group],
        )
        for group in usergroup_resources
    ]
    internal_resource[internal_schema.ResourceType.POLICY] = policy_resource

    ##Resource(device)

    resource_resource = [
        internal_schema.Resource(
            name="0000000001", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000002", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000003", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000004", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000005", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000006", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000007", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000008", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000009", type="LoRa sensor", scopes=scopes_resources
        ),
        internal_schema.Resource(
            name="0000000010", type="LoRa sensor", scopes=scopes_resources
        ),
    ]
    internal_resource[internal_schema.ResourceType.RESOURCE] = resource_resource

    ##permissions
    permission_resource = [
        internal_schema.ScopeBasePermission(
            name=resource.name + "_" + scope.name + "_" + "permissions",
            resources=resource,
            scopes=scope,
            policies=["site", "site/BLK_A", "site/BLK_A/101"],
        )
        for resource in resource_resource
        for scope in scopes_resources
    ]
    internal_resource[internal_schema.ResourceType.PERMISSION] = permission_resource

    print("123")
    print("123")
    print("123")
    print("123")
    print("123")

    return internal_resource
