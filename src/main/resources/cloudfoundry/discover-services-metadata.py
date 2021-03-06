#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

from cloudfoundry.util import CFClientUtil
from java.io import File
import simplejson as json
import urllib2
import time

sqlClient = deployed.container
space = sqlClient.getProperty("space")
cfClient = CFClientUtil.createSpaceClient(space)

appName = "discovery-%s-%s" % (deployed.name, space.getProperty('spaceName'))
uris = ["%s.%s" % (appName, space.getProperty("organization").getProperty('defaultDomain'))]


print "Creating discovery application"
cfClient.createApplication(appName, uris=uris)
print "Binding db service"
cfClient.bindService(appName, deployed.getProperty('cloudFoundryDbService'))

print "Uploading discovery application code"
cfClient.uploadApplication(appName, File('ext/cloudfoundry/discoveryapp'))
print "Starting discovery application"
cfClient.startApplication(appName, deployed.retrialCount, deployed.waitTime)

print "Fetch information from http://%s" % uris[0]

retryCount = 0
while retryCount < 20:
    req = urllib2.Request("http://%s" % uris[0])
    try:
        response = urllib2.urlopen(req)
        vcapServices = json.load(response)
        break
    except urllib2.HTTPError, e:
        print "failed to connect to discovery application. will retry in 5 secondes"
        time.sleep(5)
        retryCount += 1

if retryCount == 20:
    raise Exception("Could not access discovery application")

print "Find database credentials"
for vcapService in vcapServices.keys():
    for vcapServiceInstance in vcapServices[vcapService]:
        if "mysql" in vcapServiceInstance["tags"]:
            print "Found database creds"
            creds = vcapServiceInstance["credentials"]
            context.setAttribute("%s-username" % vcapServiceInstance["name"], creds["username"])
            context.setAttribute("%s-password" % vcapServiceInstance["name"], creds["password"])
            context.setAttribute("%s-host" % vcapServiceInstance["name"], creds["hostname"])
            context.setAttribute("%s-db" % vcapServiceInstance["name"], creds["name"])

cfClient.logout()
