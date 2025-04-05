from googleapiclient import discovery
from google.auth import default

credentials, _ = default()
compute = discovery.build('compute', 'v1', credentials=credentials)

project = 'pw-techfest-team-10'
zone = 'europe-west1-c'
instance = 'elk-vm'

# Pobranie danych o instancji
result = compute.instances().get(project=project, zone=zone, instance=instance).execute()

# Przykład: wypisanie adresu IP
network_interfaces = result.get('networkInterfaces', [])
if network_interfaces:
    ip_address = network_interfaces[0].get('networkIP')
    print("Internal IP:", ip_address)
