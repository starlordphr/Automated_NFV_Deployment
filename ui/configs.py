'''
This script handles parsing SLA configurations for ui script to use
'''

# Tutorial at:
# https://docs.python.org/2/library/configparser.html

import sys, os
from ConfigParser import ConfigParser

sla_configs = {}

_cfg = None

# constants

SERVER_CONFIG = {
	"FLAVOR_NAME" : "",
	"IMAGE_NAME" : "",
	"PRIVATE_NETWORK_NAME" : "",
	"PUBLIC_NETWORK_NAME" : "",
	"SECURITY_GROUP_NAME" : "optional",
	"KEY_NAME" : "optional",
	"INSTANCE_NAME" : ""
}

OAI_CONFIGS = {
	'eNodeB' : {
		'TIME_ZONE' : "optional"
	},
	'ue' : {
		'TIME_ZONE' : "optional"
	},
	'hss' : {},
	'mme' : {},
	'spgw' : {}
}

def parse_sla_config(fname):
	# global all constants
	global _cfg, sla_configs

	# check file existence
	if not os.path.isfile(fname):
		raise RuntimeError("[configs.py] %s: file does not exist!" % fname)

	_cfg = ConfigParser()
	_cfg.read(fname)

	if not _cfg.has_section('meta'):
		raise RuntimeError("[configs.py] %s: config file missing 'meta' section!" % fname)

	for vm_name, vm_type in _cfg.items('meta'):
		# get deployment configuration for vm
		deploy_config = _get_deploy_config(vm_name, vm_type)

		# get oai configuration for vm
		oai_configs = _get_oai_configs(vm_name)

		sla_configs[vm_name] = {
			"vm_type" : vm_type,
			"deploy_config" : deploy_config,
			"oai_configs" : oai_configs
		}

def _try_get_option(sect, opt, data_type='str', optional=False):
	data_type = data_type.lower()
	if _cfg.has_option(sect, opt):
		if data_type == 'str' or data_type == 'string':
			return _cfg.get(sect, opt)
		elif data_type == 'int' or data_type == 'integer':
			return _cfg.getint(sect, opt)
		elif data_type == 'float':
			return _cfg.getfloat(sect, opt)
		elif data_type == 'bool' or data_type == 'boolean':
			return _cfg.getboolean(sect, opt)
		else:
			raise RuntimeError("[configs.py] %s: unrecognized data type spec" % data_type)
	elif optional:
		return None
	else:
		raise RuntimeError("[configs.py] Section '%s' missing option '%s'!" % (sect, opt))

# returns (data_type, optional)
def _opt_of_opt(opt):
	# defaults
	data_type = 'str'
	optional = False

	if type(opt) == str:
		opt = opt.split()
		optional = "optional" in opt
		if optional:
			opt.remove("optional")
		if len(opt) > 0:
			data_type = opt[0]

	return data_type, optional

def _get_deploy_config(vm_name, vm_type):
	sect = '%s-deploy' % vm_name
	if vm_type == 'server':
		ret = dict(SERVER_CONFIG)

		for opt in ret:
			data_type, optional = _opt_of_opt(ret[opt])
			ret[opt] = _try_get_option(sect, opt, data_type, optional)

		return ret
	elif vm_type == 'some other type':
		return None
	else:
		raise RuntimeError("Unknown VM type in configuration: %s" % vm_type)

def _get_oai_configs(vm_name):
	ret = {}
	for oai_opt in OAI_CONFIGS:
		sect = '%s-%s' % (vm_name, oai_opt)
		if _cfg.has_section(sect):
			if len(_cfg.options(sect)) == 0:
				ret[oai_opt] = {}
			else:
				conf = dict(OAI_CONFIGS[oai_opt])

				for opt in conf:
					data_type, optional = _opt_of_opt(conf[opt])
					conf[opt] = _try_get_option(sect, opt, data_type, optional)

				ret[oai_opt] = conf

	# check if UE and eNodeB coexists since they're really close
	if ret.has_key('eNodeB') and ret.has_key('ue'):
		coexists = True
		if len(ret['eNodeB']) == 0 and len(ret['ue']) > 0:
			ret['eNodeB_ue'] = ret['ue']
		elif len(ret['eNodeB']) > 0 and len(ret['ue']) == 0:
			ret['eNodeB_ue'] = ret['eNodeB']
		elif len(ret['eNodeB']) == 0 and len(ret['ue']) == 0:
			ret['eNodeB_ue'] = 0
		else:
			# different configuration for UE and eNodeB, keep both
			coexists = False

		if coexists:
			ret.pop('eNodeB')
			ret.pop('ue')

	return ret
