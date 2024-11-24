#  AUTOCONN2 -Mastering Network Observability: From Fundamentals to Advanced  (18/11/24 Afternoon session)

Sponsored by Kentik

### Control theory is at the base of observability.

We want to get metrics from the system, measure against some base line and determine what's the system health.


- automate away human intervention

- create feedback loops

(2 more but he was too quick)


### 2 problems:
- volume of data
- many types of data (format)

### Monitoring vs Observability
Monitoring takes the info on a graph/dashboard

Observability implies that your information has a purpose and you can use it to act on it
while traditional monitoring can have hard threshold to generate alerts etc..
Observability can lead to discover trends in the absence of hard thresholds

Observability includes:
- Metrics
- events (messages with timestamps)
- Log pretty much like events but mainly text based
- Traces (e.g packt flows/traces etcc)

### Network Observability workflow
. ingest huge amount of information
. clean, transformm normalize, classify, leabel group (similar to ML pre processing stuff)
. Advanced analytics, predict, baseline, correlate
  Find strong correlation between event
. visualize, filter and alert
. integrate with other tools (even driven automation?)

### Network Observability Tools
- Promethes
- telegraf
- Elk stack
- Jaeger
- Cilium Hubble
- grafana

these are all free

--- setup your kentik account

Primary:
SNMP 
Streaming telementry
Flow
Synthetic tests results
cloud flows logs

Metadata:
- SNMP
- GEO IP
- IP reputation data
- routing information
- rack unit, pod, cab
- etc..

Streaming dial out to the device
- needs a collector
  - that dial to the device and tells the device which path they want to subscribe to (this is done via a GNMI request)
  - the device then sends data using Goggle Protocol buffer  as a tcp stream to the collector

streaming use a lot less processing on the device and you get much better granularity (like every second the metric path is pushed out)
and it does not hav to wait for the polling period to get info
it can also stream out to multiple endpoints  and it is automation friendly

#### API and CLIs
if no push methods are available we have to use these (APIs and CLIs)

### Open Telemetry
it is part of Cloud Native OPen Foundation (CNOF)
it is a greamework and toolkit designed to create and manage telemetry data
 - collection of APIs, SDKs and tools
 - som projects included in this:
   - OTLP
   - Jaeger
   - Prometheus

### Flows
- sFlow
- Netflow v5
- Netflow v9
- IPFIX
- IPFIX 315 

the ipfix 315 doesn't create a flow cache anymore which is instead done by the previous version of ipfix/netflow
the good thing is that flows info are not cached but sent in real time
the down side is that the amount of flows per second sent increase significantly 


### Active vs Passive Monitoring
In active monitoring you have agents or anyway probes that simulate traffic, application etc.. and measure application metrics (e.g. page load response time etc..)

### Telemetry enrichment
this matches networ/netflow data with application and data infomation to trace what's behind ip and ports.
this gives a better context to read what the data is about



Valerio123!  <-- kentik account pwd

Check Cribl vs Kafka

------------------------------------------------------

# gnic lab commands

gnmic  --insecure -a 172.20.20.6:6030 -u admin -p admin capabilities

export GNMI_HOST=

gnmic --insecure -a 172.20.20.11:6030 -u admin -p admin get --path "openconfig:/interfaces/interface"

### config
gnmic --insecure -a 172.20.20.11:6030 -uadmin -padmin get --path "openconfig:/interfaces/interface/config"


### state
gnmic --insecure -a 172.20.20.11:6030 -uadmin -padmin get --path "openconfig:/interfaces/interface/state"

One of the nicest features of gNMI is the ability to subscribe to a stream of data with a secure connection over TCP. (UDP jooke would be here but you probably wouldnt get it). There are different types of subscriptions you can make. Try and think how you might use these in different scenarios.

Streams: a. Polling - this means the network device occasionally polls the needed information and sends to the client at whatever interval the client asks. b. ON_CHANGE - When something changes, the change information is sent to the client. c. TARGET_DEFINED - The network device is the target. This means that the device will chose what makes sense to send at intervals (like counters) and what to send when somethng changes(like interface state)

