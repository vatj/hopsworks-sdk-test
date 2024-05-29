from confluent_kafka import Consumer


def _init_kafka_consumer(
    self,
    feature_group: Union[FeatureGroup, ExternalFeatureGroup],
    offline_write_options: Dict[str, Any],
) -> Consumer:
    # setup kafka consumer
    consumer_config = self._get_kafka_config(
        feature_group.feature_store_id, offline_write_options
    )
    if "group.id" not in consumer_config:
        consumer_config["group.id"] = "hsfs_consumer_group"

    return Consumer(consumer_config)