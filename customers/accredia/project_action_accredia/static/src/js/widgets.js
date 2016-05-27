openerp.project_action_accredia = function (instance) {

    instance.project_action_accredia.DocliteUrlCloseWidget = instance.doclite.DocliteUrlWidget.extend({
        template: 'FieldUrl',
        initialize_content: function() {
            this._super();
            var $button = this.$el.find('button');
            $button.click(this.on_button_clicked);
            var $elem = this.$el;
            $elem.click(this.on_elem_clicked);
            this.setupFocus($button);
        },
        on_button_clicked: function() {
            if (!this.get('value')) {
                this.do_warn(_t("Resource Error"), _t("This resource is empty"));
            } else {
                var url = $.trim(this.get('value'));
                if(/^www\./i.test(url))
                    url = 'http://'+url;
                window.open(url);
            }
        },
        on_elem_clicked: function() {
            this.getParent().getParent().check_exit();
        }
    });
    instance.web.form.widgets.add('nameandurlclose', 'instance.project_action_accredia.DocliteUrlCloseWidget');

};
