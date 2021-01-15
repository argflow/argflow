import json
import os
import pytest

from starlette.testclient import TestClient

from argflow_ui import ArgflowUI
from argflow_ui.argumentation_graph import ContributionType, Direction, NodeType, NodeContentType

EXPLANATIONS = [
    {
        "name": "Test1",
        "input": ["0"],
        "conclusion": ["2"],
        "nodes": {
            "0": {
                "node_type": NodeType.INPUT,
                "content_type": NodeContentType.IMAGE,
                "strength": 1.5,
                "children": {
                    "1": {
                        "contribution_type": ContributionType.SUPPORT,
                        "weight": 1.5,
                    }
                },
                "payload": "/api/resources/test1/test1.png",
            },
            "1": {
                "node_type": NodeType.REGULAR,
                "content_type": NodeContentType.IMAGE,
                "strength": 1.5,
                "children": {
                    "2": {
                        "contribution_type": ContributionType.SUPPORT,
                    }
                },
                "payload": {
                    "filter": {
                        "payload": "/api/resources/test1/filters/1.png",
                    },
                    "feature": {
                        "payload": "/api/resources/test1/features/1.png",
                    },
                },
            },
            "2": {
                "node_type": NodeType.CONCLUSION,
                "content_type": NodeContentType.STRING,
                "children": {},
                "payload": "a_test",
                "certainty": 99.99,
            },
        },
    },
    {
        "name": "Test2",
        "input": ["0"],
        "conclusion": ["2"],
        "nodes": {
            "0": {
                "node_type": NodeType.INPUT,
                "content_type": NodeContentType.IMAGE,
                "strength": 0.5,
                "children": {
                    "1": {
                        "contribution_type": ContributionType.ATTACK,
                    }
                },
                "payload": "/api/resources/test1/test2.png",
            },
            "1": {
                "node_type": NodeType.REGULAR,
                "content_type": NodeContentType.IMAGE,
                "strength": 0.5,
                "children": {
                    "2": {
                        "contribution_type": ContributionType.ATTACK,
                    }
                },
                "payload": {
                    "filter": {
                        "payload": "/api/resources/test2/filters/1.png",
                    },
                    "feature": {
                        "payload": "/api/resources/test2/features/1.png",
                    },
                },
            },
            "2": {
                "node_type": NodeType.CONCLUSION,
                "content_type": NodeContentType.STRING,
                "children": {},
                "payload": "cat",
                "certainty": 42,
            },
        },
    },
]
TEST_FOLDER = "Test model folder"
GRAPH_FILENAME = "graph.json"


@pytest.fixture
def test_data():
    if os.path.exists(TEST_FOLDER):
        # We probably don't want to delete it automatically in case it contains
        # something useful
        raise Exception("Relict test folder detected: delete it and try again")

    os.mkdir(TEST_FOLDER)

    model_path = os.path.join(TEST_FOLDER, "model")
    test1_path = os.path.join(TEST_FOLDER, "test1")
    test2_path = os.path.join(TEST_FOLDER, "test2")
    os.mkdir(model_path)
    os.mkdir(test1_path)
    os.mkdir(test2_path)

    with open(os.path.join(test1_path, GRAPH_FILENAME), "w+") as f:
        f.write(json.dumps(EXPLANATIONS[0]))

    with open(os.path.join(test2_path, GRAPH_FILENAME), "w+") as f:
        f.write(json.dumps(EXPLANATIONS[1]))

    yield EXPLANATIONS

    os.remove(os.path.join(test1_path, GRAPH_FILENAME))
    os.remove(os.path.join(test2_path, GRAPH_FILENAME))
    os.rmdir(test1_path)
    os.rmdir(test2_path)
    os.rmdir(model_path)
    os.rmdir(TEST_FOLDER)


@pytest.fixture
def test_client():
    return TestClient(ArgflowUI())


class TestExplanations:
    def test_retrieve_one(self, test_data, test_client):
        response = test_client.get(f"/api/models/{TEST_FOLDER}/explanations/test2")
        data = response.json()

        assert "explanation" in data
        assert "interactions" in data
        assert "interaction_result" in data

        explanation = data["explanation"]
        assert explanation["name"] == "Test2"
        assert explanation["input"] == test_data[1]["input"]
        assert explanation["conclusion"] == test_data[1]["conclusion"]
        assert len(explanation["nodes"]) == 3

        interactions = data["interactions"]
        assert len(interactions) == 1
        assert interactions[0]["node"] == test_data[1]["conclusion"][0]
        assert interactions[0]["direction"] == Direction.TO.value

        interaction_result = data["interaction_result"]
        assert interaction_result is None

    def test_retrieve_all(self, test_data, test_client):
        response = test_client.get(f"/api/models/{TEST_FOLDER}/explanations")
        data = response.json()
        assert len(data) == len(test_data)
