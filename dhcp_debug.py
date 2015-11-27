#!/usr/bin/python
import datetime

def parse_leases(lease_file):
	leases = {}
	lease = {}
	in_lease = False
	for line in lease_file:
		if line.lstrip().startswith('#'):

			continue
		tokens = line.split()

		if len(tokens) == 0:
			continue
		key = tokens[0].lower()

		if key == 'lease':
			if in_lease:
				raise Exception('Parsing error')
			else:
				in_lease = True
				lease = {'id': None, 'ip' : tokens[1], 'count': 1, 'client-hostname': ''}
		elif key == 'hardware':
			if not in_lease:
				raise Exception('Parsing error')
			else:
				in_lease = True
				lease['id'] = tokens[2].replace(';','')

		elif key == 'uid' or key == 'client-hostname':
			if not in_lease:
				raise Exception('Parsing error')
			else:
				lease[key] = tokens[1].replace(';','')

		elif key == '}':
			
			if in_lease:
				if lease['id'] not in leases:
					leases[lease['id']] = lease
				else:
					leases[lease['id']]['count'] += 1
					leases[lease['id']]['ip'] = lease['ip']
					if leases[lease['id']]['client-hostname'] == '':
						leases[lease['id']]['client-hostname'] = lease['client-hostname']

			lease = {}
			in_lease = False

	return leases

def count_active_leases(all_leases, now):
	count = 0
	for lease in all_leases.itervalues():
		if timestamp_inbetween(now, lease['starts'], lease['ends']):
			count += 1
	return count

def print_unique_leases(all_leases, gwname):
	print "------------"+gwname+"------------"
	#for lease in all_leases.itervalues():
	#	print "ID:" + lease['id'] + ', COUNT: ' + str(lease['count'])
	i = 0
	for lease in sorted(all_leases.items(),key=lambda x: x[1]['count'],reverse=True):
		lease = lease[1]
  		#print lease
  		print "ID:" + lease['id'] + ', COUNT: ' + str(lease['count']) + ', IP: '+lease['ip']+', HOSTNAME: ' + lease['client-hostname']
  		i += 1
  		if i > 5:
  			break

def timestamp_inbetween(now, start, end):
	return start < now < end

lease_files = [
	{
		'file' : 'dhcp_parad0x.leases',
		'name' : 'parad0x'
	},
	{
		'file' : 'dhcp_c1024.leases',
		'name' : 'c1024'
	},
	{
		'file' : 'dhcp_fussel.leases',
		'name' : 'fussel'
	},
	{
		'file' : 'dhcp_descilla.leases',
		'name' : 'des2'
	}
]

for file in lease_files:
	print_unique_leases(parse_leases(open(file['file'], 'r')), file['name'])

# scp root@c1024.ffms:/var/lib/dhcp/dhcpd.leases dhcp_c1024.leases && scp root@parad0x.ffms:/var/lib/dhcp/dhcpd.leases dhcp_parad0x.leases && scp root@fussel.ffms:/var/lib/dhcp/dhcpd.leases dhcp_fussel.leases && scp root@5.9.86.145:/var/lib/dhcp/dhcpd.leases dhcp_descilla.leases
