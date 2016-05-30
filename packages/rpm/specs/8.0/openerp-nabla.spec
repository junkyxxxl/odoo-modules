%define     version 8.0

Name:       odoo-nabla
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

Summary: Modules for Odoo for Nabla.
Group: System Environment/Daemons
%description
Modules for Odoo for Nabla.

%package custom-nabla
Summary: Modules for Odoo for customer Nabla Srl.
%description custom-nabla
Modules for Odoo for customer Nabla Srl.

%prep
%setup -q -n src

%install

install -d %{buildroot}/var/log/odoo

# Install the init scripts and conf
install -m 644 -D %SOURCE1 %{buildroot}%{_sysconfdir}/odoo/openerp-server.conf
install -m 700 -D %SOURCE5 %{buildroot}/lib/systemd/system/odoo-update.service

install -d %{buildroot}%{python_sitelib}/openerp/addons/
install -d %{buildroot}%{python_sitelib}/openerp/addons/isa

#Isa srl
cp -r isa-srl/accounting/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/base_isa/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/hr/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/l10n_it/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/marketing/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/mrp/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/partner-contact/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/product/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/project/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/purchase/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/sales/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/stock/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/users_multi_signature/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/web/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r isa-srl/website/* %{buildroot}%{python_sitelib}/openerp/addons/isa

# Customer
cp -r customers/nabla/* %{buildroot}%{python_sitelib}/openerp/addons/isa

# Oca
cp -r oca/account-financial-reporting/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/account-financial-tools/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/account-invoicing/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/account-payment/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/connector-telephony/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/bank-payment/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/community_data_files/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/l10n-italy/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/reporting-engine/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/server-tools/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/stock-logistics-warehouse/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/webkit-tools/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/knowledge/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/web/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/partner-contact/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/procurement/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/purchase-workflow/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/sale-workflow/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r oca/product/* %{buildroot}%{python_sitelib}/openerp/addons/isa

#Third part
cp -r third-party/* %{buildroot}%{python_sitelib}/openerp/addons/isa
cp -r third-party/website-sale-addons/* %{buildroot}%{python_sitelib}/openerp/addons/isa

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