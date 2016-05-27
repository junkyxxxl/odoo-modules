## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<style type="text/css">
 	        .overflow_ellipsis {
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }
            
	        ${css}

.style-r2 {
    background-color: #efefef;
}	        
		</style>
	</head>
	<body>

  		<%!
        def amount(text):
        	return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
  		%>
  		

  		<%setLang(user.lang)%>
  		       
  		       
  		        
  		<% get_wizard_params(data["form"]) %>
  		
        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell" style="width: 425px">${_('Filtro azienda:')}</div>
                <div class="act_as_cell" style="width: 240px">${_('Data da:')}</div>
                <div class="act_as_cell" style="width: 240px">${_('Data a:')}</div>
                <div class="act_as_cell" style="width: 425px">${_('Filtro conti:')}</div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell" style="width: 425px">${data["form"]["company_id"][1] or ''}</div>
                <div class="act_as_cell" style="width: 240px">${formatLang(data["form"]["date_from"] or '', date=True)}</div>
                <div class="act_as_cell" style="width: 240px">${formatLang(data["form"]["date_to"] or '', date=True)}</div>
                <div class="act_as_cell" style="width: 425px">${data["form"]["account_id"][1] or ''}</div>
            </div>
        </div>  		
  		
        <div class="account_title bg" style="width: 1330px; margin-top: 20px; padding-bottom: 5px; font-size: 15px;">
      		<b><div class = "act_as_cell" style="background-color: #ffffff; width: 1330px;">${_('Movimenti analitici')}</div></b>     
        </div>  	
        
        <div class="act_as_table list_table" style="padding-top: 2px; border-bottom: solid 1px;">
        
            <div class="act_as_thead">
                <div class="act_as_row labels">
                    <div class="act_as_cell first_column" style="width: 160px;">${_('Data')}</div>                               
                    <div class="act_as_cell" style="width: 160px;">${_('REF')}</div>                                
                    <div class="act_as_cell" style="width: 230px;">${_('Descrizione')}</div>
                    <div class="act_as_cell" style="width: 230px;">${_('Giornale analitico')}</div>
                    <div class="act_as_cell" style="width: 230px;">${_('Conto analitico')}</div>
                    <div class="act_as_cell" style="width: 160px;">${_('Acquisti')}</div>
                    <div class="act_as_cell" style="width: 160px;">${_('Vendite')}</div>
                </div>
            </div>
        	
			<div class="act_as_tbody">
				%for move in get_journal_moves():
					<div class="act_as_row line" style="border-bottom: solid 1px; border-color: #efefef;">
						<div class="act_as_cell  first_column" style="width: 160px;">${move.date or ''}</div>  
						<div class="act_as_cell  first_column" style="width: 160px;">${move.ref or ''}</div>
						<div class="act_as_cell  first_column" style="width: 230px;">${move.name or ''}</div>  
						<div class="act_as_cell  first_column" style="width: 230px;">${move.journal_id.name or ''}</div>  
						<div class="act_as_cell  first_column" style="width: 230px;">
							%if move.account_id.parent_id.name:
								${move.account_id.parent_id.name}/
							%endif
							${move.account_id.name or ''}
						</div>  
						<div class="act_as_cell  first_column" style="width: 160px;">
							%if move.amount <= 0:
              					${formatLang(move.amount) | amount}
          					%else:
              					${''}
          					%endif
						</div>  
						<div class="act_as_cell  first_column" style="width: 160px;">
					        %if move.amount >= 0:
              					${formatLang(move.amount) | amount}
          					%else:
              					${''}
          					%endif
						</div>    
					</div>
				%endfor
				
              	<div class = "act_as_row labels">
              		<div class = "act_as_cell" style="width: 160px;"><b>${_('Totale')}</b></div>
              		<div class = "act_as_cell" style="width: 160px;"><br /> </div>
              		<div class = "act_as_cell" style="width: 230px;"><br /> </div>
              		<div class = "act_as_cell" style="width: 230px;"><br /> </div>
              		<div class = "act_as_cell" style="width: 230px;"><br /> </div>
              		<div class = "act_as_cell" style="width: 160px;">${formatLang(get_journal_totals(False)) | amount}</div>
              		<div class = "act_as_cell" style="width: 160px;">${formatLang(get_journal_totals()) | amount}</div>
				</div>
			</div>
		</div>
</body>
</html>
