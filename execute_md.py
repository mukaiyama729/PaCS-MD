import os, glob, re, pathlib, shutil
from pacs_MD import PaCSMD
from manipulate_files import FileManipulator


class PaCSExecuter(FileManipulator):

    def __init__(self, base_dir):
        self.base_dir = base_dir
        super().__init__(base_dir)

    def multi_pacs_md(self, how_many, method, node, ngpus_per_node=1, runmode=4, restart: int=0, nbins=30, ntomp=1, groups=(), parallel=4, **kwargs):
        if method == 'dist':
            for i in range(1, how_many+1, 1):
                dir_path = os.path.join(self.base_dir, 'trial{}'.format(i))
                self.copy_all_files(self.base_dir, dir_path)
                PaCSMD(
                    dir_path,
                    node,
                    ngpus_per_node,
                    runmode,
                    restart,
                    nbins,
                    ntomp,
                    parallel
                ).exe_pacs_md('dist', groups, **kwargs)

    def single_pacs_md(self, method, node, ngpus_per_node=1, runmode=4, restart: int=0, nbins=30, ntomp=1, groups=(), **kwargs):
        if method == 'dist':
            PaCSMD(
                self.base_dir,
                node,
                ngpus_per_node,
                runmode,
                restart,
                nbins,
                ntomp
            ).exe_pacs_md('dist', groups, **kwargs)
