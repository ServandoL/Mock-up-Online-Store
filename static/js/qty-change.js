$(document).ready(function() {
    var minQty = 1;
    $(".qty-change-plus").on("click", function() {
        var quantity = $(this).siblings("input").val()
        quantity = isNaN(quantity) ? 1: quantity;
        quantity++;
        $(this).siblings("input").val(quantity)
    });

    $(".qty-change-minus").on("click", function() {
        var quantity = $(this).siblings("input").val()
        quantity = isNaN(quantity) ? 1: quantity;
        quantity--;
        if (quantity < minQty) {
            quantity = 1;
        }
        $(this).siblings("input").val(quantity)
    });
});