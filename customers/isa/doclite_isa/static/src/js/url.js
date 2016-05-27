openerp.doclite_isa = function(instance, m) {

    var _t = instance.web._t,
        QWeb = instance.web.qweb;
    instance.web.Sidebar.include({
        redraw: function() {
            var self = this;
            this._super.apply(this, arguments);

            self.$el.find('.oe_sidebar_add_attachment').after(QWeb.render('UploadUrlDocliteItem', {widget: self}))
            self.$el.find('.oe_sidebar_upload_doclite').on('click', function (e) {
                self.on_upload_doclite();
            });
            self.$el.find('.oe_sidebar_add_attachment').after(QWeb.render('FindUrlDocliteItem', {widget: self}))
            self.$el.find('.oe_sidebar_find_doclite').on('click', function (e) {
                self.on_find_doclite();
            });
        },
        on_upload_doclite: function() {
            var self = this;

            // Find their matching names
            var dataset = new instance.web.DataSetSearch(self, 'doclite.server', self.session.context, []);
            dataset.read_slice(['ip_address', 'port', 'base_path']).done(function(result) {
                _.each(result, function(v, k) {
                    var user = new instance.web.DataSetSearch(self, 'res.users', self.session.user_context, [
                        ['id', '=', self.session.uid]
                    ]);

                    return user.read_slice(['id']).then(function (res) {
                        if (_.isEmpty(res) )
                            return;

                        var url = 'http://' + v.ip_address + ':' + v.port + v.base_path
    
                        var view = self.getParent();
                        var ids = ( view.fields_view.type != "form" )? view.groups.get_selection().ids : [ view.datarecord.id ];
                        if( !_.isEmpty(ids) ){
            
                            //alert(url + '/doclite/web/app.php/doclite/OE/upload/' + self.session.uid + '/' + view.dataset.model + '/' + ids[0] + '');
                            window.open(url + 'doclite/OE/upload/' + self.session.uid + '/' + view.dataset.model + '/' + ids[0] + '', '_blank');
                            return;
                        };

                    });
                });
            });

        },
        on_find_doclite: function() {
            var self = this;

            // Find their matching names
            var dataset = new instance.web.DataSetSearch(self, 'doclite.server', self.session.context, []);
            dataset.read_slice(['ip_address', 'port', 'base_path']).done(function(result) {
                _.each(result, function(v, k) {
                    var user = new instance.web.DataSetSearch(self, 'res.users', self.session.user_context, [
                        ['id', '=', self.session.uid]
                    ]);

                    return user.read_slice(['id']).then(function (res) {
                        if (_.isEmpty(res) )
                            return;

                        var url = 'http://' + v.ip_address + ':' + v.port + v.base_path ;
    
                        var view = self.getParent();
                        var ids = ( view.fields_view.type != "form" )? view.groups.get_selection().ids : [ view.datarecord.id ];
                        if( !_.isEmpty(ids) ){
            
                            //alert(url + '/doclite/web/app.php/doclite/OE/find/' + self.session.uid + '/' + view.dataset.model + '/' + ids[0] + '');
                            window.open(url + 'doclite/OE/find/' + self.session.uid + '/' + view.dataset.model + '/' + ids[0] + '', '_blank');
                            return;
                        };

                    });
                });
            });

        }
    });
};
