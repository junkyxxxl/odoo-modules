%define     version 8.0

Name:       openerp-isa
Version:    %{version}
Release:    %{?BUILD_NUMBER}%{?dist}

License:    AGPLv3 and GPLv3 and BSD and LGPLv2+
Group:      System Environment/Daemons
Summary:    Business Applications
URL:        http://www.isa.it
Source0:    src.tar.gz

#Requires:   openerp = %{version}-%{?BUILD_NUMBER}%{?dist}

Summary: Modules for OpenERP for customers.
Group: System Environment/Daemons
%description
Modules for OpenERP for customers.

%package custom-isa
Summary: Modules for OpenERP for ISA srl.
%description custom-isa
OpenERP Modules for internal use - ISA srl.

%package website-isa
Summary: Modules Websitefor ISA srl.
%description website-isa
OpenERP Modules for website - ISA srl.

%package custom-readytec
Summary: Modules for OpenERP for customer Readytec SpA.
%description custom-readytec
Modules for OpenERP for customer Readytec SpA.

%package custom-mattioli
Summary: Modules for OpenERP for customer Mattioli Srl.
%description custom-mattioli
Modules for OpenERP for customer Mattioli Srl.

%package custom-omniapart
Summary: Modules for OpenERP for customer Omniapart Srl.
%description custom-omniapart
Modules for OpenERP for customer Omniapart Srl.

%package custom-ricci_international
Summary: Modules for OpenERP for customer Ricci International Srl.
%description custom-ricci_international
Modules for OpenERP for customer Ricci International Srl.

%package custom-montecristo
Summary: Modules for OpenERP for customer Montecristo Srl.
%description custom-montecristo
Modules for OpenERP for customer Montecristo Srl.

%package custom-primapaint
Summary: Modules for OpenERP for customer Primapaint Srl.
%description custom-primapaint
Modules for OpenERP for customer Primapaint Srl.

%package custom-idi
Summary: Modules for OpenERP for customer Idi Srl.
%description custom-idi
Modules for OpenERP for customer Idi Srl.

%package custom-b2pharma
Summary: Modules for OpenERP for customer B2pharma Srl.
%description custom-b2pharma
Modules for OpenERP for customer B2pharma Srl.

%package custom-flati
Summary: Modules for OpenERP for customer Flati Srl.
%description custom-flati
Modules for OpenERP for customer Flati Srl.

