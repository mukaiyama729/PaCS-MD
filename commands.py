
gmxcommand="gmx_mpi "
mpicommand="mpirun -np "

def gmxcmd(use_emp: bool=True):
    return "gmx_mpi " if use_emp==True else "mpirun -np 1 gmx_mpi "

def gmxcmd2(process: int):
    # "mpirun -np 'process' gmx_mpi "
    return "mpirun -np {} gmx_mpi ".format(process)

def gmxcmd2lastloop(runmodelastloop):
	tmpstr = mpicommand + str(runmodelastloop)+" gmx_mpi "
	return tmpstr
