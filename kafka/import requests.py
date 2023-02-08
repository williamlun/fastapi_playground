import requests

url = "http://172.16.12.225:31808/api/gateways/3853014813ce0007/frames"
headers = {
    "Accept": "application/json",
    "Grpc-Metadata-Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhcyIsImV4cCI6MTY3MTc2MzE5MCwiaWQiOjEsImlzcyI6ImFzIiwibmJmIjoxNjcxNjc2NzkwLCJzdWIiOiJ1c2VyIiwidXNlcm5hbWUiOiJhZG1pbiJ9.9RKoBRGESee7fdbVJ9Pf0Ip8zYkKjASDxh6EDSAXA78",
}
s = requests.Session()
with s.get(url, stream=True, headers=headers) as resp:
    for line in resp.iter_lines(chunk_size=1):
        print(line)
