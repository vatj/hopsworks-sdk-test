from typing import List, Literal, TYPE_CHECKING, Union
from botocore.response import StreamingBody
import boto3

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl
    from hopsworks_sdk.feature_store import storage_connector as sc

def _read_s3(
    self,
    storage_connector: sc.S3Connector,
    location: str,
    data_format: str,
    dataframe_type: Literal["pandas", "polars", "default"] = "default",
) -> List[Union[pd.DataFrame, pl.DataFrame]]:
    # get key prefix
    path_parts = location.replace("s3://", "").split("/")
    _ = path_parts.pop(0)  # pop first element -> bucket

    prefix = "/".join(path_parts)

    if storage_connector.session_token is not None:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=storage_connector.access_key,
            aws_secret_access_key=storage_connector.secret_key,
            aws_session_token=storage_connector.session_token,
        )
    else:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=storage_connector.access_key,
            aws_secret_access_key=storage_connector.secret_key,
        )

    df_list = []
    object_list = {"is_truncated": True}
    while object_list.get("is_truncated", False):
        if "NextContinuationToken" in object_list:
            object_list = s3.list_objects_v2(
                Bucket=storage_connector.bucket,
                Prefix=prefix,
                MaxKeys=1000,
                ContinuationToken=object_list["NextContinuationToken"],
            )
        else:
            object_list = s3.list_objects_v2(
                Bucket=storage_connector.bucket,
                Prefix=prefix,
                MaxKeys=1000,
            )

        for obj in object_list["Contents"]:
            if not self._is_metadata_file(obj["Key"]) and obj["Size"] > 0:
                obj = s3.get_object(
                    Bucket=storage_connector.bucket,
                    Key=obj["Key"],
                )
                if dataframe_type.lower() == "polars":
                    df_list.append(self._read_polars(data_format, obj["Body"]))
                else:
                    df_list.append(self._read_pandas(data_format, obj["Body"]))
    return df_list