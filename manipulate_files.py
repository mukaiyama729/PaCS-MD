import os, sys, glob, logging, shutil
import datetime


logger = logging.getLogger('pacs_md')

class FileManipulator:

    def __init__(self, top_dir):
        logger.debug(top_dir)
        self.top_dir = top_dir
        self.current_dir = os.getcwd()
        self.log_file_name = None

    def make_dir(self, dir, exist=True):
        logger.info(f'creating {dir}')
        os.makedirs(dir, exist_ok=exist)

    def change_dir(self, to_dir):
        os.chdir(to_dir)
        self.current_dir = os.getcwd()

    def create_file(self, name):
        logger.info(f'create {name} file')
        try:
            with open(name, "x") as f:
                f.write("")
            self.log_file_name = name
        except FileExistsError:
            logger.warning('Same file exists.')
            today = datetime.date.today()
            today = str(today).replace('-','')
            file_name = today + 'pacs.log'
            self.file_name = file_name
            file1 = open(file_name, 'w')
            file1.write(today)
            file1.close()
        finally:
            f.close()

    def create_log_file(self, name='pacs.log'):
        logger.info(f'create log file {name}')
        self.create_file(os.path.join(self.top_dir, name))

    def copy_file(self, file, dir1, dir2):
        logger.info(f'copy file {file} from {dir1} to {dir2}')
        shutil.copyfile(os.path.join(dir1, file), dir2)

    def copy_files(self, pattern, dir1, dir2):
        logger.info(f'copy file having {pattern} pattern from {dir1} to {dir2}')
        for file_path in glob.glob(os.path.join(dir1, pattern)):
            shutil.copyfile(file_path, os.path.join(dir2, os.path.basename(file_path)))

    def copy_all_files(self, from_dir, to_dir):
        logger.info(f'copy all files from {from_dir} to {to_dir}')
        shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)

    def copy_intial_files(self, initial_file_paths, to_dir):
        logger.info(f'copy initial files to {to_dir}')
        shutil.copy(initial_file_paths['topol'], os.path.join(to_dir, os.path.basename(initial_file_paths['topol'])))
        shutil.copy(initial_file_paths['index'], os.path.join(to_dir, os.path.basename(initial_file_paths['index'])))
        shutil.copy(initial_file_paths['input'], os.path.join(to_dir, os.path.basename(initial_file_paths['input'])))
        shutil.copy(initial_file_paths['md'], os.path.join(to_dir, os.path.basename(initial_file_paths['md'])))
        posres = initial_file_paths['posres']
        if len(posres) > 0:
            for itp_file_path in initial_file_paths['posres']:
                shutil.copy(itp_file_path, os.path.join(to_dir, os.path.basename(itp_file_path)))
        logger.info(f'finished copy initila files')

    def write_file(self, file_path, txt):
        logger.info(f'write {txt} to {file_path}')
        with open(file_path, 'w') as f:
            f.write(txt)
            f.close()
        logger.info('finished writing')


