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

    def _update_zone(self, zone):
        '''Update a given Zone. This method will handle incrementing the SOA serial for you.

        :param zone: The zone to update.
        :return: True if successful otherwise False.
        '''

        # Increment the serial.
        zone['zone']['soa']['serial'] += 1
        name = zone['zone']['name']
        url = urljoin(self.baseurl, '/config-dns/v1/zones/{0}'.format(name))
        headers = {'content-type': 'application/json'}
        result = self.session.post(url, data=json.dumps(zone), headers=headers)

        if result.status_code != 204:
            log.error('Something went very wrong with updating the zone "{0}": {1}', name, result.text)
            return False
        return True

    def fetch_zone(self, zone_name):
        '''Fetch a dictionary representation of a zone file.

        :param zone_name: This is the name of the zone e.g. example.com.
        :return: A dict containing a zone.
        '''
        url = urljoin(self.baseurl, '/config-dns/v1/zones/{0}'.format(zone_name))
        result = self.session.get(url)
        if result.status_code == 404:
            log.error('Zone "{0}" not found.', zone_name)
            return None
        return result.json()

    def list_records(self, zone_name, record_type=None):
        '''List all records for a particular zone.

        :param zone_name: This is the name of the zone e.g. example.com.
        :param record_type: (Optional) The type of records to limit the list to.
        :return: A list containing all records for the zone.
        '''

        zone = self.fetch_zone(zone_name)['zone']
        records = []
        for key, val in zone.items():
            if not isinstance(val, list): continue
            for record in val:
                record['type'] = key.upper()
                records.append(record)

        # Add a filter by record type if provided
        if record_type:
            return [r for r in records if r['type'] == record_type.upper()]
        return records

    def add_record(self, zone_name, record_type, name, target, ttl=600):
        '''Add a new DNS record to a zone.

        If the record exists, this will still return successfully so it is safe to re-run.

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

        zone['zone'][record_type].append({'name': name, 'target': target, 'ttl': ttl, 'active': True})
        return self._update_zone(zone)

    def remove_record(self, zone_name, record_type, name, target):
        '''Remove a DNS record from a given zone.

        :param zone_name: Name of the zone to remove a record from.
        :param name: This is the "from" section. That is for web01.example.com, this would be web01.
        :param target: This is the "to" section e.g. "10.0.0.1".

        :return: Returns True if successful, otherwise False.
        '''
        record_type = record_type.lower()
        zone = self.fetch_zone(zone_name)
        if not zone:
            raise AkamaiDNSError('Zone {0} not found.'.format(zone_name))

        for record in self.list_records(zone_name, record_type):
            if (record['name'].lower() == name.lower()) and (record['target'] == target):
                record.pop('type', None)
                zone['zone'].get(record_type).remove(record)
                return self._update_zone(zone)
        return True

    def fetch_records(self, zone_name, record_type, name):
        ''' Fetch list of records matching a particular type and name.

        :param zone_name: Name of the zone to remove a record from.
        :param record_type: Type of record (a, cname, ptr, etc).
        :param name: This is the "from" section. That is for web01.example.com, this would be web01.

        :return: Returns a potentially empty list of records.
        '''

        records = self.list_records(zone_name, record_type)
        return [r for r in records if r['name'] == name.lower()]
