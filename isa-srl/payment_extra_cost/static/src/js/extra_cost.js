$(document).ready(function(){
    //Controllo in caso di cambiamento Metodi di pagamento
    //Quando cambiano i termini di pagamento aggiorno i valori 
    //relativi alla consegna (potrebbero essere imputati costi aggiuntvi)
    //e setto evntuali termini di pagamento all'interno dell'ordine.
    $('#payment_method').find("input[name='acquirer']").change(function(e){
        var acquirer_id = $(this).val();
        window.location.href = '/shop/payment?acquirer_id=' + acquirer_id;
    });
});