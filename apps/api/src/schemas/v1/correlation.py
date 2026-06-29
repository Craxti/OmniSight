from pydantic import ConfigDict, Field
from src.schemas.correlation import AlertIdentifier
from src.schemas.v1.common import PaginationParams


class ResolveRequestV1(PaginationParams):
    alerts: list[AlertIdentifier]


class CorrelationIngestRequestV1(PaginationParams):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "alerts": [
                        {"hostname": "app-01"},
                        {"ip": "10.0.0.5"},
                    ],
                    "source": "monitoring-system",
                    "depth": 3,
                    "page": 1,
                    "page_size": 100,
                    "webhook_url": "https://monitoring.example/hooks/rsm",
                    "dispatch_webhook": True,
                }
            ]
        }
    )
    alerts: list[AlertIdentifier]
    source: str | None = None
    depth: int = Field(default=3, ge=1, le=10)
    webhook_url: str | None = None
    dispatch_webhook: bool = False
