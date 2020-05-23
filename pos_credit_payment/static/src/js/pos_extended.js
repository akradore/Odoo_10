
odoo.define('pos_credit_payment.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var Model = require('web.DataModel');
    

    var _t = core._t;
    
    models.load_models({
        model: 'credit.history',
        fields: ['date', 'pos_order_id', 'pos_order_amount', 'used_credit_amount', 'balance_credit_amount', 'partner_id'],
        domain: null,
        loaded: function(self, pos_credit_history) {
            self.pos_credit_history = pos_credit_history;
        },
    });


    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
            partner_model.fields.push('custom_credit');
            
            var journal_model = _.find(this.models, function(model){ return model.model === 'account.journal'; });
            journal_model.fields.push('credit');
            return _super_posmodel.initialize.call(this, session, attributes);
        },
        push_order: function(order, opts){
            var self = this;
            var pushed = _super_posmodel.push_order.call(this, order, opts);
            var client = order && order.get_client();
            
            if (client){
                order.paymentlines.each(function(line){
                    var journal = line.cashregister.journal;
            
                    var amount = line.get_amount();
                    if (journal['credit'] === true){
                    if (amount <= client.custom_credit){
                      var updated = client.custom_credit - amount;
                      
                      
                      var model1 = new Model('res.partner');
                      model1.call('write', [client['id'], {'custom_credit' : updated}]).then(null);
                      
                      //var model2 = new Model('res.partner');
                      //model1.call('create_credit_history', {'used_credit_amount' : amount, 'balance_credit_amount': updated, 'partner_id': client['id']}).then(null);
                      
                      //new Model('pos.gift.coupon').call('search_coupon', [partner_id ? partner_id.id : 0, entered_code]).fail(function(unused, event) {
                        //    }).done(function(output)
                        /*console.log("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO", order)
                        new Model('res.partner').call('create_credit_history',[client, amount, updated, client, order])
                        	
                        	.then(function(data){return data;},function(err,event){
                        	 event.preventDefault();
                        	    return false;
                        	     });*/
                         //});

                    }
                    else{
                    }
                   }
                });
            }
            return pushed;
        }
    });


  screens.PaymentScreenWidget.include({
        validate_order: function(options) {
            var currentOrder = this.pos.get_order();
            
            var plines = currentOrder.get_paymentlines();
            
            var dued = currentOrder.get_due();
            
            var changed = currentOrder.get_change();
            
            var clients = currentOrder.get_client();
            
            if (clients){  //if customer is selected
		        for (var i = 0; i < plines.length; i++) {
		           if (plines[i].cashregister.journal['type'] === "cash" && plines[i].cashregister.journal['credit'] === true) { //we've given Miscellaneous Type
				       if(plines[i]['amount'] > clients.custom_credit){ // Make Condition that amount is greater than selected customer's credit amount
						   this.gui.show_popup('error',{
						        'title': _t('Not Sufficient Credit'),
						        'body': _t('Customer has not Sufficient Credit To Pay'),
						    });
						    return;
				    }
				  }
		        } 
			}
			
		        for (var i = 0; i < plines.length; i++) {

		           	 if (plines[i].cashregister.journal['credit'] === true){
					 //if(plines[i]['amount'] > clients.custom_credit){
					  
				       if(currentOrder.get_change() > 0){ // Make Condition that amount is greater than selected customer's credit amount
						   this.gui.show_popup('error',{
				            'title': _t('Payment Amount Exceeded'),
				            'body': _t('You cannot Pay More than Total Amount'),
				        });
                		return;
				    }
				    
				    // Make Condition: Popup Occurs When Customer is not selected on credit payment method, While any other payment method, this error popup will not be showing
				    if (!currentOrder.get_client()){
				        this.gui.show_popup('error',{
				            'title': _t('Unknown customer'),
				            'body': _t('You cannot use Credit payment. Select customer first.'),
				        });
				        return;
				    }
				    
				  }
		        } //}

            if(currentOrder.get_orderlines().length === 0){
                this.gui.show_popup('error',{
                    'title': _t('Empty Order'),
                    'body': _t('There must be at least one product in your order before it can be validated.'),
                });
                return;
            }

            this._super(options);
        },


     
    });




});
