from typing import AnyStr, Any, Dict
import re, os, logging,glob
from logging import getLogger
import warnings
from enum import Enum
from methods import DistPaCSMD

logger = logging.getLogger('pacs_md')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('./pacs_log.log')
fmt = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)

class FileError(Exception):

    pass

class PaCSMD:

    file_to_pattern = { 'topol': 'topol*.top', 'index': 'index*.ndx', 'input': 'input*.gro', 'md': 'md*.mdp', 'posres': '*.itp', 'sel': 'sel.dat' }

    def __init__(self, work_dir, node, ngpus_per_node, runmode=4, restart: int=0) -> None:
        self.work_dir = work_dir
        self.log = 'pacs_md.log'
        self.restart = False if restart == 0 else True
        self.check_necessary_files()
        self.node = node
        self.ngpus_per_node = ngpus_per_node
        self.runmode = runmode

    def gpu_tasks(self):
        tasks_per_node = self.runmode // self.node
        gpu_set = tasks_per_node // self.ngpus_per_node
        remained_tasks = tasks_per_node % self.ngpus_per_node
        gpu_id_set = ','.join(map(str, [i for i in range(self.ngpus)]))
        self.gpu_tasks = ''
        while gpu_set > 0:
            self.gpu_tasks += gpu_id_set
            gpu_set -= 1

        if remained_tasks:
            for i in range(remained_tasks):
                self.gpu_tasks += ',' + str(i)
        return self.gpu_tasks

    def gpu_id(self):
        logger.debug(f'output: {self.ngpus_per_node}')
        gpu_id = ','.join(map(str, [i for i in range(self.ngpus_per_node)]))
        logger.info(f'gpu id: {gpu_id}')
        return gpu_id

    def set_group(self, groupA: str, groupB: str) -> None:
        self.groupA = groupA
        self.groupB = groupB

    def check_necessary_files(self) -> None:
        #itp files are only list object.
        self.file_paths = {}
        self.files = {}
        for file_name, pattern in PaCSMD.file_to_pattern.items():
            logger.info('checking file of {}'.format(file_name))
            self.check_file(file_name, pattern)
        logger.info('finished checking files')

    def check_file(self, file_name: str, pattern) -> None:
        files = glob.glob(os.path.join(self.work_dir, pattern))
        if file_name == 'posres':
            self.file_paths[file_name] = files
            self.files[file_name] = []
            if not(files):
                logger.info('any itp files were not found.')
            else:
                logger.info('postion restraint files were found.')
                for file_path in files:
                    self.files[file_name].append(os.path.basename(file_path))

        else:
            if any(files) and len(files) == 1:
                self.file_paths[file_name] = files[0]
                self.files[file_name] = os.path.basename(files[0])
                logger.info('{} file was found.'.format(file_name))
            elif any(files) and len(files) > 1:
                logger.warn('There are files more than one. First matched file was chosen.')
                self.file_paths = files[0]
                self.files = os.path.basename(files[0])
            else:
                logger.error(f'Any file was not found at {self.work_dir} directory. Please make {file_name} file.')
                raise FileError

    def exe_pacs_md(self, method='dist', groups=(), **kwargs):
        logger.debug(method)
        if method == 'dist':
            logger.info('starting dist pacs md')
            if not(groups):
                logger.error('groups is not specified. please write groups like (ProteinA, ProteinB) which is tuple object')
            else:
                DistPaCSMD(self.work_dir, self.file_paths, self.files, groups, method, gpuid=self.gpu_id(), runmode=self.runmode, **kwargs).execute_md()
