import ldap3
import os
from getpass import getpass

LDAP_HOST = "ldap.jumpcloud.com"
LDAP_PORT = "389"
LDAP_BASE_DN = "ou=Users,o=638853a7676fe04ccf41a9ed,dc=jumpcloud,dc=com"
LDAP_DOMAIN = "jumpcloud.com"
LDAP_USER = "jumpcloud"
LDAP_EXCLUDED_ACCOUNTS = ""

# Main changes are in the user and server : 
# BEFORE : 
user = "%s\%s" % (LDAP_DOMAIN, LDAP_USER)
ldap_server = "%s:%s" % (LDAP_HOST, LDAP_PORT)
# AFTER : 
user = "uid=%s,%s" % (LDAP_USER, LDAP_BASE_DN) 
ldap_server = LDAP_HOST # No Domain

SSL = True
authentication = ldap3.SIMPLE

LDAP_PASSWORD = getpass()

print ('ldap_server: %s' % ldap_server)
print ('use_ssl: %s' % SSL)
print ('user: %s' % user)
print ('password %s' % LDAP_PASSWORD)
print ('authentication: %s' % authentication)

server = ldap3.Server(ldap_server, get_info=ldap3.ALL, use_ssl=SSL)
conn = ldap3.Connection(
    LDAP_HOST,
    user=user,
    password=LDAP_PASSWORD,
    # authentication=ldap3.NTLM, # NTLM -> Microsoft auth, not working here
    raise_exceptions=True,
    auto_bind=True)

attributes = [
           "givenName",
           "sn",
           #"sAMAccountName", -> Microsoft identifier, not available
           "mail",
           #"thumbnailPhoto" -> attribute not available neither 
       ]
conn.search(LDAP_BASE_DN, '(objectclass=person)', attributes=attributes)

for entry in conn.entries:
    print(entry)
