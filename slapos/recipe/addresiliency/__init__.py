##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from slapos.recipe.librecipe import GenericSlapRecipe

import os


class Recipe(GenericSlapRecipe):
    """ This class provides the installation of the resilience
        scripts on the partition.

        bin/takeover will perform a rename (must be run manually).
        bin/bully will monitor, run elections and perform renames when needed.
    """

    def _install(self):
        path_list = []

        confpath = os.path.join(self.options['etc'], 'bully.conf')

        ip_list = self.parameter_dict['ip-list']
        print 'Creating bully configuration with ips : %s\n' % ip_list

        conf = self.createFile(confpath,
                               self.substituteTemplate(
                               self.getTemplateFilename('bully.conf.in'),
                               {
                                   'self_id': int(self.parameter_dict['number']),
                                   'ip_list': ip_list
                                   }
                               ))
        path_list.append(conf)

        slap_connection = self.buildout['slap-connection']

        if self.optionIsTrue('enable-bully-service', default=False):
            bully_dir = self.options['services']
        else:
            bully_dir = self.options['bin']

        bully_wrapper = self.createPythonScript(
            name=os.path.join(bully_dir, self.options['wrapper-bully']),
            absolute_function='slapos.recipe.addresiliency.bully.run',
            arguments={
                'confpath': confpath,
                'server_url': slap_connection['server-url'],
                'key_file': slap_connection.get('key-file'),
                'cert_file': slap_connection.get('cert-file'),
                'computer_id': slap_connection['computer-id'],
                'partition_id': slap_connection['partition-id'],
                'software': slap_connection['software-release-url'],
                'namebase': self.parameter_dict['namebase'],
            })

        path_list.append(bully_wrapper)

        takeover_wrapper = self.createPythonScript(
            name=os.path.join(self.options['bin'], self.options['wrapper-takeover']),
            absolute_function='slapos.recipe.addresiliency.takeover.run',
            arguments={
                'server_url': slap_connection['server-url'],
                'key_file': slap_connection.get('key-file'),
                'cert_file': slap_connection.get('cert-file'),
                'computer_id': slap_connection['computer-id'],
                'partition_id': slap_connection['partition-id'],
                'software': slap_connection['software-release-url'],
                'namebase': self.parameter_dict['namebase'],
            })

        path_list.append(takeover_wrapper)

        return path_list


