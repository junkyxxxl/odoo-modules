openerp.purchase_product_variant_grid = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var num_dims = 0;
    var types = [];
    var attribute_names = [];    
    var rows = [];
    var rows_name = [];
    var columns = [];
    var columns_name = [];
    var columns_lenght = 0;
    var q_products = [];
    var t_products = [];
    var products_id = [];
    var products_qty = [];
    var products_price = [];				/**/
    var copied_row = [];				
    var copied_price = [];				/**/
    var to_sync = [];
    var lastValidTemplate;
    var lock = false;
    var product_template = new instance.web.Model("product.template");
    var product_product = new instance.web.Model("product.product");    
    var edited = false;
    var initialized = false;   
    
    instance.purchase_product_variant_grid.qtyWidget = instance.web.form.FormWidget.extend(instance.web.form.ReinitializeWidgetMixin, {
        
        init: function() 
        {
	      
 //           window.alert("init");
        	this._super.apply(this, arguments);
        	var self = this;
	    self.edited = false;
	    self.initialized = false;
	    self.$('[name="submit"]').attr( "disabled", true );
	    self.$('[name="annulla"]').attr( "disabled", true );		
            this.set({
                order_lines: [],
            });
            this.updating = false;
        	this.defs = [];
            this.field_manager.on("field_changed:order_line", this, this.query_quants);
            this.field_manager.on("field_changed:template_id", this, function() 
            {
                this.set({"template_id": this.field_manager.get_field_value("template_id")});
            });
	    this.field_manager.on("field_changed:value_filter_id", this, function() 
            {
                this.set({"value_filter_id": this.field_manager.get_field_value("value_filter_id")});
            });	    
	    this.field_manager.on("field_changed:show_totals", this, function() 
            {
                this.set({"show_totals": this.field_manager.get_field_value("show_totals")});
            });	
            this.field_manager.on("field_changed:order_id", this, function() 
            {
                this.set({"order_id": this.field_manager.get_field_value("order_id")});
            });
            this.field_manager.on("field_changed:state", this, function() 
            {
                this.set({"state": this.field_manager.get_field_value("state")});
            });
        //    this.on("change:order_lines", this, this.update_quants);
            this.res_o2m_drop = new instance.web.DropMisordered();
            this.render_drop = new instance.web.DropMisordered();
        //    window.alert(JSON.stringify(this.field_manager.get_field_value("order_line")));            
        },
        query_quants: function() {
  //          window.alert("query_quants");
            var self = this;
            if (self.updating)
                return;
            var commands = this.field_manager.get_field_value("order_line");
        //    window.alert(JSON.stringify(this.field_manager.get_field_value("order_line")));
            this.res_o2m_drop.add(new instance.web.Model(this.view.model).call("fnct_prova", ["order_line", commands, [], 
                    new instance.web.CompoundContext()]))
                .done(function(result) {
                self.querying = true;
                self.field_manager.set_values({template_id: false});
                self.field_manager.set_values({value_filter_id: false});		
                self.set({order_lines: result});
                self.querying = false;
            });
        },
        update_quants: function() {
 //         window.alert("update_quants");
            var self = this;
            if (self.querying)
                return;
            self.updating = true;
            tmp=self.get("order_lines");
            for(i=0; i<tmp.length;i++)
            {   
            	tmp[i]['state']= self.get("state");
		if(tmp[i]['state']=='sent')
		{
		  tmp[i]['state']='draft';
		}
            }
            self.field_manager.set_values({order_line: tmp}).done(function() {
            	self.updating = false;
            });
            
 
        },
        initialize_field: function() {
//            window.alert("initialize_field");
            instance.web.form.ReinitializeWidgetMixin.initialize_field.call(this);
            var self = this;
            self.on("change:order_lines", self, self.initialize_content);
            self.on("change:template_id", self, self.tmp_initialize_content);
            self.on("change:value_filter_id", self, self.initialize_content);	    
            lastValidTemplate = self.get("template_id");
        },
	
	tmp_initialize_content: function()
	{
	    var self = this;
	    if(!self.initialized)
	    {
	      self.update_quants();
	      self.initialized = true;
	    }
	    if(!self.get("template_id"))
	    {
	      self.initialized = false;
	    }
	    self.initialize_content();
	    if(self.edited == true)
	    {
	      self.$('[name="submit"]').attr( "disabled", false );
	      self.$('[name="annulla"]').attr( "disabled", false );	      
	    }
	},
		
        initialize_content: function() 
    	{
 //           window.alert("initialize_content");
            QWeb = instance.web.qweb;
            _t = instance.web._t;
            num_dims = 0;
            types = [];
	    attribute_names = [];
            rows = [];
            rows_name = [];
            columns = [];
            columns_name = [];
            q_products = [];
            t_products = [];
            products_id = [];
            products_qty = [];
	    products_price = [];			/**/
	    copied_row = [];				
	    copied_price = [];				/**/
	    to_sync = [];	    
	    lock = false;	    
            stock_quant = new instance.web.Model("stock.quant");
            var product_template = new instance.web.Model("product.template");
	    var product_product = new instance.web.Model("product.product");
	    
            var self = this;            
//            self.update_quants();            
            if (!self.get("template_id"))
            {	
            	self.num_dims = num_dims;
            	self.$el.html(QWeb.render("purchase_product_variant_grid.qtyWidget", {widget: self}));
            	return;           
            }
            
            this.destroy_content();     

            return this.render_drop.add(product_template.call("get_template_dimension_count", [self.get("template_id"),self.get("value_filter_id")]).then(function(count) 
            {
            	if(count==false) return;
            	num_dims = count;
            	if(count<1 || count>2)
            	{
            		self.columns = columns;
            		self.columns_name = columns_name;
			self.columns_lenght = columns.length;
            		self.rows = rows;
            		self.rows_name = rows_name;
			self.attribute_names = attribute_names;
            		self.products_id = products_id;
            		self.products_qty = products_qty;
			self.products_price = products_price;		/**/
			self.copied_row = copied_row;			
			self.copied_price = copied_price;		/**/
			self.to_sync = to_sync;				
			self.lock = lock;
            		self.num_dims = 0;
            		self.display_data();
			self.display_icons();
            		window.alert("Hai selezionato un template non valido!");            		
            		return;
            	}
            	lastValidTemplate = self.get("template_id");
            	product_template.call("get_template_dimension", [self.get("template_id"),self.get("value_filter_id")]).then(function(result) 
            	{
                	if(result==false) return;
            		types = result;
			attribute_names[0] = types[0][1];
            		product_template.call("get_dimension_options", [self.get("template_id"),types[0][0]]).then(function(result) 
            		{
                    	if(result==false) return;
            			var t_columns = result;
            			for(var i=0;i<t_columns.length;i++)
            			{
            				columns[i]=t_columns[i][0];
            				columns_name[i]=t_columns[i][1];
            			}
            			
            			//CALCOLO LE QUANTITA' A PARTIRE DALLE LINEE GIA' IN ORDINE
            			//self.update_quants();
            			xyz = self.field_manager.get_field_value("order_line");
            			q_products = new Array();
            			q_id_products = new Array();
            			j = 0;
            			for(i=0;i<xyz.length;i++)
            			{
            				if(xyz[i][2]!=false)
            				{
            					q_products[j]= new Array();
            					if(_.isObject(xyz[i][2]["product_id"]))
            					{
            						q_products[j][0]=xyz[i][2]["product_id"][0];
            					}
            					else 
            					{
            						q_products[j][0]=xyz[i][2]["product_id"];            						
            					}			
            					q_products[j][1]=xyz[i][2]["product_qty"];
						q_products[j][2]=xyz[i][2]["price_unit"];		/**/						
            					j++;
            				}           		
            			}

    					product_template.call("get_product_list", [self.get("template_id"),self.get("value_filter_id")]).then(function(result)
        				{
    	                	if(result==false) return;
    						t_products = result;
    						if(num_dims == 2)
	                		{
						attribute_names[1] = types[1][1];
		                		product_template.call("get_dimension_options", [self.get("template_id"),types[1][0]]).then(function(result) 
		            			{
		                        		if(result==false) return;
		                    			var t_rows = result;					
		                    			for(i=0;i<t_rows.length;i++)
		                    			{
		                    				rows[i]=t_rows[i][0];
		                    				rows_name[i]=t_rows[i][1];
		                    			}
		                            	products_id = new Array();
		                            	products_qty = new Array();
						products_price = new Array();			/**/

		                            	for(i=0;i<rows.length;i++)
		                            	{
		                            		products_id[i] = new Array();
		                            		products_qty[i] = new Array();
							products_price[i] = new Array(); 	/**/
		                            		
		                            		for(j=0;j<columns.length;j++)
		                            		{
		                            			products_id[i][j]=null;
		                            			products_qty[i][j]=0;
								products_price[i][j]=0;		/**/
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
							if(index_r<0)
							  continue;
							if(index_c<0)
							  continue;
													  
							products_id[index_r][index_c]=t_products[i][0];
							
		                            		var pr_qty = 0;
							var pr_prc = 0;				/**/
		                            		for(j=0;j<q_products.length;j++)
		                            		{
		                            			if(q_products[j][0]== t_products[i][0])
		                            			{
		                            				pr_qty+= q_products[j][1];
									pr_prc+= q_products[j][2];
		                            			}
		                            		}
		                            		products_qty[index_r][index_c]=pr_qty;
							products_price[index_r][index_c]=pr_prc;
		                            	}			                            	
    			                		self.columns = columns;
    			                		self.columns_name = columns_name;
							self.columns_lenght = columns.length;
				                		self.rows = rows;
				                		self.rows_name = rows_name;
								self.attribute_names = attribute_names;
				                		self.products_id = products_id;
				                		self.products_qty = products_qty;
								self.products_price = products_price;	/**/
								self.copied_row = copied_row;
								self.copied_price = copied_price;	/**/
								self.to_sync = to_sync;	
								self.lock = lock;
				                		self.num_dims = num_dims;
				                		self.display_data();
								self.display_icons();
		            			}); 
	                		}
	                		else
	                		{
                				rows[0]=-1;
                				rows_name[0]=" ";
                    			
	                			products_id = new Array();
                            	products_qty = new Array();
				products_price = new Array();

                        		products_id[0] = new Array();
                        		products_qty[0] = new Array();
					products_price[0] = new Array();
                        		
                        		for(var j=0;j<columns.length;j++)
                        		{
                        			products_id[0][j]=null;
                        			products_qty[0][j]=0;
						products_price[0][j]=0;
                        		}

                            	for(i=0; i<t_products.length;i++)
                            	{
                            		var index_c = _.indexOf(columns, t_products[i][1],false);
                            		products_id[0][index_c]=t_products[i][0];
                            		
                            		var pr_qty = 0;
					var pr_prc = 0;
                            		for(j=0;j<q_products.length;j++)
                            		{
                            			if(q_products[j][0]== t_products[i][0])
                            			{
                            				pr_qty+= q_products[j][1];
							pr_prc+= q_products[j][2];
                            			}
                            		}
                            		products_qty[0][index_c]=pr_qty;
					products_price[0][index_c]=pr_prc;
                            	}
		                		self.columns = columns;
		                		self.columns_name = columns_name;
						self.columns_lenght = columns.length;
		                		self.rows = rows;
		                		self.rows_name = rows_name;
						self.attribute_names = attribute_names;
		                		self.products_id = products_id;
		                		self.products_qty = products_qty;
						self.products_price = products_price;		/**/
						self.copied_row = copied_row;
						self.copied_price = copied_price;		/**/
						self.to_sync = to_sync;		
						self.lock = lock;
		                		self.num_dims = num_dims;
		                		self.display_data();
						self.display_icons();
	                		}
        				});          			
            		});           		
        		});
            }));            
    	},
        destroy_content: function() 
        {
//            window.alert("destroy_content");
            if (this.dfm) 
            {
                this.dfm.destroy();
                this.dfm = undefined;
            }
        },
        display_data: function() 
        {   
//        	window.alert("display_data");
        	var self = this;
    		self.$el.html(QWeb.render("purchase_product_variant_grid.qtyWidget", {widget: self}));
		
		self.$('[name="submit"]').click(function()
		{
		    setTimeout(function(){
			self.update_quants();	
			self.edited = false;
			self.$('[name="submit"]').attr( "disabled", true );
			self.$('[name="annulla"]').attr( "disabled", true );
			self.field_manager.set_values({saved: true}); 
		    }, 700);		  
		});
		self.$('[name="annulla"]').click(function()
		{
		    self.query_quants();	
		    self.edited = false;
		    self.$('[name="submit"]').attr( "disabled", true );
		    self.$('[name="annulla"]').attr( "disabled", true );
		    self.field_manager.set_values({saved: true});
		});		
		
            _.each(self.rows, function(row) {
                _.each(self.columns, function(column) {
                	if (!self.get('effective_readonly')) 
                	{
				if (self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)] > 0)
				{
					self.get_box(rows_name[_.indexOf(rows,row)], columns_name[_.indexOf(columns,column)]).attr( "class", "oe_purchase_order_grid_input_focused" );
				}
				self.get_box(rows_name[_.indexOf(rows,row)], columns_name[_.indexOf(columns,column)]).val(self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]).change(function(){
				if (self.lock)
				{
				    $(this).val(self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]);
				    return;
				}	                        
				var num = $(this).val();
	                        if (isNaN(num) || num<0)
	                        {
	                        	$(this).val(self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]);
	                        }
	                        else
	                        {
					self.lock = true;
					self.edited = true;
					self.$('[name="submit"]').attr( "disabled", false );
					self.$('[name="annulla"]').attr( "disabled", false );
					self.field_manager.set_values({saved: false});				  
	                        	var Num = Number(num);                        	
	                        	if(Num==0)
	                        	{
	                        		$(this).val(0);	
						$(this).attr( "class", "oe_purchase_order_grid_input" );
	                        	}
	                        	else
					{
						$(this).attr( "class", "oe_purchase_order_grid_input_focused" );  
					}
	                        	tmpRow = {
	                        	           'product_qty':Num,
	                        	           'product_id' :products_id[_.indexOf(rows,row)][_.indexOf(columns,column)],
	                        	           'state' : self.get("state")              	           
	                        			 };
	                        	products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]=Num;
	                        	self.display_totals();
	                        	new instance.web.Model("purchase.order.line").call("onchange_product_id", [new Array(),self.field_manager.get_field_value("pricelist_id"), tmpRow["product_id"], tmpRow["product_qty"], false, self.field_manager.get_field_value("partner_id"), self.field_manager.get_field_value("date_order"), self.field_manager.get_field_value("fiscal_position"), false, "", false, self.get("state")]).then(function(result)
	                            {	
	        //                		window.alert(JSON.stringify(result));
	        //                		window.alert(JSON.stringify(result["value"]));
	                            	if("warning" in result && tmpRow["product_qty"]!=0)
	                            	{
	                            		if("title" in result["warning"] && "message" in result["warning"])
	                            		{
	                            			window.alert(result["warning"]["message"]);                            	
	                            		}
	                            	}
	                            	tmpRes=
	                            	{
	                     	           'product_qty':tmpRow["product_qty"],
	                     	           'product_id' :tmpRow["product_id"],
	                     	           'price_unit' : result["value"]["price_unit"],
	                     	           'date_planned': result["value"]["date_planned"],
	                     	           'taxes_id' : [[6,false,result["value"]["taxes_id"]]],
	                     	           'state' : self.get("state"),
	                     	           'product_uom':result["value"]["product_uom"],
	                     	           'name':result["value"]["name"]
	                            	}                         	
	                            	if(tmpRes['state']=='sent')
					{
					  tmpRes['state']='draft';
					}
					if(typeof(result["value"]["uos_qty"])!=undefined)
					{
					  tmpRes['uos_qty'] = result["value"]["uos_qty"];
					}
					if(typeof(result["value"]["uos_id"])!=undefined)
					{
					  tmpRes['uos_id'] = result["value"]["uos_id"];
					}
	                            	self.sync(tmpRes);
					products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]=Num;
					products_price[_.indexOf(rows,row)][_.indexOf(columns,column)]=tmpRes['price_unit'];
	                        	self.display_totals();
					self.lock = false;					
	                            });
	                        }                    
	                	});
                	}
                	else 
                	{
			  self.get_box(rows_name[_.indexOf(rows,row)], columns_name[_.indexOf(columns,column)]).html(self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)]);
			  if (self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)] > 0)
			  {
			    self.get_box(rows_name[_.indexOf(rows,row)], columns_name[_.indexOf(columns,column)]).attr( "class", "oe_purchase_order_grid_box_focused" );
			  }
			  
			}
			product_product.call("get_active", [self.products_id[_.indexOf(rows,row)][_.indexOf(columns,column)]]).then(function(check)
			{
			  if (!check)
			  {
			      self.get_box(rows_name[_.indexOf(rows,row)], columns_name[_.indexOf(columns,column)]).attr( "disabled", "True" );			  
			  }
			});			
                });
            });
            self.display_totals(); 
        },
        get_box: function(row, column) {
            return this.$('[data-row="' + row + '"][data-column="' + column + '"]');
        },
        get_copy: function(row) {
            return this.$('[copy="' + row + '"]');
        },	
        get_paste: function(row) {
            return this.$('[paste="' + row + '"]');
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
  //          window.alert("display_totals");
        	var self = this;
        	var column_sum = _.map(_.range(self.columns.length), function() { return 0 });
		var column_sum_price = _.map(_.range(self.columns.length), function() { return 0 });		/**/
        	var super_tot = 0;
		var super_tot_price = 0;		/**/
        	_.each(self.rows, function(row) {
        		var row_sum = 0;
			var row_sum_price = 0;		/**/
                _.each(self.columns, function(column) {
                	var sum = self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)];
			var sum_price = self.products_price[_.indexOf(rows,row)][_.indexOf(columns,column)];	/**/
                	super_tot+=sum;
			super_tot_price+=sum_price*sum;		/**/
                	row_sum+=sum;
			row_sum_price+=sum_price*sum;		/**/
                	column_sum[_.indexOf(columns,column)]+=sum;
			column_sum_price[_.indexOf(columns,column)]+=sum_price*sum;			/**/
                });
		if (self.get("show_totals"))
		  self.get_row_total(rows_name[_.indexOf(rows,row)]).html(row_sum.toString()+'/'+row_sum_price.toFixed(2).toString()+'€'); /*MODIFICATA*/
		else
		  self.get_row_total(rows_name[_.indexOf(rows,row)]).html(row_sum.toString()); /*MODIFICATA*/		
		  
		  
                _.each(self.columns, function(column) {
		  
		    if (self.get("show_totals"))
		      self.get_column_total(columns_name[_.indexOf(columns,column)]).html(column_sum[_.indexOf(columns,column)].toString()+'/'+column_sum_price[_.indexOf(columns,column)].toFixed(2).toString()+'€');		/*MODIFICATA*/
		    else
		      self.get_column_total(columns_name[_.indexOf(columns,column)]).html(column_sum[_.indexOf(columns,column)].toString()); /*MODIFICATA*/
                });
		if (self.get("show_totals"))	  
		  self.get_super_total().html(super_tot.toString()+'/'+super_tot_price.toFixed(2).toString()+'€');		/*MODIFICATA*/
		else
		  self.get_super_total().html(super_tot.toString());		/*MODIFICATA*/
            });                
        },
        display_icons: function()
        {
//  		window.alert("display_icons");
        	var self = this;
        	_.each(self.rows, function(row) {
        		var row_sum = 0;
			self.get_copy(rows_name[_.indexOf(rows,row)]).click(function() 
			{
			    while(self.to_sync.length > 0) {
			      self.to_sync.pop();
			    }		    
			    self.copied_row = [];
			    self.copied_price = [];
			    for(i=0;i<columns.length;i++)
			    {
				self.copied_row[i]=self.products_qty[_.indexOf(rows,row)][i];
				self.copied_price[i]=self.products_price[_.indexOf(rows,row)][i];
			    }
			});
			self.get_paste(rows_name[_.indexOf(rows,row)]).click(function() 
			{
			  if(self.copied_row != null && self.copied_price != null && self.copied_row.length > 0 && self.copied_price.length > 0) 
			  {		    
			    for(i=0;i<columns.length;i++)
			    {
				self.products_qty[_.indexOf(rows,row)][i]=self.copied_row[i];
				self.products_price[_.indexOf(rows,row)][i]=self.copied_price[i];
			    }
			    _.each(self.columns, function(column) 
			    {
				tmpRow = {
					    'product_qty':self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)],
					    'product_id' :products_id[_.indexOf(rows,row)][_.indexOf(columns,column)],
					    'state' : self.get("state")              	           
				};

				new instance.web.Model("purchase.order.line").call("onchange_product_id", [new Array(),self.field_manager.get_field_value("pricelist_id"), tmpRow["product_id"], tmpRow["product_qty"], false, self.field_manager.get_field_value("partner_id"), self.field_manager.get_field_value("date_order"), self.field_manager.get_field_value("fiscal_position"), false, "", false, self.get("state")]).then(function(result)
				{	
		      //  		window.alert(JSON.stringify(result));
		      //  		window.alert(JSON.stringify(result["value"]));
					tmpRes=
					{
					    'product_qty':self.products_qty[_.indexOf(rows,row)][_.indexOf(columns,column)],
					    'product_id' :products_id[_.indexOf(rows,row)][_.indexOf(columns,column)],
					    'price_unit' : result["value"]["price_unit"],
					    'date_planned': result["value"]["date_planned"],
					    'taxes_id' : [[6,false,result["value"]["taxes_id"]]],
					    'state' : self.get("state"),
					    'product_uom':result["value"]["product_uom"],
					    'name':result["value"]["name"]
					}
					if(tmpRes['state']=='sent')
					{
					  tmpRes['state']='draft';
					}
					self.to_sync.push(tmpRes);
				});							
				
			    });
			    self.display_data();
			    
			    self.edited = true;
			    self.$('[name="submit"]').attr( "disabled", false );
			    self.$('[name="annulla"]').attr( "disabled", false );
			    self.field_manager.set_values({saved: false});			    
			    
			    setTimeout(function(){
				self.buffered_sync();
			    }, 1500);			    
			  }
			});
            });	  
	},
        sync: function(record) {
//            window.alert("sync - "+JSON.stringify(record));
            var self = this;
	    var ops = self.get("order_lines");
            self.set({order_lines: this.generate_o2m_value(record)});	    
//            self.update_quants();
        },
	buffered_sync: function() {
//	    window.alert("buffered_sync");
	    var self = this;
	    self.record = self.get("order_lines");    
	    for(t=0;t<self.to_sync.length;t++)
	    { 
//	      window.alert("record: "+JSON.stringify(self.to_sync[t]));
	      for(i=0; i<self.record.length;i++)
	      {   
		if(_.isObject(self.record[i]["product_id"]))
		{
		  if(self.record[i]['product_id'][0]==to_sync[t]['product_id'])
		  {
		    self.record.splice(i,1);
		    i--;
		  }
		}
		else 
		{
		  if(self.record[i]['product_id']==to_sync[t]['product_id'])
		  {
		    self.record.splice(i,1);	    
		    i--;
		  }            						
		}
	      }	      
	      if(self.to_sync[t].product_qty>0)
		self.record.push(self.to_sync[t]);
//	      window.alert("righe: "+JSON.stringify(self.record));	      
	    }
	    
	    self.set({order_lines: self.record});
//            self.update_quants();
	    self.display_icons();
	},	
        generate_o2m_value: function(record) {
 //           window.alert("generate_o2m_value");
            var self = this;
            
            var ops = self.get("order_lines");
            for(i=0; i<ops.length;i++)
            {   
            	//Setto il field state dei campi già presenti (potrebbero non averlo)
            	ops[i]['state']= self.get("state");
		if(ops[i]['state']=='sent')
		{
		  ops[i]['state']='draft';
		}
            	//Se sto inserendo un articolo già inserito, rimuovo tutte le altre righe con lo stesso product_id
				if(_.isObject(ops[i]["product_id"]))
				{
	            	if(ops[i]['product_id'][0]==record['product_id'])
	            	{
	            		ops.splice(i,1);
	            		i--;
	            	}
				}
				else 
				{
	            	if(ops[i]['product_id']==record['product_id'])
	            	{
	            		ops.splice(i,1);
	            		i--;
	            	}            						
				}
            }
            // Le righe con quantità 0 o meno non devono essere mostrate
            if(record["product_qty"]>0)
            {            
            	ops.push(record);    
            }
            return ops;
        }
    });

    instance.web.form.custom_widgets.add('purchase_grid_widget', 'instance.purchase_product_variant_grid.qtyWidget');

};

