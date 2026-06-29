from tests.rsm_helpers import seed_chain
from tests.v1_helpers import API_V1, j


def test_graph_layout_persists_and_merges(client, auth_headers):
    _, root_id, _ = seed_chain(client, auth_headers)

    empty = client.get(f"{API_V1}/resources/{root_id}/graph-layout", headers=auth_headers)
    assert empty.status_code == 200
    assert j(empty)["layout"]["positions"] == {}

    save = client.put(
        f"{API_V1}/resources/{root_id}/graph-layout",
        headers=auth_headers,
        json={
            "relation_filter": "*",
            "positions": {
                "1": {"x": 10, "y": 20},
                "2": {"x": 30, "y": 40},
            },
        },
    )
    assert save.status_code == 200, save.text
    body = j(save)["layout"]
    assert body["root_ci_id"] == root_id
    assert body["positions"]["1"] == {"x": 10, "y": 20}

    merge = client.put(
        f"{API_V1}/resources/{root_id}/graph-layout",
        headers=auth_headers,
        json={
            "relation_filter": "*",
            "positions": {
                "1": {"x": 99, "y": 88},
                "3": {"x": 50, "y": 60},
            },
        },
    )
    assert merge.status_code == 200
    merged = j(merge)["layout"]["positions"]
    assert merged["1"] == {"x": 99, "y": 88}
    assert merged["2"] == {"x": 30, "y": 40}
    assert merged["3"] == {"x": 50, "y": 60}

    loaded = client.get(f"{API_V1}/resources/{root_id}/graph-layout", headers=auth_headers)
    assert loaded.status_code == 200
    assert j(loaded)["layout"]["positions"] == merged

    clear = client.delete(f"{API_V1}/resources/{root_id}/graph-layout", headers=auth_headers)
    assert clear.status_code == 204

    after_clear = client.get(f"{API_V1}/resources/{root_id}/graph-layout", headers=auth_headers)
    assert after_clear.status_code == 200
    assert j(after_clear)["layout"]["positions"] == {}
