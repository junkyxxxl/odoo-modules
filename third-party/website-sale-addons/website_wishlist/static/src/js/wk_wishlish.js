$(document).ready(function()
{
	var ids;
    $('.oe_website_sale').each(function(ev)
    {
        ids = $('#wishlist_ids').attr('ids');

        if (ids)
            ids = ids.replace(/[\[\]']+/g,'').replace(/\s/g, '').split(',');
        else
            ids = [];
        if ($("input[name='product_id']").is(':radio'))
            var product_id = $("input[name='product_id']:checked").attr('value');
        else
            var product_id = $("input[name='product_id']").attr('value');
        if($.inArray(product_id, ids) != -1)
        {
            $(".add_to_wishlist").html(' Added to Wishlist').css("color", "green");
            $(".add_to_wishlist").css("text-decoration", "None");
        }
        else
        {
            $(".add_to_wishlist").html(' Add to Wishlist').css("color", "#337ab7")
        }
    });

    $('.oe_website_sale').on('change', function(ev)
    {
        if ($("input[name='product_id']").is(':radio'))
            var product_id = $("input[name='product_id']:checked").attr('value');
        else
            var product_id = $("input[name='product_id']").attr('value');
        if($.inArray(product_id, ids) != -1)
        {
            $(".add_to_wishlist").html(' Added to Wishlist').css("color", "green");
            $(".add_to_wishlist").css("text-decoration", "None");
        }
        else
        {
            $(".add_to_wishlist").html(' Add to Wishlist').css("color", "#337ab7");
        }
    });

    $('.add_to_wishlist').on('click', function(e)
    {
        if ($("input[name='product_id']").is(':radio'))
            var product = $("input[name='product_id']:checked").attr('value');
        else
            var product = $("input[name='product_id']").attr('value');
        console.log(product);
        e.preventDefault();
        openerp.jsonRpc('/wishlist/add_to_wishlist', 'call', {'product': product})
        .then(function (res)
        {
            if(res>0)
            {
                ids.push(product.toString());
                $('.my_wishlist_quantity').parent().parent().removeClass("hidden");
                $('.my_wishlist_quantity').html(res).hide().fadeIn(600);
                $(".add_to_wishlist").html(' Added to Wishlist').css("color", "green");
                $(".add_to_wishlist").css("text-decoration", "None");
            }
            else
            {
                $('.my_wishlist_quantity').parent().parent().addClass("hidden");
            }
        }).fail(function (err)
        {
          console.log('fail');
        });

    });

   $(".remove_whishlist").on("click", function(e)
    {
        var product = $(this).attr("whishlist-id");
        e.preventDefault();
        openerp.jsonRpc('/wishlist/remove_from_wishlist', 'call', {'product': product})
        .then(function (res)
        {
            if(res>0)
            {
                $('.my_wishlist_quantity').parent().parent().removeClass("hidden");
                $('.my_wishlist_quantity').html(res).hide().fadeIn(600);
            }
            else
            {
                $('.my_wishlist_quantity').parent().parent().addClass("hidden");
            }
        }).fail(function (err)
        {
          console.log('fail');
        });
        var row = $(this).closest('tr');
        row.fadeOut(1000);
    });

   $(".btn.btn-primary.pull-right.mb31").on("click", function(e)
    {
        var product_id = parseInt($(this).attr("product-id"),10);
        var value = 1;
        var $input = $(this);
        if ($input.data('update_change'))
        {
            return;
        }
        e.preventDefault();
        openerp.jsonRpc("/shop/cart/update_json", 'call', {
        'line_id': NaN,
        'product_id': product_id,
        'add_qty': value})
        .then(function (data)
        {
            $input.data('update_change', false);
            if (value !== 1)
            {
                $input.trigger('change');
                return;
            }
            var $q = $(".my_cart_quantity");
            if (data.cart_quantity)
            {
                $q.parent().parent().removeClass("hidden");
            }
            else
            {
                $q.parent().parent().addClass("hidden");
                $('a[href^="/shop/checkout"]').addClass("hidden")
            }
            $q.html(data.cart_quantity).hide().fadeIn(600);
        }).fail(function (err)
        {
          console.log('fail');
        });

        var row = $(this).closest('tr');
        row.fadeOut(1000);
        openerp.jsonRpc('/wishlist/remove_from_wishlist', 'call', {'product': product_id})
        .then(function (res)
        {
            if(res>0)
            {
                $('.my_wishlist_quantity').parent().parent().removeClass("hidden");
                $('.my_wishlist_quantity').html(res).hide().fadeIn(600);
            }
            else
            {
                $('.my_wishlist_quantity').parent().parent().addClass("hidden");
            }
        }).fail(function (err)
        {
          console.log('fail');
        });
    });

    //Verifica disponibilità prodotti in wishlist
    $('table#wishlist_products > tbody > tr').each(function(){
        $this = this;
        product= $($this).find('a#add_to_cart').attr('product-id');
        $($this).find('#'+product+'.wk_hidden_stock').removeClass('wk_show_stock');
        $($this).find('#'+product).addClass('wk_show_stock');
        var value = $($this).find('#'+product).attr('value');
        var allow = $($this).find('#'+product).attr('allow');
        if (value<1)
        {
            if (allow<1)
            {
                $($this).find('#add_to_cart').removeClass('js_check_product');
                $($this).find('#add_to_cart').attr('disabled','disabled');

            }
            else
            {
                $($this).find('#add_to_cart').addClass('js_check_product');
            }
        }
    });

});