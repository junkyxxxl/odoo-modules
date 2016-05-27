
openerp.export_vettura_dhl = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function () {
            var self = this;
            this._super.apply(this, arguments);
            
            if (self.getParent().ViewManager.active_view == 'list' && this.getParent().name == 'DdT') {
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportDdtMain', {widget: self}));
                self.$el.find('#export_ddt_dhl').on('click', function(){self.on_sidebar_export_ddt_dhl_xls('ddt')});
            }
            if (self.getParent().ViewManager.active_view == 'list' && this.getParent().name == 'Fattura') {
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportDdtInvoiceMain', {widget: self}));
                self.$el.find('#export_invoice_dhl').on('click', function(){self.on_sidebar_export_ddt_dhl_xls('invoice')});
            } 
        },
        on_sidebar_export_ddt_dhl_xls: function($type){
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
            if ($type == 'ddt'){
	            $.blockUI();
	            view.session.get_file({
	                url: '/isa/export/xls_ddt',
	                data: {data: JSON.stringify({
	                    model: view.model,
	                    rows: export_rows
	                })},
	                complete: $.unblockUI
	            });
	        }
            if ($type == 'invoice'){
	            $.blockUI();
	            view.session.get_file({
	                url: '/isa/export/xls_invoice_ddt',
	                data: {data: JSON.stringify({
	                    model: view.model,
	                    rows: export_rows
	                })},
	                complete: $.unblockUI
	            });
	        }
        }
    });
}
