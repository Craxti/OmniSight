from src.models import Relation
from src.services.export.tabular import build_csv, build_xlsx

RELATION_CSV_HEADERS = ["source_name", "target_name", "relation_type", "status", "data_source"]


def _relation_row(rel: Relation) -> list:
    return [
        rel.source_ci.name,
        rel.target_ci.name,
        rel.relation_type,
        rel.status,
        rel.data_source or "",
    ]


def build_relations_csv(relations: list[Relation]) -> str:
    return build_csv(RELATION_CSV_HEADERS, relations, _relation_row)


def build_relations_xlsx(relations: list[Relation]):
    return build_xlsx("Relations", RELATION_CSV_HEADERS, relations, _relation_row)
