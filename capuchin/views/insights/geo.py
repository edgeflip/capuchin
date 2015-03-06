from capuchin import db
from capuchin import config
from capuchin.models.city import City
import logging
import json

class CityPopulation(object):

    def __init__(self, client):
        and_ = [{
            "term": {
                "clients.id": str(client._id)
            }
        }]
        query = {
            "query":{
                "filtered":{"filter":{"and":and_}},
            },
            "aggregations":{
                "cities":{
                    "terms":{
                        "script":"doc['location_name.city.facet'].value+','+doc['location_name.state.facet'].value",
                        "size":200,
                    }
                }
            }
        }
        ES = db.init_elasticsearch()
        res = ES.search(
            config.ES_INDEX,
            config.USER_RECORD_TYPE,
            size=0,
            _source=False,
            body=query
        )
        logging.info(res)
        self.data = []
        for i in res['aggregations']['cities']['buckets']:
            logging.debug(i)
            city, state = i['key'].split(",")
            if city:
                c = City.find_one({"full_state":state, "city":city})
                if c:
                    self.data.append({
                        "name":"{},{}".format(c.city, c.state),
                        "lat":c.lat,
                        "lng":c.lng,
                        "count": i['doc_count']
                    })

    def dump(self):
        return json.dumps(self.data)
