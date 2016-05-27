$(document).ready(function(){
  
    $(".wk_voucher").click(function(){
       								
      	
       secret_code = $("#voucher_13d_code").val(); 
       
       
       openerp.jsonRpc('/website/voucher/', 'call', {'secret_code': secret_code})
                  .then(function (result) {
                  		if(result['status'])
                      {
       							     
                         $(".success_msg").css('display','block')
                         $(".success_msg").html(result['message']); 
                         $(".success_msg").fadeOut(3000);
                         $(location).attr('href',"/shop/cart");
                  		}
                      else{
                        $(".error_msg").css('display','block')
                        $(".error_msg").html(result['message']); 
                        $(".error_msg").fadeOut(5000);
                      // setTimeout(function(){
                      //      $(".error_msg").css('display','none')
                      //      $("#voucher_13d_code").val('');
                      // }, 2000);
                    }
                  	
                   }).fail(function (err) {
                      // console.error(err);
                      //  alert('Connection Error. Try again later !!!!'); 
                      $(".error_msg").css('display','block')
                      $(".error_msg").html('Unknown Error ! Please try again later.'); 
                      $(".error_msg").fadeOut(5000);       
                    });
        
        
    });
     var wk_product_id = parseInt($('.wk_def_pro_id').attr('id'),10);
    $('.oe_website_sale').each(function () 
	  {

        var oe_website_sale = this;
        $(oe_website_sale).find(".oe_cart input.js_quantity").each(function ()
        {
        	
            var $input = $(this);
            var $dom = $(this).closest('tr');
            var product_id = parseInt($(this).data('product-id'),10);
            if(product_id==wk_product_id)
            {
                $dom.find('div.oe_website_spinner').hide();
                $dom.find('span.voucher-remove').show();

            }
        });
    });
});