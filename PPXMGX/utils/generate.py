import os
import shutil


def main():
    """ 用于生成打包成exe所需的文件以及文件夹 """
    root = r"D:/PPX"
    current = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if os.path.exists(root):
        shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root, exist_ok=True)
    # 目录的移动添加
    shutil.copytree(os.path.join(current, 'PPXMGX/api'), os.path.join(root, 'api'))
    # shutil.copytree(os.path.join(current, 'gui/dist'), os.path.join(root, 'gui/dist'))
    shutil.copytree(os.path.join(current, 'Python38'), os.path.join(root, 'Python38'))
    shutil.copytree(os.path.join(current, 'PPXMGX/utils'), os.path.join(root, 'utils'))
    # 文件的移动和添加
    shutil.copy(os.path.join(current, 'PPXMGX/main.py'), os.path.join(root, 'main.py'))
    shutil.copy(os.path.join(current, 'PPXMGX/meihua.py'), os.path.join(root, 'meihua.py'))
    shutil.copy(os.path.join(current, 'PPXMGX/meihua2.py'), os.path.join(root, 'meihua2.py'))
    shutil.copy(os.path.join(current, 'PPXMGX/meihua_new.py'), os.path.join(root, 'meihua_new.py'))
    shutil.copy(os.path.join(current, 'PPXMGX/start.exe'), os.path.join(root, 'start.exe'))
    # shutil.copy(os.path.join(current, 'ConsoleApp6.dll'), os.path.join(root, 'ConsoleApp6.dll'))
    # shutil.copy(os.path.join(current, 'ConsoleApp6.runtimeconfig.json'), os.path.join(root, 'ConsoleApp6.runtimeconfig.json'))


if __name__ == "__main__":
    main()
