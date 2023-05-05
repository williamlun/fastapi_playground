import requests

base_url = "https://172.16.14.162/iot-cms-webserver/sites/hklah/devices/"

payload = {}
headers = {"Authorization": "Basic "}

devices = [
    "Atlasen-LeoV2-AC1F09FFFE078028",
    "Atlasen-LeoV2-AC1F09FFFE0854AF",
    "Atlasen-LeoV2-AC1F09FFFE0854B5",
    "Atlasen-LeoV2-AC1F09FFFE0854D5",
    "Atlasen-LeoV2-AC1F09FFFE0854E3",
    "Atlasen-LeoV2-AC1F09FFFE0854EA",
    "Atlasen-LeoV2-AC1F09FFFE0854F3",
    "Atlasen-LeoV2-AC1F09FFFE0854FD",
    "Atlasen-LeoV2-AC1F09FFFE085511",
    "Atlasen-LeoV2-AC1F09FFFE0855D7",
    "Atlasen-LeoV2-AC1F09FFFE0855D8",
    "Atlasen-LeoV2-AC1F09FFFE085705",
    "Atlasen-LeoV2-AC1F09FFFE085710",
    "Atlasen-LeoV2-AC1F09FFFE08572D",
    "Atlasen-LeoV2-AC1F09FFFE08572E",
    "Atlasen-LeoV2-AC1F09FFFE085731",
    "Atlasen-LeoV2-AC1F09FFFE0A3D16",
    "Atlasen-LeoV2-AC1F09FFFE0A3D80",
    "Atlasen-LeoV2-AC1F09FFFE0A3D83",
    "Atlasen-LeoV2-AC1F09FFFE0A3D8A",
    "Atlasen-LeoV2-AC1F09FFFE0A3DA5",
    "Atlasen-LeoV2-AC1F09FFFE0A3DCA",
    "Atlasen-LeoV2-AC1F09FFFE0A3DE2",
    "Atlasen-LeoV2-AC1F09FFFE0A3E0F",
    "Atlasen-LeoV2-AC1F09FFFE0A3E15",
    "Atlasen-LeoV2-AC1F09FFFE0A3E2B",
    "Atlasen-LeoV2-AC1F09FFFE0A3E5F",
    "Atlasen-LeoV2-AC1F09FFFE0A3E83",
    "Atlasen-LeoV2-AC1F09FFFE0A3E91",
    "Atlasen-LeoV2-AC1F09FFFE0A3EA8",
    "BACnet-ES-190-40-1-101-47808",
    "ManThink-GDOx11-5a53012a000003ab",
    "ManThink-GDOx11-5a53012a0000048c",
    "ManThink-GDOx11-5a53012a00000491",
    "ManThink-GDOx11-5a53012a000004b2",
    "ManThink-GDOx11-5a53012a000004bb",
    "ManThink-GDOx11-5a53012a000004bc",
    "ManThink-GDOx11-5a53012a000004be",
    "ManThink-GDOx11-5a53012a000004c2",
    "ManThink-GDOx11-5a53012a000004fb",
    "ManThink-GDOx11-5a53012a000004fc",
    "ManThink-GDOx11-5a53012a0000066a",
    "ManThink-GDOx11-5a53012a0000066c",
    "ManThink-GDOx11-5a53012a0000066f",
    "ManThink-GDOx11-5a53012a00000670",
    "ManThink-GDOx11-5a53012a00000671",
    "ManThink-GDOx11-5a53012a00000675",
    "ManThink-GDOx11-5a53012a00000678",
    "ManThink-GDOx11-5a53012a0000067d",
    "ManThink-GDOx11-5a53012a0000067e",
    "ManThink-GDOx11-5a53012a00000681",
    "ManThink-GDOx11-5a53012a00000683",
    "ManThink-GDOx11-5a53012a00000688",
    "ManThink-GDOx11-5a53012a00000689",
    "ManThink-GDOx11-5a53012a0000068d",
    "ManThink-GDOx11-5a53012a00000692",
    "ManThink-GDOx11-5a53012a00000695",
    "ManThink-GDOx11-5a53012a000006a2",
    "ManThink-GDOx11-5a53012a000006a6",
    "ManThink-GDOx11-5a53012a000006a7",
    "ManThink-GDOx11-5a53012a000006a8",
    "ManThink-GDOx11-5a53012a000006ad",
    "ManThink-GDOx11-5a53012a000006b2",
    "ManThink-GDOx11-5b53012a0000066a",
    "ManThink-GDOx11-5b53012a0000066c",
    "ManThink-GDOx11-5b53012a0000066f",
    "ManThink-GDOx11-5b53012a00000670",
    "ManThink-GDOx11-5b53012a00000671",
    "ManThink-GDOx11-5b53012a00000675",
    "ManThink-GDOx11-5b53012a00000678",
    "ManThink-GDOx11-5b53012a0000067d",
    "ManThink-GDOx11-5b53012a0000067e",
    "ManThink-GDOx11-5b53012a00000681",
    "ManThink-GDOx11-5b53012a00000683",
    "ManThink-GDOx11-5b53012a00000688",
    "ManThink-GDOx11-5b53012a00000689",
    "ManThink-GDOx11-5b53012a0000068d",
    "ManThink-GDOx11-5b53012a00000692",
    "ManThink-GDOx11-5b53012a00000695",
    "ManThink-GDOx11-5b53012a000006a2",
    "ManThink-GDOx11-5b53012a000006a6",
    "ManThink-GDOx11-5b53012a000006a7",
    "ManThink-GDOx11-5b53012a000006a8",
    "ManThink-GDOx11-5b53012a000006ad",
    "ManThink-GDOx11-5b53012a000006b2",
]

for device in devices:
    response = requests.request(
        "DELETE", base_url + device, headers=headers, data=payload, verify=False
    )
    print(response.text)

my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for i in my_list:
    print(i)
