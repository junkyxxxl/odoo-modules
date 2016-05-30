Name:       openerp
Version:    8.0
%define     oeversion 8.0
Release:    %{?BUILD_NUMBER}%{?dist}

License:    AGPLv3 and GPLv3 and BSD and LGPLv2+
Group:      System Environment/Daemons
Summary:    Business Applications Server
URL:        http://www.openerp.com
Source0:    src.tar.gz
Source1:    openerp-server.conf
Source3:    openerp-gen-cert
Source4:    odoo.service
Source5:    odoo-update.service

Requires:   wkhtmltox
Requires:   libpng12
Requires:   babel
Requires:   ntp
Requires:   tmpwatch
Requires:   libjpeg-devel
Requires:   libxml2-python
Requires:   libxml2-devel
Requires:   graphviz
Requires:   libxslt-python
Requires:   libxslt-devel
Requires:   python-yaml
Requires:   python
Requires:   python-devel
Requires:   ghostscript
#Requires:   pydot
#Requires:   pywebdav
Requires:   python-babel
Requires:   python-dateutil
Requires:   python-feedparser
Requires:   python-imaging
Requires:   python-ldap
Requires:   python-lxml
Requires:   python-mako
Requires:   python-openid
Requires:   python-pip >= 1.5.6-5
Requires:   python-psycopg2
Requires:   python-reportlab
Requires:   python-simplejson
#Requires:   python-vatnumber
Requires:   python-vobject
Requires:   python-werkzeug
#Requires:   python-ZSI
#Requires:   python-xlwt
Requires:   python-pillow
#Requires:   python-pillow-devel
#Requires:   python-qrcode
Requires:   pytz
#Requires:   PyXML
Requires:   PyYAML
#Requires:   pyPdf
#Requires:   mx
Requires:   python-matplotlib
Requires:   python-psutil
Requires:   python-docutils
Requires:   python-jinja2
Requires:   python-mock
Requires:   python-unittest2
Requires:   byacc
Requires:   poppler-utils
Requires:   postgresql-python
Requires:   postgresql-devel
Requires:   python-decorator
#Requires:   python-gevent
Requires:   libevent-devel
Requires:   python-ordereddict
#Requires:   python-gdata
Requires:   pyserial
#Requires:   pyusb
#Requires:   python-unidecode
#Requires:   python-GeoIP
Requires:   GeoIP
Requires:   GeoIP-devel
#Requires:   htmlparser
Requires:   python-markupsafe
Requires:   python-requests
Requires:   pyOpenSSL
Requires:   pyparsing
Requires:   MySQL-python
Requires:   python-passlib

Requires:   python-lesscpy
Requires:   nodejs-clean-css
Requires:   nodejs-less

Requires(post):  chkconfig
Requires(post):  gcc
Requires(preun): chkconfig
Requires(preun): initscripts

#BuildRequires:  pydot
BuildRequires:  python
BuildRequires:  python-devel
BuildRequires:  python-babel
BuildRequires:  python-setuptools
BuildRequires:  python2-devel

#Conflicts: python-gdata
Conflicts: python-gevent

# Prevent brp-java-repack-jars from being run.
%define __jar_repack %{nil} 

%description
OpenERP is a complete ERP and CRM. The main features are accounting (analytic
and financial), stock management, sales and purchases management, tasks
automation, marketing campaigns, help desk, POS, etc. Technical features include
a distributed server, flexible workflows, an object database, a dynamic GUI,
customizable reports, and XML-RPC interfaces.

%prep
%setup -q -n src/odoo-8.0

# Empty file and of no use.
rm addons/base_report_designer/openerp_sxw2rml/office.dtd

# Prebuilt binaries, bundled libs and foreign packaging
rm -rf win32 debian setup.nsi
rm -rf bin/pychart

# Client-side plugin, until we can build it under Fedora.
rm -rf addons/outlook/plugin/

