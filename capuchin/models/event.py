from capuchin import db
import logging


def record_event(client, event_type, **kwargs):
    INFLUX = db.init_influxdb()

    columns = ["type"]
    columns.extend(kwargs.iterkeys())

    values = [event_type]
    values.extend(kwargs.itervalues())

    data = [{
        'name': "events.{}.{}".format(client._id, event_type),
        'columns': columns,
        'points': [values],
    }]

    logging.debug("Writing: %s", data)
    try:
        res = INFLUX.write_points(data)
        logging.info(res)
    except Exception as exc:
        logging.warning(exc, exc_info=True)


class Event(object):

    def __init__(self, client, event, **kwargs):
        super(Event, self).__init__()
        record_event(client, event, **kwargs)
