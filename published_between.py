import sys
import xml.etree.ElementTree as ET
import requests
import csv

CHAOS_ACCESSPOINT_GUID = 'C4C2B8DA-A980-11E1-814B-02CEA2621172'
DATETIME_FORMAT = '%d/%m/%y %H:%M:%S'


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
    return v.encode('utf8') if v else ''

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

        objects = get_all_objects(query, sort='apc4c2b8da-a980-11e1-814b-02cea2621172_PubStart+asc')

        with open(sys.argv[3], 'wb') as output_file:
            output_writer = csv.writer(output_file)
            output_writer.writerow([
                'title',
                'asset_id',
                'produciton_id',
                'duration',
                'published_on_dka_date',
                'first_published_date',
                'url'
            ])
            for o in objects:
                metadata = get_object_metadata(o, '5906a41b-feae-48db-bfb7-714b3e105396')
                ns = {
                    'dka': 'http://www.danskkulturarv.dk/DKA2.xsd'
                }
                #ET.dump(o)
                if metadata is None:
                    print('Found an object without metadata attached.')
                else:
                    title = metadata.find('dka:Title', ns).text
                    external_identifier = metadata.find('dka:ExternalIdentifier', ns).text
                    metafields = metadata.findall('dka:Metafield', ns)

                    production_id = [f.find('dka:Value', ns).text
                                     for f in metafields
                                     if f.find('dka:Key', ns).text == 'ProductionId']
                    # We need only one
                    production_id = production_id[0] if len(production_id) > 0 else ''

                    duration = [f.find('dka:Value', ns).text
                                       for f in metafields
                                       if f.find('dka:Key', ns).text == 'Duration']
                    # We need only one
                    duration = duration[0] if len(duration) > 0 else ''

                    if duration:
                        # Convert duration to hours
                        duration_secs = float(duration) / 1000.0
                        duration_minutes = duration_secs / 60.0
                        duration_hours = duration_minutes / 60.0
                        duration = '{:.2f}'.format(duration_hours)

                    # First published
                    first_published_date = metadata.find('dka:FirstPublishedDate', ns).text

                    #object_created_date = o.find('DateCreated').text
                    accesspoint_startdate = o.find('AccessPoints').find('AccessPoint_Object_Join').find('StartDate').text

                    url = 'http://www.danskkulturarv.dk/chaos_post/%s/' % o.find('GUID').text

                    row = [
                        or_empty(title),
                        or_empty(external_identifier),
                        or_empty(production_id),
                        or_empty(duration),
                        #or_empty(object_created_date),
                        or_empty(accesspoint_startdate),
                        or_empty(first_published_date),
                        or_empty(url)
                    ]
                    output_writer.writerow(row)
    else:
        print('Needs at least three runtime arguments, ex: %s '
              '1970-01-01T12:00:00Z '
              '2015-12-30T12:00:00Z '
              'output.csv' % sys.argv[0])
