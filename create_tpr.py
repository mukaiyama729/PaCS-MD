import os, logging
from commands import gmxcmd, gmxcmd2, mpicommand, gmxcommand
logger = logging.getLogger('pacs_md')

class CreateTprFile:

    def __init__(self, dir, initial_files, top_dir):
        self.top_dir = top_dir
        self.dir = os.path.join(dir, '')
        self.initial_files = initial_files

    def create_tpr_file(self, ranked_com_dist, n ,m):
        self.arrange_needed_files_for_DPaCS(ranked_com_dist, n, m)

        logger.info(f'{n}th {m}: creating tpr file to {self.dir}')
        os.system(
            gmxcmd()+"grompp -f "+ self.dir + self.initial_files['md'] +
            " -c " + self.dir + self.initial_files['input'] +
            " -p " + self.dir + self.initial_files['topol'] +
            " -n " + self.dir + self.initial_files['index'] +
            " -o " + self.dir + "topol.tpr" +
            " -r " + self.dir + self.initial_files['input'] +
            " -maxwarn 10"
        )
        logger.info(f'{n}th {m}: end creating tpr file')

    def arrange_needed_files_for_DPaCS(self, ranked_com_dist, n, m):
        logger.info('%sth %s: arrange needed files', n, m)
        os.system(
            "echo 'System' | " + gmxcmd() + "trjconv" +
            " -f " + os.path.join(self.top_dir, self.pick_out_dir(ranked_com_dist, n-1, m)) + 'traj_comp.xtc' +
            " -s " + os.path.join(self.top_dir, self.pick_out_dir(ranked_com_dist, n-1, m)) + 'topol.tpr' +
            " -o " + os.path.join(self.dir, self.initial_files['input']) +
            " -dump " + str(float(ranked_com_dist[-1 * m,0]))
        )

        logger.info('%sth %s: finished arranging', n, m)

        logger.info(f'{n}th {m}: copy {self.top_dir}/md.mdp to {self.dir}')
        os.system("cp -r " + os.path.join(self.top_dir, self.initial_files['md']) + ' ' + self.dir)

        logger.info(f'{n}th {m}: copy {self.top_dir}/topol.top to {self.dir}')
        os.system("cp -r " + os.path.join(self.top_dir, self.initial_files['topol']) + ' ' + self.dir)
        if any(self.initial_files['posres']):
            logger.info(f'{n}th {m}: copy {self.top_dir}/*.itp to {self.dir}')
            os.system("cp -r " + os.path.join(self.top_dir, '*.itp') + ' ' + self.dir)

        logger.info(f'{n}th {m}: copy {self.top_dir}/index.ndx to {self.dir}')
        os.system("cp -r " + os.path.join(self.top_dir, self.initial_files['index']) + ' ' + self.dir)

    def specify_dir(self, n, m):
        return 'pacs-{}-{}/'.format(n, m)

    def pick_out_dir(self, ranked_com_dist, n, m):
        logger.info('%sth %s: selected is {}'.format(ranked_com_dist[-1 * m, 0:3]), n, m)
        return self.specify_dir(n, int(ranked_com_dist[-1 * m, 2]))

    def exec_md(self, ntomp, gpuid):
        self.create_tpr_file()
        os.system(
            gmxcmd2(30) + "mdrun -s " + self.dir + "topol.tpr" +
            " -o " + self.dir + "traj.trr" +
            " -x " + self.dir + "traj_comp.xtc" +
            " -e " + self.dir + "ener.edr" +
            " -g " + self.dir + "md.log" +
            " -c " + self.dir + "confout.gro" +
            " -cpo " + self.dir + "state.cpt" +
            " -pme gpu" +
            " -npme 1" +
            " -v -ntomp " + str(ntomp) +
            " -gpu_id " + str(gpuid)
        )

