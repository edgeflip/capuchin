from capuchin import db
from capuchin import config
from capuchin.models.city import City
import logging
import json
import csv
from collections import Counter

class CityPopulation(object):

    def __init__(self, client, top_n):
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
                        "size":top_n,
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


class AudienceLocation(object):

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
                        "size":1000,
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
        with open('./data/county_lookup.json', 'r') as county_file:
            county_lookup = json.load(county_file)

        with open('./data/county_names.csv') as county_name_file:
            rows = csv.DictReader(county_name_file, delimiter=",")
            county_names = { "{}{}".format(r['StateFIPS'].lstrip('0'), r['CountyFIPS']): r['CountyName'] for r in rows}

        with open("./data/states_abbreviations.csv") as states:
            rows = csv.DictReader(states, delimiter=",")
            state_lookup = {r['State']:r['Abbreviation'] for r in rows}

        with open("./data/county_pop.json") as pop_file:
            pop_lookup = json.load(pop_file)

        self.data = Counter()
        counties = Counter()
        for i in res['aggregations']['cities']['buckets']:
            city, state = i['key'].split(",")
            if city:
                state_code = state_lookup.get(state)
                if state_code:
                    key = state_code.lower() + "_" + city.lower()
                    county = county_lookup.get(key, None)
                    if county:
                        logging.info(county + key)
                        pop = pop_lookup[county]
                        mangled_county = county.lstrip('0')
                        if i['doc_count'] > 1:
                            counties[mangled_county] += i['doc_count'] * 100000 / float(pop)

        self.data = [{
            "id": k,
            "users": v,
            "name": county_names.get(k, ''),
        } for k,v in counties.iteritems()]

    def dump(self):
        return json.dumps(self.data)
