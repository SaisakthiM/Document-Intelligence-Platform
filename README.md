mariadb -u root -p                  ─╯
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 3
Server version: 11.8.6-MariaDB Arch Linux

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> show databases
    -> ;
+--------------------+
| Database           |
+--------------------+
| cinema             |
| employees          |
| information_schema |
| inventory_db       |
| main_data          |
| mysql              |
| performance_schema |
| sai                |
| sys                |
+--------------------+
9 rows in set (0.011 sec)

MariaDB [(none)]> create database book_db;
Query OK, 1 row affected (0.001 sec)

MariaDB [(none)]> exit
Bye
