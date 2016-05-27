$(document).ready(function(){
    //Verifico quali campi abilitre in base al tipo cliente selezionato
    $('#is_company, #is_user').change(function(){
        if($('#is_company').is(':checked')){
            //Se si tratta di una società visualizzo Company name e partita iva
            //e nascondo Cognome e Codice fiscale
            $('input[name=street]').closest('div[class*=form-group]').show();
            $('input[name=vat]').closest('div[class*=form-group]').show();
            $('input[name=person_surname]').closest('div[class*=form-group]').hide();
            $('input[name=fiscalcode]').closest('div[class*=form-group]').hide();
        }else if($('#is_user').is(':checked')){
            $('input[name=person_surname]').closest('div[class*=form-group]').show();
            $('input[name=fiscalcode]').closest('div[class*=form-group]').show();
            $('input[name=street]').closest('div[class*=form-group]').hide();
            $('input[name=vat]').closest('div[class*=form-group]').hide();
        }
    });
    //Simulo il change sul tipo cliente per settare i campi visibili/non visibili
    $('#is_company, #is_user').trigger('change');
});