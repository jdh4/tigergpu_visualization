# conda create --name ldap-env -c conda-forge python-ldap <asciimatics>
# conda activate ldap-env

import ldap

puUrl = "ldaps://ldap.princeton.edu"
puBase = "o=Princeton University,c=US"
searchFilter = "uid=jdh4"
searchAttribute = ["cn", "uid", "mail", "department"]
searchScope = ldap.SCOPE_SUBTREE

l = ldap.initialize(puUrl)
l.protocol_version = ldap.VERSION3
l.simple_bind_s()
ldap_result = l.search_s(puBase, searchScope, searchFilter, searchAttribute)
l.unbind_s()

print(ldap_result)
