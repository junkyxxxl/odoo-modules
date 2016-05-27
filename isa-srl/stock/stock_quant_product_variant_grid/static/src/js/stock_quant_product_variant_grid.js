openerp.stock_quant_product_variant_grid = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var num_dims = 0;
    var types = [];
    var rows = [];
    var rows_name = [];
    var columns = [];
    var columns_name = [];
    var q_products = [];
    var t_products = [];
    var products_id = [];
    var products_qty = [];
    var lastValidTemplate;
    var stock_quant = new instance.web.Model("stock.quant");
    var product_template = new instance.web.Model("product.template");

    instance.stock_quant_product_variant_grid.qtyWidget = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        
        init: function() 
        {
           
        	this._super.apply(this, arguments);
        	var self = this;
            this.set({
                stock_quants: [],
            });
            this.updating = false;
        	this.defs = [];
            this.field_manager.on("field_changed:stock_quant_ids", this, this.query_quants);
            this.field_manager.on("field_changed:location_id", this, function() 
            {
                this.set({"location_id": this.field_manager.get_field_value("location_id")});
            });
            this.field_manager.on("field_changed:company_id", this, function() 
            {
                this.set({"company_id": this.field_manager.get_field_value("company_id")});
            });
            this.field_manager.on("field_changed:template_id", this, function() 
            {
                this.set({"template_id": this.field_manager.get_field_value("template_id")});
            });
            this.on("change:stock_quants", this, this.update_quants);
            this.res_o2m_drop = new instance.web.DropMisordered();
            this.render_drop = new instance.web.DropMisordered();
        },
        query_quants: function() {
            var self = this;
            if (self.updating)
                return;
            var commands = this.field_manager.get_field_value("stock_quant_ids");
            this.res_o2m_drop.add(new instance.web.Model(this.view.model).call("resolve_2many_commands", ["stock_quant_ids", commands, [], 
                    new instance.web.CompoundContext()]))
                .done(function(result) {
                self.querying = true;
                self.set({stock_quants: result});
                self.querying = false;
            });
        },
        update_quants: function() {
            var self = this;
            if (self.querying)
                return;
            self.updating = true;
            self.field_manager.set_values({stock_quant_ids: self.get("stock_quants")}).done(function() {
                self.updating = false;
            });
        },
        initialize_field: function() {
        	
            instance.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:stock_quants", self, self.initialize_content);
            self.on("change:location_id", self, self.initialize_content);
            self.on("change:company_id", self, self.initialize_content);
            self.on("change:template_id", self, self.initialize_content);            
            lastValidTemplate = self.get("template_id");
        },
        initialize_content: function() 
    	{
            QWeb = instance.web.qweb;
            _t = instance.web._t;
            num_dims = 0;
            types = [];
            rows = [];
            rows_name = [];
            columns = [];
            columns_name = [];
            q_products = [];
            t_products = [];
            products_id = [];
            products_qty = [];
            stock_quant = new instance.web.Model("stock.quant");
            var product_template = new instance.web.Model("product.template");
            
            var self = this;
            
            if (!self.get("location_id") || !self.get("template_id") || !self.get("company_id"))
                return;
            this.destroy_content();     

            return this.render_drop.add(product_template.call("get_template_dimension_count", [self.get("template_id")]).then(function(count) 
            {
            	num_dims = count;
            	if(count<1 || count>2)
            	{
            		self.columns = columns;
            		self.columns_name = columns_name;
            		self.rows = rows;
            		self.rows_name = rows_name;
            		self.products_id = products_id;
            		self.products_qty = products_qty;
            		self.num_dims = 0;
            		self.display_data();
            		window.alert("Hai selezionato un template non valido!");            		
            		return;
            	}
            	lastValidTemplate = self.get("template_id");
            	product_template.call("get_template_dimension", [self.get("template_id")]).then(function(result) 
            	{
            		types = result;	
            		product_template.call("get_dimension_options", [self.get("template_id"),types[0][0]]).then(function(result) 
            		{
            			var t_columns = result;
            			for(var i=0;i<t_columns.length;i++)
            			{
            				columns[i]=t_columns[i][0];
            				columns_name[i]=t_columns[i][1];
            			}
                        stock_quant.call("get_product_quantities", [self.get("template_id"), self.get("location_id"), self.get("company_id")]).then(function(result)
    					{
    						q_products = result;
    						
        					product_template.call("get_product_list", [self.get("template_id")]).then(function(result)
            				{
        						t_products = result;
        						if(num_dims == 2)
		                		{ 
			                		product_template.call("get_dimension_options", [self.get("template_id"),types[1][0]]).then(function(result) 
			            			{					               			
			                    			var t_rows = result;
			                    			for(i=0;i<t_rows.length;i++)
			                    			{
			                    				rows[i]=t_rows[i][0];
			                    				rows_name[i]=t_rows[i][1];
			                    			}
			                            	
			                            	products_id = new Array();
			                            	products_qty = new Array();

			                            	for(i=0;i<rows.length;i++)
			                            	{
			                            		products_id[i] = new Array();
			                            		products_qty[i] = new Array();
			                            		
			                            		for(j=0;j<columns.length;j++)
			                            		{
			                            			products_id[i][j]=null;
			                            			products_qty[i][j]=0;
			                            		}
			                            	}

			                            	for(i=0; i<t_products.length;i++)
			                            	{
			                            		var index_r;
			                            		var index_c;
			                            		var temp = _.indexOf(rows, t_products[i][1],false);
			                            		if(temp>=0)
			                            		{
			                            			index_r=temp;
			                            			index_c=_.indexOf(columns, t_products[i][2],false);
			                            		}
			                            		else
			                            		{
			                            			index_r=_.indexOf(rows,t_products[i][2],false);
			                            			index_c=_.indexOf(columns, t_products[i][1],false);
			                            		}
			                            		products_id[index_r][index_c]=t_products[i][0];
			                            		
			                            		var pr_qty = 0;
			                            		for(j=0;j<q_products.length;j++)
			                            		{
			                            			if(q_products[j][0]== t_products[i][0])
			                            			{
			                            				pr_qty+= q_products[j][1];
			                            			}
			                            		}
			                            		products_qty[index_r][index_c]=pr_qty;
			                            	}			                            	
        			                		self.columns = columns;
        			                		self.columns_name = columns_name;
					                		self.rows = rows;
					                		self.rows_name = rows_name;
					                		self.products_id = products_id;
					                		self.products_qty = products_qty;
					                		self.num_dims = num_dims;
					                		self.display_data();
			            			}); 
		                		}
		                		else
		                		{
                    				rows[0]=-1;
                    				rows_name[0]=" ";
	                    			
		                			products_id = new Array();
	                            	products_qty = new Array();

                            		products_id[0] = new Array();
                            		products_qty[0] = new Array();
                            		
                            		for(var j=0;j<columns.length;j++)
                            		{
                            			products_id[0][j]=null;
                            			products_qty[0][j]=0;
                            		}

	                            	for(i=0; i<t_products.length;i++)
	                            	{
	                            		var index_c = _.indexOf(columns, t_products[i][1],false);
	                            		products_id[0][index_c]=t_products[i][0];
	                            		
	                            		var pr_qty = 0;
	                            		for(j=0;j<q_products.length;j++)
	                            		{
	                            			if(q_products[j][0]== t_products[i][0])
	                            			{
	                            				pr_qty+= q_products[j][1];
	                            			}
	                            		}
	                            		products_qty[0][index_c]=pr_qty;
	                            	}
			                		self.columns = columns;
			                		self.columns_name = columns_name;
			                		self.rows = rows;
			                		self.rows_name = rows_name;
			                		self.products_id = products_id;
			                		self.products_qty = products_qty;
			                		self.num_dims = num_dims;
			                		self.display_data();
		                		}
            				});
    					});
            		});           		
        		});
            }));            
    	},
        destroy_content: function() 
        {
            if (this.dfm) 
            {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        display_data: function() 
        {    
        	var self = this;
    		self.$el.html(QWeb.render("stock_quant_product_variant_grid.qtyWidget", {widget: self}));
            _.each(self.rows, function(row) {
                _.each(self.columns, function(column) {
                	self.get_box(rows_name[_.indexOf(rows,row)], columns_name[_.indexOf(columns,column)]).val(self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]).change(function(){
                        var num = $(this).val();
                        if (isNaN(num))
                        {
                        	$(this).val(self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]);
                        }
                        else
                        {
                        	var Num = Number(num);
                        	
							var today = new Date();
							var dd = today.getDate();
							var mm = today.getMonth()+1; //January is 0!
							var yyyy = today.getFullYear();
				            var curHour = today.getHours() < 10 ? '0' + today.getHours() : today.getHours();
				            var curMinute = today.getMinutes() < 10 ? '0' + today.getMinutes() : today.getMinutes();
				            var curSeconds = today.getSeconds() < 10 ? '0' + today.getSeconds() : today.getSeconds();
							
							if(dd<10) {
							    dd='0'+dd
							} 
							
							if(mm<10) {
							    mm='0'+mm
							} 
							
							var todayStr = yyyy+'-'+mm+'-'+dd+ ' '+curHour+':'+curMinute+':'+curSeconds;
							
                        	tmpRow = {
                        	           'qty':Num-products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)],
                        	           'location_id':self.get("location_id"),
                        	           'product_id' :products_id[_.indexOf(rows,row)][_.indexOf(columns,column)],
                        	           'company_id' :self.get("company_id"),
                        	           'in_date'	:instance.web.str_to_datetime(todayStr)
                        			 };
                        	products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]=Num;
                        	self.display_totals();
                        	self.sync(tmpRow);
                        }                    
                	});
                });
            });
            self.display_totals(); 
        },
        get_box: function(row, column) {
            return this.$('[data-row="' + row + '"][data-column="' + column + '"]');
        },
        get_row_total: function(row) {
            return this.$('[data-row-total="' + row + '"]');
        },
        get_column_total: function(column) {
            return this.$('[data-column-total="' + column + '"]');
        },
        get_super_total: function() {
            return this.$('.oe_quantities_superTotal');
        },
        display_totals: function()
        {
        	var self = this;
        	var column_sum = _.map(_.range(self.columns.length), function() { return 0 });
        	var super_tot = 0;
        	_.each(self.rows, function(row) {
        		var row_sum = 0;
                _.each(self.columns, function(column) {
                	var sum = self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)];
                	super_tot+=sum;
                	row_sum+=sum;
                	column_sum[_.indexOf(columns,column)]+=sum;
                });
                self.get_row_total(rows_name[_.indexOf(rows,row)]).html(row_sum);
                _.each(self.columns, function(column) {
                    self.get_column_total(columns_name[_.indexOf(columns,column)]).html(column_sum[_.indexOf(columns,column)]);
                });
                self.get_super_total().html(super_tot);
            });                
        },
        sync: function(record) {
            var self = this;
            self.setting = true;
            self.set({stock_quants: this.generate_o2m_value(record)});
            self.update_quants();
            self.setting = false;
        },
        generate_o2m_value: function(record) {
            var self = this;
            var ops = self.get("stock_quants");
            ops.push(record);    
            return ops;
        }
    });

    instance.web.form.custom_widgets.add('quantities_per_template', 'instance.stock_quant_product_variant_grid.qtyWidget');

};

