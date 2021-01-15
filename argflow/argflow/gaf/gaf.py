import os
import json
import time
import networkx as nx

from enum import Enum
from .framework import Framework
from .payload import Payload, PayloadType


class NodeType(Enum):

    INPUT = 0
    ARGUMENT = 1
    CONCLUSION = 2


class GAF:

    def __init__(self, confidence=0, predicted_class=None):
        self._G = nx.DiGraph()
        self._framework = None

    def add_argument(self, node, strength=None, payload=None):
        if not payload is None:
            if not isinstance(payload, Payload):
                raise TypeError('payload must be of type Payload')
        self._G.add_node(node, strength=strength,
                         payload=payload, type=NodeType.ARGUMENT)

    def add_input(self, node, payload=None):
        if not payload is None:
            if not isinstance(payload, Payload):
                raise TypeError('payload must be of type Payload')
        self._G.add_node(node, payload=payload, type=NodeType.INPUT)

    def add_conclusion(self, node, confidence, predicted_class, payload=None):
        if not payload is None:
            if not isinstance(payload, Payload):
                raise TypeError('payload must be of type Payload')
        self._G.add_node(node, payload=payload, confidence=confidence,
                         predicted_class=predicted_class, type=NodeType.CONCLUSION)

    def remove_node(self, node):
        self._G.remove_node(node)

    def add_relation(self, u, v, relation):
        if self._framework is None:
            # Check if the relation provided is valid
            if isinstance(relation, Framework):
                self._framework = type(relation)
            else:
                raise TypeError(
                    'Relation type must be part of an argumentation framework.')
        else:
            # Check if the relation provided is consistent with the existing GAF
            if not isinstance(relation, self._framework):
                raise TypeError(
                    'Relation type must be consistent for a given GAF')
        self._G.add_edge(u, v, relation=relation)

    def remove_relation(self, u, v):
        self._G.remove_edge(u, v)
        # If the graph is now empty, remove all constraints on relation types
        if not self._framework is None and len(self._G.edges) == 0:
            self._framework = None

    def arguments(self):
        """
        Get all arguments in the GAF.
        """
        return dict(filter(lambda x: x[1]['type'] == NodeType.ARGUMENT, self._G.nodes(data=True)))

    def inputs(self):
        """
        Get all inputs in the GAF.
        """
        return dict(filter(lambda x: x[1]['type'] == NodeType.INPUT, self._G.nodes(data=True)))

    def conclusions(self):
        """
        Get all conclusions in the GAF.
        """
        return dict(filter(lambda x: x[1]['type'] == NodeType.CONCLUSION, self._G.nodes(data=True)))

    def relations_from(self, node):
        """
        Get all relations (edges) leaving a node.

        node            - a node.
        """
        return list(self._G.edges(node, data=True))

    def serialise(self, name='GAF', root_dir='', payloads_dir=''):
        """
        Serialise a GAF.

        name            - name of the GAF.
        root_dir        - path to the directory where all visualisations are saved. 
                          Don't forget to point the portal to this directory too!
        payloads_dir    - path to save the payloads relative to the root.
        """
        input_nodes, intermediate_nodes, conclusion_nodes = self.inputs(
        ), self.arguments(), self.conclusions()
        G_nodes = dict(self._G.nodes(data=True))
        g = {}
        g['name'] = name
        g['input'] = [str(node) for node in input_nodes]
        g['conclusion'] = [str(node) for node in conclusion_nodes]
        nodes = {}
        for node in input_nodes:
            children = {
                v: self._create_child_obj('neutral') for _, v, data in self.relations_from(node)
            }
            nodes[node] = self._create_node_obj(
                'input',
                G_nodes[node]['payload'],
                children,
                root_dir,
                payloads_dir
            )
        for node in intermediate_nodes:
            children = {
                v: self._create_child_obj(data['relation']) for _, v, data in self.relations_from(node)
            }
            nodes[node] = self._create_node_obj(
                'regular',
                G_nodes[node]['payload'],
                children,
                root_dir,
                payloads_dir,
                strength=G_nodes[node]['strength']
            )
        for node in conclusion_nodes:
            nodes[node] = self._create_node_obj(
                'conclusion',
                Payload(str(G_nodes[node]['predicted_class']),
                        PayloadType.STRING),
                {},
                root_dir,
                payloads_dir
            )
            nodes[node]['certainty'] = float(G_nodes[node]['confidence'] * 100)
        g['nodes'] = nodes
        return json.dumps(g, indent=4, sort_keys=True)

    def _create_node_obj(self, node_type, payload, children, root_dir, payloads_dir, strength=None):
        node = {}
        if not strength is None:
            node['strength'] = float(strength)
        node['node_type'] = node_type
        if not payload is None:
            payload_obj = self._create_payload(
                payload, root_dir, payloads_dir)
            node['content_type'] = payload.content_type
            node['payload'] = payload_obj
        node['children'] = children
        return node

    def _create_child_obj(self, contribution_type):
        child = {}
        child['contribution_type'] = contribution_type
        return child

    def _create_payload(self, payload, root_dir, payloads_dir):
        # Check if valid payload
        if not isinstance(payload, Payload):
            raise TypeError(f'Invalid or empty payload type: {type(payload)}')
        # Generate payload object (for JSON serialisation) accordingly
        if payload.content_type == PayloadType.STRING:
            return payload.content
        elif payload.content_type == PayloadType.IMAGE:
            filename = f'{time.time()}.jpg'
            save_path = os.path.join(root_dir, payloads_dir, filename)
            payload.content.save(save_path)
            return os.path.join(payloads_dir, filename)
        elif payload.content_type == PayloadType.IMAGE_PAIR:
            fst, snd = payload.content
            # Save first image
            filename_fst = f'{time.time()}_fst.jpg'
            save_path_fst = os.path.join(root_dir, payloads_dir, filename_fst)
            fst.save(save_path_fst)
            # Save second image
            filename_snd = f'{time.time()}_snd.jpg'
            save_path_snd = os.path.join(root_dir, payloads_dir, filename_snd)
            snd.save(save_path_snd)
            return {
                'filter': {
                    'payload': os.path.join(payloads_dir, filename_fst)
                },
                'feature': {
                    'payload': os.path.join(payloads_dir, filename_snd)
                }
            }
