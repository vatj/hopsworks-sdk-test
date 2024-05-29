from pyhive import hive
from pyhive.exc import OperationalError
from thrift.transport.TTransport import TTransportException


def _create_hive_connection(
    self,
    host: str,
    jks_trust_store_path: str,
    jks_key_store_path: str,
    cert_key: str,
    feature_store: feature_store.FeatureStore,
    hive_config: Optional[Dict[str, Any]] = None,
) -> hive.Connection:
    """Create a connection to Hive server."""
    try:
        return hive.Connection(
            host=host,
            port=9085,
            # database needs to be set every time, 'default' doesn't work in pyhive
            database=feature_store,
            configuration=hive_config,
            auth="CERTIFICATES",
            truststore=jks_trust_store_path,
            keystore=jks_key_store_path,
            keystore_password=cert_key,
        )
    except (TTransportException, AttributeError) as err:
        raise ValueError(
            f"Cannot connect to hive server. Please check the host name '{client.get_instance()._host}' "
            "is correct and make sure port '9085' is open on host server."
        ) from err
    except OperationalError as err:
        if err.args[0].status.statusCode == 3:
            raise RuntimeError(
                f"Cannot access feature store '{feature_store}'. Please check if your project has the access right."
                f" It is possible to request access from data owners of '{feature_store}'."
            ) from err