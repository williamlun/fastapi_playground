## Get alarm parameters from device

### Endpoint and protocol

`/api/v1/devices/{device_name}/params`

REST, GET method

### Inputs

|                | Param type  | Data type                      | Example                         |
| -------------- | ----------- | ------------------------------ | ------------------------------- |
| Authorization  | header      | Authorization: Bearer          | NA                              |
| device_name    | path param  | string                         | `Netvox-RB11E-7012018a559504e1` |
| severity       | query param | Optional Enum - severity       | `CRITICAL`                      |
| condition_type | query param | Optional Enum - condition_type | `SIMPLE`                        |
| operator       | query param | Optional Enum - operator       | `GREATER`                       |
| field          | query param | Optional string                | `temperature`                   |

### Output format

```json
{
    "CRITICAL_SIMPLE_GT_temperature":
        {
            "ENABLED": true,
            "THRESHOLD": 50,
            "AUTOCLEAR": true,
            "CLEARTHRESHOLD": 45,
            "CLEARREPEATING": 3,
        }
}
```


## Create alarm parameters

### Endpoint and protocol

`/api/v1/devices/{device_name}/params`

REST, POST method

### Inputs

|                  | Param type   | Data type             | Example                         |
| ---------------- | ------------ | --------------------- | ------------------------------- |
| Authorization    | header       | Authorization: Bearer | NA                              |
| device_name      | path param   | string                | `Netvox-RB11E-7012018a559504e1` |
| alarm parameters | request body | json                  | see below                       |

```json
{
    "CRITICAL_SIMPLE_GT_temperature":
        {
            "CLEARREPEATING": 3,
        }
}
```

### Output format

```json
{
    "CRITICAL_SIMPLE_GT_temperature":
        {
            "ENABLED": true,
            "THRESHOLD": 50,
            "AUTOCLEAR": true,
            "CLEARTHRESHOLD": 45,
            "CLEARREPEATING": 3,
        }
}
```


## Edit alarm parameters

### Endpoint and protocol

`/api/v1/devices/{device_name}/params`

REST, PUT method

### Inputs

|                  | Param type   | Data type             | Example                         |
| ---------------- | ------------ | --------------------- | ------------------------------- |
| Authorization    | header       | Authorization: Bearer | NA                              |
| device_name      | path param   | string                | `Netvox-RB11E-7012018a559504e1` |
| alarm parameters | request body | json                  | see below                       |

```json
{
    "CRITICAL_SIMPLE_GT_temperature":
        {
            "ENABLED": false,
        }
}
```

### Output format

```json
{
    "CRITICAL_SIMPLE_GT_temperature":
        {
            "ENABLED": false,
            "THRESHOLD": 50,
            "AUTOCLEAR": true,
            "CLEARTHRESHOLD": 45,
            "CLEARREPEATING": 3,
        }
}
```


## Delete alarm parameters

### Endpoint and protocol

`/api/v1/devices/{device_name}/params`

REST, DELETE method

### Inputs

|                  | Param type   | Data type             | Example                         |
| ---------------- | ------------ | --------------------- | ------------------------------- |
| Authorization    | header       | Authorization: Bearer | NA                              |
| device_name      | path param   | string                | `Netvox-RB11E-7012018a559504e1` |
| alarm parameters | request body | json                  | see below                       |

```json
{
    "CRITICAL_SIMPLE_GT_temperature":
        {
            "CLEARREPEATING": 3,
        }
}
```