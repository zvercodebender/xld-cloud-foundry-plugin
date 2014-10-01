from cloudfoundry.util import CFClientUtil
import sys

def new_instance(id, ciType):
    return Type.valueOf(ciType).descriptor.newInstance(id)

def create_or_read(ci):
    if not repositoryService.exists(ci.id):
        ci = repositoryService.create([ci])[0]
    else:
        ci = repositoryService.read(ci.id)
    return ci

def reverse_engineer_domain(domain, organizationId):
    organizationCi = create_or_read(new_instance(organizationId, "cf.Organization"))
    domain = new_instance("%s/%s" % (organizationId, domain.name), "cf.Domain")
    if not repositoryService.exists(domain.id):
        domain.setProperty("domainName", domain.name)
        domain.setProperty("organization", organizationCi)
        repositoryService.create([domain])


cfClient = CFClientUtil.createOrganizationClient(thisCi)

if cfClient is None:
	sys.exit("Could not connect to cloudfoundry organization")

domains = cfClient.discoverDomains(thisCi.getProperty("organizationName"))

for domain in domains:
	reverse_engineer_domain(domain, thisCi.getProperty("id"))