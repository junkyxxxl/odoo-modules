openerp.barcode_extension = function(instance, local){

    var module = instance.stock;
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;

    module.PickingEditorWidget = module.PickingEditorWidget.extend({
        //Ridefinisco la funzione blink per autoposizionare lo scroll della pagina
        blink: function(op_id){
            var $op_id = op_id,
                that = this,
                _super = this._super.bind(this);
            //cambio colore alla riga se non ha una classe specifica
            this.$('.js_pack_op_line[data-id="'+op_id+'"]').css("background-color", "#abbafc");
            $('body, html').animate({
                scrollTop: that.$('.js_pack_op_line[data-id="'+op_id+'"]').offset().top -
                                ($(window).height()-$('.js_pack_op_line[data-id="'+op_id+'"]').outerHeight()-8)
            }, {
                duration: 500,
                complete: function() {
                    that.$('.js_pack_op_line[data-id="'+op_id+'"]').find('i[data-role=show-pack]').trigger('click');
                    return _super($op_id);
                }
            });
        },
        //Ridefinisco la funzione get_rows per modificare i colori ed emettere un suono in caso
        //di quantità utilizzata > di quantità richiesta
        get_rows: function(){
            rows=this._super();
            var packoplines = this.getParent().packoplines,
                self= this,
                number_decimal = this.getParent().number_decimal;
            _.each(rows, function(row){
                /**
                 * Aggiungo l'eventuale informazione del package_id (l'attuale package_id in realtà
                 * è riferito al result_package_id e cioè al pacco creato direttamente da interfaccia
                 * barcode)
                **/
                if(row.cols.package_id === undefined){
                    //Cerco l'id su packoplines
                    packopline = _.findWhere(packoplines, {id: row.cols.id});
                    row.cols.from_package_id = packopline.package_id[0] || undefined;
                }else{
                    row.cols.from_package_id = undefined;
                }
                //Cerco l'id se il package_id delle righe non è valorizzato, altrimeni si tratta della riga
                //caricata contenente l'informazioni sul pacco creato da interfaccia barcode
                if(number_decimal){
                    row.cols.rem = self.fixedDecimal(row.cols.rem, number_decimal);
                    row.cols.qty = self.fixedDecimal(row.cols.qty, number_decimal);
                }
                if(row.classes == 'danger '){
                    row.classes = 'more_danger ';
                    //Emissione audio per quantità richiesta maggiore di pianificata se ho scansionato il prodotto
                    //specifico e se lo prevede la configurazione
                    if (self.getParent().last_product_id === row.cols.product_id &&
                        self.getParent().play_sound_larger_amount){
                        audio = $('audio#gtqty').get()[0];
                        audio.play();
                    }
                }
            });
            return rows;
        },
        load_package_content: function(package_id){

            var load_content = function(package_id){
                var package_deffered = $.Deferred();
                new openerp.Model('stock.quant.package')
                            .query(['quant_ids'])
                            .filter([['id', '=', package_id]])
                            .all()
                            .then(function(opackage){
                                new openerp.Model('stock.quant')
                                .call('read',[opackage[0].quant_ids, []])
                                .then(function(quants){
                                    package_deffered.resolve(quants);
                                });
                            });
                return package_deffered.promise();
            }

            return load_content(package_id);
        },
        //Funzione per sistemare la visualizzazione dei decimali con javascript.
        fixedDecimal: function(amount, decimals){
            if(typeof(amount) != 'number') return amount;
            amount = round_di(amount,decimals).toFixed(decimals);
            amount = parseFloat(amount);
            num_decimal = this.decimalPlaces(amount);
            //amount = openerp.instances[this.session.name].web.format_value(round_di(amount, num_decimal), { type: 'float', digits: [69, num_decimal]});
            return amount;
        },
        decimalPlaces: function(num) {
            var match = (''+num).match(/(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
            if (!match) { return 0; }
            return Math.max(
                0,
                // Number of digits right of decimal point.
                (match[1] ? match[1].length : 0)
                // Adjust for scientific notation.
                - (match[2] ? +match[2] : 0));
        },
        //Ridefinizione funzione check_content_screen per controllo su produzione per impedirechiusura ordine
        //se quantità minime non soddisfatte (comportamento configurabile in configurazione per azienda)
        //Solo se il tipo di picking è uguale a quello impostato in configurazione
        check_content_screen:function(){
            this._super();
            /**
             * Non devo eseguire il blocco di evasione ordine se:
             * - Il picking type è diverso da quello impostato in configurazione OPPURE
             * - Non è settato il flag check_quantity in configurazione OPPURE
             * - E' impostato il force_check_quantity in configurazione
             */
            if (this.getParent().picking_type_id != this.getParent().picking_list_type_id ||
                !this.getParent().check_quantity ||
                this.getParent().force_check_quantity){
                return;
            }
            var self = this,
                check_rows = this.$('.js_pack_op_line:not(.processed):not(.hidden)').map(function(){
                    return {
                        'row_id': $(this).data('id'),
                        'qties': $(this).find('.js_qty').val()
                    }
                }),
                can_finish = true,
                processed = this.$('.js_pack_op_line.processed'),
                container = this.$('.js_pack_op_line.container_head:not(.processed):not(.hidden)');
            //Per ogni riga controllo che la quantità minima sia soddisfatta, altrimenti blocco l'evadi ordine.
            _.each(check_rows,function(row) {
                id = row.row_id;
                original_row = _.find(self.rows, function(item){
                    return item.cols.id == id;
                });
                if(parseInt(row.qties, 10) < parseInt(original_row.cols.qty, 10)) can_finish = false;
            });
            if (!can_finish){
                if (container.length===0){
                    self.$('.js_drop_down').addClass('disabled');
                }
                else {
                    self.$('.js_drop_down').removeClass('disabled');
                }
                if (processed.length === 0){
                    self.$('.js_pick_done').addClass('disabled');
                }
                else {
                    self.$('.js_pick_done').removeClass('disabled');
                }
            }
            else{
                self.$('.js_drop_down').removeClass('disabled');
                self.$('.js_pick_done').removeClass('disabled');
            }
        },
        renderElement: function(){
            var self = this;
            this._super();
            this.$('.js_create_lot').click(function(){
                var op_id = $(this).parents("[data-id]:first").data('id');
                var $lot_modal = self.$el.siblings('#js_LotChooseModal');
                $.blockUI();
                stock_pack_operation = new instance.web.Model('stock.pack.operation');
                stock_pack_operation.call('search_lot', {
                    package_id: op_id
                }).then(function(result){
                    var lots = result.lots;
                    $lot_modal.on('shown.bs.modal', function(){
                        self.$('.js_lot_scan > option').each(function(){
                            if($(this).val() == "") return;
                            $(this).remove();
                        });
                        self.$('.js_lot_scan').select2({
                            placeholder: "Select a state",
                            allowClear: true,
                            tags: lots
                        });
                        self.$('.js_lot_scan').select2('open');
                        $.unblockUI();
                    });
                });
            });
            //Gestione evento per visualizzazione contenuto del pacco.
            this.$('i[data-role=show-pack]').click(function(){ self.getParent().show_pack_id(this); });
        }
    });

    module.PickingMainWidget = module.PickingMainWidget.extend({
        //Ridefinisco la funzione scan per richidere la conferma di aggiunta riga di prodotto in caso di
        //scansione codice a barre non previsto.
        init: function(parent,params){
            this.last_product_id = null;
            var self = this;
            //Reperisco le configurazioni (dall'azienda)
            stock_pack_operation = new instance.web.Model('stock.pack.operation')
            stock_pack_operation.call('get_barcode_configuration').then(function(config_data){
                self.play_sound_larger_amount = config_data.play_sound_larger_amount;
                self.play_sound_article_not_available = config_data.play_sound_article_not_available;
                self.confirmation_article_not_available = config_data.confirmation_article_not_available;
                self.picking_list_type_id = config_data.picking_list_type_id;
                self.check_quantity = config_data.check_quantity;
                self.force_check_quantity = config_data.force_check_quantity;
                self.number_decimal = config_data.number_decimal;
            });
            return this._super(parent, params);
        },
        scan: function(ean){
            var self = this;
            _super = this._super.bind(this);
            var product_visible_ids = this.picking_editor.get_visible_ids();
            stock_pack_operation = new instance.web.Model('stock.pack.operation');
            stock_pack_operation.call('operation_exists', {
                    picking_id: self.picking.id,
                    barcode_str: ean,
                    visible_op_ids: product_visible_ids
            }).then(function(exist){
                    //Se l'articolo esiste oppure non è richiesta la conferma in configurazione richiamo la funzione base
                    if(exist.find || !self.confirmation_article_not_available){
                        //Verifico se devo emettere il suono di articolo non presente in lista
                        if (self.play_sound_article_not_available && !exist.find){
                            audio = $('audio#notExist').get()[0];
                            audio.play();
                        }
                        self.last_product_id = exist.product_id;
                        return _super(ean);
                    }else{
                        self.last_product_id = false;
                        if (self.play_sound_article_not_available){
                            audio = $('audio#notExist').get()[0];
                            audio.play();
                        }
                        $dialog = new instance.web.Dialog(this,{
                                        title: 'Articolo non presente in lista',
                                        buttons: {
                                            Ok: function() {
                                               _super(ean);
                                               $dialog.close();
                                            },
                                            Annulla: function(){
                                                $dialog.close();
                                            }
                                        }
                        },'<div>Premere <code>ok</code> per aggiungere il prodotto.</div>');
                        $dialog.open();
                        $dialog.$buttons.find('span').find('button:contains("Ok")').addClass('btn btn-danger ');
                        $dialog.$buttons.find('span').find('button:contains("Annulla")').addClass('btn btn-default ');
                    }
            });
        },
        scan_product_id: function(product_id,increment,op_id){ //performs the same operation as a scan, but with product id instead
            var self = this;
            this.last_product_id = product_id;
            return new instance.web.Model('stock.picking')
                .call('process_product_id_from_ui', [self.picking.id, product_id, op_id, increment])
                .then(function(result){
                    return self.refresh_ui(self.picking.id);
                });
        },
        //Ridefinizione funzione done per controllo se abilitazione forzatura.
        done: function(){
            var self = this,
                _super = this._super.bind(this);
            //Non richiedo la conferma se il picking type è diverso da quello settato in configurazione o se
            //non è configurata la forzatura
            if(!this.force_check_quantity ||
                this.picking_type_id != this.picking_list_type_id ){
                return _super();
            }
            $dialog = new instance.web.Dialog(this,{
                title: 'Richiesta di conferma',
                buttons:{
                    Conferma: function(){
                        _super();
                        $dialog.close();
                    },
                    Annulla: function(){
                        $dialog.close();
                    }
                }
            },'<div>Confermi evasione ordine con quantità minime non soddisfatte ?</div>');
            $dialog.open();
            $dialog.$buttons.find('span').find('button:contains("Conferma")').addClass('btn btn-danger ');
            $dialog.$buttons.find('span').find('button:contains("Annulla")').addClass('btn btn-default ');
        },
        //Visualizzazione del pacco
        show_pack_id: function(selector){
            var self = this,
                pack_group = $(selector).closest('tr').data('id'),
                tr = $(selector).closest('tr');
            if($(selector).hasClass('fa-minus-square')){
                $(selector).closest('tr').nextAll('tr[data-group_pack='+pack_group+']').remove();
            }else{
                this.picking_editor.load_package_content($(selector).data('package_id')).then(function(result){
                    var s = instance.web.qweb.render('package-content',{
                        'pack_quants': result,
                        'group_id': pack_group
                    });
                    $(tr).after(s);
                });
            }
            this.$(selector).toggleClass('fa-minus-square');
        }
    });

}