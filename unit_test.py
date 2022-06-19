import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import requests
from threading import Thread
from time import time, sleep

API_BASEURL = "https://0.0.0.0:80/api"

ROOT_ID = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"

IMPORT_BATCHES = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Товары",
                "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "parentId": None
            }
        ],
        "updateDate": "2022-02-01T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
            },
            {
                "type": "OFFER",
                "name": "jPhone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 79999
            },
            {
                "type": "OFFER",
                "name": "Xomiа Readme 10",
                "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 59999
            }
        ],
        "updateDate": "2022-02-02T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Телевизоры",
                "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
            },
            {
                "type": "OFFER",
                "name": "Samson 70\" LED UHD Smart",
                "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 32999
            },
            {
                "type": "OFFER",
                "name": "Phyllis 50\" LED UHD Smarter",
                "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 49999
            }
        ],
        "updateDate": "2022-02-03T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Goldstar 65\" LED UHD LOL Very Smart",
                "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                "price": 69999
            },
        ],
        "updateDate": "2022-02-03T15:00:00.000Z"
    }
]

WRONG_IMPORT_BATCHES = [
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Товар с родителем-товаром",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa00",
                "parentId": "863e1a7a-1304-42ae-943b-179184c077e3",
                "price": 90999
            }
        ],
        "updateDate": "2022-02-04T12:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": None,
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa01",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": 50999
            }
        ],
        "updateDate": "2022-02-04T13:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Категория, имеющая цену",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa02",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": 999
            }
        ],
        "updateDate": "2022-02-04T14:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Товар, не имеющий цену как поле",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa03",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
            }
        ],
        "updateDate": "2022-02-04T15:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Товар, имеющий цену null",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa04",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": None
            }
        ],
        "updateDate": "2022-02-04T16:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Товар, имеющий отрицательную цену",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa05",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": -9000
            }
        ],
        "updateDate": "2022-02-04T17:00:00.000Z"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Запрос с невалидной датой 1",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa06",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": 90364
            }
        ],
        "updateDate": "18:00:00 18.06.2022"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Запрос с невалидной датой 2",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa07",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": 90364
            }
        ],
        "updateDate": "2022.02.04 19:00:00"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Запрос с невалидной датой 3",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa08",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": 90364
            }
        ],
        "updateDate": "2022/02/04 20:00:00"
    },
    {
        "items": [
            {
                "type": "OFFER",
                "name": "Запрос с невалидной датой 4",
                "id": "d515e43f-f3f6-4471-bb77-6b455017aa09",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
                "price": 90364
            }
        ],
        "updateDate": "2022/02/04T21:00"
    },
]

EXPECTED_TREE = {
    "type": "CATEGORY",
    "name": "Товары",
    "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
    "price": 58599,
    "parentId": None,
    "date": "2022-02-03T15:00:00.000Z",
    "children": [
        {
            "type": "CATEGORY",
            "name": "Телевизоры",
            "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
            "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            "price": 50999,
            "date": "2022-02-03T15:00:00.000Z",
            "children": [
                {
                    "type": "OFFER",
                    "name": "Samson 70\" LED UHD Smart",
                    "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 32999,
                    "date": "2022-02-03T12:00:00.000Z",
                    "children": None,
                },
                {
                    "type": "OFFER",
                    "name": "Phyllis 50\" LED UHD Smarter",
                    "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 49999,
                    "date": "2022-02-03T12:00:00.000Z",
                    "children": None
                },
                {
                    "type": "OFFER",
                    "name": "Goldstar 65\" LED UHD LOL Very Smart",
                    "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 69999,
                    "date": "2022-02-03T15:00:00.000Z",
                    "children": None
                }
            ]
        },
        {
            "type": "CATEGORY",
            "name": "Смартфоны",
            "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
            "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            "price": 69999,
            "date": "2022-02-02T12:00:00.000Z",
            "children": [
                {
                    "type": "OFFER",
                    "name": "jPhone 13",
                    "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "price": 79999,
                    "date": "2022-02-02T12:00:00.000Z",
                    "children": None
                },
                {
                    "type": "OFFER",
                    "name": "Xomiа Readme 10",
                    "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "price": 59999,
                    "date": "2022-02-02T12:00:00.000Z",
                    "children": None
                }
            ]
        },
    ]
}


def request(path, method="GET", data=None, json_response=False):
    try:
        params = {
            "url": f"{API_BASEURL}{path}",
            "method": method,
            "headers": {},
        }

        if data:
            params["data"] = json.dumps(
                data, ensure_ascii=False).encode("utf-8")
            params["headers"]["Content-Length"] = len(params["data"])
            params["headers"]["Content-Type"] = "application/json"

        req = urllib.request.Request(**params)

        with urllib.request.urlopen(req) as res:
            res_data = res.read().decode("utf-8")
            if json_response:
                res_data = json.loads(res_data)
            return res.getcode(), res_data
    except urllib.error.HTTPError as e:
        return e.getcode(), None


