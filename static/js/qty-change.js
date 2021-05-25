$(document).ready(function() {
    var minQty = 1;
    $("#qty-change-plus").click(function() {
        var quantity = $("#qty-number").val();
        quantity = isNaN(quantity) ? 1: quantity;
        quantity++;
        $("#qty-number").val(quantity)
    });

    $("#qty-change-minus").click(function() {
        var quantity = $("#qty-number").val();
        quantity = isNaN(quantity) ? 1: quantity;
        quantity--;
        if (quantity < minQty) {
            quantity = 1;
        }
        $("#qty-number").val(quantity)
    });
});