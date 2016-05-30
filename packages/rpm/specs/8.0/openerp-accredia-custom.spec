%define     version 8.0

Name:       openerp-accredia-custom
Version:    %{version}
Release:    %{?BUILD_NUMBER}%{?dist}

License:    AGPLv3 and GPLv3 and BSD and LGPLv2+
Group:      System Environment/Daemons
Summary:    Business Applications
URL:        http://www.isa.it
Source0:    src.tar.gz

Requires:   openerp-accredia = %{version}-%{?BUILD_NUMBER}%{?dist}

Summary: Modules for OpenERP for customers.
Group: System Environment/Daemons
%description
Modules for OpenERP for customers.

%package accredia
Summary: Modules for OpenERP for customer Accredia.
%description accredia
Modules for OpenERP for customer Accredia.

%prep
%setup -q -n src

%install
install -d %{buildroot}%{python_sitelib}/openerp/addons/

#Isa srl
cp -r isa-srl/* %{buildroot}%{python_sitelib}/openerp/addons/

# Third party
cp -r oca/account-financial-reporting/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/account-financial-tools/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/account-invoicing/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/account-payment/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/connector-telephony/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/bank-payment/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/community_data_files/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/l10n-italy/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/reporting-engine/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/server-tools/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/stock-logistics-warehouse/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/webkit-tools/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/knowledge/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/web/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/partner-contact/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/purchase-workflow/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r salesagent-commissions/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r third-party/* %{buildroot}%{python_sitelib}/openerp/addons/

# Themes
cp -r themes/* %{buildroot}%{python_sitelib}/openerp/addons/

# Customers
cp -r customers/accredia/* %{buildroot}%{python_sitelib}/openerp/addons/


%files accredia
%{python_sitelib}/openerp/addons/account_accredia
%{python_sitelib}/openerp/addons/account_banking_accredia
%{python_sitelib}/openerp/addons/account_chart_accredia
%{python_sitelib}/openerp/addons/account_invoice_report_accredia
%{python_sitelib}/openerp/addons/accredia_custom
%{python_sitelib}/openerp/addons/accredia_purchase
%{python_sitelib}/openerp/addons/doclite_accredia
%{python_sitelib}/openerp/addons/hr_accredia
%{python_sitelib}/openerp/addons/hr_expense_accredia
%{python_sitelib}/openerp/addons/hr_timesheet_invoice_accredia
%{python_sitelib}/openerp/addons/project_accredia
%{python_sitelib}/openerp/addons/project_action_accredia
%{python_sitelib}/openerp/addons/project_long_term_accredia
%{python_sitelib}/openerp/addons/sale_accredia

%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/doclite
%{python_sitelib}/openerp/addons/project_work_daily
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit_xls
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/hr_expense_multicurrencies
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/account_invoice_force_number
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/database_cleanup

%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/account_invoice_intracee
# Not required
#%{python_sitelib}/openerp/addons/partner_firstname
#%{python_sitelib}/openerp/addons/l10n_it_withholding_tax
#%{python_sitelib}/openerp/addons/stock_invoice_picking
#%{python_sitelib}/openerp/addons/stock_invoice_picking_incoterm
#%{python_sitelib}/openerp/addons/stock_picking_invoice_link
#%{python_sitelib}/openerp/addons/base_partner_merge
#%{python_sitelib}/openerp/addons/stock_makeover
#%{python_sitelib}/openerp/addons/account_central_journal_ext_isa
#%{python_sitelib}/openerp/addons/l10n_it_partially_deductible_vat
#%{python_sitelib}/openerp/addons/account_voucher_menu
#%{python_sitelib}/openerp/addons/base_headers_webkit

%files
%{python_sitelib}/openerp/addons/*

%changelog
