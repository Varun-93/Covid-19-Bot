import json
import os
import requests
import http.client
from flask import Flask
from flask import request
from flask import make_response
from mail import *

app=Flask(__name__)

@app.route('/webhook',methods=['POST'])

def webhook():
    req = request.get_json(silent=True, force=True)
    print(json.dumps(req, indent=4))
    res = makeResponse(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeResponse(req):
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    parameters = result.get("parameters")
    pincode=parameters.get("pincode")
    toaddress=parameters.get("email")
    statename=parameters.get("geo-city")
    country=parameters.get("geo-country")
    intent = result.get("intent").get('displayName')

    conn = http.client.HTTPSConnection("api.covid19india.org")
    conn.request("GET", "/data.json", '', headers={})
    res = conn.getresponse()
    data = res.read()
    string = data.decode("utf-8")
    json_obj = json.loads(string)


    if(intent=='Pincode wise'):

        resp = requests.get("https://pincode.saratchandra.in/api/pincode/"+pincode)
        rj = resp.json()['data'][0]
        state = str(rj['state_name']).title()
        district = str(rj['district'])

        # Connection for district data api call
        conn1 = http.client.HTTPSConnection("api.covid19india.org")
        conn1.request("GET", "/state_district_wise.json", '', headers={})
        res1 = conn1.getresponse()
        data1 = res1.read()
        string1 = data1.decode("utf-8")
        json_obj1 = json.loads(string1)

        for i in range(1, 38):

            if json_obj['statewise'][i]['state'] == state:
                c_state_wise = json_obj['statewise'][i]['confirmed']
                ac_state_wise = json_obj['statewise'][i]['active']
                r_state_wise = json_obj['statewise'][i]['recovered']
                d_state_wise = json_obj['statewise'][i]['deaths']
                time = json_obj['statewise'][i]['lastupdatedtime']
                break

        try:
            c_district_wise = json_obj1[state]['districtData'][district]['confirmed']
            mailit(toaddress)
            fulfillmenttext=('Total cases as per last updated time ' + time + ' for ' + state + ' is: ' + c_state_wise + '. Active cases being: ' + ac_state_wise + ' and the Recovered cases: ' + r_state_wise + ' with number of deaths being equal to '+d_state_wise+'. While for your district ' + district + ' there are total ' + str(c_district_wise) + ' cases.')
        except:
            mailit(toaddress)
            fulfillmenttext=('Total cases for ' + state + ' is: ' + c_state_wise + '. Active cases being: ' + ac_state_wise + ' and the Recovered cases: ' + r_state_wise + ' with number of deaths being equal to '+d_state_wise+'. While could not find any information about your district.')

    elif(intent=='State wise'):

        try:
            for i in range(1, 38):

                if json_obj['statewise'][i]['state'] == statename:
                    c_state_wise = json_obj['statewise'][i]['confirmed']
                    ac_state_wise = json_obj['statewise'][i]['active']
                    r_state_wise = json_obj['statewise'][i]['recovered']
                    d_state_wise = json_obj['statewise'][i]['deaths']
                    time = json_obj['statewise'][i]['lastupdatedtime']
                    mailit(toaddress)
                    fulfillmenttext = ('Total cases as per last updated time ' + time + ' for ' + statename + ' is: ' + c_state_wise + '. Active cases being: ' + ac_state_wise + ' and the Recovered cases: ' + r_state_wise + ' with number of deaths being equal to '+d_state_wise+'.')
                    break
                else:
                    fulfillmenttext = ' '

            if fulfillmenttext == ' ':
                mailit(toaddress)
                fulfillmenttext=('I was unable to find the new cases for the state you mentioned. I am trying to learn more')

        except:
            mailit(toaddress)
            fulfillmenttext=('I was unable to find the new cases for the state you mentioned. I am trying to learn more')

    elif(intent=='Total cases in India'):
        ac_country_wise=json_obj['statewise'][0]['active']
        c_country_wise=json_obj['statewise'][0]['confirmed']
        r_country_wise = json_obj['statewise'][0]['recovered']
        d_country_wise = json_obj['statewise'][0]['deaths']
        time = json_obj['statewise'][0]['lastupdatedtime']
        fulfillmenttext = ('Total cases as per last updated time ' + time + ' for ' + country + ' is: ' + c_country_wise + '. Active cases being: ' + ac_country_wise + ' and the Recovered cases: ' + r_country_wise + ' with number of deaths being equal to ' + d_country_wise + '.')

    elif (intent == 'New cases in India'):
        nc_country_wise = json_obj['statewise'][0]['deltaconfirmed']
        c_country_wise = json_obj['statewise'][0]['confirmed']
        nr_country_wise = json_obj['statewise'][0]['deltarecovered']
        nd_country_wise = json_obj['statewise'][0]['deltadeaths']
        time = json_obj['statewise'][0]['lastupdatedtime']
        fulfillmenttext = ('Total new cases as per last updated time ' + time + ' for ' + country + ' is: ' + nc_country_wise + ' and the new Recovered cases: ' + nr_country_wise + ' while there has been ' + nd_country_wise + ' new deaths. Total updated cases in ' + country + ' now equals to ' + c_country_wise + '.')

    else:
        try:
            conn = http.client.HTTPSConnection("api.covid19india.org")
            conn.request("GET", "/data.json", '', headers={})
            res = conn.getresponse()
            data = res.read()
            string = data.decode("utf-8")
            json_obj = json.loads(string)

            for i in range(1, 38):

                if json_obj['statewise'][i]['state'] == statename:
                    c_state_wise = json_obj['statewise'][i]['confirmed']
                    ncc_state_wise = json_obj['statewise'][i]['deltaconfirmed']
                    ncr_state_wise = json_obj['statewise'][i]['deltarecovered']
                    ncd_state_wise = json_obj['statewise'][i]['deltadeaths']
                    time = json_obj['statewise'][i]['lastupdatedtime']
                    fulfillmenttext = (
                                'Total new cases as per last updated time ' + time + ' for ' + statename + ' is: ' + ncc_state_wise + ' and the new Recovered cases: ' + ncr_state_wise + ' while there has been ' + ncd_state_wise + ' new deaths. Total updated cases in ' + statename + ' now equals to ' + c_state_wise + '.')
                    break
                else:
                    fulfillmenttext = ' '

            if fulfillmenttext == ' ':
                fulfillmenttext=('I was unable to find the new cases for the state you mentioned. I am trying to learn more')
        except:
            fulfillmenttext=('I was unable to find the new cases for the state you mentioned. I am trying to learn more')


    return {
        "fulfillmentText": fulfillmenttext
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')