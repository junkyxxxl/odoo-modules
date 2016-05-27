
openerp.web_export_picking_montecristo = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (self.getParent().ViewManager.active_view == 'list' && this.getParent().name == 'Picking list') {
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportPickingMain', {widget: self}));
                self.$el.find('#export_picking').on('click', self.on_sidebar_export_picking_xls);
            }
        },

        on_sidebar_export_picking_xls: function () {
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
                url: '/web/export/xls_picking',
                data: {data: JSON.stringify({
                    model: view.model,
                    rows: export_rows
                })},
                complete: $.unblockUI
            });
        }
    });

};
