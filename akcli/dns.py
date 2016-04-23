import sys
import json
import logging
import requests
from akamai.edgegrid import EdgeGridAuth

if sys.version_info.major < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

log = logging.getLogger(__name__)

class AkamaiDNSError(Exception):
    pass


class AkamaiDNS(object):
    def __init__(self, baseurl, client_token, client_secret, access_token):
        self.baseurl = baseurl
        self.session = requests.Session()
        self.session.auth = EdgeGridAuth(client_token=client_token,
                                         client_secret=client_secret,
                                         access_token=access_token,
                                         max_body=128 * 1024)

    def _update_zone(self, zone_name):
        '''Update a given Zone. This method will handle incrementing the SOA serial for you.

        :param zone_name: This is the name of the zone e.g. example.com.
        :return:
        '''
        # Increment the serial.
        name = zone_name['zone']['name']
        zone_name['zone']['soa']['serial'] += 1

        # POST the updated zone file.
        url = urljoin(self.baseurl, '/config-dns/v1/zones/{0}'.format(name))
        headers = {'content-type': 'application/json'}
        result = self.session.post(url, data=json.dumps(zone_name), headers=headers)

        if result.status_code != 204:
            log.error('Something went very wrong with updating the zone "%s"', zone_name)
        return True

    def fetch_zone(self, zone_name):
        '''Fetch a dictionary representation of a zone file.

        :param zone_name: This is the name of the zone e.g. example.com.
        :return: A dict containing a zone.
        '''
        url = urljoin(self.baseurl, '/config-dns/v1/zones/{0}'.format(zone_name))
        result = self.session.get(url)
        if result.status_code == 404:
            log.error('Zone "%s" not found.', zone_name)
            return None
        return result.json()

    def list_records(self, zone_name, record_type=None):
        '''List all records for a particular zone.

        :param zone_name: This is the name of the zone e.g. example.com.
        :param record_type: (Optional) The type of records to limit the list to.
        :return: A list containing all records for the zone.
        '''

        records = []
        zone = self.fetch_zone(zone_name)['zone']
        if record_type:
            record_type = record_type.lower()
            for record in zone.get(record_type):
                record['type'] = record_type.upper()
                records.append(record)
        else:

            for key, val in zone.items():
                if isinstance(val, list):
                    for record in val:
                        record['type'] = key.upper()
                        records.append(record)
        return records

    def fetch_record(self, zone_name, record_type, name):
        '''Fetch a dictionary representation of a particular DNS record.

        :param zone_name: This is the name of the zone e.g. example.com.
        :param name: This is the "from" section. That is for web01.example.com, this would be web01.
        :param record_type:
        :return:
        '''

        for record in self.list_records(zone_name, record_type):
            if record['name'] == name:
                return record
        return None

    def record_exists(self, zone_name, record_type, name):
        '''Determine if a particular DNS record already exists.

        :param zone_name: Name of the zone to add a record to.
        :param record_type: Type of record (a, cname, ptr, etc).
        :param name: This is the "from" section. That is for web01.example.com, this would be web01.
        :return: True if record found, otherwise False.
        '''
        record_type = record_type.lower()
        if self.fetch_record(zone_name=zone_name, record_type=record_type, name=name):
            return True
        return False

    def add_record(self, zone_name, record_type, name, target, ttl=600):
        '''Add a new DNS record to a zone.

        :param zone_name: Name of the zone to add a record to.
        :param record_type: Type of record (a, cname, ptr, etc).
        :param name: This is the "from" section. That is for web01.example.com, this would be web01.
        :param target: This is the "to" section e.g. "10.0.0.1".
        :param ttl: The DNS record time to live value. Defaults to 600.
        :return: Returns True if successful, otherwise False.
        '''
        record_type = record_type.lower()
        zone = self.fetch_zone(zone_name)
        if not zone:
            raise AkamaiDNSError('Zone {0} not found.'.format(zone_name))

        if self.record_exists(zone_name=zone_name, record_type=record_type, name=name):
            return True

        new_record = {'name': name, 'target': target, 'ttl': ttl, 'active': True}
        zone['zone'].get(record_type).append(new_record)
        return self._update_zone(zone)

    def remove_record(self, zone_name, record_type, name):
        '''Remove a DNS record from a given zone.

        :param zone_name: Name of the zone to remove a record from.
        :param name: This is the "from" section. That is for web01.example.com, this would be web01.
        :return: Returns True if successful, otherwise False.
        '''
        record_type = record_type.lower()
        zone = self.fetch_zone(zone_name)
        if not zone:
            raise AkamaiDNSError('Zone {0} not found.'.format(zone_name))

        record = self.fetch_record(zone_name, record_type, name)
        record.pop('type', None)
        zone['zone'].get(record_type).remove(record)
        return self._update_zone(zone)
