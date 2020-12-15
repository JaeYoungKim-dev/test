%define name SS-DB-5.0.0.1
%define rel el7
%define path /opt/ssbr/3rdparty
Summary: mariadb installer
Name: %{name}
Version: rel
Release: %{rel}
License: boan
Source0: %{name}.tar.gz
BuildRoot: /var/tmp/mariadb-buildroot
%description
Install MariaDB Package.

%prep

%install
if [ -d $RPM_BUILD_ROOT ]; then rm -r $RPM_BUILD_ROOT; fi

mkdir -p $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/ssbr/3rdparty/
cp -p $RPM_SOURCE_DIR/%{name}.tar.gz $RPM_BUILD_ROOT/opt/ssbr/3rdparty/%{name}.tar.gz &&

%clean

%files
%{path}/%{name}.tar.gz

%post
mkdir -p %{path}/%{name}

tar zxf %{path}/%{name}.tar.gz -C /opt/ssbr/3rdparty/%{name}
#rm -f %{path}/%{name}.tar.gz
ln -sfn %{path}/%{name}/mariadb %{path}/mariadb

# MySQL complie 

/usr/sbin/groupadd mysql
/usr/sbin/useradd -r -g mysql mysql

cd /opt/ssbr/3rdparty/mariadb

/bin/chown -R mysql .
/bin/chgrp -R mysql .

/bin/cp ./support-files/my-large.cnf /etc/my.cnf
    
/bin/cp -p ./bin/mysqldump /usr/bin/
/bin/cp -p ./bin/mysql /usr/bin/

/bin/cp ./support-files/mysql.server /etc/init.d/mysqld

/bin/rm -rf /usr/lib64/libmysqlclient.so.*

/sbin/chkconfig --del mysqld
/sbin/chkconfig --add mysqld
/sbin/chkconfig --list | grep mysqld

/etc/init.d/mysqld start

sleep 2

# MySQL PATH Setting

/bin/cp ~/.bash_profile ~/.bash_profile_bak
sed '/PATH=/s/$/:\/opt\/ssbr\/3rdparty\/mariadb\/bin/' ~/.bash_profile_bak > ~/.bash_profile

sleep 1
source ~/.bash_profile


# input start

DBNAME_CHOICE=""
DBUSER_CHOICE=""
DBPASS_CHOICE=""

DBNAME_MSG="1. Enter the name of DB. (ex: ssbr) :"
DBUSER_MSG="2. Enter the DB user. (ex: ssbr) :"
DBPASS_MSG="3. Enter the password for the DB user. (ex: system):"

echo

echo -n "${DBNAME_MSG}"
while read line ; do
        if [ -s $line ]; then echo -n "${DBNAME_MSG}" ; continue
        else DBNAME_CHOICE=$line; break;
        fi
done < /dev/tty

echo

echo -n "${DBUSER_MSG}"
while read line ; do
        if [ -s $line ]; then echo -n "${DBUSER_MSG}" ; continue
        else DBUSER_CHOICE=$line; break;
        fi
done < /dev/tty

echo

echo -n "${DBPASS_MSG}"
while read line ; do
        if [ -s $line ]; then echo -n "${DBPASS_MSG}" ; continue
        else  DBPASS_CHOICE=$line; break;
        fi
done < /dev/tty

echo

%{path}/mariadb/bin/mysqladmin -u root -psystem create ${DBNAME_CHOICE}


# MySQL User Creat
echo "grant all privileges on *.* to '${DBUSER_CHOICE}'@'%' identified by '${DBPASS_CHOICE}';" >> default.mysql.qr
echo "grant all privileges on *.* to '${DBUSER_CHOICE}'@'localhost' identified by '${DBPASS_CHOICE}';" >> default.mysql.qr

echo "set global sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';" >> default.mysql.qr
echo "set session sql_mode='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';" >> default.mysql.qr
echo "SET GLOBAL log_bin_trust_function_creators='ON';" >> default.mysql.qr

echo "SET GLOBAL log_bin_trust_function_creators = 1;" >> default.mysql.qr
echo "ALTER DATABASE ${DBNAME_CHOICE} CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci;" >> default.mysql.qr

echo "FLUSH PRIVILEGES;" >> default.mysql.qr

mysql -u root -psystem mysql < default.mysql.qr

sleep 1
#end


%preun
if [ -d "%{path}/mariadb" ]; then
	/etc/init.d/mysqld stop
	/sbin/chkconfig --del mysqld
	/usr/sbin/userdel mysql
fi

%postun
/bin/rm -rf /usr/lib64/libmysqlclient.so.18

if [ -d "%{path}/mariadb" ]; then
	/bin/rm /etc/init.d/mysqld
	/bin/rm /etc/my.cnf
	unlink %{path}/mariadb
	rm -rf %{path}/%{name}
fi
