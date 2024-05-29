from typing import Any, Dict, Union, TYPE_CHECKING
from confluent_kafka import Producer

if TYPE_CHECKING:
    from hopsworks_sdk.feature_store.feature_group import FeatureGroup, ExternalFeatureGroup


def _init_kafka_producer(
    self,
    feature_group: Union[FeatureGroup, ExternalFeatureGroup],
    offline_write_options: Dict[str, Any],
) -> Producer:
    # setup kafka producer
    return Producer(
        self._get_kafka_config(feature_group.feature_store_id, offline_write_options)
    )