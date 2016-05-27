$(document).ready(function() 
{
    $('.oe_website_sale').each(function () 
    {
        var oe_website_sale = this;
        $(oe_website_sale).find(".oe_cart input.js_quantity").on("change", function (ev) 
        {
            var $input = $(this);
            var value = parseInt($input.val(), 10);
            var $dom = $(this).closest('tr');
            var line_id = parseInt($input.data('line-id'),10);
            var product_id = parseInt($input.data('product-id'),10);
            openerp.jsonRpc("/shop/cart/update_json/msg", 'call', 
            {
                'line_id': line_id,
                'product_id': parseInt($input.data('product-id'),10),
                'set_qty': value
            })
            .then(function (msg) 
            {
                if(msg)
                {
                    $dom.popover('destroy');
                    $dom.popover
                    ({
                        content:"You are Trying to Add More Than Available Quantity of Product.",
                        title:"WARNING!!",
                        placement:"top",
                        trigger:'focus',
                    });
                    $dom.popover('show'); 
                }
                else
                {
                    $dom.popover('destroy');
                }
                setTimeout(function() {$dom.popover('destroy')},2000);
            });
            
        });
    });

    $(document).on('click','.js_check_product', function(ev)
    {
        var $form = $(this).closest('form');
        var product_id =  parseInt($form.find('input[type="hidden"][name="product_id"]').first().val(),10);
        var add_qty =  parseInt($form.find('input[type="text"][name="add_qty"]').first().val(),10);
        openerp.jsonRpc("/shop/cart/update/msg", 'call', 
            {
                'product_id': product_id,
                'add_qty': add_qty
            })
            .then(function (result) 
            {
                if(result.status=='deny')
                {
                    $form.find('input[type="text"][name="add_qty"]').first().val(result.remain_qty);
                    $('#add_to_cart').popover
                    ({
                        content:"You Already Added All Avalible Quantity of Product in Your Cart, You Can not Add More Quantity.",
                        title:"WARNING!!",
                        placement:"left",
                        trigger:'focus',
                    });
                    $('#add_to_cart').popover('show');
                    setTimeout(function() {$('#add_to_cart').popover('destroy')},2000);

                }
                else
                {
                    $('#add_to_cart').popover('destroy');
                }
            });
    });
    
    $temp = $('.oe_website_sale').find('input[type="text"][name="add_qty"]');

    $temp.on('change', function(ev)
    {
        var $form = $(this).closest('form');
        var product_id =  parseInt($form.find('input[type="hidden"][name="product_id"]').first().val(),10);
        var add_qty =  parseInt($form.find('input[type="text"][name="add_qty"]').first().val(),10);
        openerp.jsonRpc("/shop/cart/update/msg", 'call', 
            {
                'product_id': product_id,
                'add_qty': add_qty
            })
            .then(function (result) 
            {
            	console.log(result);
                if(result.status=='deny')
                {
                    $form.find('input[type="text"][name="add_qty"]').first().val(result.remain_qty);
                    $('.css_quantity').popover
                    ({
                        content:"You Can Not Add More Quantity.",
                        title:"WARNING!!",
                        placement:"top",
                        trigger:'focus',
                    });
                    $('.css_quantity').popover('show');
                    setTimeout(function() {$('.css_quantity').popover('destroy')},2000);

                }
                else
                {
                	$('.css_quantity').popover('destroy');
                }
            });
    });

     $('.fa-shopping-cart').on('click', function(ev)
    {
        var $form = $(this).closest('form');
        var $msg = $form.find('.fa-shopping-cart');
        var product_id =  parseInt($form.find('input[type="hidden"][name="product_id"]').first().val(),10);
        openerp.jsonRpc("/shop/cart/update/msg", 'call', 
            {
                'product_id': product_id,
                'add_qty': 1
            })
            .then(function (msg) 
            {
                if(msg)
                {
                    alert("You Can Add Not This Product in Your Cart.")
                }
            });
    });
});