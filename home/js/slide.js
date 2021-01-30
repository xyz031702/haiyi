// function to handle Swiper Slider Plugin
var swiperHandler = function() {
	var swiperDefault = $('.horizontal-slider');
	if (swiperDefault.length) {
		swiperDefault.each(function() {
			var _this = $(this);
			var swiper = new Swiper(_this, {
				pagination : _this.find('.swiper-pagination'),
				paginationClickable : _this.find('.swiper-pagination'),
				loop : false,
				observer: true,
				observeParents: true,
				autoplay : 3000,
				nextButton : _this.find('.swiper-button-next'),
				prevButton : _this.find('.swiper-button-prev'),
			});
		});
	}
};