
openerp.account_invoice_zip = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (self.getParent().ViewManager.active_view == 'list' && this.getParent().name == 'Fattura') {
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportInvoiceZipMain', {widget: self}));
                self.$el.find('#export_invoice_zip').on('click', self.on_sidebar_export_invoice_zip);
            }
        },

        on_sidebar_export_invoice_zip: function () {
            var self = this,
                view = this.getParent(),
                children = view.getChildren();
            rows = view.$el.find('.oe_list_content > tbody > tr');
            export_rows = [];
            $.each(rows, function () {
                $row = $(this);
                // find only rows with data
                if ($row.attr('data-id')) {
                    export_row = [];
                    
                    checked = $row.find('th input[type=checkbox]').attr("checked");
                    if (children && checked === "checked") {
                    	//alert($row.attr('data-id'))
                    	export_rows.push($row.attr('data-id'));                     
                    }
                }
            });
            $.blockUI();
            view.session.get_file({
                url: '/web/export/zip_invoices',
                data: {data: JSON.stringify({
                    model: view.model,
                    rows: export_rows
                })},
                complete: $.unblockUI
            });
        }
    });

};
