"""Well-known infrastructure ports for host discovery inference."""

DB_PORTS = frozenset({5432, 3306, 1433, 1521, 27017, 5433, 5434, 5435, 6379})
QUEUE_PORTS = frozenset({9092, 9093, 2181, 29092, 5672})
INFRA_PORTS = DB_PORTS | QUEUE_PORTS
