# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, AccessError
import csv
import base64
import io as StringIO
import xlrd
from odoo.tools import ustr
import requests
import codecs

class import_product_var_wizard(models.TransientModel):
    _name="import.product.var.wizard"

    import_type = fields.Selection([
        ('csv','CSV File'),
        ('excel','Excel File')
        ], default="csv", string="Import File Type", required=True)
    file = fields.Binary(string="File",required=True)
    
    @api.multi
    def show_success_msg(self,counter,skipped_line_no):
        
        #to close the current active wizard        
        action = self.env.ref('sh_all_in_one_import.sh_import_product_var_action').read()[0]
        action = {'type': 'ir.actions.act_window_close'} 
        
        #open the new success message box    
        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False                                   
        context = dict(self._context or {})
        dic_msg = str(counter) + " Records imported successfully"
        if skipped_line_no:
            dic_msg = dic_msg + "\nNote:"
        for k,v in skipped_line_no.items():
            dic_msg = dic_msg + "\nRow No " + k + " " + v + " "
        context['message'] = dic_msg   
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
            }   

    
    @api.multi
    def import_product_var_apply(self):

        product_tmpl_obj = self.env['product.template']
        #perform import lead
        if self and self.file:
            #For CSV
            if self.import_type == 'csv':
                counter = 1
                skipped_line_no = {}
                try:
                    file = str(base64.decodestring(self.file).decode('utf-8'))
                    myreader = csv.reader(file.splitlines())
                    skip_header=True
                    running_tmpl = None     
                    created_product_tmpl = False   
                    has_variant = False                                                    
                    for row in myreader:
                        try:
                            if skip_header:
                                skip_header=False
                                counter = counter + 1
                                continue
                            
                            if row[0] not in (None,""):
                                var_vals = {}
                                if row[0] != running_tmpl:
                                    running_tmpl = row[0]
                                    tmpl_vals = {}
                                    
                                    tmpl_vals.update({'name' : row[0]})
                                    
                                    tmpl_vals.update({'sale_ok' : True})
                                    if row[1].strip() == 'FALSE':
                                        tmpl_vals.update({'sale_ok' : False})                                        
                                    
                                    tmpl_vals.update({'purchase_ok' : True})
                                    if row[2].strip() == 'FALSE':
                                        tmpl_vals.update({'purchase_ok' : False})                                 
                                    
                                                                      
                                    if row[3].strip() == 'Service':
                                        tmpl_vals.update({'type' : 'service'})                                          
                                    elif row[3].strip() == 'Stockable Product':
                                        tmpl_vals.update({'type' : 'product'})                                                                            
                                    else:
                                        tmpl_vals.update({'type' : 'consu'})    
                                        
                                    if row[4].strip() in (None,""):
                                        search_category = self.env['product.category'].search([('name','=','All')], limit = 1)
                                        if search_category:
                                            tmpl_vals.update({'categ_id' : search_category.id })                                             
                                        else:
                                            skipped_line_no[str(counter)] = " - Category -  not found. "                                         
                                            counter = counter + 1
                                            continue   
                                    else:
                                        search_category = self.env['product.category'].search([('name','=',row[4].strip())], limit = 1)
                                        if search_category:
                                            tmpl_vals.update({'categ_id' : search_category.id })    
                                        else:
                                            skipped_line_no[str(counter)] = " - Category not found. " 
                                            counter = counter + 1
                                            continue     
                                        
                                        
                                    if row[5].strip() in (None,""):
                                        search_uom = self.env['product.uom'].search([('name','=','Unit(s)')], limit = 1)
                                        if search_uom:
                                            tmpl_vals.update({'uom_id' : search_uom.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Unit of Measure - Unit(s) not found. "                                         
                                            counter = counter + 1
                                            continue                                        
                                    else:
                                        search_uom = self.env['product.uom'].search([('name','=',row[5].strip())], limit = 1)
                                        if search_uom:
                                            tmpl_vals.update({'uom_id' : search_uom.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Unit of Measure not found. "                                         
                                            counter = counter + 1
                                            continue   
                                                                            
                                    if row[6].strip() in (None,""):
                                        search_uom_po = self.env['product.uom'].search([('name','=','Unit(s)')], limit = 1)
                                        if search_uom_po:
                                            tmpl_vals.update({'uom_po_id' : search_uom_po.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Purchase Unit of Measure - Unit(s) not found. "                                         
                                            counter = counter + 1
                                            continue                                        
                                    else:
                                        search_uom_po = self.env['product.uom'].search([('name','=',row[6].strip())], limit = 1)
                                        if search_uom_po:
                                            tmpl_vals.update({'uom_po_id' : search_uom_po.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Purchase Unit of Measure not found. "                                         
                                            counter = counter + 1
                                            continue                                                                                                                                                     
                                
                                    customer_taxes_ids_list = []
                                    some_taxes_not_found = False
                                    if row[7].strip() not in (None,""):
                                        for x in row[7].split(','):
                                            x = x.strip()
                                            if x != '':
                                                search_customer_tax = self.env['account.tax'].search([('name','=',x)], limit = 1)
                                                if search_customer_tax:
                                                    customer_taxes_ids_list.append(search_customer_tax.id)
                                                else:
                                                    some_taxes_not_found = True
                                                    skipped_line_no[str(counter)]= " - Customer Taxes " + x +  " not found. "                                                 
                                                    break
                                    
                                    if some_taxes_not_found:
                                        counter = counter + 1                                    
                                        continue  
                                    else:
                                        tmpl_vals.update({'taxes_id' : [(6, 0, customer_taxes_ids_list)] })
                                    
                                                                                                           
                                    vendor_taxes_ids_list = []
                                    some_taxes_not_found = False
                                    if row[8].strip() not in (None,""):
                                        for x in row[8].split(','):
                                            x = x.strip()
                                            if x != '':
                                                search_vendor_tax = self.env['account.tax'].search([('name','=',x)], limit = 1)
                                                if search_vendor_tax:
                                                    vendor_taxes_ids_list.append(search_vendor_tax.id)
                                                else:
                                                    some_taxes_not_found = True
                                                    skipped_line_no[str(counter)]= " - Vendor Taxes " + x +  " not found. "                                                 
                                                    break
                                    
                                    if some_taxes_not_found:
                                        counter = counter + 1                                    
                                        continue          
                                    else:
                                        tmpl_vals.update({'supplier_taxes_id' : [(6, 0, vendor_taxes_ids_list)] })
                                        
                                    tmpl_vals.update({'description_sale' : row[9] })   
                                    
                                    tmpl_vals.update({'invoice_policy' : 'order' })                                       
                                    if row[10].strip() == 'Delivered quantities':
                                        tmpl_vals.update({'invoice_policy' : 'delivery' })
                                        
                                    if row[11] not in (None,""):
                                        tmpl_vals.update({'list_price' : row[11]})
                                    
                                    if row[12] not in (None,""):
                                        tmpl_vals.update({'standard_price' : row[12]})                                            
                                    
                                    
                                    if row[13].strip() in (None,"") or row[14].strip() in (None,""):
                                        
                                        has_variant = False
                                        if row[15] not in (None,""):                                         
                                            tmpl_vals.update({'default_code' : row[15]})   
                                        
                                        if row[16] not in (None,""):
                                            tmpl_vals.update({'barcode' : row[16]})                                                                                                                                                                                                                                  
                                                                                       
                                        if row[17] not in (None,""):
                                            tmpl_vals.update({'weight' : row[17]})       
                                            
                                        if row[18] not in (None,""):
                                            tmpl_vals.update({'volume' : row[18]})  
                                            
                                            
                                        if row[20].strip() not in (None,""):   
                                            image_path = row[20].strip()
                                            if "http://" in image_path or "https://" in image_path:
                                                try:
                                                    r = requests.get(image_path)
                                                    if r and r.content:
                                                        image_base64 = base64.encodestring(r.content) 
                                                        tmpl_vals.update({'image': image_base64})
                                                    else:
                                                        skipped_line_no[str(counter)] = " - URL not correct or check your image size. "                                            
                                                        counter = counter + 1                                                
                                                        continue
                                                except Exception as e:
                                                    skipped_line_no[str(counter)] = " - URL not correct or check your image size " + ustr(e)   
                                                    counter = counter + 1 
                                                    continue                                              
                                                
                                            else:
                                                try:
                                                    with open(image_path, 'rb') as image:
                                                        image.seek(0)
                                                        binary_data = image.read()
                                                        image_base64 = codecs.encode(binary_data, 'base64')     
                                                        if image_base64:
                                                            tmpl_vals.update({'image': image_base64})
                                                        else:
                                                            skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this app. "                                            
                                                            counter = counter + 1                                                
                                                            continue                                                                       
                                                except Exception as e:
                                                    skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this app. " + ustr(e)   
                                                    counter = counter + 1 
                                                    continue                                                
                                            
                                            
                                            
                                            
                                    else:
                                        has_variant = True
                                            
                              
                                    created_product_tmpl = product_tmpl_obj.create(tmpl_vals)       
                                    if has_variant == False and row[19] not in (None,""):
                                        if created_product_tmpl and created_product_tmpl.product_variant_id and created_product_tmpl.type == 'product':
                                            stock_vals = {'product_tmpl_id' : created_product_tmpl.id,
                                                          'new_quantity'    : row[19], 
                                                          'product_id'      : created_product_tmpl.product_variant_id.id
                                                          }
                                            created_qty_on_hand = self.env['stock.change.product.qty'].create(stock_vals)
                                            if created_qty_on_hand:
                                                created_qty_on_hand.change_product_qty()                                            
                                        
                                        
                                        
                                        
                                                        
                                
                                if created_product_tmpl and  has_variant:
                                    pro_attr_line_obj = self.env['product.attribute.line']
                                    pro_attr_value_obj = self.env['product.attribute.value']
                                    pro_attr_obj = self.env['product.attribute']
                                    if row[13].strip() not in (None,"") and row[14].strip() not in (None,""):
                                        attr_ids_list = []
                                        for attr in row[13].split(','):
                                            attr = attr.strip()
                                            if attr != '':
                                                search_attr_name = False
                                                search_attr_name = pro_attr_obj.search([('name','=', attr )], limit = 1)
                                                if not search_attr_name:
                                                    search_attr_name = pro_attr_obj.create({'name' : attr })
                                                attr_ids_list.append(search_attr_name.id)
                                        attr_value_list = []
                                        for attr_value in row[14].split(','):
                                            attr_value = attr_value.strip()
                                            if attr_value != '':
                                                attr_value_list.append(attr_value)
                                        
                                        attr_value_ids_list = []
                                        if len(attr_ids_list) == len(attr_value_list):
                                            i = 0
                                            while i < len(attr_ids_list):
                                                search_attr_value = False
                                                search_attr_value = pro_attr_value_obj.search([('name','=',attr_value_list[i])], limit = 1)
                                                
                                                if not search_attr_value:
                                                    search_attr_value = pro_attr_value_obj.create({'name' : attr_value_list[i],
                                                                                                   'attribute_id' : attr_ids_list[i]
                                                                                                    })
                                             
                                                attr_value_ids_list.append(search_attr_value.id)
                                                i += 1 
                                        else:
                                            skipped_line_no[str(counter)] = " - Number of attributes and it's value not equal. "                                              
                                            counter = counter + 1
                                            continue
                                        if attr_value_ids_list and attr_ids_list:
                                            i = 0
                                            while i < len(attr_ids_list):
                                                search_attr_line = pro_attr_line_obj.search([
                                                                                        ('attribute_id','=',attr_ids_list[i] ),
                                                                                        ('product_tmpl_id','=',created_product_tmpl.id),
                                                                                        ],limit = 1)
                                                if search_attr_line:
                                                    past_values_list = []
                                                    past_values_list = search_attr_line.value_ids.ids
                                                    past_values_list.append( attr_value_ids_list[i] )
                                                    search_attr_line.write({'value_ids': [(6,0, past_values_list  )] })
                                                else:
                                                    created_attr_line = pro_attr_line_obj.create({'attribute_id' : attr_ids_list[i],
                                                                              'value_ids': [(6,0,[ attr_value_ids_list[i] ] )],
                                                                              'product_tmpl_id' : created_product_tmpl.id,
                                                                           })
                                                i += 1 
                                        created_product_tmpl.create_variant_ids()
                                        if created_product_tmpl.product_variant_ids:
                                            for product_varient in created_product_tmpl.product_variant_ids:
                                                if product_varient.attribute_value_ids and product_varient.attribute_value_ids.ids == attr_value_ids_list:

                                                    if row[15] not in (None,""):                                         
                                                        var_vals.update({'default_code' : row[15]})   
                                                    
                                                    if row[16] not in (None,""):
                                                        var_vals.update({'barcode' : row[16]})                                                                                                                                                                                                                                                                           
                                                                                                   
                                                    if row[17] not in (None,""):
                                                        var_vals.update({'weight' : row[17]})       
                                                        
                                                    if row[18] not in (None,""):
                                                        var_vals.update({'volume' : row[18]})  
                                                        

                                                  
                                                    if product_varient.type == 'product' and row[19] != '':
                                                        stock_vals = {'product_tmpl_id' : created_product_tmpl.id,
                                                                      'new_quantity'    : row[19], 
                                                                      'product_id'      : product_varient.id
                                                                      }
                                                        created_qty_on_hand = self.env['stock.change.product.qty'].create(stock_vals)
                                                        if created_qty_on_hand:
                                                            created_qty_on_hand.change_product_qty()    
                                                            
                                                    
                                                    
                                                    
                                                    if row[20].strip() not in (None,""):   
                                                        image_path = row[20].strip()
                                                        if "http://" in image_path or "https://" in image_path:
                                                            try:
                                                                r = requests.get(image_path)
                                                                if r and r.content:
                                                                    image_base64 = base64.encodestring(r.content) 
                                                                    var_vals.update({'image': image_base64})
                                                                else:
                                                                    skipped_line_no[str(counter)] = " - URL not correct or check your image size. "                                            
                                                                    counter = counter + 1                                                
                                                                    continue
                                                            except Exception as e:
                                                                skipped_line_no[str(counter)] = " - URL not correct or check your image size " + ustr(e)   
                                                                counter = counter + 1 
                                                                continue                                              
                                                            
                                                        else:
                                                            try:
                                                                with open(image_path, 'rb') as image:
                                                                    image.seek(0)
                                                                    binary_data = image.read()
                                                                    image_base64 = codecs.encode(binary_data, 'base64')     
                                                                    if image_base64:
                                                                        var_vals.update({'image': image_base64})
                                                                    else:
                                                                        skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this app. "                                            
                                                                        counter = counter + 1                                                
                                                                        continue                                                                       
                                                            except Exception as e:
                                                                skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this app. " + ustr(e)   
                                                                counter = counter + 1 
                                                                continue                                                                                                         
                                                    
                                                    product_varient.write(var_vals)
                                                    
                                                    
                                        
                                counter = counter + 1                                                
                            else:
                                skipped_line_no[str(counter)]=" - Name is empty. "  
                                counter = counter + 1                                   
                                
                            
                        except Exception as e:
                            skipped_line_no[str(counter)]=" - Value is not valid. " + ustr(e)   
                            counter = counter + 1 
                            continue          
                            
                except Exception as e:
                    raise UserError(_("Sorry, Your csv file does not match with our format" + ustr(e)))
                
                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_records, skipped_line_no)
                    return res

            
            #For Excel
            if self.import_type == 'excel':
                
                counter = 1
                skipped_line_no = {}                  
                try:
                    wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file))
                    sheet = wb.sheet_by_index(0)     
                    skip_header = True    
                    running_tmpl = None     
                    created_product_tmpl = False   
                    has_variant = False              
                             
                    for row in range(sheet.nrows):
                        try:
                            if skip_header:
                                skip_header = False
                                counter = counter + 1
                                continue
                            
                            if sheet.cell(row,0).value not in (None,""):
                                var_vals = {}
                                if sheet.cell(row,0).value != running_tmpl:
                                    running_tmpl = sheet.cell(row,0).value
                                    tmpl_vals = {}
                                    
                                    tmpl_vals.update({'name' : sheet.cell(row,0).value })
                                    
                                    tmpl_vals.update({'sale_ok' : True})
                                    if sheet.cell(row,1).value.strip() == 'FALSE':
                                        tmpl_vals.update({'sale_ok' : False})                                        
                                    
                                    tmpl_vals.update({'purchase_ok' : True})
                                    if sheet.cell(row,2).value.strip() == 'FALSE':
                                        tmpl_vals.update({'purchase_ok' : False})                                 
                                    
                                                                      
                                    if sheet.cell(row,3).value.strip() == 'Service':
                                        tmpl_vals.update({'type' : 'service'})                                          
                                    elif sheet.cell(row,3).value.strip() == 'Stockable Product':
                                        tmpl_vals.update({'type' : 'product'})                                                                            
                                    else:
                                        tmpl_vals.update({'type' : 'consu'})    
                                        
                                    if sheet.cell(row,4).value.strip() in (None,""):
                                        search_category = self.env['product.category'].search([('name','=','All')], limit = 1)
                                        if search_category:
                                            tmpl_vals.update({'categ_id' : search_category.id })                                             
                                        else:
                                            skipped_line_no[str(counter)] = " - Category -  not found. "                                         
                                            counter = counter + 1
                                            continue   
                                    else:
                                        search_category = self.env['product.category'].search([('name','=',sheet.cell(row,4).value.strip())], limit = 1)
                                        if search_category:
                                            tmpl_vals.update({'categ_id' : search_category.id })    
                                        else:
                                            skipped_line_no[str(counter)] = " - Category not found. " 
                                            counter = counter + 1
                                            continue     
                                        
                                        
                                    if sheet.cell(row,5).value.strip() in (None,""):
                                        search_uom = self.env['product.uom'].search([('name','=','Unit(s)')], limit = 1)
                                        if search_uom:
                                            tmpl_vals.update({'uom_id' : search_uom.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Unit of Measure - Unit(s) not found. "                                         
                                            counter = counter + 1
                                            continue                                        
                                    else:
                                        search_uom = self.env['product.uom'].search([('name','=',sheet.cell(row,5).value.strip())], limit = 1)
                                        if search_uom:
                                            tmpl_vals.update({'uom_id' : search_uom.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Unit of Measure not found. "                                         
                                            counter = counter + 1
                                            continue   
                                                                            
                                    if sheet.cell(row,6).value.strip() in (None,""):
                                        search_uom_po = self.env['product.uom'].search([('name','=','Unit(s)')], limit = 1)
                                        if search_uom_po:
                                            tmpl_vals.update({'uom_po_id' : search_uom_po.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Purchase Unit of Measure - Unit(s) not found. "                                         
                                            counter = counter + 1
                                            continue                                        
                                    else:
                                        search_uom_po = self.env['product.uom'].search([('name','=',sheet.cell(row,6).value.strip())], limit = 1)
                                        if search_uom_po:
                                            tmpl_vals.update({'uom_po_id' : search_uom_po.id }) 
                                        else:
                                            skipped_line_no[str(counter)] = " - Purchase Unit of Measure not found. "                                         
                                            counter = counter + 1
                                            continue                                                                                                                                                     
                                
                                    customer_taxes_ids_list = []
                                    some_taxes_not_found = False
                                    if sheet.cell(row,7).value.strip() not in (None,""):
                                        for x in sheet.cell(row,7).value.split(','):
                                            x = x.strip()
                                            if x != '':
                                                search_customer_tax = self.env['account.tax'].search([('name','=',x)], limit = 1)
                                                if search_customer_tax:
                                                    customer_taxes_ids_list.append(search_customer_tax.id)
                                                else:
                                                    some_taxes_not_found = True
                                                    skipped_line_no[str(counter)]= " - Customer Taxes " + x +  " not found. "                                                 
                                                    break
                                    
                                    if some_taxes_not_found:
                                        counter = counter + 1                                    
                                        continue  
                                    else:
                                        tmpl_vals.update({'taxes_id' : [(6, 0, customer_taxes_ids_list)] })
                                    
                                                                                                           
                                    vendor_taxes_ids_list = []
                                    some_taxes_not_found = False
                                    if sheet.cell(row,8).value.strip() not in (None,""):
                                        for x in sheet.cell(row,8).value.split(','):
                                            x = x.strip()
                                            if x != '':
                                                search_vendor_tax = self.env['account.tax'].search([('name','=',x)], limit = 1)
                                                if search_vendor_tax:
                                                    vendor_taxes_ids_list.append(search_vendor_tax.id)
                                                else:
                                                    some_taxes_not_found = True
                                                    skipped_line_no[str(counter)]= " - Vendor Taxes " + x +  " not found. "                                                 
                                                    break
                                    
                                    if some_taxes_not_found:
                                        counter = counter + 1                                    
                                        continue          
                                    else:
                                        tmpl_vals.update({'supplier_taxes_id' : [(6, 0, vendor_taxes_ids_list)] })
                                        
                                    tmpl_vals.update({'description_sale' : sheet.cell(row,9).value })   
                                    
                                    tmpl_vals.update({'invoice_policy' : 'order' })                                       
                                    if sheet.cell(row,10).value.strip() == 'Delivered quantities':
                                        tmpl_vals.update({'invoice_policy' : 'delivery' })
                                        
                                    if sheet.cell(row,11).value not in (None,""):
                                        tmpl_vals.update({'list_price' : sheet.cell(row,11).value })
                                    
                                    if sheet.cell(row,12).value not in (None,""):
                                        tmpl_vals.update({'standard_price' : sheet.cell(row,12).value })                                            
                                    
                                    
                                    if sheet.cell(row,13).value.strip() in (None,"") or sheet.cell(row,14).value.strip() in (None,""):
                                        
                                        has_variant = False
                                        if sheet.cell(row,15).value not in (None,""):                                         
                                            tmpl_vals.update({'default_code' : sheet.cell(row,15).value })   
                                        
                                        if sheet.cell(row,16).value not in (None,""):
                                            tmpl_vals.update({'barcode' : sheet.cell(row,16).value })                                                                                                                                                                                                                                  
                                                                                       
                                        if sheet.cell(row,17).value not in (None,""):
                                            tmpl_vals.update({'weight' : sheet.cell(row,17).value })       
                                            
                                        if sheet.cell(row,18).value not in (None,""):
                                            tmpl_vals.update({'volume' : sheet.cell(row,18).value })  
                                            
                                            
                                        if sheet.cell(row,20).value.strip() not in (None,""):   
                                            image_path = sheet.cell(row,20).value.strip()
                                            if "http://" in image_path or "https://" in image_path:
                                                try:
                                                    r = requests.get(image_path)
                                                    if r and r.content:
                                                        image_base64 = base64.encodestring(r.content) 
                                                        tmpl_vals.update({'image': image_base64})
                                                    else:
                                                        skipped_line_no[str(counter)] = " - URL not correct or check your image size. "                                            
                                                        counter = counter + 1                                                
                                                        continue
                                                except Exception as e:
                                                    skipped_line_no[str(counter)] = " - URL not correct or check your image size " + ustr(e)   
                                                    counter = counter + 1 
                                                    continue                                              
                                                
                                            else:
                                                try:
                                                    with open(image_path, 'rb') as image:
                                                        image.seek(0)
                                                        binary_data = image.read()
                                                        image_base64 = codecs.encode(binary_data, 'base64')     
                                                        if image_base64:
                                                            tmpl_vals.update({'image': image_base64})
                                                        else:
                                                            skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this app. "                                            
                                                            counter = counter + 1                                                
                                                            continue                                                                       
                                                except Exception as e:
                                                    skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this app. " + ustr(e)   
                                                    counter = counter + 1 
                                                    continue                                                
                                            
                                            
                                            
                                            
                                    else:
                                        has_variant = True    
                                    created_product_tmpl = product_tmpl_obj.create(tmpl_vals)       
                                    if has_variant == False and sheet.cell(row,19).value not in (None,""):
                                        if created_product_tmpl and created_product_tmpl.product_variant_id and created_product_tmpl.type == 'product':
                                            stock_vals = {'product_tmpl_id' : created_product_tmpl.id,
                                                          'new_quantity'    : sheet.cell(row,19).value, 
                                                          'product_id'      : created_product_tmpl.product_variant_id.id
                                                          }
                                            created_qty_on_hand = self.env['stock.change.product.qty'].create(stock_vals)
                                            if created_qty_on_hand:
                                                created_qty_on_hand.change_product_qty()                                            
                                        
                                        
                                        
                                        
                                                        
                                
                                if created_product_tmpl and  has_variant:
                                    pro_attr_line_obj = self.env['product.attribute.line']
                                    pro_attr_value_obj = self.env['product.attribute.value']
                                    pro_attr_obj = self.env['product.attribute']
                                    if sheet.cell(row,13).value.strip() not in (None,"") and sheet.cell(row,14).value.strip() not in (None,""):
                                        attr_ids_list = []
                                        for attr in sheet.cell(row,13).value.split(','):
                                            attr = attr.strip()
                                            if attr != '':
                                                search_attr_name = False
                                                search_attr_name = pro_attr_obj.search([('name','=', attr )], limit = 1)
                                                if not search_attr_name:
                                                    search_attr_name = pro_attr_obj.create({'name' : attr })
                                                attr_ids_list.append(search_attr_name.id)
                                        attr_value_list = []
                                        for attr_value in sheet.cell(row,14).value.split(','):
                                            attr_value = attr_value.strip()
                                            if attr_value != '':
                                                attr_value_list.append(attr_value)
                                        
                                        attr_value_ids_list = []
                                        if len(attr_ids_list) == len(attr_value_list):
                                            i = 0
                                            while i < len(attr_ids_list):
                                                search_attr_value = False
                                                search_attr_value = pro_attr_value_obj.search([('name','=',attr_value_list[i])], limit = 1)
                                                
                                                if not search_attr_value:
                                                    search_attr_value = pro_attr_value_obj.create({'name' : attr_value_list[i],
                                                                                                   'attribute_id' : attr_ids_list[i]
                                                                                                    })
                                                attr_value_ids_list.append(search_attr_value.id)
                                                i += 1 
                                        else:
                                            skipped_line_no[str(counter)] = " - Number of attributes and it's value not equal. "                                              
                                            counter = counter + 1
                                            continue
                                        if attr_value_ids_list and attr_ids_list:
                                            i = 0
                                            while i < len(attr_ids_list):
                                                search_attr_line = pro_attr_line_obj.search([
                                                                                        ('attribute_id','=',attr_ids_list[i] ),
                                                                                        ('product_tmpl_id','=',created_product_tmpl.id),
                                                                                        ],limit = 1)
                                                if search_attr_line:
                                                    past_values_list = []
                                                    past_values_list = search_attr_line.value_ids.ids
                                                    past_values_list.append( attr_value_ids_list[i] )
                                                    search_attr_line.write({'value_ids': [(6,0, past_values_list  )] })
                                                else:
                                                    created_attr_line = pro_attr_line_obj.create({'attribute_id' : attr_ids_list[i],
                                                                              'value_ids': [(6,0,[ attr_value_ids_list[i] ] )],
                                                                              'product_tmpl_id' : created_product_tmpl.id,
                                                                               })
                                                i += 1 
                                        created_product_tmpl.create_variant_ids()
                                        if created_product_tmpl.product_variant_ids:
                                            for product_varient in created_product_tmpl.product_variant_ids:
                                                if product_varient.attribute_value_ids and product_varient.attribute_value_ids.ids == attr_value_ids_list:

                                                    if sheet.cell(row,15).value not in (None,""):                                         
                                                        var_vals.update({'default_code' : sheet.cell(row,15).value })   
                                                    
                                                    if sheet.cell(row,16).value not in (None,""):
                                                        var_vals.update({'barcode' : sheet.cell(row,16).value })                                                                                                                                                                                                                                                                           
                                                                                                   
                                                    if sheet.cell(row,17).value not in (None,""):
                                                        var_vals.update({'weight' : sheet.cell(row,17).value })       
                                                        
                                                    if sheet.cell(row,18).value not in (None,""):
                                                        var_vals.update({'volume' : sheet.cell(row,18).value })  
                                                        

                                                  
                                                    if product_varient.type == 'product' and sheet.cell(row,19).value != '':
                                                        stock_vals = {'product_tmpl_id' : created_product_tmpl.id,
                                                                      'new_quantity'    : sheet.cell(row,19).value, 
                                                                      'product_id'      : product_varient.id
                                                                      }
                                                        created_qty_on_hand = self.env['stock.change.product.qty'].create(stock_vals)
                                                        if created_qty_on_hand:
                                                            created_qty_on_hand.change_product_qty()    
                                                            
                                                    
                                                    
                                                    
                                                    if sheet.cell(row,20).value.strip() not in (None,""):   
                                                        image_path = sheet.cell(row,20).value.strip()
                                                        if "http://" in image_path or "https://" in image_path:
                                                            try:
                                                                r = requests.get(image_path)
                                                                if r and r.content:
                                                                    image_base64 = base64.encodestring(r.content) 
                                                                    var_vals.update({'image': image_base64})
                                                                else:
                                                                    skipped_line_no[str(counter)] = " - URL not correct or check your image size. "                                            
                                                                    counter = counter + 1                                                
                                                                    continue
                                                            except Exception as e:
                                                                skipped_line_no[str(counter)] = " - URL not correct or check your image size " + ustr(e)   
                                                                counter = counter + 1 
                                                                continue                                              
                                                            
                                                        else:
                                                            try:
                                                                with open(image_path, 'rb') as image:
                                                                    image.seek(0)
                                                                    binary_data = image.read()
                                                                    image_base64 = codecs.encode(binary_data, 'base64')     
                                                                    if image_base64:
                                                                        var_vals.update({'image': image_base64})
                                                                    else:
                                                                        skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this app. "                                            
                                                                        counter = counter + 1                                                
                                                                        continue                                                                       
                                                            except Exception as e:
                                                                skipped_line_no[str(counter)] = " - Could not find the image or please make sure it is accessible to this app. " + ustr(e)   
                                                                counter = counter + 1 
                                                                continue                                                                                                         
                                                    
                                                    product_varient.write(var_vals)
                                                    
                                                    
                                        
                                counter = counter + 1                                                
                            else:
                                skipped_line_no[str(counter)]=" - Name is empty. "  
                                counter = counter + 1                                   
                                
                            
                        except Exception as e:
                            skipped_line_no[str(counter)]=" - Value is not valid. " + ustr(e)   
                            counter = counter + 1 
                            continue          
                            
                except Exception as e:
                    raise UserError(_("Sorry, Your excel file does not match with our format" + ustr(e)))
                
                if counter > 1:
                    completed_records = (counter - len(skipped_line_no)) - 2
                    res = self.show_success_msg(completed_records, skipped_line_no)
                    return res
                            