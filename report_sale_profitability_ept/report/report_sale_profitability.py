from odoo import api, fields, models, tools


class Sales_Report(models.Model):
    # Private attributes
    _name = "sales.report.ept"
    _description = "Sales Profitability Report"
    _order = "date desc"
    _auto = False
    
    # Fields declaration
    product_id = fields.Many2one("product.product",string="Product",index=True,help="Product")
    delivered_qty = fields.Float(string="Delivered Qty",default=0.0,help="Delivered Qty")
    return_qty = fields.Float(string="Returned Qty",default=0.0,help="Returned Qty")
    company_id = fields.Many2one("res.company",string="Company",help="Company")
    return_rate = fields.Float(string="Return Rate",default=0.0,help="Return Rate")
    value = fields.Float(string="Sales Value",default=0.0,help="Value")
    cost  = fields.Float(string="Cost",default=0.0,help="Cost")
    profit = fields.Float(string="Profit",default=0.0,help="Profit")
    profitability = fields.Float(string="Profitability",default=0.0,help="Profitability")
    date = fields.Date(string="Date", index=True)
    
    def get_profitability_report(self):
        request = """
            CREATE OR REPLACE VIEW %s AS (
                with sales as (
                    select 
                    ROW_NUMBER() over() AS id,
                    company_id,
                    product_id
                    ,date::date,
                    sum(delivered_qty) as delivered_qty, 
                    sum(return_qty) as return_qty, 
                    max(sale_price_unit) as delivery_unit_price,
                    max(return_price_unit) as return_unit_price, 
                    max(sale_cost) as delivery_cost, 
                    max(return_cost) as return_cost 
                    from
                     (
                        select 
                        stock_move.company_id as company_id,
                        stock_move.product_id,
                        stock_move.date as date,
                        sum(product_qty) as delivered_qty,
                        0 as return_qty,
                        sum(round((price_subtotal/sale_order_line.product_uom_qty),2)) as sale_price_unit,
                        0 as return_price_unit,
                        sum(abs(stock_move.price_unit)) as sale_cost ,
                        0 as return_cost
                        from stock_move 
                        inner join stock_location on stock_location.id=stock_move.location_dest_id and stock_location.usage='customer'
                        inner join sale_order_line on sale_order_line.id=stock_move.sale_line_id 
                        where stock_move.state='done' 
                        group by stock_move.product_id,sale_order_line.product_uom_qty,stock_move.date,stock_move.company_id
                    
                        Union All

                        select 
                        stock_move.company_id as company_id,
                        stock_move.product_id,                        
                        stock_move.date as date,
                        sum(product_qty) as delivered_qty,
                        0 as return_qty,
                        sum(round((price_subtotal/pos_order_line.qty),2)) as sale_price_unit,                    
                        0 as return_price_unit,
                        sum(abs(stock_move.price_unit)) as sale_cost ,
                        0 as return_cost
                        from stock_move 
                        inner join stock_location on stock_location.id=stock_move.location_dest_id and stock_location.usage='customer'                       
                        inner join pos_order on pos_order.picking_id = stock_move.picking_id 
                        inner join pos_order_line on pos_order_line.order_id = pos_order.id and pos_order_line.product_id = stock_move.product_id
                        where stock_move.state='done' 
                        group by stock_move.product_id,stock_move.date,pos_order_line.qty,stock_move.company_id                        
                        
                        Union All
                        
                        select 
                        stock_move.company_id as company_id,
                        stock_move.product_id,
                        Date(stock_move.date),
                        0 as delivered_qty,
                        sum(product_qty) as return_qty,
                        0 as sale_price_unit,
                        sum(round((price_subtotal/sale_order_line.product_uom_qty),2)) as return_price_unit,
                        0 as sale_cost,
                        sum(abs(stock_move.price_unit)) as return_cost
                        from stock_move 
                        inner join stock_location on stock_location.id=stock_move.location_id and stock_location.usage='customer'
                        inner join sale_order_line on sale_order_line.id=stock_move.sale_line_id 
                        where stock_move.state='done'
                        group by stock_move.company_id,stock_move.product_id,sale_order_line.product_uom_qty,stock_move.date
                                                
                        Union All

                        select 
                        stock_move.company_id as company_id,
                        stock_move.product_id,
                        Date(stock_move.date),
                        0 as delivered_qty,
                        sum(product_qty) as return_qty,
                        0 as sale_price_unit,
                        sum(round((price_subtotal/pos_order_line.qty),2)) as return_price_unit,
                        0 as sale_cost,
                        sum(abs(stock_move.price_unit)) as return_cost
                        from stock_move 
                        inner join stock_location on stock_location.id=stock_move.location_id and stock_location.usage='customer'
                        inner join pos_order on pos_order.picking_id = stock_move.picking_id 
                        inner join pos_order_line on pos_order_line.order_id = pos_order.id  and pos_order_line.product_id = stock_move.product_id
                        where stock_move.state='done'
                        group by stock_move.company_id,stock_move.product_id,pos_order_line.qty,stock_move.date                        
                        )T2
                        Group by company_id,product_id,date::date
                )
         select 
            id,
            company_id,
            product_id,
            date,
            delivered_qty,
            return_qty,
            round((return_qty/(CASE delivered_qty WHEN 0 Then 1 ELSE delivered_qty END)),2) as return_rate,
            (delivery_unit_price*delivered_qty-return_unit_price*return_qty) as value,
            (delivery_cost*delivered_qty-return_cost*return_qty) as cost,
            (delivery_unit_price*delivered_qty-return_unit_price*return_qty)-(delivery_cost*delivered_qty-return_cost*return_qty) as profit,
            ((delivery_unit_price*delivered_qty-return_unit_price*return_qty)-(delivery_cost*delivered_qty-return_cost*return_qty))/(CASE delivery_unit_price WHEN 0 Then 1 ELSE delivery_unit_price END) as profitability
            from sales
            );
        """ % (self._table)        
        return request
    
    @api.model_cr
    def init(self):
        """
            This is special method and this is automatically call when class object is created.   
        """
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(self.get_profitability_report())