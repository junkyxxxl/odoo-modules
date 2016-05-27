openerp.web_import_ddt_b2pharma = function (instance, local){
	
	var _t = instance.web._t,
    	_lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	
	//Se devo ridisegnare un componente
	instance.web.Sidebar.include({
		redraw: function () {
			var self = this;
            this._super.apply(this, arguments);
            if (this.getParent().ViewManager.active_view == 'list' && this.getParent().name == 'Import ddt movements'){
            	this.$el.find('.oe_sidebar').find('li').last().after('<li><a href="#" data-process><span class="fa fa-gear"/> Elabora movimenti</a></li>');
            	this.$el.find('.oe_sidebar').find('li > a[data-process]').on('click',function(e){
            		//per non entrare all'interno della logica di odoo
            		e.preventDefault();
            		e.stopPropagation();
            		//Devo reperire le righe selezionate
            		view = self.getParent(),
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
            		var model = new instance.web.Model("track.import.ddt");
            		$.blockUI();
            		model.call("process_track",{selected_row: export_rows}).then(function(){
            			$.unblockUI();
            			self.do_action({
            				'type': 'ir.actions.client',
            				'tag': 'reload'
            			});
            		},function(){
            			$.unblockUI();
            		});
            	})
            }
        }
	});
	
	
	//Se devo modificare un componente.
	instance.web.Sidebar = instance.web.Sidebar.extend({
		start: function(){
			var self = this;
            this._super.apply(this, arguments);
            //Solo nella vista dei ddt
            if (this.getParent().ViewManager.active_view == 'list' && this.getParent().name == 'Import ddt movements'){
            	//Gestione pulsante di importazione ddt al posto del pulsante import normale
            	//Nascondo il pulsante di creazione (non lo faccio dalla vista perchè comunque mi serve
            	//il pulsante importa.
            	this.getParent().$buttons.children('button[class*=oe_list_add]').hide();
            	this.getParent().$buttons
            					.children('.oe_alternative')
            					.children('a.oe_list_button_import')
            					.replaceWith("<a href='#' data-import='ddt' class='oe_bold'>Importa DDT</a>");
            	this.getParent().$buttons.find('a[data-import=ddt]').on('click', function(){
            		self.do_action({
            			type: 'ir.actions.act_window',
            			res_model: 'web.import.ddt.b2pharma.wizard',
            			views: [[false, 'form']],
            			name: "Importa DDT",
            			target: 'new'
            		})
            	});
            }
		}
	});

};
