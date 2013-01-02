import os
import sys
import logging

from autotest.client import test
from autotest.client import utils
from autotest.client.shared import git
from autotest.client.shared import error

class autotest_rpc_server(test.test):
    version = 1
    @error.context_aware
    def run_once(self,
                 autotest_uri='git://github.com/autotest/autotest.git',
                 arc_uri='git://github.com/clebergnu/arc.git'):

        error.context("Checking out autotest", logging.info)
        autotest_repo = git.GitRepoHelper(autotest_uri,
                                          destination_dir=self.srcdir)
        autotest_repo.execute()

        error.context("Checking out autotest rpc client (arc)", logging.info)
        arc_repo = git.GitRepoHelper(arc_uri,
                                     destination_dir=self.srcdir)
        arc_repo.execute()

        # ensure the checked out code is used
        autotest_dir = os.path.join(self.srcdir, 'autotest')
        arc_dir = os.path.join(self.srcdir, 'arc')

        # We should favor the newly checked out code over the one we're running
        sys.path.insert(0, self.srcdir)
        sys.path.insert(1, arc_dir)
        os.environ['PYTHONPATH'] = '%s:%s:%s' % (self.srcdir,
                                                 arc_dir,
                                                 os.environ.get('PYTHONPATH', ''))

        #
        # Package dependencies
        #
        package_deps = os.path.join(autotest_dir,
                                    'autotest',
                                    'installation_support',
                                    'autotest-install-packages-deps')
        utils.system(package_deps)

        #
        # Database Setup
        #
        # FIXME: portability
        utils.system('systemctl start mysqld.service')

        database_turnkey = os.path.join(autotest_dir,
                                        'autotest',
                                        'installation_support',
                                        'autotest-database-turnkey')
        utils.system('%s -s' % database_turnkey)
