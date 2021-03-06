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
import sys
import stack.file
import stack.commands

class Implementation(stack.commands.Implementation):	
	"""
	Copy a Linux OS CD. This is when the CD is a standard CentOS
	RHEL or Scientific Linux CD
	"""

	def run(self, args):

		(clean, prefix, treeinfo) = args

		name = None
		vers = None
		arch = None

		file = open(treeinfo, 'r')
		for line in file.readlines():
			a = line.split('=')

			if len(a) != 2:
				continue

			key = a[0].strip()
			value = a[1].strip()

			if key == 'family':
				if value == 'Red Hat Enterprise Linux':
					name = 'RHEL'
				elif value == 'CentOS':
					name = 'CentOS'
			elif key == 'version':
				vers = value
			elif key == 'arch':
				arch = value
		file.close()

		if not name:
			name = "BaseOS"
		if not vers:
			vers = stack.version
		if not arch:
			arch = 'x86_64'
			
		OS = 'redhat'
		roll_dir = os.path.join(prefix, name, vers, OS, arch)
		destdir = os.path.join(roll_dir, 'RPMS')

		if clean and os.path.exists(roll_dir):
			print 'Cleaning %s version %s ' % (name, vers),
			print 'for %s from pallets directory' % arch
			os.system('/bin/rm -rf %s' % roll_dir)
			os.makedirs(roll_dir)

		print 'Copying "%s" (%s,%s) pallet ...' % (name, vers, arch)
		if not os.path.exists(destdir):
			os.makedirs(destdir)

		cdtree = stack.file.Tree(self.owner.mountPoint)
		for dir in cdtree.getDirs():
			for file in cdtree.getFiles(dir):
				if not file.getName().endswith('.rpm'):
					continue
				if file.getPackageArch() != 'src' and \
					file.getBaseName() != 'comps' and \
					file.getName() != 'comps.rpm' \
					and not (arch == 'i386' and \
					re.match('^kudzu.*', file.getBaseName())):
						os.system('cp -p %s %s' % (
							file.getFullName(), 
							destdir))
		#
		# lay down a minimal roll XML config file
		#
		f = open('%s' % os.path.join(roll_dir, 'roll-%s.xml' % name),
			'w')
		f.write('<roll name="%s" interface="6.0.2">\n' % name)
		f.write('<info version="%s" release="%s" arch="%s" os="%s"/>\n' % (vers, stack.release, arch, OS))
		f.write('<iso maxsize="0" bootable="0"/>\n')
		f.write('</roll>\n')
		f.close()

		return (name, vers, arch)


