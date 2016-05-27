$(document).ready(function() {
    
    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;
       
        $(oe_website_sale).on('change', function (ev) {
            var product = $("input[name='product_id']").attr('value');
            $('.wk_hidden_stock').removeClass('wk_show_stock');
            $('#'+product).addClass('wk_show_stock');
            var value = $('#'+product).attr('value');
            var allow = $('#'+product).attr('allow');
            if (value<1)
            {  
                if (allow<1)
                {
                    
                    $('#add_to_cart').removeClass('js_check_product');
                    $('#add_to_cart').attr('disabled','disabled');
                }
                else
                {    
                    
                    $('#add_to_cart').addClass('js_check_product');
                    $('#add_to_cart').removeAttr('disabled');
                    
                }
            }
            else if(value>=1)
            {
                $('#add_to_cart').addClass('js_check_product');
                $('#add_to_cart').removeAttr('disabled');
            }

        });

        var product = $("input[name='product_id']").attr('value');
        $('.wk_hidden_stock').removeClass('wk_show_stock');
        $('#'+product).addClass('wk_show_stock');
        var value = $('#'+product).attr('value');
        var allow = $('#'+product).attr('allow');
        if (value<1)
        {  
            if (allow<1)
            {
                $('#add_to_cart').removeClass('js_check_product');
                $('#add_to_cart').attr('disabled','disabled');

            }
            else
            {    
                $('#add_to_cart').addClass('js_check_product');
            }
        }
        
    });
    
    //Se mi trovo nella wishlist nascondo l'email per la notifica di disponibilita
    if($('.remove_whishlist').length>0){
    	$('div.wk_notify_main').hide();
    	$('.out-of-stock-status').css('margin-top','0px');
    }

});