def deep_sort_children(node):
    if node.get("children"):
        node["children"].sort(key=lambda x: x["id"])

        for child in node["children"]:
            deep_sort_children(child)


def print_diff(expected, response):
    with open("expected.json", "w") as f:
        json.dump(expected, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    with open("response.json", "w") as f:
        json.dump(response, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    subprocess.run(["git", "--no-pager", "diff", "--no-index",
                    "expected.json", "response.json"])


def test_import():
    for index, batch in enumerate(IMPORT_BATCHES):
        print(f"Importing batch {index}")
        response = requests.post(API_BASEURL + '/imports', json=batch)
        status = response.status_code

        assert status == 200, f"Expected HTTP status code 200, got {status}"

    print("Test import passed.")


def test_wrong_import():
    for index, batch in enumerate(WRONG_IMPORT_BATCHES):
        print(f"Importing wrong batch {index}")
        response = requests.post(API_BASEURL + '/imports', json=batch)
        status = response.status_code

        assert status == 400, f"Expected HTTP status code 400, got {status}"

    print("Test wrong import passed.")


def test_nodes():
    status, response = request(f"/nodes/{ROOT_ID}", json_response=True)
    # print(json.dumps(response, indent=2, ensure_ascii=False))

    assert status == 200, f"Expected HTTP status code 200, got {status}"

    deep_sort_children(response)
    deep_sort_children(EXPECTED_TREE)
    if response != EXPECTED_TREE:
        print_diff(EXPECTED_TREE, response)
        raise AssertionError("Response tree doesn't match expected tree.")

    print("Test nodes passed.")


def test_sales():
    params = urllib.parse.urlencode({
        "date": "2022-02-04T00:00:00.000Z"
    })
    status, response = request(f"/sales?{params}", json_response=True)
    assert status == 200, f"Expected HTTP status code 200, got {status}"
    print("Test sales passed.")


def test_stats():
    params = urllib.parse.urlencode({
        "dateStart": "2022-02-01T00:00:00.000Z",
        "dateEnd": "2022-02-03T00:00:00.000Z"
    })
    status, response = request(
        f"/node/{ROOT_ID}/statistic?{params}", json_response=True)

    assert status == 200, f"Expected HTTP status code 200, got {status}"
    print("Test stats passed.")


def test_delete():
    for index, items in enumerate(IMPORT_BATCHES[::-1]):
        print(f"Deleting batch {index}")
        status = requests.delete(API_BASEURL + "/delete/" + items['items'][0]['id']).status_code
        assert status == 200, f"Expected HTTP status code 200, got {status}"

        for item in items['items']:
            status = requests.get(API_BASEURL + "/nodes/" + item['id']).status_code
            assert status == 404, f"Expected HTTP status code 404, got {status}"

    print("Test delete passed.")


def test_multithreading():
    def f1():
        url = API_BASEURL + "/nodes/" + IMPORT_BATCHES[1]['items'][1]['id']
        requests.get(url + '?threading_test=true')
        print(1, 'got')

    def f2():
        url = API_BASEURL + "/nodes/" + IMPORT_BATCHES[1]['items'][2]['id']
        requests.get(url + '?threading_test=true')
        print(2, 'got')

    def test_consistently():
        t = time()
        f1()
        f2()
        print('Последовательно:', time() - t)
        return time() - t

    def test_simultaneously():
        thread1 = Thread(target=f1)
        thread2 = Thread(target=f2)

        thread1.start()
        thread2.start()
        t = time()
        while thread1.is_alive() or thread2.is_alive():
            pass

        print('Параллельно:', time() - t)
        return time() - t

    a = test_consistently()
    b = test_simultaneously()

    assert round(a / b) == 2, f'Excepted 2, got {round(a / b)}'
    print('Test multithreading passed')


def test_all():
    test_import()
    sleep(1)
    test_wrong_import()
    sleep(1)
    test_nodes()
    # sleep(1)
    # test_multithreading()
    # sleep(1)
    # test_delete()

    # sleep(1)
    # test_sales()
    # sleep(1)
    # test_stats()


def main():
    global API_BASEURL
    test_name = None

    for arg in sys.argv[1:]:
        if re.match(r"^https?://", arg):
            API_BASEURL = arg
        elif test_name is None:
            test_name = arg

    if API_BASEURL.endswith('/'):
        API_BASEURL = API_BASEURL[:-1]

    if test_name is None:
        test_all()
    else:
        test_func = globals().get(f"test_{test_name}")
        if not test_func:
            raise NameError(f"Unknown test: {test_name}")
        test_func()


if __name__ == "__main__":
    main()
