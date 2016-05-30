$(document).ready(function () {
	
var price_from = $.find("#price_range") && $.find("#price_range")[0] && $.find("#price_range")[0].value.split(";")[0];
var price_to = $.find("#price_range") && $.find("#price_range")[0] && $.find("#price_range")[0].value.split(";")[1];
var price_min = $.find("#price_range") && $.find("#price_range")[0] &&$.find("#price_range")[0].value.split(";")[2];
var price_max = $.find("#price_range") && $.find("#price_range")[0] && $.find("#price_range")[0].value.split(";")[3];
var step = $.find("#price_range") && $.find("#price_range")[0] && $.find("#price_range")[0].value.split(";")[4];

$("#price_range").ionRangeSlider({
        keyboard: true,
        min: price_min,
        max: price_max,
        from: price_from,
        to: price_to,
        type: 'double',
        step: step,
        grid: true,
	});
});
