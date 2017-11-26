import re, string, numpy, json

# for printing with color / style
class bcolors:
	# colors
	RED='\033[31m'
	GREEN='\033[32m'
	YELLOW='\033[33m'
	CYAN='\033[36m'
	GRAY='\033[37m'
	NC='\033[0m' # No Color

	# styles
	BOLD = '\033[1m'
	ITALIC = '\033[3m'
	UNDERLINE = '\033[4m'
	BLINK = '\033[5m'

def print_highlight(msg):
	print "%s%s%s" % (bcolors.CYAN, msg, bcolors.NC)

def print_error(msg):
	print "%s%s%s" % (bcolors.RED, msg, bcolors.NC)

def print_warning(msg):
	print "%s%s%s" % (bcolors.YELLOW, msg, bcolors.NC)

def print_pass(msg):
	print "%s%s%s" % (bcolors.GREEN, msg, bcolors.NC)

def print_comment(msg):
	print "%s%s%s" % (bcolors.GRAY, msg, bcolors.NC)

def _is_empty(obj):
	return obj == None or len(obj) == 0

def _is_hex(s):
	if not type(s) is str:
		return False
	return all(c in string.hexdigits for c in s)

def _parse_row(row, colcount=-1):
	ret = row.split('|')
	for idx, entry in enumerate(ret):
		entry = entry.strip()
		ret[idx] = entry
	# remove all empty strings
	while ret.count('') != 0:
		ret.remove('')
	if colcount >= 0 and len(ret) < colcount:
		for i in xrange(colcount - len(ret)):
			ret.append('')
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
			col_vals.append(_parse_row(row, len(col_names[0])))

	if len(col_names) > 1:
		# in case it takes multiple rows for a title
		col_names = numpy.array(col_names).transpose()
		for idx, name in col_names:
			col_names[idx] = ' '.join(name)
	elif len(col_names) == 1:
		col_names = col_names[0]
	else:
		# Assumes incorrect input
		return None

	ret = []
	for row in col_vals:
		if len(col_names) != len(row):
			return None
		entry = {}
		for idx, val in enumerate(row):
			# as for now we don't eval
			# so everything returned as string
			col_name = col_names[idx]
			entry[col_name] = val
		ret.append(entry)

	return ret

def format_dict(obj):
	return json.dumps(obj, indent=2)
