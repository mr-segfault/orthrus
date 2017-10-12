import unittest
from orthrus.commands import *
from orthrusutils.orthrusutils import *

class TestOrthrusCoverage(unittest.TestCase):

    description = 'Test harness'
    orthrusdirname = '.orthrus'
    config = {'orthrus': {'directory': orthrusdirname}}
    abconf_file = orthrusdirname + '/conf/abconf.conf'
    routineconf_file = orthrusdirname + '/conf/routineconf.conf'

    def test_coverage(self):
        args = parse_cmdline(self.description, ['coverage', '-j', self.add_cmd.job.id])
        cmd = OrthrusCoverage(args, self.config)
        self.assertTrue(cmd.run())
        time.sleep(3*TEST_SLEEP)
        self.assertTrue(os.path.isfile(self.add_cmd.job.rootdir + '/afl-out/cov/web/index.html'))

    def test_coverage_abtest(self):
        args = parse_cmdline(self.description, ['coverage', '-j', self.add_cmd_abtest.job.id])
        cmd = OrthrusCoverage(args, self.config)
        self.assertTrue(cmd.run())

    @classmethod
    def setUpClass(cls):
        # Create
        args = parse_cmdline(cls.description, ['create', '-fuzz', '-cov'])
        cmd = OrthrusCreate(args, cls.config)
        assert cmd.run(), "Failed class cmd"
        # Add routine
        routineconf_dict = {'job_type': 'routine', 'fuzz_cmd': 'main @@', 'num_jobs': 1,
                            'job_desc': [{'fuzzer': 'afl-fuzz', 'fuzzer_args': '', 'seed_dir': './seeds'}
                                         ]
                            }
        with open(cls.routineconf_file, 'w') as routineconf_fp:
            json.dump(routineconf_dict, routineconf_fp, indent=4)
        args = parse_cmdline(cls.description, ['add', '--jobconf={}'.format(cls.routineconf_file)])
        cls.add_cmd = OrthrusAdd(args, cls.config)
        assert cls.add_cmd.run(), "Failed class cmd"
        # Add a/b test
        abconf_dict = {'job_type': 'abtests', 'fuzz_cmd': 'main @@', 'num_jobs': 2,
                       'job_desc': [{'fuzzer': 'afl-fuzz', 'fuzzer_args': '', 'seed_dir': './seeds'},
                                    {'fuzzer': 'afl-fuzz-fast', 'fuzzer_args': '', 'seed_dir': './seeds'}
                                    ]
                       }
        with open(cls.abconf_file, 'w') as abconf_fp:
            json.dump(abconf_dict, abconf_fp, indent=4)
        args = parse_cmdline(cls.description, ['add', '--jobconf={}'.format(cls.abconf_file)])
        cls.add_cmd_abtest = OrthrusAdd(args, cls.config)
        assert cls.add_cmd_abtest.run(), "Failed class cmd"
        # Start routine
        args = parse_cmdline(cls.description, ['start', '-j', cls.add_cmd.job.id])
        start_cmd = OrthrusStart(args, cls.config)
        assert start_cmd.run(), "Failed class cmd"
        time.sleep(TEST_SLEEP)
        # Stop routine
        args = parse_cmdline(cls.description, ['stop', '-j', cls.add_cmd.job.id])
        cmd = OrthrusStop(args, cls.config, True)
        assert cmd.run(), "Failed class cmd"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.orthrusdirname)