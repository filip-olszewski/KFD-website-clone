{**
* PrestaShop module created by VEKIA, a guy from official PrestaShop community ;-)
*
* @author    VEKIA https://www.prestashop.com/forums/user/132608-vekia/
* @copyright 2010-2015 VEKIA
* @license   This program is not free software and you can't resell and redistribute it
*
* CONTACT WITH DEVELOPER
* support@mypresta.eu
*}

<section id="featuredcategory" class="featured-products tab-pane fade in">
    {if isset($products) && $products}
        <div class="products">
            {foreach from=$products item="product"}
                {include file="catalog/_partials/miniatures/product.tpl" product=$product}
            {/foreach}
        </div>
    {else}
        <ul id="categoryfeatured" class="categoryfeatured tab-pane">
            <li class="alert alert-info">{l s='No featured products at this time.' mod='featuredcategory'}</li>
        </ul>
    {/if}
</section>