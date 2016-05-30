(function(){
  'use strict';
  var website = openerp.website;
  
//var ajax = require('web.ajax');
//var core = require('web.core');
//var animation = require('web_editor.snippets.animation');
//var website = require('website.website');
//
//var _t = core._t;
//var qweb = core.qweb;

website.snippet.animationRegistry.js_get_objects = website.snippet.Animation.extend({
//animation.registry.js_get_objects = animation.Class.extend({  
    selector : ".js_get_objects",

    start: function(){
      this.redrow();
    },
    stop: function(){
      this.clean();
    },

    redrow: function(debug){
      this.clean(debug);
      this.build(debug);
    },

    clean:function(debug){
      this.$target.empty();
    },
    
    
    apply_carousel:function(debug){
    	var self = this;
    	var carouselCount = 0;
  	  	$(".owl-carousel").each(function () {
  			$(this).attr("id", "owl-carousel" + carouselCount);
  				$('#owl-carousel' + carouselCount).owlCarousel({
  							   items:self.$target.data("objects_in_slide"),
  							   loop:true,
  							   lazyLoad : true,
  							   dots:false,
  							   navigation:true,
  							   pagination:false,
  							   margin:20,
  							   navigationText:['<i class="fa fa-angle-left fa-1x"></i>','<i class="fa fa-angle-right fa-1x"></i>'],
  							   itemsDesktop : [1199,3],
  							   itemsDesktopSmall : [979,2],
  							   itemsMobile : [767,1],
  							   responsiveClass:true,
  				        });
  				        carouselCount++;
  				    });
    },
    
    build: function(debug){
      var self     = this,
      limit    = self.$target.data("objects_limit"),
      in_row    = self.$target.data("objects_in_row"),
      filter_id  = self.$target.data("filter_by_filter_id"),
      objects_in_slide = self.$target.data("objects_in_slide"),
      object_name = self.$target.data("object_name"),
      custom_controller = self.$target.data("custom_controller"),
      template = self.$target.data("template");
      
      self.$target.attr("contenteditable","False");

      if(!objects_in_slide)objects_in_slide = 8;
      if(!limit)limit = 3;
      if(!filter_id)filter_id = false;
      if(!template) template = 'snippet_object_carousel_73lines.media_list_template';
	  var rpc_end_point = '/snippet_object_carousel_73lines/render';
      if (custom_controller == '1'){
    	  rpc_end_point='/snippet_object_carousel_73lines/render/'+object_name;
      };
      console.log("AAAAAAAAa-------------------",rpc_end_point,template,filter_id,objects_in_slide,limit,object_name,in_row);
      openerp.jsonRpc(rpc_end_point, 'call', {
        'template': template,
        'filter_id': filter_id,
        'objects_in_slide' : objects_in_slide,
        'limit': limit,
        'object_name':object_name,
        'in_row':in_row,
      }).then(function(objects) {
    	  $(objects).appendTo(self.$target);
    	  self.apply_carousel(objects);
      }).then(function(){
    	  self.loading(debug);
      }).fail(function(e) {
        return;
      });
    },
    
    loading: function(debug){
    	//function to hook things up after build    	
    }
    
});

})();