# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@


import os
import stat
import time
import sys
import string
import stack.commands

class command(stack.commands.ApplianceArgumentProcessor,
	stack.commands.add.command):
	pass

class Command(command):
	"""
	Add an appliance specification to the database.
	
	<arg type='string' name='appliance'>
	The appliance name (e.g., 'backend', 'frontend', 'nas').
	</arg>

	<param type='string' name='membership'>
	The full membership name of the appliance. This name will be displayed
	in the appliances menu by insert-ethers (e.g., 'NAS Appliance'). If
	not supplied, the membership name is set to the appliance name.
	</param>

	<param type='string' name='node'>
	The name of the root XML node (e.g., 'backend', 'nas'). If
	not supplied, the node name is set to the appliance name.
	</param>
	
	<param type='bool' name='public'>
	True means this appliance will be displayed by 'insert-ethers' in 
	the Appliance menu. The default is 'yes'.
	</param>

	<example cmd='add appliance nas membership="NAS Appliance" node=nas public=yes'>
	</example>
	"""

	def run(self, params, args):

		if len(args) != 1:
			self.abort('must supply one appliance')
		app_name = args[0]
					
		(mem_name, node, public) = \
			self.fillParams(
				[('membership', ), 
				('node', ''),
				('public', 'y')])

		public  = self.bool2str(self.str2bool(public))
		
		if not mem_name:
			mem_name = string.capitalize(app_name)

		#
		# check for duplicates
		#
		rows = self.db.execute("""
			select * from appliances where name='%s'
			""" % app_name)
		if rows > 0:
			self.abort('appliance "%s" already exists' % app_name)

		#
		# ok, we're good to go
		#
		self.db.execute("""
			insert into appliances (name, membership, public) values
			('%s', '%s', '%s')
			""" %  (app_name, mem_name, public))

		if not node:
			kickstartable = False
		else:
			kickstartable = True
			self.command('add.appliance.attr', [ app_name, 'node', node ])

		self.command('add.appliance.attr', [ app_name, 'kickstartable',
			self.bool2str(kickstartable) ])
		
		if kickstartable:
			next_server = None

			try:
				next_server = self.db.getHostAttr('localhost',
					'Kickstart_PrivateKickstartHost')
			except:
				rows = self.db.execute("""select value from
					global_attributes where
					attr='Kickstart_PrivateKickstartHost'
					""")

				if rows == 1:
					next_server, = self.db.fetchone()

			if next_server:
				self.command('add.appliance.attr', [app_name,
					'dhcp_nextserver', next_server])

				self.command('add.appliance.attr', [app_name,
					'dhcp_filename', 'pxelinux.0' ])