gnmic  --insecure -a 172.20.20.11:6030 -uadmin -padmin  subscribe --path "/interfaces/interface/state" --mode "stream" --stream-mode "on_change"

there are different streaming mode..

the on_change is similar to traps (but they are reliable)

### other gnmi command
gnmic --insecure -a 172.20.20.6:6030 -uadmin -padmin get --path "network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=BGP]/bgp/neighbors/neighbor[neighbor-address=10.0.250.2]/afi-safis/afi-safi[afi-safi-name=L2VPN_EVPN]/state"


```
[ script to generate alert via gnmi]
# Modules
from pygnmi.client import gNMIclient
# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
# Variables
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
from_sms = "+60318675309"
to_sms = "+12125555555"
host = ('172.20.20.5', '6030')

client = Client(account_sid, auth_token)

def alert(result):
    message = client.messages.create(
        body= message,
        from_="+18722412622",
        to="+16039789085",
)


# Body
if __name__ == '__main__':
    with gNMIclient(target=host, username='admin', password='admin', insecure=True) as gc:
        result = gc.get(path=['network-instances/network-instance[name=default]/protocols/protocol[identifier=BGP][name=BGP]/bgp/neighbors/neighbor[neighbor-address=10.0.250.2]/afi-safis/afi-safi[afi-safi-name=L2VPN_EVPN]/state])

    #do things here, call other functions
		#
    message = "BGP Message" + str(result)

    alert(message,from_sms,to_sms)
```

------------------------------------------------------

# data analysis foundamental (Phil Gervasi)

we want to automate analysis as much as possible and get insights

we use here 3 algorithms but first:
- what type of data do you have
- what kind of DB or source do you have
- what is yor final goal?
  - predict latency? bandwidh utilization? anomaly detection?

first normalize data:
- imputation: if you are missing a value you can replace it with something (median, mean? time series interpolation (basically mean of the 2 closest values)? )
- removal: or you can remove the value


# now Transform your data (Data Transformation)
normalization of format or values scales other 
- normalization (e.g. min-max normalization)
  Useful in K-nearest neighbours where fetures of large magnitude could dominate
  rescale: change the scale of the data so that it's between zero and one
  
  however sometime you want the raw value

- standardization
  transform data to a mean of zero and a standard deviation of 1
  it's not a range between [0,1]
  you use it to compare z-scores
  this can be used for outlier detection

- logarithminc
- exponential
- polynomial
- box-cox
- rank
this is easy for numerical data but more complex for textual data

## anomaly detection
1. Point anomalies - single instances of data
2. contextual anomalies - data points that are outliers in a specific context
3. collective anomalies

Clustering to find outliers (anomalies)
- k-means clustering using packet loss and latency as dimnesions (in the example)


Note: of course yuo have to train the model

## predictive analysis (logistic)
Logistic Regression (more of a classification)
- used to predict if data belongs to a particular predefined class (binary)
- can I use it to classify the network as healthy or degraded?

## predictive analysis (linear)
- Time series model that assumes a linear relationship between the input and output
- If the relationship is more complex and not linear, linear regression may not capture it accurately (common with network telemetry data)
 (well you can have transformation or kernel functions..)

Example - again aybe packet loss and latency?

Note that nettwork data is pretty seasonal (as in mybe weekly or daily patterns) so you can use SARIMA (seasonal Arima) models



-------------------------
### Lots of telemety

How do we bring everything together?

- SNMP (is staying for some time at least)
- Devops collects data in Influx/Prom/Grafana
    - grafana requires skills for large organizations

Streaming Telemetry:
 - lots of interest
 - but who supports everything? (commercial products?)
 - not everything available via streaming telemetry

 syslog:
 - splunk and elk stacks are the most commons


Workflow Tasks
Observability tools are critical to running a network, but it can often be work to keep your inventory in the observability platforms

Source Of Truth
In the last ~5 years there has been an explosion of support in our industry for open SoT systems such as Netbox
(Alternative: Nautobot/Opsmill)