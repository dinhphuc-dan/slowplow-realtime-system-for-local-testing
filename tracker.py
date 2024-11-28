from snowplow_tracker import (
    Snowplow,
    EmitterConfiguration,
    Subject,
    TrackerConfiguration,
    PagePing,
    PageView,
    ScreenView,
    SelfDescribing,
    SelfDescribingJson,
    AsyncEmitter,
    Tracker,
    Subject,
)

import requests
import uuid
import time


def main():

    tracker_id = uuid.uuid4().hex
    user_id = uuid.uuid4().hex

    """ use default emitter """
    # tracker_config = TrackerConfiguration(encode_base64=True)
    # emitter_config = EmitterConfiguration(
    #     batch_size=3,
    #     request_timeout=(10, 20),
    #     custom_retry_codes={500: False, 401: True},  # Don't retry 500, retry 401
    # )

    # Snowplow.create_tracker(
    #     endpoint="http://localhost:6060",
    #     namespace=tracker_id,
    #     tracker_config=tracker_config,
    #     emitter_config=emitter_config,
    #     app_id="wowow_1",
    # )

    # tracker = Snowplow.get_tracker(tracker_id)

    """ setup our own Emitter"""

    emitter = AsyncEmitter(
        # for snowplow micro
        # endpoint="localhost:6060",
        # for snowplow local test
        # endpoint="localhost:15100",
        # for snowplow mini
        # endpoint="104.154.240.235",
        # for snowplow production 1
        endpoint="34.111.250.149",
        protocol="http",
        port=None,
        batch_size=5,
        on_success=None,
        on_failure=None,
        request_timeout=(10, 20),
        custom_retry_codes={500: False, 401: True},  # Don't retry 500, retry 401
    )

    subject = Subject()
    subject.set_user_id(user_id)
    print(user_id)

    tracker = Tracker(
        namespace=tracker_id,
        emitters=emitter,
        app_id="wowow_2",
        encode_base64=True,
        subject=subject,
    )

    page_view = PageView(page_url="https://www.snowplow.io", page_title="Homepage")
    tracker.track(page_view)

    page_ping = PagePing(page_url="https://www.snowplow.io", page_title="Homepage")
    tracker.track(page_ping)

    id = tracker.get_uuid()
    screen_view = ScreenView(id_=id, name="phucdinh02")
    tracker.track(screen_view)

    link_click = SelfDescribing(
        SelfDescribingJson(
            schema="iglu:phucdinhtest01/whatthehell/jsonschema/1-0-0",
            data={"phone_number": 123456789, "email": "phucdinhtestlinkclick0"},
        )
    )
    tracker.track(link_click)

    link_click_1 = SelfDescribing(
        SelfDescribingJson(
            schema="iglu:phucdinhtest01/whatthehell_1/jsonschema/1-0-0",
            data={"phone_number": 987654321, "email": "phucdinhtestlinkclick1"},
        )
    )
    tracker.track(link_click_1)

    # manually sent event
    # tracker.flush()


if __name__ == "__main__":
    for i in range(201):
        print(f"Total event: {i}")
        main()
        time.sleep(5)
