odoo.define('snippet_product_carousel_73lines.product_carousel', function (require) {
"use strict";

var ajax = require('web.ajax');
var animation = require('web_editor.snippets.animation');
var rating = require('rating.rating');
var website = require('website.website');
var core = require('web.core');

require('snippet_object_carousel_73lines.object_carousel');


animation.registry.js_get_objects = animation.registry.js_get_objects.extend({

	    roundToHalf: function(value) {
	        var converted = parseFloat(value); // Make sure we have a number
	        var decimal = (converted - parseInt(converted, 10));
	        decimal = Math.round(decimal * 10);
	        if(decimal == 5){
	            return (parseInt(converted, 10)+0.5);
	        }
	        if((decimal < 3) || (decimal > 7)){
	            return Math.round(converted);
	        }else{
	            return (parseInt(converted, 10)+0.5);
	        }
	    },
	
	    loading: function(debug){
	    	var self     = this;
	    	$.when(this._super(debug)).then(function(debug){
	    		var card_list=$.find('.o_rating_star_card');
	    		$(card_list).each(function () {
	    			 var default_value = $(this).find('input').data('default');
	    			 var star_list = $(this).find('i');
	    			 default_value = self.roundToHalf(default_value);
	    			 var index = Math.floor(default_value);
	    			 var decimal = default_value - index;
	    			 $(star_list).removeClass('fa-star fa-star-half-o').addClass('fa-star-o');
	    			 $(this).find("i:lt("+index+")").removeClass('fa-star-o fa-star-half-o').addClass('fa-star');
	    			 if(decimal){
	    				 $(this).find("i:eq("+(index)+")").removeClass('fa-star-o fa-star fa-star-half-o').addClass('fa-star-half-o');
	    			 }
    			 });
	        });
	    }
	});	
});
