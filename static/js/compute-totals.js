$(document).ready(function() {
    var subtotal = 0;
    var tax = 0.0825;
    $(".subtotal").each(function() {
        var amnt = ($(this).text().substring(1)); // Remove the "$"
        subtotal += parseFloat(amnt);
    });
    $(".amount").val("$"+subtotal.toFixed(2));
    var taxAmount = tax * subtotal
    $(".tax").val("$"+taxAmount.toFixed(2))
    var totalAmount = taxAmount + subtotal
    $(".total").val("$"+totalAmount.toFixed(2))
});