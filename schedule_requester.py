import os
import json
import logging
from html.parser import HTMLParser
import boto3
import requests

logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

logging.basicConfig(
    format='%(asctime)s %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)

client = boto3.client("s3")


class ScheduleExtractor(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self._pending_data = False
        self._data = None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._pending_data = True

    def handle_endtag(self, tag):
        if tag == "script":
            self._pending_data = False

    def handle_data(self, data):
        marker = "DisconSchedule.preset ="
        if self._pending_data:
            if marker in data:
                for line in data.splitlines():
                    if line.startswith(marker):
                        raw_json_data = line[len(marker):].lstrip()
                        self._data = json.loads(raw_json_data)

    def data(self):
        return self._data


def handler(event, context):
    schedule_source_url = os.getenv("SCHEDULE_SOURCE_URL")
    bucket = os.getenv("BUCKET")

    logging.info(f"Requesting schedule info from {schedule_source_url}...")
    parser = ScheduleExtractor()
    resp = requests.get(os.getenv("SCHEDULE_SOURCE_URL"))
    if resp.status_code != 200:
        logging.error(f"Failed to get schedule, {resp.status_code=}")
        return {
            'statusCode': 500,
            'body': 'Error'
        }
    parser.feed(resp.text)
    raw_data = parser.data()
    schedule_data = raw_data.get(
        "data") if raw_data is not None else None
    if schedule_data is None:
        logger.error(
            f"Failed to get schedule. Please check what {schedule_source_url} responds")
        return {
            'statusCode': 500,
            'body': 'Error'
        }
    client.put_object(Body=json.dumps(
        schedule_data), Bucket=bucket, Key='schedule.json')
    return {
        'statusCode': 200,
        'body': 'Success'
    }


if __name__ == "__main__":
    print(handler(None, None))
