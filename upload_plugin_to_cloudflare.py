import logging
import boto3
from botocore.exceptions import ClientError
import os
from datetime import date
from Azenqos import version
import pack_plugin

def upload_file(s3_client, file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

today = date.today()
date_str = today.strftime("%Y-%m-%d")
version = "%.03f" % version.VERSION
target_fp = "azenqos_qgis_plugin_{}_{}.zip".format(date_str, version)

pack_plugin.pack(target_fp)

assert os.path.exists(target_fp)

s3 = boto3.resource('s3',
  endpoint_url = 'https://952caf433cb964142d361020549e1f4c.r2.cloudflarestorage.com',
  aws_access_key_id = '3fff8812ff3cc21ef37fed699a985466',
  aws_secret_access_key = '0d7303d2d3495b0baee3df7ff61009e6551602db98065f4034e003693b81eb61'
)

s3_client = boto3.client('s3',
  endpoint_url = 'https://952caf433cb964142d361020549e1f4c.r2.cloudflarestorage.com',
  aws_access_key_id = '3fff8812ff3cc21ef37fed699a985466',
  aws_secret_access_key = '0d7303d2d3495b0baee3df7ff61009e6551602db98065f4034e003693b81eb61'
)

bucket = s3.Bucket('firmwares')

print('Objects:')
azenqos_qgis_plugin_list = []
for item in bucket.objects.all():
  print(' - ', item.key)
  if item.key.startswith("azenqos_qgis_plugin"):
        azenqos_qgis_plugin_list.append(item.key)
        
response = s3_client.delete_object(
    Bucket='firmwares',
    Key='azenqos_qgis_plugin/test.txt',
)

print(response)

object_name = "azenqos_qgis_plugin/{}".format(target_fp)
upload_file(s3_client, target_fp, "firmwares", object_name)


os.remove(target_fp)

assert not os.path.exists(target_fp)

