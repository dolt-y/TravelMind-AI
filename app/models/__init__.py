"""业务领域模型包；接口传输模型统一放在 schemas 包中。"""

from .poi import POI, POILocation

__all__ = ["POI", "POILocation"]
