import apiai
import json
import requests
import urllib


#api.ai client

APIAI_ACCESS_TOKEN ="xxxxxxxxxxxxx"
ai = apiai.ApiAI(APIAI_ACCESS_TOKEN)

PLACES_API = 'xxxxxxxxxxx'



HELP_MSG = """
Hi there, Im a place bot..
I can help you find different places around you.
Just type where and what are you looking for.
For example- Coffee Shops in Connaught place
"""

def build_url(search_text='',types_text=''):
    base_url='https://maps.googleapis.com/maps/api/place/textsearch/json'
    key_string='?key='+PLACES_API
    query_string='&query='+urllib.parse.quote(search_text)
    sensor_string='&sensor=false'
    type_string=''
    if types_text!='':
        type_string='&types='+urllib.parse.quote(types_text)
    url = base_url+key_string+query_string+sensor_string+type_string
    search_results=requests.get(url)
    return search_results.json()

def photo_url(refer):
    base_url='https://maps.googleapis.com/maps/api/place/photo'
    key_string='&key='+PLACES_API
    size_string='?maxwidth=400'
    reference_string='&photoreference='+refer
    url=base_url+size_string+reference_string+key_string
    return url

def apiai_response(query,session_id):
    """ function to fetch api.ai response"""
    request=ai.text_request()
    request.lang='en'
    request.session_id=session_id
    request.query=query
    response = request.getresponse()
    return json.loads(response.read().decode('utf8'))


def parse_response(response):
    """func to parse resp and return param and intent"""
    result = response['result']
    params = result.get('parameters')
    intent = result['metadata'].get('intentName')
    whole_query=result.get('resolvedQuery')
    return intent,params,whole_query



def fetch_reply(query,session_id):
    """ main func to fetch reply for chatbot and return a reply"""
    response=apiai_response(query,session_id)
    print(response)
    intent,params,whole_query=parse_response(response)


    reply={}


    if response['result']['action'].startswith('smalltalk'):
        reply['type']='smalltalk'
        reply['data']=response['result']['fulfillment']['speech']

    elif intent=="places":
        reply['type'] = 'Places'
        params['sender_id']=session_id
        placess=build_url(search_text=whole_query)

        places_elements = []

        i=0

        for data in placess['results']:
            element={}
            if i<10:
                i+=1
                element['title']=data['name']
                element['subtitle']=data['formatted_address']
                try:
                    reference_id=data['photos'][0].get('photo_reference')
                    element['image_url']=photo_url(reference_id)
                    maps=(data['photos'][0].get('html_attributions')[0].split('=')[1].split('>')[0]).replace('"',"")

                    element['buttons']=[{
                    "type":"web_url",
                    "title":"Photos and Map",
                    "url": maps }]

                except:
                    pass

            else:
                break

            places_elements.append(element)

        reply['data']=places_elements


    else:
        reply['type']= 'none'
        reply['data']= [{"type":"payload","payload":"SHOW_HELP","title":"click here for help"}]

    return reply
