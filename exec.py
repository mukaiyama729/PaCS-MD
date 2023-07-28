from execute_md import PaCSExecuter
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
    parser.add_argument('--how_many', type=int, help='何回pacsmdを繰り返すか')

    arg = parser.parse_args()
    arranged_args = { k: v for k, v in vars(arg).items() if v is not None }
    if arranged_args['ngpus']:
        arranged_args['ngpus_per_node'] = arranged_args.pop('ngpus')
    else:
        arranged_args.pop('ngpus')
    try:
        arranged_args['groups'] = (arranged_args.pop('group1'), arranged_args.pop('group2'))
    except KeyError:
        remain = set(['group1', 'group2']) - set(arranged_args.keys())
        if len(remain) == 2:
            pass
        else:
            print('groupが一つだけです。')
            raise Exception
    logger = logging.getLogger('pacs_md')
    logger.debug(arranged_args)
    work_dir = arranged_args.pop('work_dir')
    PaCSExecuter(work_dir).multi_pacs_md(**arranged_args)



