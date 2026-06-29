"""Unit tests for shared ``repositories/queries/*`` builders."""

from src.repositories.queries.relations import build_adjacency_from_edges, dependency_adjacency_select


def test_build_adjacency_from_edges():
    forward, reverse = build_adjacency_from_edges([(1, 2), (2, 3)])
    assert forward == {1: {2}, 2: {3}}
    assert reverse == {2: {1}, 3: {2}}


def test_dependency_adjacency_select_restricts_both_endpoints():
    stmt = dependency_adjacency_select(ci_ids={1, 2, 3}, relation_types=("depends_on",))
    where_sql = " ".join(str(clause) for clause in stmt._where_criteria)
    assert "source_ci_id" in where_sql
    assert "target_ci_id" in where_sql
    assert "relation_type" in where_sql
