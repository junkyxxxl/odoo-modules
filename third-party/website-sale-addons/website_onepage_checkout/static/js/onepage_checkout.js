$(document).ready(function () {
	function getPostAddressFields(elms, data) 
	{
	    elms.each(function(index) 
	    {
	      data[$(this).attr('name')] = $(this).val();
	    });
    	return data;
	}

	$('.btn-1').on('click', function(ev)
	{
		var billingElms  = $('#onepage_billing input, #onepage_billing select')
	      , shippingElms = $('#onepage_shipping input, #onepage_shipping select')
	      , data         = {};

	    data = getPostAddressFields(billingElms, data);

	    if ($('#onepage_billing select[name=shipping_id]').val() == '-1') {
	      data = getPostAddressFields(shippingElms, data);
	    }

	    $('.oe_website_sale_onepage .has-error').removeClass('has-error');
	    console.log(data);

	    openerp.jsonRpc('/shop/onepage/confirm_order', 'call', data)
	      .then(function (result) 
	      { 
	      	console.log(result);
	        if (result) 
	        {
	        	if (result.success) 
	        	{
	            	$('.panel-1').attr('class', '').addClass('panel panel-success panel-1');
	            	$(".panel-1").next().find('a.collapsed').removeClass('hide_class').trigger("click");
	            }
	        	else if (result.errors) 
	        	{
	        		$('.panel-1').attr('class', '').addClass('panel panel-danger panel-1');
	        		$(".panel-1").next().find('a.collapsed').addClass('hide_class')
	            	for (var key in result.errors) 
	            	{
	            		if ($('.oe_website_sale_onepage input[name=' + key + ']').length > 0) 
	            		{
	                		$('.oe_website_sale_onepage input[name=' + key + ']').parent().addClass('has-error');
	            		} 
	            		else if ($('.oe_website_sale_onepage select[name=' + key + ']').length > 0) 
	            		{
	                		$('.oe_website_sale_onepage select[name=' + key + ']').parent().addClass('has-error');
	            		}
	            	}
	        	}
	        } 
	        else 
	        {
	          window.location.href = '/shop';
	        }
	    });
	});

	$('.btn-2').on('click', function(e)
	{
		$('.panel-2').attr('class', '').addClass('panel panel-success panel-2');
		$("a.c3").removeClass('hide_class').trigger("click");
	});

	// when choosing an delivery carrier, update the total prices
    $('.onepage_delivery').on('click', function (ev) 
    {
		var carrierId = $(ev.currentTarget).val();
		openerp.jsonRpc('/shop/checkout/delivery_option', 'call', {'carrier_id': carrierId})
		.then(function (result) 
		{
			console.log(result);
			if (result) 
			{
				if (result.success) 
				{
					if (result.order_total) 
					{
						$('#order_total .oe_currency_value').text(result.order_total);
						$('#onepage_total .oe_currency_value').text(result.order_total);
						var total_ammount=(result.order_total).toString().replace(',', '');
						$('.oe_website_sale').find('input[name="amount"]').val(total_ammount);
					}
					if (result.order_total_taxes) 
					{
						$('#order_total_taxes .oe_currency_value').text(result.order_total_taxes);
						$('#onepage_taxes .oe_currency_value').text(result.order_total_taxes);
					}
					if (result.order_subtotal) 
					{
						$('#order_subtotal .oe_currency_value').text(result.order_subtotal);
						$('#onepage_subtotal .oe_currency_value').text(result.order_subtotal);
					}
					if (result.order_total_delivery) 
					{
						$('#order_delivery .oe_currency_value').text(result.order_total_delivery);
						$('#onepage_delivery .oe_currency_value').text(result.order_total_delivery);

					}
				}
			} 
			else 
			{
				window.location.href = '/shop';
			}
		});
		
	});
});
