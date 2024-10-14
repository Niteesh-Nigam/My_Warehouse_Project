import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/nitzz/my_warehouse_project/install/warehouse_py_pkg'
