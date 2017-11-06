import re, string, numpy

def _is_empty(obj):
	return obj == None or len(obj) == 0

def _is_hex(s):
	if not type(s) is str:
		return False
	return all(c in string.hexdigits for c in s)

def _parse_row(row):
	ret = row.split('|')
	for idx, entry in enumerate(ret):
		entry = entry.strip()
		ret[idx] = entry
	# remove all empty strings
	while ret.count('') != 0:
		ret.remove('')
	return ret

def parse_openstack_table(s):
	'''
	Example format:
+----+-----------+-------+------+-----------+-------+-----------+
| ID | Name      |   RAM | Disk | Ephemeral | VCPUs | Is Public |
+----+-----------+-------+------+-----------+-------+-----------+
| 1  | m1.tiny   |   512 |    1 |         0 |     1 | True      |
| 2  | m1.small  |  2048 |   20 |         0 |     1 | True      |
| 3  | m1.medium |  4096 |   40 |         0 |     2 | True      |
| 4  | m1.large  |  8192 |   80 |         0 |     4 | True      |
| 42 | m1.nano   |    64 |    0 |         0 |     1 | True      |
| 5  | m1.xlarge | 16384 |  160 |         0 |     8 | True      |
| 84 | m1.micro  |   128 |    0 |         0 |     1 | True      |
| c1 | cirros256 |   256 |    0 |         0 |     1 | True      |
| d1 | ds512M    |   512 |    5 |         0 |     1 | True      |
| d2 | ds1G      |  1024 |   10 |         0 |     1 | True      |
| d3 | ds2G      |  2048 |   10 |         0 |     2 | True      |
| d4 | ds4G      |  4096 |   20 |         0 |     4 | True      |
+----+-----------+-------+------+-----------+-------+-----------+
	'''
	if not type(s) is str:
		return None

	col_names = []
	col_vals = []

	s = s.replace('\r','')
	rows = s.split('\n')
	bar_count = 0

	for row in rows:
		m = re.match("\+-*\+-*\+\n?", row)
		if m != None:
			bar_count += 1
		elif bar_count == 1:
			# titles
			col_names.append(_parse_row(row))
		elif bar_count == 2:
			# rows with data
			col_vals.append(_parse_row(row))

	if len(col_names) > 1:
		# in case it takes multiple rows for a title
		col_names = numpy.array(col_names).transpose()
		for idx, name in col_names:
			col_names[idx] = ' '.join(name)
	else:
		# naturally throw an error if it's empty
		col_names = col_names[0]

	ret = []
	for row in col_vals:
		entry = {}
		for idx, val in enumerate(row):
			# as for now we don't eval
			# so everything returned as string
			col_name = col_names[idx]
			entry[col_name] = val
		ret.append(entry)

	return ret
