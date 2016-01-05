# coding=utf-8

import sys
import xml.etree.ElementTree as ET
import requests
import csv
import datetime
from google import get_all_events

CHAOS_ACCESSPOINT_GUID = 'C4C2B8DA-A980-11E1-814B-02CEA2621172'

def get_objects(query, sort='', pageIndex=0, pageSize=100):
    data = {
        'query': query,
        'accessPointGUID': CHAOS_ACCESSPOINT_GUID,
        'includeMetadata': 'true',
        'includeFiles': 'true',
        'includeObjectRelations': 'true',
        'includeAccessPoints': 'true',
        'sort': sort,
        'pageIndex': pageIndex,
        'pageSize': pageSize
    }
    url = 'http://api.danskkulturarv.dk/Object/Get'
    r = requests.get(url, params=data)
    if r.status_code == 200:
        portal_result = ET.fromstring(r.text.encode('utf8'))
        module_result = portal_result.find('ModuleResults').find('ModuleResult')
        return module_result.find('Results').findall('Result')
    else:
        raise Exception('Could not get the object from CHAOS.')


def get_all_objects(query, sort=''):
    all_objects = []
    pageIndex = 0
    while True:
        objects = get_objects(query, sort, pageIndex)
        print('Got page indexed %u' % pageIndex)
        pageIndex += 1
        # Were objects returned?
        if(len(objects) > 0):
            all_objects += objects
        else:
            break
    return all_objects


def get_object_metadata(object, metadata_guid):
    metadatas = object.find('Metadatas').findall('Result')
    metadatas = [m for m in metadatas if m.find('MetadataSchemaGUID').text == metadata_guid]
    if metadatas:
        metadata = metadatas[0].find('MetadataXML').text.encode('utf8')
        return ET.fromstring(metadata)
    else:
        return None


def or_empty(v):
    if type(v) == str:
        return v.encode('utf8')
    elif type(v) == unicode:
        return v
    elif type(v) == int:
        return v
    else:
        return ''

if __name__ == '__main__':
    if len(sys.argv) >= 4:
        from_time = sys.argv[1]
        to_time = sys.argv[2]
        query = [
            'DKA-Organization: "DR"',
            'apc4c2b8da-a980-11e1-814b-02cea2621172_PubStart: [%s TO %s]' % (from_time, to_time)
        ]
        query = " AND ".join(query)
        print("Requesting: %s" % query)

        ga_ids = 'ga:51793449'
        start_date = '2015-01-01'
        end_date = '2015-12-31'

        plays = get_all_events(ga_ids,
                               'JW Player Video Plays',
                               start_date,
                               end_date)

        completes = get_all_events(ga_ids,
                                   'JW Player Video Completes',
                                   start_date,
                                   end_date)
        objects = get_all_objects(query, sort='apc4c2b8da-a980-11e1-814b-02cea2621172_PubStart+asc')

        with open(sys.argv[3], 'wb') as output_file:
            output_writer = csv.writer(output_file)
            output_writer.writerow([
                'Titel',
                'AssetID',
                'ProductionId',
                'Varighed',
                'Påbegyndte afspilninger',
                'Påbegyndte afspilningstimer',
                'Gennemførte afspilninger',
                'Gennemførte afspilningstimer',
                'Publiceret på DKA',
                'Først publiceret',
                'Webadresse',
                'Webadresse (alternativ)'
            ])
            for o in objects:
                metadata = get_object_metadata(o, '5906a41b-feae-48db-bfb7-714b3e105396')
                crowd_metadata = get_object_metadata(o, 'a37167e0-e13b-4d29-8a41-b0ffbaa1fe5f')
                ns = {
                    'dka': 'http://www.danskkulturarv.dk/DKA2.xsd',
                    'dkac': 'http://www.danskkulturarv.dk/DKA-Crowd.xsd'
                }
                #ET.dump(o)
                if metadata is None:
                    print('Found an object without metadata attached.')
                else:
                    title = metadata.find('dka:Title', ns).text
                    external_identifier = metadata.find('dka:ExternalIdentifier', ns).text
                    metafields = metadata.findall('dka:Metafield', ns)

                # PRODUCTION ID
                    production_id = [f.find('dka:Value', ns).text
                                     for f in metafields
                                     if f.find('dka:Key', ns).text == 'ProductionId']
                    # We need only one product
                    production_id = production_id[0] if len(production_id) > 0 else ''

                # DURATION
                    duration = [f.find('dka:Value', ns).text
                                       for f in metafields
                                       if f.find('dka:Key', ns).text == 'Duration']
                    # We need only one duration
                    duration = duration[0] if len(duration) > 0 else ''
                    # Remove anything but numbers from duration
                    duration_only_numbers = ''.join(c for c in duration if c.isdigit())

                    if duration_only_numbers:
                        # Convert duration to hours
                        duration_secs = float(duration_only_numbers) / 1000.0
                        duration_minutes = duration_secs / 60.0
                        duration_hours = duration_minutes / 60.0
                    else:
                        duration_hours = 0

                # FIRST PUBLISHED
                    first_published_date = metadata.find('dka:FirstPublishedDate', ns).text
                    # Remove T00:00:00
                    first_published_date = first_published_date.replace("T00:00:00", "")
                    # Year first
                    if len(first_published_date) == 10:
                        if first_published_date.index('-') == 2:
                            first_published_date = datetime.datetime.strptime(first_published_date, '%d-%m-%Y').strftime('%Y-%m-%d')

                # PUBLISHED ON DKA
                    accesspoint_startdate = o.find('AccessPoints').find('AccessPoint_Object_Join').find('StartDate').text
                    # Remove everything after first space
                    accesspoint_startdate = accesspoint_startdate.split(' ', 1)[0]
                    # Year first
                    if len(accesspoint_startdate) == 10:
                        if accesspoint_startdate.index('-') == 2:
                            accesspoint_startdate = datetime.datetime.strptime(accesspoint_startdate, '%d-%m-%Y').strftime('%Y-%m-%d')

                # URL
                    url = 'http://www.danskkulturarv.dk/chaos_post/%s/' % o.find('GUID').text

                # SLUG
                    slug = None if crowd_metadata is None else crowd_metadata.find('dkac:Slug', ns).text
                    urlslug = 'http://www.danskkulturarv.dk/dr/%s/' % slug

                # PLAY COUNT
                    play_count = plays.get(urlslug, 0)

                # PLAYED HOURS
                    played_hours = play_count * duration_hours

                # COMPLETED COUNT
                    completed_count = completes.get(urlslug, 0)

                # COMPLETED HOURS
                    completed_hours = completed_count * duration_hours

                # FORMATED DURATION
                    duration_formatted = '{:.2f}'.format(duration_hours)
                    played_hours_formatted = '{:.2f}'.format(played_hours)
                    completed_hours_formatted = '{:.2f}'.format(completed_hours)

                # Populate row
                    row = [
                        or_empty(title),
                        or_empty(external_identifier),
                        or_empty(production_id),
                        or_empty(duration_formatted),
                        or_empty(play_count),
                        or_empty(played_hours_formatted),
                        or_empty(completed_count),
                        or_empty(completed_hours_formatted),
                        #or_empty(object_created_date),
                        or_empty(accesspoint_startdate),
                        or_empty(first_published_date),
                        or_empty(urlslug),
                        or_empty(url)
                    ]
                    output_writer.writerow(row)
    else:
        print('Needs at least three runtime arguments, ex: %s '
              '2015-01-01T12:00:00Z '
              '2015-12-30T12:00:00Z '
              'output.csv' % sys.argv[0])
