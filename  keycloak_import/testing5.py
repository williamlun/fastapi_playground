import requests
import json

_svc_url = "http://127.0.0.1:8080/admin/realms/atal234"
token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJpTEd3TDZwb3hmakpnY016Mm0zS2ZjbjB6a3Q5TVRKQU13REU4MnV5WHhFIn0.eyJleHAiOjE2NjcyODE3ODUsImlhdCI6MTY2NzI4MTcyNSwianRpIjoiMDZhZmEzMGItZjYwNC00MTU2LTlmMDEtMzNiMDM0YzZiODI1IiwiaXNzIjoiaHR0cDovLzEyNy4wLjAuMTo4MDgwL3JlYWxtcy9tYXN0ZXIiLCJzdWIiOiI0Y2UyZmUyYS05NThlLTQ3ZTAtOGMzYS0wNDgzMDU3MThhNzMiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJhZG1pbi1jbGkiLCJzZXNzaW9uX3N0YXRlIjoiZjUxM2U0ZmUtN2QxNC00YzA2LWE4OTItMWEwNzFiY2VmOThmIiwiYWNyIjoiMSIsInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsInNpZCI6ImY1MTNlNGZlLTdkMTQtNGMwNi1hODkyLTFhMDcxYmNlZjk4ZiIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYWRtaW4iLCJlbWFpbCI6IndpbGxpYW1sZXVuZ0BhdGFsLmNvbSJ9.fCAfuh75fdT-LB_spGnXvdc5EwdUFTp6xVWH8TnuSMDK0pfEGzcsRqdjKYvkc6glcLa-PqnPf78f0TnTfE2_8PGStK8XC_wx8aajEj175Hpr6y1QhZYy6Zq-DsxTg_PHwCgGyKhhh3hCQ1TvhLX2srx5OfKfsLiZeh2CVxLKs_9XtTS9bjChi_Kh_MkttFbBuTR3p8s2LKMULrvKV0CTy8g1VGQ5rd8Yx65euVzGPqeJHLlWc7OCmnXkmA2r5wIW4ek3WgGi5WDrUBl4OjzReHLr6x9c6O7BI0NklmWfgSGfphyMDBDwKyAOybtC_f2LVdxc0_prSX4VvCe-gqJikg"
_req_header = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

item = {"name": "dfdfgaad"}
condi = {"error": "not found", "name": "dfdfgaad"}

mylist = []


# response = requests.post(url, headers=header, data=json.dumps(item))


def myfunc():
    response = requests.get(_svc_url, headers=_req_header, params=condi)
    if response.status_code > 300:
        return response.status_code
    return response.json()


def myfunc1(mylist):
    for record in mylist:
        print(record)
        return record
    return None


class P:
    val = 1

    def show(self):
        print("P class")
        self.innerfunc()

    def innerfunc(self):
        print("PP method")


class C(P):
    val = 2

    def show(self):
        print("C class")
        self.innerfunc()

    def innerfunc(self):
        print("CC method")


muobj = C().show()


print("123")
