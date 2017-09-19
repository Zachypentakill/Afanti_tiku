setTimeout(dealKH, 200);

function  dealKH() {
    //处理选择题选项
    if ($(".aft_option_wrapper").length && $(".aft_option").length ) {
        console.log($(".aft_option_wrapper").length);
        console.log($(".aft_option").length);

        $(".aft_option_wrapper").each(function(index, el) {
            var wrapper_width_half = (this.getBoundingClientRect().width-8) * 0.5,
                counter = 0,
                atf_option_arr = $(this).find(".aft_option");

            atf_option_arr.each(function(index, el) {
                if (this.getBoundingClientRect().width <= wrapper_width_half ) {
                    counter++
                }
            });
            if (counter === 4) {
                var option_b = atf_option_arr.eq(1).html(),
                    option_d = atf_option_arr.eq(3).html();
                atf_option_arr.eq(3).parent().remove();
                atf_option_arr.eq(1).parent().remove();
                atf_option_arr.eq(0).parent().append("<td class='aft_option'>" + option_b + "</td>");
                atf_option_arr.eq(2).parent().append("<td class='aft_option'>" + option_d + "</td>");
                atf_option_arr.each(function(index, el) {
                    $(this).css('width', wrapper_width_half-4);
                });
            }
        });
    }
}
