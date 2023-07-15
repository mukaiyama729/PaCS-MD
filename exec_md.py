from pacs_MD import PaCSMD
import sys
import argparse
sys.path.append('./')
import logging

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # コマンドライン引数を定義
    parser.add_argument('--work_dir', type=str, help='ワーキングディレクトリ')
    parser.add_argument('--node', type=int, help='nodeの数')
    parser.add_argument('--ngpus', type=int, help='gpuの数')
    parser.add_argument('--runmode', type=int, help='総プロセス数')
    parser.add_argument('--restart', type=int, help='リスタートするかどうか1 or 0')
    parser.add_argument('--method', type=str, help='pacsmdの手法')
    parser.add_argument('--ntomp', type=int, help='スレッド数')
    parser.add_argument('--group1', type=str, help='distPaCSMDなら指定')
    parser.add_argument('--group2', type=str, help='distPaCSMDなら指定')

    arg = parser.parse_args()
    arranged_args = { k: v for k, v in vars(arg).items() if v is not None }
    print(arranged_args)
    pacs_md_vars = ['work_dir', 'node', 'ngpus', 'runmode', 'restart']
    vars_for_exec = ['method', 'ntomp', 'group1', 'group2']
    pacs_md_dict = { key: arranged_args[key] for key in pacs_md_vars }
    pacs_md_dict['ngpus_per_node'] = pacs_md_dict.pop('ngpus')
    vars_md_dict = { key: arranged_args[key] for key in vars_for_exec }
    try:
        vars_md_dict['groups'] = (vars_md_dict.pop('group1'), vars_md_dict.pop('group2'))
    except KeyError:
        remain = set(['group1', 'group2']) - set(vars_md_dict.keys())
        if len(remain) == 2:
            pass
        else:
            print('groupが一つだけです。')
            raise Exception

    pacs = PaCSMD(**pacs_md_dict)
    logger = logging.getLogger('pacs_md')
    logger.debug(pacs_md_dict)
    logger.debug(vars_md_dict)
    pacs.exe_pacs_md(**vars_md_dict)
