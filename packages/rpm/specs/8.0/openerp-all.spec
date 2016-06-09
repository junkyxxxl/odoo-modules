%define     version 8.0

Name:       odoo-all
Version:    %{version}
Release:    %{?BUILD_NUMBER}%{?dist}

License:    AGPLv3 and GPLv3 and BSD and LGPLv2+
Group:      System Environment/Daemons
Summary:    Business Applications
URL:        http://www.isa.it
Source0:    src.tar.gz
Source1:    openerp-server.conf
Source5:    odoo-update.service

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
Requires:   libffi-devel
Requires:   openssl-devel
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

Summary: Modules for Odoo for All Customers.
Group: System Environment/Daemons
%description
Modules for Odoo for All Customers.

%package custom-all
Summary: Modules for Odoo for customer All Customers.
%description custom-all
Modules for Odoo for customer All Customers.

%prep
%setup -q -n odoo-modules

%install

install -d %{buildroot}/var/log/odoo

# Install the init scripts and conf
install -m 644 -D %SOURCE1 %{buildroot}%{_sysconfdir}/odoo/openerp-server.conf
install -m 700 -D %SOURCE5 %{buildroot}/lib/systemd/system/odoo-update.service

install -d %{buildroot}%{python_sitelib}/openerp/addons/
install -d %{buildroot}%{python_sitelib}/openerp/addons/isa

#Isa srl
find isa-srl -maxdepth 2 -mindepth 2 -type d -exec cp -R --backup=numbered -t %{buildroot}%{python_sitelib}/openerp/addons/isa {} +

# All Customer
find customers -maxdepth 2 -mindepth 2 -type d -exec cp -R --backup=numbered -t %{buildroot}%{python_sitelib}/openerp/addons/isa {} +

# Oca
find oca -maxdepth 2 -mindepth 2 -type d -exec cp -R --backup=numbered -t %{buildroot}%{python_sitelib}/openerp/addons/isa {} +

#Third part
find third-party -maxdepth 1 -mindepth 1 -type d -exec cp -R --backup=numbered -t %{buildroot}%{python_sitelib}/openerp/addons/isa {} +

#Aeroo report
cp -r aeroo/* %{buildroot}%{python_sitelib}/openerp/addons/isa


%files
%config(noreplace) /lib/systemd/system/odoo-update.service
%attr(0660,root,odoo) %config(noreplace) %{_sysconfdir}/odoo/openerp-server.conf
%attr(0755,odoo,odoo) %dir /var/log/odoo

%{python_sitelib}/openerp/addons/*

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
pip install http://download.gna.org/pychart/PyChart-1.39.tar.gz --upgrade
pip install codicefiscale --upgrade
pip install pyxb --upgrade
pip install unicodecsv --upgrade
pip install pysftp --upgrade
pip install http://launchpad.net/aeroolib/trunk/rc2/+download/aeroolib.tar.gz --upgrade

%changelog