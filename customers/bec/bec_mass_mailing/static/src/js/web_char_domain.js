openerp.bec_mass_mailing = function(instance){
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.web.form.FieldCharDomain.include({
        on_click: function(event) {
            event.preventDefault();
            var self = this;
            var model = this.options.model || this.field_manager.get_field_value(this.options.model_field);
            this.pop = new instance.web.form.SelectCreatePopup(this);
            var domain = [];

            domain = instance.web.pyeval.eval('domain', self.get_value());

            this.pop.select_element(
                model, {
                    title: this.get('effective_readonly') ? 'Selected records' : 'Select records...',
                    readonly: this.get('effective_readonly'),
                    disable_multiple_selection: this.get('effective_readonly'),
                    no_create: this.get('effective_readonly'),
                }, domain, this.build_context());
            this.pop.on("elements_selected", self, function(element_ids) {
                if (this.pop.$('input.oe_list_record_selector').prop('checked')) {
                    var search_data = this.pop.searchview.build_search_data();
                    var domain_done = instance.web.pyeval.eval_domains_and_contexts({
                        domains: search_data.domains,
                        contexts: search_data.contexts,
                        group_by_seq: search_data.groupbys || []
                    }).then(function (results) {
			var domain = [["id","in",element_ids]];
			return domain;
                    });
                }
                else {
                    var domain = [["id", "in", element_ids]];
                    var domain_done = $.Deferred().resolve(domain);
                }
                $.when(domain_done).then(function (domain) {	  
                    var domain = self.pop.dataset.domain.concat(domain || []);
                    self.set_value(domain);
                });
            });
        }
    });
}