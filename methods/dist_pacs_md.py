import os, sys, glob, shutil, logging
from manipulate_files import FileManipulator
from multiprocessing import Pool
from commands import gmxcmd, gmxcmd2, mpicommand, gmxcommand, gmxcmd2lastloop
from create_tpr import CreateTprFile
import numpy as np

logger = logging.getLogger('pacs_md')
outfn = 'pacs'

class DistPaCSMD(FileManipulator):

    def __init__(self, top_dir, initial_file_paths:dict, initial_files:dict, groups, method:str='dist', com_max_dist:float=7.0, nbins=30, nround=100, ntomp=0, gpuid='0011', runmode=30, gpu=1) -> None:
        logger.info('creating DistPaCSMD object')
        self.top_dir = top_dir
        logger.info('working dir is ' + self.top_dir)
        super().__init__(top_dir)
        self.initial_file_paths = initial_file_paths
        self.initial_files = initial_files
        self.method = method
        self.max_dist = com_max_dist
        self.nbins = nbins
        self.nround = nround
        self.ntomp = ntomp
        self.gpuid = gpuid
        self.runmode = runmode
        self.gpu = gpu
        self.groups = groups

    def inital_md(self) -> bool:
        self.write_log_file('PaCS MD is going to run ')
        self.write_log_file('Number of bins is {}'.format(str(self.nbins)))
        self.write_log_file("Number of ROUND is {}".format(str(self.nround)))
        self.write_log_file("Simulation is running from the beginning. ")
        #call gromacs to run for the first cycle
        self.write_log_file('++++++++++++++++')
        self.write_log_file('ROUND 0. ')
        self.write_log_file('1111 Max to Min Ranking 1111')
        self.write_log_file('+ Bin +++ Step +')

        logger.info('copy intial files')
        self.copy_intial_files(self.initial_file_paths, os.path.join(self.top_dir, 'pacs-0-0'))

        self.top_dir_path = os.path.join(self.top_dir, '')
        first_file_path = os.path.join(self.top_dir, 'pacs-0-0/')
        logger.info('making tprfiles for first md')
        os.system(
            gmxcmd() + "grompp" +
            " -f " + first_file_path + self.initial_files['md'] +
            " -c " + first_file_path + self.initial_files['input'] +
            " -p " + first_file_path + self.initial_files['topol'] +
            " -n " + first_file_path + self.initial_files['index'] +
            " -o " + first_file_path + "topol.tpr" +
            " -r " + first_file_path + self.initial_files['input'] +
            " -maxwarn 10"
        )
        logger.debug(
            gmxcmd() + "grompp" +
            " -f " + first_file_path + self.initial_files['md'] +
            " -c " + first_file_path + self.initial_files['input'] +
            " -p " + first_file_path + self.initial_files['topol'] +
            " -n " + first_file_path + self.initial_files['index'] +
            " -o " + first_file_path + "topol.tpr" +
            " -r " + first_file_path + self.initial_files['input'] +
            " -maxwarn 10"
        )
        logger.debug(self.initial_files)

        logger.info('execute initial mdrun')
        logger.debug(
            gmxcmd2(2) + "mdrun" +
            " -s " + first_file_path + "topol.tpr" +
            " -o " + first_file_path + "traj.trr" +
            " -x " + first_file_path + "traj_comp.xtc" +
            " -e " + first_file_path + "ener.edr" +
            " -g " + first_file_path + "md.log" +
            " -c " + first_file_path + "confout.gro" +
            " -cpo " + first_file_path + "state.cpt" +
            " -pme " + "gpu" +
            " -npme " + "1" +
            " -v -ntomp " + str(self.ntomp)
        )
        if self.gpu:
            commnd = (
                gmxcmd2(2) + "mdrun" +
                " -s " + first_file_path + "topol.tpr" +
                " -o " + first_file_path + "traj.trr" +
                " -x " + first_file_path + "traj_comp.xtc" +
                " -e " + first_file_path + "ener.edr" +
                " -g " + first_file_path + "md.log" +
                " -c " + first_file_path + "confout.gro" +
                " -cpo " + first_file_path + "state.cpt" +
                " -pme " + "gpu" +
                " -npme " + "1" +
                " -v -ntomp " + str(self.ntomp)
            )
        else:
            commnd = (
                gmxcmd2(self.runmode) + "mdrun" +
                " -s " + first_file_path + "topol.tpr" +
                " -o " + first_file_path + "traj.trr" +
                " -x " + first_file_path + "traj_comp.xtc" +
                " -e " + first_file_path + "ener.edr" +
                " -g " + first_file_path + "md.log" +
                " -c " + first_file_path + "confout.gro" +
                " -cpo " + first_file_path + "state.cpt" +
                " -npme " + "1" +
                " -v -ntomp " + str(self.ntomp)
            )
        os.system(commnd)

        logger.info('comvert trajctory of initial md')
        os.system(
            "echo 'System' | " + gmxcmd() + "trjconv" +
            " -s " + first_file_path  + "topol.tpr" +
            " -f " + first_file_path + "traj_comp.xtc" +
            " -o " + first_file_path + "traj_comp-noPBC.xtc" +
            " -pbc mol" +
            " -ur compact"
        )

        logger.info('calculate distance of initial md')
        os.system(
            gmxcmd() + "distance" +
            " -f " + first_file_path + "traj_comp-noPBC.xtc" +
            " -s " + first_file_path + "topol.tpr" +
            " -n " + first_file_path + self.initial_files['index'] +
            " -oall " + first_file_path + "pacs-0-0.xvg" +
            " -xvg " + "none" +
            " -tu " + "ps" +
            " -sf " + os.path.join(self.top_dir, "sel.dat")
        )

        logger.info('rank com dist of initial md')
        self.com_dist = np.loadtxt(self.top_dir_path + 'pacs-0-0/pacs-0-0.xvg')
        logger.debug(self.com_dist)
        self.com_dist_for_one_round = np.concatenate(
            (
                self.com_dist,
                np.zeros((len(self.com_dist[:,1]), 1))
            ), 1
        )
        self.ranked_com_dist = self.com_dist_for_one_round[np.lexsort((self.com_dist_for_one_round[:,0], self.com_dist_for_one_round[:,1]))]
        logger.info(self.ranked_com_dist[-1:-31:-1, :])
        #logfileに上位３０を書き込む

    def write_log_file(self, massage):
        os.system("echo {} >> {}".format(massage, os.path.join(self.top_dir, self.log_file_name)))

    def parallel_md(self, n):
        if self.runmode == 1:
            for m in range(1, self.nbins + 1):
                if self.gpu >= 0 and self.ntomp >= 0:
                    os.system(
                        gmxcmd2(self.runmode) + " mdrun -deffnm " + "pacs-{}-{}".format(n, m) + "/topol" +
                        " -v" +
                        " -ntomp " + str(self.ntomp) +
                        " -gpu_id " + str(self.gpuid)
                    )
                else:
                    os.system(
                        gmxcmd2(self.runmode) + " mdrun -deffnm " + "pacs-{}-{}".format(n, m) + "/topol" + " -v" +
                        " -ntomp " + str(self.ntomp)
                    )
        else:
            mdloop = self.nbins // self.runmode
            logger.info(f'{n}th: mdloop is {mdloop}')
            if mdloop * self.runmode < self.nbins:
                lastloop = self.nbins % self.runmode
                logger.info(f'{n}th: lastloop is {lastloop}')
            else:
                lastloop = 0
                logger.info(f'{n}th: lastloop is {lastloop}')
            for x in range(mdloop):
                multidir = ""
                for m in range(x * self.runmode + 1, (x + 1) * self.runmode + 1):
                    multidir += self.top_dir_path + 'pacs-{}-{} '.format(n, m)
                logger.info(f'{n}th: run parallel md for {multidir}')
                #gpu使うか使わないか
                if self.gpu:
                    command = (
                        gmxcmd2(self.runmode) + "mdrun" +
                        " -multidir " + multidir.rstrip() +
                        ' -s ' + 'topol' +
                        ' -v' +
                        ' -ntomp ' + str(self.ntomp) +
                        ' -gpu_id ' + str(self.gpuid)
                    )
                else:
                    command = (
                        gmxcmd2(self.runmode) + "mdrun" +
                        " -multdir " + multidir.rstrip() +
                        " s " + "topol" +
                        " -v" +
                        " -ntomp " + str(self.ntomp)
                    )
                logger.info(f'{n}th: mdrun command is \n {command}')
                os.system(command)
                logger.info(f'{n}th: finished parallel md for {multidir}')

            if lastloop > 0:
                multidir = ""
                for m in range(mdloop * self.runmode + 1, self.nbins + 1):
                    multidir += self.top_dir_path + 'pacs-{}-{} '.format(n, m)
                logger.info(f'{n}th: run parallel md for {multidir}')
                if self.gpu:
                    command = (
                        gmxcmd2lastloop(lastloop) + "mdrun" +
                        ' -multidir ' + multidir.rstrip() +
                        ' -s ' + 'topol' +
                        ' v' +
                        ' -ntomp ' + str(self.ntomp) +
                        ' -gpu_id ' + str(self.gpuid[0:lastloop*2-1])
                    )
                else:
                    command = (
                        gmxcmd2lastloop(lastloop) + "mdrun" +
                        ' -multidir ' + multidir.rstrip() +
                        ' -s ' + 'topol' +
                        ' v' +
                        ' -ntomp ' + str(self.ntomp)
                    )
                logger.info(f'{n}th: lastloop mdrun command is \n {command}')
                os.system(command)
                logger.info(f'{n}th: finished parallel md for {multidir}')

    def calc_distance(self, n):
        for m in range(1, self.nbins + 1, 1):
            logger.info(f'{n}th {m}: start creating xvg file')
            self.create_xvg_file(n, m)
            logger.info(f'{n}th {m}: loading pacs.xvg file')
            com_dist = np.loadtxt(self.top_dir_path + 'pacs-{}-{}/'.format(n, m) + 'pacs-{}-{}.xvg'.format(n, m))
            logger.info(f'{n}th {m}: label to distance')
            labeled_com_dist = np.concatenate(
                (
                    com_dist,
                    np.ones((com_dist.shape[0], 1)) * m
                ), 1
            )
            if m > 1:
                self.com_dist_for_one_round = np.concatenate(
                    (self.com_dist_for_one_round, labeled_com_dist), 0
                )
            else:
                self.com_dist_for_one_round = labeled_com_dist

    def create_xvg_file(self, n, m):
        logger.info(f'{n}th {m}: create traj_comp-noPBC.xtc at {self.top_dir_path}pacs{n}-{m} dir')
        os.system(
            "echo System | " +
            gmxcmd() + 'trjconv' +
            ' -s ' + self.top_dir_path + 'pacs-{}-{}/'.format(n, m) + 'topol.tpr'
            ' -f ' + self.top_dir_path + 'pacs-{}-{}/'.format(n, m) + 'traj_comp.xtc' +
            ' -o ' + self.top_dir_path + 'pacs-{}-{}/'.format(n, m) + 'traj_comp-noPBC.xtc' +
            ' -pbc ' + 'mol' +
            ' -ur ' + 'compact'
        )
        logger.info(f'{n}th {m}: finished creating traj_comp-noPBC.xtc')

        logger.info(f'{n}th {m}: calculating distance at {self.top_dir}pacs{n}-{m} dir')
        os.system(
            gmxcmd() + 'distance' +
            ' -f ' + self.top_dir_path + 'pacs-{}-{}/'.format(n, m) + 'traj_comp-noPBC.xtc' +
            ' -s ' + self.top_dir_path + 'pacs-{}-{}/'.format(n, m) + 'topol.tpr' +
            ' -n ' + self.top_dir_path + 'pacs-{}-{}/'.format(n, m) + self.initial_files['index'] +
            ' -oall ' + self.top_dir_path + 'pacs-{}-{}/'.format(n, m) + 'pacs-{}-{}.xvg'.format(n, m) +
            ' -xvg ' + 'none' +
            ' -tu ' + 'ps' +
            ' -sf ' + self.top_dir_path + 'sel.dat'
        )
        logger.info(f'{n}th {m}: finished calculating distance')

    def execute_md(self):
        self.write_file(
            self.initial_file_paths['sel'],
            f'com of group "{self.groups[0]}" plus com of group "{self.groups[1]}"'
        )
        self.working_dir = os.path.join(self.top_dir, 'pacs-0-0')
        logger.info('working dir is ' + self.working_dir)
        self.make_dir(self.working_dir)
        self.create_log_file('pacs.log')
        logger.info('start initial md')
        self.inital_md()
        logger.info('first md is finished')
        n = 1
        while n < self.nround:
            self.write_log_file('++++++++++++++++')
            self.write_log_file(f'ROUND "{n}". ')
            self.write_log_file('1111 Max to Min Ranking 1111')
            self.write_log_file('+ Bin +++ Step +')
            logger.info('{}th: start parallel md for {}th'.format(n, n))
            logger.info('{}th: preparing files and dirs for parallel md'.format(n))
            self.prepare_for_md(n)
            self.parallel_md(n)
            self.calc_distance(n)
            if self.is_finish(n):
                break
            logger.info(f'{n}th: go to next step {n+1}')
            n += 1

    def restart_md(self, from_n):

        while from_n < self.nround:
            self.write_log_file('++++++++++++++++')
            self.write_log_file(f'ROUND "{from_n}". ')
            self.write_log_file('1111 Max to Min Ranking 1111')
            self.write_log_file('+ Bin +++ Step +')
            self.prepare_for_md(from_n)
            self.parallel_md(from_n)
            self.calc_distance(from_n)
            if self.is_finish(from_n):
                break
            from_n += 1


    def is_finish(self, n):
        self.ranked_com_dist = self.com_dist_for_one_round[np.lexsort((self.com_dist_for_one_round[:,0], self.com_dist_for_one_round[:,1]))]
        if (self.max_dist > 0.0) and (self.ranked_com_dist[-1, 1] < self.max_dist) and (n == (self.nround - 1)):
            self.nround += 1
            logger.info(f'distance does not exceed max_dist but n is equal to {self.nround - 1}')
            return False
        elif (self.max_dist > 0.0) and (self.ranked_com_dist[-1, 1] > self.max_dist) and (n < (self.nround - 1)):
            logger.info('distance exceeded so end parallel md')
            return True
        else:
            logger.info('distance does not exceed max_dist')
            return False

    def prepare_for_md(self, n, process=30):
        self.create_dirs(n)
        self.create_tpr_files(n, process)

    def create_tpr_files(self, n, process):
        logger.info('%sth: create tpr files', n)
        p = Pool(process)
        for m in range(1, self.nbins + 1, 1):
            logger.info('%sth %s: creating tpr file', n, m)
            p.apply_async(
                CreateTprFile(
                    self.top_dir_path + 'pacs-{}-{}'.format(n, m),
                    self.initial_files,
                    self.top_dir
                ).create_tpr_file(self.ranked_com_dist, n, m)
            )
        p.close()
        p.join()

    def create_dirs(self, n):
        logger.info('{}th: creating dirs'.format(n))
        for m in range(1, self.nbins + 1, 1):
            logger.info('creating %s dir', 'pacs-{}-{}'.format(n, m))
            os.makedirs(os.path.join(self.top_dir, 'pacs-{}-{}/'.format(n, m)))






