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

        <%
        initial_balance_text = {'initial_balance': _('Computed'), 'opening_balance': _('Opening Entries'), False: _('No')}
        %>
	    <% get_wizard_params(data["form"]["date_maturity"],data["form"]["partner_ids"]) %>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell" style="width: 159px">${_('Data riferimento')}</div>
                <div class="act_as_cell" style="width: 120px">${_('Modalità')}</div>
                <div class="act_as_cell" style="width: 950px">${_('Filtro Partner')}</div>
                <div class="act_as_cell" style="width: 1px"></div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${formatLang(data["form"]["date_maturity"] or '', date=True)}</div>
                <div class="act_as_cell">
                	%if get_mode():
                		${_('A SCADERE')}
                	%else:
                		${_('SCADUTO')}
                	%endif
                </div>
                <div class="act_as_cell">
                	%if data["form"]["print_customers"]:
                		${_('Customers; ')}
                	%endif
                	%if data["form"]["print_suppliers"]:
                		${_('Suppliers; ')}
                	%endif
					%for partner in data["form"]["partner_ids"]:
						${get_partner_name(partner)+'; '}
					%endfor
				</div>
                <div class="act_as_cell"><br></div>
            </div>
        </div>

      	<% supertotalscaduto = 0 %>
      	<% supertotal30 = 0 %>
      	<% supertotal60 = 0 %>
      	<% supertotal90 = 0 %>
      	<% supertotal120 = 0 %>
      	<% supertotal150 = 0 %>
      	<% supertotal180 = 0 %>
      	<% supertotaloltre = 0 %>

    	%for group in get_move_line():
          	%if group.ids:
          	                        
                    <div class="account_title bg" style="width: 1230px; margin-top: 20px; padding-bottom: 5px; font-size: 15px;">
                      		<b><div class = "act_as_cell" style="background-color: #ffffff; width: 1230px;">${group[0].partner_id and group[0].partner_id.name or ''}</div></b>     
                    </div>
                    
                    <div class="act_as_table list_table" style="padding-top: 2px; border-bottom: solid 1px;">
        
                        <div class="act_as_thead">
                            <div class="act_as_row labels">
                                <div class="act_as_cell first_column" style="width: 70px;">${_('DATA SCADENZA')}</div>                               
                                <div class="act_as_cell" style="width: 90px;">${_('FATTURA')}</div>                                
                                <div class="act_as_cell" style="width: 70px;">${_('DATA FATTURA')}</div>
                                <div class="act_as_cell" style="width: 100px;">${_('TOTALE DOCUMENTO')}</div>
                                <div class="act_as_cell" style="width: 70px;">
                                	%if get_mode():
	                                	${_('SCADUTO')}
	                                %else:
	                                	${_('A SCADERE')}
	                                %endif
                                </div>
                                <div class="act_as_cell" style="width: 70px;">${_('30 gg')}</div>
                                <div class="act_as_cell" style="width: 70px;">${_('60 gg')}</div>
                                <div class="act_as_cell" style="width: 70px;">${_('90 gg')}</div>
                                <div class="act_as_cell" style="width: 70px;">${_('120 gg')}</div>
                                <div class="act_as_cell" style="width: 70px;">${_('150 gg')}</div>
                                <div class="act_as_cell" style="width: 70px;">${_('180 gg')}</div>
                                <div class="act_as_cell" style="width: 70px;">${_('OLTRE')}</div>                                
                                <div class="act_as_cell" style="width: 90px;">${_('DOCUMENTO DI ORIGINE')}</div>
                                <div class="act_as_cell" style="width: 60px;">${_('REF. PARTNER')}</div>                                
                                <div class="act_as_cell" style="width: 150px;">${_('TERMINI DI PAGAMENTO')}</div>
                                <div class="act_as_cell" style="width: 40px;">${_('Riconc. Parz.')}</div>
                            </div>
                        </div>

                        <div class="act_as_tbody">

		                          	<% totalscaduto = 0 %>
		                          	<% total30 = 0 %>
		                          	<% total60 = 0 %>
		                          	<% total90 = 0 %>
		                          	<% total120 = 0 %>
		                          	<% total150 = 0 %>
		                          	<% total180 = 0 %>
		                          	<% totaloltre = 0 %>
		                          	%for line in group:
		                          		<div class="act_as_row line" style="border-bottom: solid 1px; border-color: #efefef; page-break-inside:avoid;">
			                                <div class="act_as_cell  first_column" style="width: 70px;">${line.date_maturity and (formatLang(line.date_maturity, date=True)) or ''}</div>    
			                                <div class="act_as_cell" style="width: 90px;">${line.stored_invoice_id.number or ''}</div>                             
			                                <div class="act_as_cell" style="width: 70px;">${line.invoice_date and (formatLang(line.invoice_date, date=True)) or ''}</div>
			                                <div class="act_as_cell" style="width: 100px; text-align: right; padding-right: 20px;">${line.debit-line.credit}</div>                                
			                                <div class="act_as_cell" style="width: 70px; text-align: right; padding-right: 20px;">
												%if get_maturity(line.date_maturity,data["form"]["date_maturity"],0,0):
													%if line.reconcile_ref:
														<% t = get_residual(line.reconcile_ref) %>
													%else:
														<% t = line.debit-line.credit %>
													%endif
													<div>${t}</div>
													<% totalscaduto = totalscaduto + t %>
												%else:
													<br />
												%endif
											</div>                                
			                                <div class="act_as_cell" style="width: 70px; text-align: right; padding-right: 20px;">
												%if get_maturity(line.date_maturity,data["form"]["date_maturity"],0,30):
													%if line.reconcile_ref:
														<% t = get_residual(line.reconcile_ref) %>
													%else:
														<% t = line.debit-line.credit %>
													%endif
													<div>${t}</div>
													<% total30 = total30 + t %>
												%else:
													<br />
												%endif
											</div> 
			                                <div class="act_as_cell" style="width: 70px; text-align: right; padding-right: 20px;">
												%if get_maturity(line.date_maturity,data["form"]["date_maturity"],30,60):
													%if line.reconcile_ref:
														<% t = get_residual(line.reconcile_ref) %>
													%else:
														<% t = line.debit-line.credit %>
													%endif
													<div>${t}</div>
													<% total60 = total60 + t %>
												%else:
													<br />
												%endif
											</div> 
			                                <div class="act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
												%if get_maturity(line.date_maturity,data["form"]["date_maturity"],60,90):
													%if line.reconcile_ref:
														<% t = get_residual(line.reconcile_ref) %>
													%else:
														<% t = line.debit-line.credit %>
													%endif
													<div>${t}</div>
													<% total90 = total90 + t %>
												%else:
													<br />
												%endif
											</div> 
			                                <div class="act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
												%if get_maturity(line.date_maturity,data["form"]["date_maturity"],90,120):
													%if line.reconcile_ref:
														<% t = get_residual(line.reconcile_ref) %>
													%else:
														<% t = line.debit-line.credit %>
													%endif
													<div>${t}</div>
													<% total120 = total120 + t %>
												%else:
													<br />
												%endif
											</div> 
			                                <div class="act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
												%if get_maturity(line.date_maturity,data["form"]["date_maturity"],120,150):
													%if line.reconcile_ref:
														<% t = get_residual(line.reconcile_ref) %>
													%else:
														<% t = line.debit-line.credit %>
													%endif
													<div>${t}</div>
													<% total150 = total150 + t %>
												%else:
													<br />
												%endif
											</div> 
			                                <div class="act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
												%if get_maturity(line.date_maturity,data["form"]["date_maturity"],150,180):
													%if line.reconcile_ref:
														<% t = get_residual(line.reconcile_ref) %>
													%else:
														<% t = line.debit-line.credit %>
													%endif
													<div>${t}</div>
													<% total180 = total180 + t %>
												%else:
													<br />
												%endif
											</div> 
			                                <div class="act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
												%if get_maturity(line.date_maturity,data["form"]["date_maturity"],180,0):
													%if line.reconcile_ref:
														<% t = get_residual(line.reconcile_ref) %>
													%else:
														<% t = line.debit-line.credit %>
													%endif
													<div>${t}</div>
													<% totaloltre = totaloltre + t %>
												%else:
													<br />
												%endif
											</div>                                  
			                                <div class="act_as_cell" style="width: 90px;">${line.invoice_origin or ''}</div>
			                                <div class="act_as_cell" style="width: 60px;">${line.partner_id.ref or ''}</div>                               
			                                <div class="act_as_cell" style="width: 150px;">
										        %if line.payment_term_id and line.payment_term_id.name:
										            ${line.payment_term_id.name}
										        %else:
										            ${''}
										        %endif
									        </div>
			                                <div class="act_as_cell" style="width: 40px;">
			                                	%if line.reconcile_ref:
			                                		SI
		                                		%else:
		                                			NO
		                                		%endif
			                                </div>
		                            	</div>
							     	%endfor
							     	
		                          	<div class = "act_as_row labels" style="page-break-inside:avoid;">
		                          		<div class = "act_as_cell" style="width: 10px;"><b>Totale:</b></div>
		                          		<div class = "act_as_cell" style="width: 90px;"><br /> </div>
		                          		<div class = "act_as_cell" style="width: 70px;"><br /> </div>
		                          		<div class = "act_as_cell" style="width: 100px;"><br /> </div>
		                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
		                          			<b>${totalscaduto}</b>
		                          		</div>
		                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
		                          			<b>${total30}</b>
		                          		</div>
		                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
		                          			<b>${total60}</b>
		                          		</div>
		                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
		                          			<b>${total90}</b>
		                          		</div>
		                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
		                          			<b>${total120}</b>
		                          		</div>
		                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
		                          			<b>${total150}</b>
		                          		</div>
		                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
		                          			<b>${total180}</b>
		                          		</div>
		                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
		                          			<b>${totaloltre}</b>
		                          		</div>
		                          		<div class = "act_as_cell" style="width: 90px;"><br /> </div>
		                          		<div class = "act_as_cell" style="width: 60px;"><br /> </div>
		                          		<div class = "act_as_cell" style="width: 150px;"><br /> </div>
		                          		<div class = "act_as_cell" style="width: 40px;"><br /> </div>                
		                          	</div>	
		                          	
							      	<% supertotalscaduto += totalscaduto %>
							      	<% supertotal30 += total30 %>
							      	<% supertotal60 += total60 %>
							      	<% supertotal90 += total90 %>
							      	<% supertotal120 += total120 %>
							      	<% supertotal150 += total150 %>
							      	<% supertotal180 += total180 %>
							      	<% supertotaloltre += totaloltre %>		                          	
		                          	                         							     	
			                    </div>
                			</div>
						%endif
				  	%endfor
				  	<br />
				  	<br />
                    <div class="act_as_table list_table" style="padding-top: 2px; border-bottom: solid 1px;">

                        <div class="act_as_thead">
                            <div class="act_as_row labels">
                          		<div class = "act_as_cell" style="width: 70px;"><br /></div>
                          		<div class = "act_as_cell" style="width: 90px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 70px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 100px;"><b>TOTALI:</b></div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 10px; width: 70px;">
                                	%if get_mode():
	                                	${_('SCADUTO')}
	                                %else:
	                                	${_('A SCADERE')}
	                                %endif
                                </div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 70px;">${_('30 gg')}</div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 70px;">${_('60 gg')}</div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 70px;">${_('90 gg')}</div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 70px;">${_('120 gg')}</div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 70px;">${_('150 gg')}</div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 70px;">${_('180 gg')}</div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 70px;">${_('OLTRE')}</div>                                
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 90px;"><br /> </div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 60px;"><br /> </div>                                
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 150px;"><br /> </div>
                                <div class="act_as_cell" style="text-align: right; padding-right: 20px; width: 40px;"><br /> </div>
                            </div>
                        </div>
                    
	                    <div class="act_as_tbody">
                          	<div class = "act_as_row labels" style="page-break-inside:avoid;">
                          		<div class = "act_as_cell" style="width: 70px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 90px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 70px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 100px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 10px;">
                          			<b>${supertotalscaduto}</b>
                          		</div>
                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
                          			<b>${supertotal30}</b>
                          		</div>
                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
                          			<b>${supertotal60}</b>
                          		</div>
                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
                          			<b>${supertotal90}</b>
                          		</div>
                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
                          			<b>${supertotal120}</b>
                          		</div>
                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
                          			<b>${supertotal150}</b>
                          		</div>
                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
                          			<b>${supertotal180}</b>
                          		</div>
                          		<div class = "act_as_cell" style="width: 70px;  text-align: right; padding-right: 20px;">
                          			<b>${supertotaloltre}</b>
                          		</div>
                          		<div class = "act_as_cell" style="width: 90px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 60px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 150px;"><br /> </div>
                          		<div class = "act_as_cell" style="width: 40px;"><br /> </div>                
                          	</div>	                    
	                    </div>
                    </div>				  	
				  	
</body>
</html>
