# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

{
    'name':'Theme Blue Boy',
    'description':'Theme Blue Boy By 73Lines',
    'category': 'Theme/Ecommerce',
    'version':'1.3',
    'author':'73Lines',
    'data': [
         
         #Snippets
         
         'snippets/s_navbar_menu_mega.xml',
         'snippets/s_navbar_menu_mid.xml',
         'snippets/s_navbar_menu_small.xml',
         'snippets/s_footer_one.xml',
         
         #Templates
         'views/assets.xml',
         'views/navbar_template.xml',
         'views/theme_mid_header_template.xml',
         'views/website_sale_template.xml',
    #     'views/rating_template.xml',
         'views/products_template.xml',
         'views/attribute_filter_template.xml',
         'views/product_collapse_categories_template.xml',
         'views/customize_model.xml',
         'data/footer_template.xml',
    ],
    
    'demo':[
         'data/navbar_demo.xml',
         'data/brand_demo.xml',
         'data/blog_post_demo.xml',
         'data/homepage.xml',
            ],
            
    'depends': [
                
                #Default Modules
                
                'website',
                'website_sale',
                'website_less',        
                'website_blog',
                
                # 73lines Depend Modules
                
                # Don't forget to see README file in order to how to install
                # In order to install complete theme, uncomment the following dependency.
                # Dependent modules are supplied in a zip file along with the theme, 
                # if you have not received it,please contact us at enquiry@73lines.com with proof of your purchase. 
                
                'snippet_blog_carousel_73lines',
                'snippet_boxed_73lines',
                'snippet_brand_carousel_73lines',
                'snippet_object_carousel_73lines',
                'snippet_product_carousel_73lines',
                'snippet_product_category_carousel_73lines',
                'snippet_recently_viewed_products_carousel_73lines',
                'website_category_banner_73lines',
                'website_customize_model_73lines',
                'website_language_flag_73lines',
                'website_mega_menu_73lines',
                'website_mid_header_73lines',
                'website_mid_header_sale_73lines',
                'website_product_by_brand_73lines',
                'website_product_content_block_73lines',
                'website_product_features_73lines',
                'website_product_multi_image_73lines',
                'website_product_price_filter_73lines',
                'website_product_share_button_73lines',
                'website_product_sorting_73lines',
                'website_product_tags_73lines',
                'website_user_wishlist_73lines',
                ],
    'images': [
        'static/description/blueboy-banner.png',
    ],
    'price': 200,
    'currency': 'EUR',
    'live_test_url': 'http://theme-blueboy.73lines.com/'
}