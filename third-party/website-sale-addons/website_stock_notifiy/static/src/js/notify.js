$(document).ready(function() {
     $(".wk_submit_div").on("click", function()
    {
        var pageURL = $(location).attr("href");
        var data = $(this).parent();
        var uid = data.attr('uid');
        var product_id = data.attr('id');
        var email = $('.wk_input_email').val();
        if (!ValidateEmail(email))
        {
            $('.div_message_notify').show().text('Email formalmente errata!');
        }
        else
        {
            openerp.jsonRpc('/website/stock_notify/', 'call', {'id':product_id, 'email': email, 'pageURL':pageURL})
            .then(function (res)
            {
                if (res == true)
                {
                    data.hide();
                    $('.div_message_notify').show().text("Verrà inviata un'email all'indirizzo indicato quando il prodotto diventa disponibile!").height(45);
                }
            }).fail(function (err)
                {
                });
        }
    });

    $(".wk_submit_div").hover(
        function () {
            $(this).css({"background-color":"#3071a9;"});
        },
        function () {
            $(this).css({"background-color":"#428bca"});
    });

    function ValidateEmail(email) {
        var expr = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
        return expr.test(email);
    };
    $(".span_undo").hover(
        function () {
            $(this).css({"color":"#1976D2"});
        },
        function () {
            $(this).css({"color":"#303F9F"});
    });

});