mv addons/* openerp/addons/


pip install pydot
#pip install pydot --upgrade

%build
NO_INSTALL_REQS=1 python ./setup.py --quiet build

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_sysconfdir}

#Install Openerp
python ./setup.py --quiet install --root=%{buildroot} --record=INSTALLED_FILES
sed -i "s|%{buildroot}||" %{buildroot}/usr/bin/openerp-server
#rm -r  %{buildroot}%{python_sitelib}/openerp
#mkdir %{buildroot}%{python_sitelib}/usr/openerp

#install -m 644 -D install/openerp-server.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/openerp-server

install -m 755 openerp-gevent %{buildroot}/usr/bin/openerp-gevent

install -d %{buildroot}%{_sysconfdir}/openerp/start.d
install -d %{buildroot}%{_sysconfdir}/openerp/stop.d

install -m 644 openerp/import_xml.rng %{buildroot}%{python_sitelib}/openerp

install -d %{buildroot}%{_libexecdir}/%{name}

install -d %{buildroot}%{python_sitelib}/openerp/addons/base/security
install -m 644 openerp/addons/base/security/* \
    %{buildroot}%{python_sitelib}/openerp/addons/base/security

install -d %{buildroot}/%{_datadir}/openerp/pixmaps

install -d %{buildroot}%{_localstatedir}/spool/openerp
install -d %{buildroot}%{_localstatedir}/run/openerp

install -d %{buildroot}/var/log/openerp

# Install the init scripts and conf
install -m 644 -D %SOURCE1 %{buildroot}%{_sysconfdir}/openerp/openerp-server.conf
install -m 700 -D %SOURCE4 %{buildroot}/lib/systemd/system/odoo.service
install -m 700 -D %SOURCE5 %{buildroot}/lib/systemd/system/odoo-update.service

%pre
getent group openerp >/dev/null || groupadd -r openerp
getent passwd openerp >/dev/null || \
    useradd -r -g openerp -d /home/openerp -s /sbin/nologin \
    -c "OpenERP Server" openerp
#usermod -d /home/openerp openerp >/dev/null 2>&1 || :

%post
pip install gdata --upgrade
pip install psycogreen --upgrade
pip install argparse --upgrade
pip install gevent-psycopg2 --upgrade
#pip install PIL --upgrade
#pip install pillow --upgrade
pip install gevent --upgrade
pip install phonenumbers --upgrade
pip install py-asterisk --upgrade
pip install pydot --upgrade
pip install xlwt --upgrade
pip install egenix-mx-base --upgrade
pip install pyusb --upgrade
pip install ZSI --upgrade
pip install PyWebDAV --upgrade
pip install vatnumber --upgrade
pip install unidecode --upgrade
pip install htmlparser --upgrade
pip install qrcode --upgrade
pip install pyPdf --upgrade
pip install http://download.gna.org/pychart/PyChart-1.39.tar.gz
pip install codicefiscale --upgrade
pip install pyxb --upgrade
pip install unicodecsv --upgrade
pip install pysftp --upgrade

/usr/bin/yes | pip uninstall PyXML

if [ ! -d /usr/lib/python2.7/site-packages/addons ];
then
    mkdir /usr/lib/python2.7/site-packages/addons/
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl stop odoo >/dev/null 2>&1

fi

%postun
if [ "$1" -ge "1" ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl restart odoo >/dev/null 2>&1
fi

%files
#%doc LICENSE README
/usr/bin/*
%config(noreplace) /lib/systemd/system/odoo.service
%config(noreplace) /lib/systemd/system/odoo-update.service
#%{_mandir}/man1/*
#%{_mandir}/man5/*
%{_datadir}/openerp
%{python_sitelib}/openerp
%{python_sitelib}/openerp-%{oeversion}*-py%{python_version}.egg-info
%attr(0755,openerp,openerp) %{_localstatedir}/run/openerp
%attr(0755,root,openerp) %dir %{_sysconfdir}/openerp
%attr(0755,openerp,openerp) %dir /var/log/openerp
%dir %{_sysconfdir}/openerp/start.d/
%dir %{_sysconfdir}/openerp/stop.d/
%attr(0660,root,openerp) %config(noreplace) %{_sysconfdir}/openerp/openerp-server.conf
#%config(noreplace) %{_sysconfdir}/logrotate.d/openerp-server
%{_datadir}/openerp/pixmaps/

%changelog

* Tue Jan 07 2014 Andrea Stirpe <a.stirpe@isa.it> 8.0-1
  - First RPM package for Openerp 8.0.