%package custom-bec
Summary: Modules for OpenERP for customer BEC Srl.
%description custom-bec
Modules for OpenERP for customer BEC Srl.

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
cp -r oca/procurement/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/purchase-workflow/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/sale-workflow/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r odoo-extra/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r salesagent-commissions/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r third-party/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r third-party/website-sale-addons/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r aeroo/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r oca/product/* %{buildroot}%{python_sitelib}/openerp/addons/


# Themes
cp -r themes/* %{buildroot}%{python_sitelib}/openerp/addons/

# Customers
cp -r customers/isa/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/readytec/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/mattioli/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/omniapart/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/ricci_international/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/montecristo/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/primapaint/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/idi/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/b2pharma/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/flati/* %{buildroot}%{python_sitelib}/openerp/addons/
cp -r customers/bec/* %{buildroot}%{python_sitelib}/openerp/addons/


%files custom-readytec
%{python_sitelib}/openerp/addons/*readytec*
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/account_journal_items_webkit
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/sale_order_report_qweb
%{python_sitelib}/openerp/addons/delivery_makeover
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/stock_sheet_report_webkit
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/base_headers_webkit
%{python_sitelib}/openerp/addons/account_invoice_template
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_voucher_cash_basis
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit_xls
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/*salesagent_commissions*
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/dbfilter_from_header
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/delivery_report_qweb
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/product_show_pricelists
%{python_sitelib}/openerp/addons/users_multi_signature
# Auto Install
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/account_asset_register_webkit
%{python_sitelib}/openerp/addons/l10n_it_asset-master
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/disable_openerp_online
#Payments
%{python_sitelib}/openerp/addons/account_direct_debit
%{python_sitelib}/openerp/addons/account_payment_extension
%{python_sitelib}/openerp/addons/account_banking_pain_base
%{python_sitelib}/openerp/addons/account_banking_payment_export
%{python_sitelib}/openerp/addons/account_banking_sepa_credit_transfer
%{python_sitelib}/openerp/addons/account_banking_sepa_direct_debit
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/stock_quant_merge
%{python_sitelib}/openerp/addons/account_journal_period_close
%{python_sitelib}/openerp/addons/l10n_it_bbone
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/attachment_preview
%{python_sitelib}/openerp/addons/partner_profit_segmentation
%{python_sitelib}/openerp/addons/auto_backup
%{python_sitelib}/openerp/addons/base_report_to_printer
%{python_sitelib}/openerp/addons/account_move_import
%{python_sitelib}/openerp/addons/account_trial_balance_period_xls

%files custom-isa
%{python_sitelib}/openerp/addons/custom_isa
%{python_sitelib}/openerp/addons/account_analytic_isa
%{python_sitelib}/openerp/addons/project_timesheet_isa
%{python_sitelib}/openerp/addons/hr_expense_isa
%{python_sitelib}/openerp/addons/hr_department_isa
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/base_res_company_isa
%{python_sitelib}/openerp/addons/hr_attendance_isa
%{python_sitelib}/openerp/addons/account_pentaho_print_isa
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/hr_employee_report
%{python_sitelib}/openerp/addons/hr_holidays_isa
%{python_sitelib}/openerp/addons/hr_overtime
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/project_custom_isa
%{python_sitelib}/openerp/addons/base_headers_webkit
%{python_sitelib}/openerp/addons/sale_isa
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit_xls
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/sale_order_report_webkit_isa
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/document_choose_directory
%{python_sitelib}/openerp/addons/document_url
%{python_sitelib}/openerp/addons/doclite
%{python_sitelib}/openerp/addons/doclite_isa
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/sale_order_report_qweb_isa
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/attachments_to_filesystem
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pricelist_customization
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/product_show_pricelists
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/stock_quant_merge
%{python_sitelib}/openerp/addons/account_journal_period_close
%{python_sitelib}/openerp/addons/l10n_it_bbone
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/attachment_preview
%{python_sitelib}/openerp/addons/partner_profit_segmentation
%{python_sitelib}/openerp/addons/auto_backup
%{python_sitelib}/openerp/addons/base_report_to_printer
%{python_sitelib}/openerp/addons/account_move_import
%{python_sitelib}/openerp/addons/account_trial_balance_period_xls
%files website-isa
# Themes
%{python_sitelib}/openerp/addons/theme_common
%{python_sitelib}/openerp/addons/theme_enark
%{python_sitelib}/openerp/addons/website_animate
%{python_sitelib}/openerp/addons/website_less

%files custom-mattioli
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/mattioli_custom
%{python_sitelib}/openerp/addons/account_chart_mattioli
%{python_sitelib}/openerp/addons/mattioli_package_manager
%{python_sitelib}/openerp/addons/mattioli_product_stock
%{python_sitelib}/openerp/addons/mattioli_report_qweb
%{python_sitelib}/openerp/addons/product_variant_grid
%{python_sitelib}/openerp/addons/sale_product_variant_grid
%{python_sitelib}/openerp/addons/account_product_variant_grid
%{python_sitelib}/openerp/addons/purchase_product_variant_grid
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/delivery_makeover
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/delivery_report_qweb
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_asset_register_webkit
%{python_sitelib}/openerp/addons/l10n_it_asset-master
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit_xls
%{python_sitelib}/openerp/addons/account_discount
%{python_sitelib}/openerp/addons/free_invoice_line
%{python_sitelib}/openerp/addons/account_custom_mattioli
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/purchase_discount
%{python_sitelib}/openerp/addons/email_cc_bcc
%{python_sitelib}/openerp/addons/sale_purchase_order_stock
%{python_sitelib}/openerp/addons/grid_custom_mattioli
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pricelist_customization
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/product_show_pricelists
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/stock_quant_merge
%{python_sitelib}/openerp/addons/account_journal_period_close
%{python_sitelib}/openerp/addons/l10n_it_bbone
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/attachment_preview
%{python_sitelib}/openerp/addons/partner_profit_segmentation
%{python_sitelib}/openerp/addons/auto_backup
%{python_sitelib}/openerp/addons/base_report_to_printer
%{python_sitelib}/openerp/addons/account_move_import
%{python_sitelib}/openerp/addons/account_trial_balance_period_xls
# Auto Install
%{python_sitelib}/openerp/addons/account_reports_grouping
%{python_sitelib}/openerp/addons/sale_order_back2draft

%files custom-omniapart
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/product_variant_grid
%{python_sitelib}/openerp/addons/sale_product_variant_grid
%{python_sitelib}/openerp/addons/account_product_variant_grid
%{python_sitelib}/openerp/addons/account_account_partner
%{python_sitelib}/openerp/addons/purchase_product_variant_grid
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/account_voucher_cash_basis
%{python_sitelib}/openerp/addons/account_vat_on_payment
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/plugin
%{python_sitelib}/openerp/addons/plugin_thunderbird
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_discount
%{python_sitelib}/openerp/addons/free_invoice_line
%{python_sitelib}/openerp/addons/vat_per_cash
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/mail_message_move
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pricelist_customization
%{python_sitelib}/openerp/addons/product_show_pricelists
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/stock_quant_merge
%{python_sitelib}/openerp/addons/account_journal_period_close
%{python_sitelib}/openerp/addons/l10n_it_bbone
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/attachment_preview
%{python_sitelib}/openerp/addons/partner_profit_segmentation
%{python_sitelib}/openerp/addons/auto_backup
%{python_sitelib}/openerp/addons/base_report_to_printer
%{python_sitelib}/openerp/addons/account_move_import
%{python_sitelib}/openerp/addons/account_trial_balance_period_xls
%{python_sitelib}/openerp/addons/purchase_to_invoice
#Custom Omniapart
%{python_sitelib}/openerp/addons/account_chart_equalitate_omniapart
%{python_sitelib}/openerp/addons/account_chart_omniapart
%{python_sitelib}/openerp/addons/account_chart_sisa_omniapart
%{python_sitelib}/openerp/addons/base_omniapart
%{python_sitelib}/openerp/addons/crm_omniapart
%{python_sitelib}/openerp/addons/hr_expense_omniapart
%{python_sitelib}/openerp/addons/omniapart_custom
%{python_sitelib}/openerp/addons/project_omniapart
%{python_sitelib}/openerp/addons/report_qweb_omniapart
%{python_sitelib}/openerp/addons/res_partner_omniapart
%{python_sitelib}/openerp/addons/sale_omniapart
%{python_sitelib}/openerp/addons/l10n_it_ea_sector
%{python_sitelib}/openerp/addons/l10n_eu_nace
%{python_sitelib}/openerp/addons/product_custom_omniapart
%{python_sitelib}/openerp/addons/mail_multicompany_omniapart
%{python_sitelib}/openerp/addons/mail_message_move_omniapart
%{python_sitelib}/openerp/addons/stock_custom_omniapart
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/email_cc_bcc
%{python_sitelib}/openerp/addons/l10n_it_asset-master
# Auto Install
%{python_sitelib}/openerp/addons/account_reports_grouping
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/sale_account_default_journal_omniapart

%files custom-ricci_international
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/product_variant_grid
%{python_sitelib}/openerp/addons/sale_product_variant_grid
%{python_sitelib}/openerp/addons/account_product_variant_grid
%{python_sitelib}/openerp/addons/purchase_product_variant_grid
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/sale_salesagent_commissions
%{python_sitelib}/openerp/addons/sale_stock_salesagent_commissions
%{python_sitelib}/openerp/addons/salesagent_commissions
%{python_sitelib}/openerp/addons/salesagent_commissions_report_qweb
%{python_sitelib}/openerp/addons/salesagent_commissions_report_webkit
%{python_sitelib}/openerp/addons/stock_salesagent_commissions
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/account_journal_items_webkit
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/sale_order_report_qweb
%{python_sitelib}/openerp/addons/stock_sheet_report_webkit
%{python_sitelib}/openerp/addons/base_headers_webkit
%{python_sitelib}/openerp/addons/account_invoice_template
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_voucher_cash_basis
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit_xls
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/dbfilter_from_header
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/account_discount
%{python_sitelib}/openerp/addons/free_invoice_line
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/sale_purchase_order_stock
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/stock_quant_merge
# Auto Install
%{python_sitelib}/openerp/addons/account_asset_register_webkit
%{python_sitelib}/openerp/addons/l10n_it_asset-master
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/account_reports_grouping
#Payments
%{python_sitelib}/openerp/addons/account_direct_debit
%{python_sitelib}/openerp/addons/account_banking_pain_base
%{python_sitelib}/openerp/addons/account_banking_payment_export
%{python_sitelib}/openerp/addons/account_banking_sepa_credit_transfer
%{python_sitelib}/openerp/addons/account_banking_sepa_direct_debit
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pricelist_customization
#Custom Ricci
%{python_sitelib}/openerp/addons/ricci_international_custom

%files custom-primapaint
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/product_variant_grid
%{python_sitelib}/openerp/addons/sale_product_variant_grid
%{python_sitelib}/openerp/addons/account_product_variant_grid
%{python_sitelib}/openerp/addons/purchase_product_variant_grid
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/delivery_report_qweb
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_asset_register_webkit
%{python_sitelib}/openerp/addons/l10n_it_asset-master
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_discount
%{python_sitelib}/openerp/addons/free_invoice_line
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/purchase_discount
%{python_sitelib}/openerp/addons/partner_credit_limit
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/sale_purchase_order_stock
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pricelist_customization
%{python_sitelib}/openerp/addons/product_ean_ept
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/product_show_pricelists
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/sale_order_print_bill
%{python_sitelib}/openerp/addons/stock_quant_merge
%{python_sitelib}/openerp/addons/account_journal_period_close
%{python_sitelib}/openerp/addons/l10n_it_bbone
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/attachment_preview
%{python_sitelib}/openerp/addons/partner_profit_segmentation
%{python_sitelib}/openerp/addons/auto_backup
%{python_sitelib}/openerp/addons/base_report_to_printer
%{python_sitelib}/openerp/addons/account_move_import
%{python_sitelib}/openerp/addons/account_trial_balance_period_xls
%{python_sitelib}/openerp/addons/report_xls
# Auto Install
%{python_sitelib}/openerp/addons/account_reports_grouping
#Custom Primapaint
%{python_sitelib}/openerp/addons/*primapaint*

%files custom-idi
%{python_sitelib}/openerp/addons/product_barcode_generator
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/product_family
%{python_sitelib}/openerp/addons/sale_order_lot
%{python_sitelib}/openerp/addons/barcode_extension
%{python_sitelib}/openerp/addons/account_journal_ddt
%{python_sitelib}/openerp/addons/custom_product_name
%{python_sitelib}/openerp/addons/sale_shipping_custom
%{python_sitelib}/openerp/addons/delivery_makeover
%{python_sitelib}/openerp/addons/account_account_partner
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/product_variant_grid
%{python_sitelib}/openerp/addons/sale_product_variant_grid
%{python_sitelib}/openerp/addons/account_product_variant_grid
%{python_sitelib}/openerp/addons/purchase_product_variant_grid
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_report_family
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/delivery_report_qweb
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_asset_register_webkit
%{python_sitelib}/openerp/addons/l10n_it_asset-master
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_discount
%{python_sitelib}/openerp/addons/free_invoice_line
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/purchase_discount
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/sale_purchase_order_stock
%{python_sitelib}/openerp/addons/sale_salesagent_commissions
%{python_sitelib}/openerp/addons/sale_stock_salesagent_commissions
%{python_sitelib}/openerp/addons/salesagent_commissions
%{python_sitelib}/openerp/addons/salesagent_commissions_report_qweb
%{python_sitelib}/openerp/addons/salesagent_commissions_report_webkit
%{python_sitelib}/openerp/addons/stock_salesagent_commissions
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pharmacode
%{python_sitelib}/openerp/addons/product_pricelist_customization
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/auth_signup_sale
%{python_sitelib}/openerp/addons/website_multi_image
%{python_sitelib}/openerp/addons/website_sale_clear_cart
%{python_sitelib}/openerp/addons/website_stock
%{python_sitelib}/openerp/addons/website_webkul_addons
%{python_sitelib}/openerp/addons/website_wishlist
%{python_sitelib}/openerp/addons/product_show_pricelists
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/mrp_picking_list
%{python_sitelib}/openerp/addons/product_ean_check
%{python_sitelib}/openerp/addons/export_vettura_dhl
%{python_sitelib}/openerp/addons/package_manager
%{python_sitelib}/openerp/addons/managing_lots_items
%{python_sitelib}/openerp/addons/invoice_mass_mailing
%{python_sitelib}/openerp/addons/binary_field_extend
%{python_sitelib}/openerp/addons/purchase_to_invoice
%{python_sitelib}/openerp/addons/partner_credit_limit
%{python_sitelib}/openerp/addons/stock_quant_merge
%{python_sitelib}/openerp/addons/account_journal_period_close
%{python_sitelib}/openerp/addons/l10n_it_bbone
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/attachment_preview
%{python_sitelib}/openerp/addons/partner_profit_segmentation
%{python_sitelib}/openerp/addons/auto_backup
%{python_sitelib}/openerp/addons/base_report_to_printer
%{python_sitelib}/openerp/addons/account_move_import
%{python_sitelib}/openerp/addons/account_trial_balance_period_xls
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/stock_move_date_expected
# Auto Install
%{python_sitelib}/openerp/addons/account_reports_grouping
#Custom Idi
%{python_sitelib}/openerp/addons/*idi*

%files custom-b2pharma
%{python_sitelib}/openerp/addons/product_barcode_generator
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/product_family
%{python_sitelib}/openerp/addons/sale_order_lot
%{python_sitelib}/openerp/addons/barcode_extension
%{python_sitelib}/openerp/addons/account_journal_ddt
%{python_sitelib}/openerp/addons/custom_product_name
%{python_sitelib}/openerp/addons/sale_shipping_custom
%{python_sitelib}/openerp/addons/account_account_partner
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/product_variant_grid
%{python_sitelib}/openerp/addons/sale_product_variant_grid
%{python_sitelib}/openerp/addons/account_product_variant_grid
%{python_sitelib}/openerp/addons/purchase_product_variant_grid
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_report_family
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/delivery_report_qweb
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_asset_register_webkit
%{python_sitelib}/openerp/addons/l10n_it_asset-master
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_discount
%{python_sitelib}/openerp/addons/free_invoice_line
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/purchase_discount
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/sale_purchase_order_stock
%{python_sitelib}/openerp/addons/sale_salesagent_commissions
%{python_sitelib}/openerp/addons/sale_stock_salesagent_commissions
%{python_sitelib}/openerp/addons/salesagent_commissions
%{python_sitelib}/openerp/addons/salesagent_commissions_report_qweb
%{python_sitelib}/openerp/addons/salesagent_commissions_report_webkit
%{python_sitelib}/openerp/addons/stock_salesagent_commissions
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pharmacode
%{python_sitelib}/openerp/addons/product_pricelist_customization
%{python_sitelib}/openerp/addons/procurement_plan
%{python_sitelib}/openerp/addons/procurement_manager
%{python_sitelib}/openerp/addons/procurement_plan_mrp
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/auth_signup_sale
%{python_sitelib}/openerp/addons/website_multi_image
%{python_sitelib}/openerp/addons/website_sale_clear_cart
%{python_sitelib}/openerp/addons/website_stock
%{python_sitelib}/openerp/addons/website_webkul_addons
%{python_sitelib}/openerp/addons/website_wishlist
%{python_sitelib}/openerp/addons/product_show_pricelists
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/product_ean_check
%{python_sitelib}/openerp/addons/export_vettura_dhl
%{python_sitelib}/openerp/addons/website_sale_checkout
%{python_sitelib}/openerp/addons/package_manager
%{python_sitelib}/openerp/addons/partner_credit_limit
%{python_sitelib}/openerp/addons/managing_lots_items
%{python_sitelib}/openerp/addons/invoice_mass_mailing
%{python_sitelib}/openerp/addons/binary_field_extend
%{python_sitelib}/openerp/addons/purchase_to_invoice
%{python_sitelib}/openerp/addons/stock_quant_merge
%{python_sitelib}/openerp/addons/payment_extra_cost
%{python_sitelib}/openerp/addons/account_invoice_kit
%{python_sitelib}/openerp/addons/account_journal_period_close
%{python_sitelib}/openerp/addons/l10n_it_bbone
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/attachment_preview
%{python_sitelib}/openerp/addons/partner_profit_segmentation
%{python_sitelib}/openerp/addons/auto_backup
%{python_sitelib}/openerp/addons/base_report_to_printer
%{python_sitelib}/openerp/addons/account_move_import
%{python_sitelib}/openerp/addons/account_trial_balance_period_xls
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/theme_blueboy
%{python_sitelib}/openerp/addons/stock_move_date_expected

# Auto Install
%{python_sitelib}/openerp/addons/account_reports_grouping
#Custom B2pharma
%{python_sitelib}/openerp/addons/*b2pharma*

%files custom-montecristo
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/product_variant_grid
%{python_sitelib}/openerp/addons/sale_product_variant_grid
%{python_sitelib}/openerp/addons/account_product_variant_grid
%{python_sitelib}/openerp/addons/purchase_product_variant_grid
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/sale_salesagent_commissions
%{python_sitelib}/openerp/addons/sale_stock_salesagent_commissions
%{python_sitelib}/openerp/addons/salesagent_commissions
%{python_sitelib}/openerp/addons/salesagent_commissions_report_qweb
%{python_sitelib}/openerp/addons/salesagent_commissions_report_webkit
%{python_sitelib}/openerp/addons/stock_salesagent_commissions
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/account_journal_items_webkit
%{python_sitelib}/openerp/addons/sale_order_report_qweb
%{python_sitelib}/openerp/addons/stock_sheet_report_webkit
%{python_sitelib}/openerp/addons/base_headers_webkit
%{python_sitelib}/openerp/addons/account_invoice_template
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_voucher_cash_basis
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit_xls
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/dbfilter_from_header
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/account_discount
%{python_sitelib}/openerp/addons/free_invoice_line
%{python_sitelib}/openerp/addons/stock_custom_montecristo
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/l10n_it_intrastat
%{python_sitelib}/openerp/addons/l10n_it_report_intrastat
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/sale_purchase_order_stock
%{python_sitelib}/openerp/addons/sale_order_price_recalculation
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/account_auto_fy_sequence
%{python_sitelib}/openerp/addons/stock_quant_merge
# Auto Install
%{python_sitelib}/openerp/addons/account_asset_register_webkit
%{python_sitelib}/openerp/addons/l10n_it_asset-master
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/account_reports_grouping
#Payments
%{python_sitelib}/openerp/addons/account_direct_debit
%{python_sitelib}/openerp/addons/account_banking_pain_base
%{python_sitelib}/openerp/addons/account_banking_payment_export
%{python_sitelib}/openerp/addons/account_banking_sepa_credit_transfer
%{python_sitelib}/openerp/addons/account_banking_sepa_direct_debit
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pricelist_customization
#Custom Montecristo
%{python_sitelib}/openerp/addons/*montecristo*
%{python_sitelib}/openerp/addons/isa_sale_analisys

%files custom-flati
%{python_sitelib}/openerp/addons/*flati*
%{python_sitelib}/openerp/addons/account_due_list_ext_isa
%{python_sitelib}/openerp/addons/account_due_date_report_webkit
%{python_sitelib}/openerp/addons/account_due_list
%{python_sitelib}/openerp/addons/account_invoice_cancel_management
%{python_sitelib}/openerp/addons/account_invoice_report_qweb
%{python_sitelib}/openerp/addons/account_makeover
%{python_sitelib}/openerp/addons/account_report
%{python_sitelib}/openerp/addons/free_invoice_line
%{python_sitelib}/openerp/addons/account_discount
%{python_sitelib}/openerp/addons/account_payment_term_preview
%{python_sitelib}/openerp/addons/account_invoice_entry_date
%{python_sitelib}/openerp/addons/account_journal_items_webkit
%{python_sitelib}/openerp/addons/base_fiscalcode
%{python_sitelib}/openerp/addons/sale_order_report_qweb
%{python_sitelib}/openerp/addons/l10n_it_ddt
%{python_sitelib}/openerp/addons/l10n_it_ddt_makeover
%{python_sitelib}/openerp/addons/stock_makeover
%{python_sitelib}/openerp/addons/stock_sheet_report_webkit
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/base_headers_webkit
%{python_sitelib}/openerp/addons/account_invoice_template
%{python_sitelib}/openerp/addons/account_move_template
%{python_sitelib}/openerp/addons/account_voucher_cash_basis
%{python_sitelib}/openerp/addons/account_ricevute_bancarie
%{python_sitelib}/openerp/addons/account_vat_registries_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_webkit_xls
%{python_sitelib}/openerp/addons/account_statement_report_webkit
%{python_sitelib}/openerp/addons/account_financial_report_horizontal
%{python_sitelib}/openerp/addons/report_xls
%{python_sitelib}/openerp/addons/*salesagent_commissions*
%{python_sitelib}/openerp/addons/account_exporter_statements
%{python_sitelib}/openerp/addons/account_exporter_statements_webkit
%{python_sitelib}/openerp/addons/account_vat_registries_report
%{python_sitelib}/openerp/addons/dbfilter_from_header
%{python_sitelib}/openerp/addons/l10n_it_spesometro
%{python_sitelib}/openerp/addons/account_vat_period_end_statement
%{python_sitelib}/openerp/addons/l10n_it_account
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/pentaho_reports
%{python_sitelib}/openerp/addons/l10n_it_e_invoice
%{python_sitelib}/openerp/addons/l10n_it_fatturapa
%{python_sitelib}/openerp/addons/l10n_it_fatturapa_out
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/l10n_it_ipa
%{python_sitelib}/openerp/addons/l10n_it_rea
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/stock_picking_transfer_enhanced
%{python_sitelib}/openerp/addons/sale_makeover
%{python_sitelib}/openerp/addons/sale_stock_makeover
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/sale_order_back2draft
%{python_sitelib}/openerp/addons/product_show_pricelists
%{python_sitelib}/openerp/addons/users_multi_signature
%{python_sitelib}/openerp/addons/stock_quant_merge
%{python_sitelib}/openerp/addons/account_journal_period_close
%{python_sitelib}/openerp/addons/l10n_it_bbone
%{python_sitelib}/openerp/addons/l10n_it_pec
%{python_sitelib}/openerp/addons/attachment_preview
%{python_sitelib}/openerp/addons/partner_profit_segmentation
%{python_sitelib}/openerp/addons/auto_backup
%{python_sitelib}/openerp/addons/base_report_to_printer
%{python_sitelib}/openerp/addons/account_move_import
%{python_sitelib}/openerp/addons/account_trial_balance_period_xls
# Auto Install
%{python_sitelib}/openerp/addons/account_central_journal_webkit
%{python_sitelib}/openerp/addons/account_asset_register_webkit
%{python_sitelib}/openerp/addons/l10n_it_asset-master
%{python_sitelib}/openerp/addons/account_voucher_makeover
%{python_sitelib}/openerp/addons/account_invoice_intracee
%{python_sitelib}/openerp/addons/disable_openerp_online
#Payments
%{python_sitelib}/openerp/addons/account_direct_debit
%{python_sitelib}/openerp/addons/account_banking_pain_base
%{python_sitelib}/openerp/addons/account_banking_payment_export
%{python_sitelib}/openerp/addons/account_banking_sepa_credit_transfer
%{python_sitelib}/openerp/addons/account_banking_sepa_direct_debit
%{python_sitelib}/openerp/addons/account_cashing_fees*
%{python_sitelib}/openerp/addons/account_commission*
%{python_sitelib}/openerp/addons/sale_stock_commission
%{python_sitelib}/openerp/addons/product_pricelist_customization
#Aeroo
%{python_sitelib}/openerp/addons/report_aeroo
%{python_sitelib}/openerp/addons/report_aeroo_ooo
%{python_sitelib}/openerp/addons/base_field_serialized

%files custom-bec
%{python_sitelib}/openerp/addons/bec*
%{python_sitelib}/openerp/addons/cq_bec*
%{python_sitelib}/openerp/addons/add_field_to_partner
%{python_sitelib}/openerp/addons/l10n_it_base
%{python_sitelib}/openerp/addons/l10n_it_vat_registries
%{python_sitelib}/openerp/addons/l10n_it_fiscalcode
%{python_sitelib}/openerp/addons/mass_editing
%{python_sitelib}/openerp/addons/web_export_view
%{python_sitelib}/openerp/addons/disable_openerp_online
%{python_sitelib}/openerp/addons/l10n_it_base_location_geonames_import
%{python_sitelib}/openerp/addons/base_location
%{python_sitelib}/openerp/addons/base_location_geonames_import
%{python_sitelib}/openerp/addons/l10n_it_base_migration_tool
%{python_sitelib}/openerp/addons/attachments_to_filesystem
%{python_sitelib}/openerp/addons/sale_order_back2draft

%files
%{python_sitelib}/openerp/addons/*

%changelog
