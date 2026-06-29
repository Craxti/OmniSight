"""Unit tests for shared topology/graph algorithms."""

from src.services.rsm.topology_algorithms import (
    bfs_reachable,
    on_same_dependency_chain,
    root_cause_candidate_ids,
)


def test_bfs_reachable():
    adj = {1: {2}, 2: {3}}
    assert bfs_reachable(1, adj) == {1, 2, 3}


def test_on_same_dependency_chain_true_for_linear_subgraph():
    forward = {1: {2}, 2: {3}}
    reverse = {2: {1}, 3: {2}}
    assert on_same_dependency_chain([1, 2, 3], forward, reverse) is True


def test_on_same_dependency_chain_false_for_branch():
    forward = {1: {2, 3}}
    reverse = {2: {1}, 3: {1}}
    assert on_same_dependency_chain([2, 3], forward, reverse) is False


def test_root_cause_candidate_ids_picks_leaves():
    forward = {1: {2}, 2: {3}}
    assert root_cause_candidate_ids([1, 2, 3], forward) == [3]
