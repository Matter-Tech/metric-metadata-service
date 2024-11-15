import enum


class DataTypeEnum(enum.Enum):
    STRING = "string"
    NUMBER = "number"
    UUID = "UUID"
    BOOLEAN = "boolean"


class EntityTypeEnum(enum.Enum):
    METRIC_SET = "metric_set"
    METRIC_SET_TREE = "metric_set_tree"
    METRIC = "metric"
    DATA_METRIC = "data_metric"
    PROPERTY = "property"


class EventTypeEnum(enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class NodeTypeEnum(enum.Enum):
    ROOT = "root"
    CATEGORY = "category"
    METRIC = "metric"
    SECTION = "section"
    CHART = "chart"


class StatusEnum(enum.Enum):
    DEPLOYED = "deployed"
    NOT_USED = "not_used"


class PlacementEnum(enum.Enum):
    ESG_INSIGHTS = "datasets/esgInsights"
    SDGS = "datasets/sdgs"
    REGULATORY = "datasets/regulatory"
    COLLECTIONS = "collections/matter"
