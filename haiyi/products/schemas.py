PRODUCT_SCHEMAS = {
    "internal": [
                ('model_id', 'str'),
                ('real_name', 'str'),
                ('quantity', 'int'),
                ('real_cost', 'float'),
                ('market_cost', 'float'),
                ('price_3w', 'float'),
                ('price_1w', 'float'),
                ('price_3k', 'float'),
                ('price_retail', 'float'),
                ('hot', 'str'),
                ('difficulty', 'str')
            ],
    "external": [
                ('model_id', 'str'),
                ('real_name', 'str'),
                ('price', 'int')
            ]
}