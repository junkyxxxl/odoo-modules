/*$(document).ready(function() {
	$(window).bind('scroll', function() {
		var navHeight = $(window).height() / 3 - 70;
		if ($(window).scrollTop() > navHeight) {
			$('.navbar').addClass('navbar-fixed-top');
		} else {
			$('.navbar').removeClass('navbar-fixed-top');
		}
	});
		$("html").niceScroll({
			cursorcolor : "#999",
			cursoropacitymin : 0,
			cursoropacitymax : 1,
			cursorwidth : "3px",
			cursorborder : "1px solid #999",
			zindex: 5000,
			smoothscroll: true,
		});
});*/


$("#back-top").hide();
//fade in #back-top
$(function() {
	$(window).scroll(function() {
		if ($(this).scrollTop() > 100) {
			$('#back-top').fadeIn();
		} else {
			$('#back-top').fadeOut();
		}
	});
	// scroll body to 0px on click
	$('#back-top a').click(function() {
		$('body,html').animate({
			scrollTop : 0
		}, 800);
		return false;
	});
});