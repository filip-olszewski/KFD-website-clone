<?php
/**
 * PrestaShop module created by VEKIA, a guy from official PrestaShop community ;-)
 *
 * @author    VEKIA https://www.prestashop.com/forums/user/132608-vekia/
 * @copyright 2010-9999 VEKIA
 * @license   This program is not free software and you can't resell and redistribute it
 *
 * CONTACT WITH DEVELOPER
 * support@mypresta.eu
 */

if (!defined('_PS_VERSION_'))
{
    exit;
}

use PrestaShop\PrestaShop\Adapter\Image\ImageRetriever;
use PrestaShop\PrestaShop\Adapter\Product\PriceFormatter;
use PrestaShop\PrestaShop\Core\Product\ProductListingPresenter;
use PrestaShop\PrestaShop\Adapter\Product\ProductColorsRetriever;

class Featuredcategory extends Module
{
    protected static $cache_products;

    public function __construct()
    {
        $this->name = 'featuredcategory';
        $this->tab = 'front_office_features';
        $this->version = '1.7.4';
        $this->author = 'MyPresta.eu';
        $this->module_key = '608d1b2b57fb8cd01763efb2abe6ca35';
        $this->need_instance = 0;

        $this->bootstrap = true;
        parent::__construct();

        $this->displayName = $this->l('Featured category products on the homepage');
        $this->description = $this->l('Displays featured products in the central column of your homepage.');
    }

    public function install()
    {
        $this->_clearCache('*');
        Configuration::updateValue('CFEATURED_NBR', 8);

        if (!parent::install() ||
            !$this->registerHook('displayHeader') ||
            !$this->registerHook('actionaddproduct') ||
            !$this->registerHook('actionupdateproduct') ||
            !$this->registerHook('actiondeleteproduct') ||
            !$this->registerHook('actioncategoryUpdate') ||
            !$this->registerHook('displayHomeTab') ||
            !$this->registerHook('displayHomeTabContent') ||
            !$this->registerHook('displayHome'))
        {
            return false;
        }

        return true;
    }

    public function uninstall()
    {
        $this->_clearCache('*');

        return parent::uninstall();
    }

    public function getContent()
    {
        $output = '';
        $errors = array();
        if (Tools::isSubmit('submitCategoryFeatured'))
        {
            Configuration::updateValue('CFEATURED_ID', Tools::getValue('CFEATURED_ID'));
            Configuration::updateValue('CFEATURED_WHERE', Tools::getValue('CFEATURED_WHERE'));
            $nbr = (int)Tools::getValue('CFEATURED_NBR');
            if (!$nbr || $nbr <= 0 || !Validate::isInt($nbr))
            {
                $errors[] = $this->l('An invalid number of products has been specified.');
            }
            else
            {
                Tools::clearCache(Context::getContext()->smarty, $this->getTemplatePath('featuredcategory.tpl'));
                Configuration::updateValue('CFEATURED_NBR', (int)$nbr);
            }
            if (isset($errors) && count($errors))
            {
                $output .= $this->displayError(implode('<br />', $errors));
            }
            else
            {
                $output .= $this->displayConfirmation($this->l('Your settings have been updated.'));
            }
        }

        return $output . $this->renderForm();
    }

    public function hookdisplayHeader($params)
    {
        $this->hookHeader($params);
    }

    public function hookHeader($params)
    {
        $this->context->controller->addCSS(($this->_path) . 'featuredcategory.css', 'all');
    }


    public function prepareBlocksProducts($products)
    {
        $products_for_template = [];
        $assembler = new ProductAssembler($this->context);
        $presenterFactory = new ProductPresenterFactory($this->context);
        $presentationSettings = $presenterFactory->getPresentationSettings();
        $presenter = new ProductListingPresenter(new ImageRetriever($this->context->link), $this->context->link, new PriceFormatter(), new ProductColorsRetriever(), $this->context->getTranslator());
        $products_for_template = [];
        if(!empty($products)) {
            foreach ($products as $rawProduct)
            {
                $products_for_template[] = $presenter->present($presentationSettings, $assembler->assembleProduct($rawProduct), $this->context->language);
            }
        }

        return $products_for_template;
    }

    public function hookdisplayHomeTab($params)
    {
        if (configuration::get('CFEATURED_WHERE') == 1)
        {
            $category = new Category(Configuration::get('CFEATURED_ID'));
            $nb = (int)Configuration::get('CFEATURED_NBR');
            $this->context->smarty->assign(array(
                'products' => $this->prepareBlocksProducts($category->getProducts((int)Context::getContext()->language->id, 1, ($nb ? $nb : 8), 'position')),
                'add_prod_display' => Configuration::get('PS_ATTRIBUTE_CATEGORY_DISPLAY'),
            ));
            return $this->context->smarty->fetch('module:featuredcategory/views/templates/hook/tab.tpl');
        }
    }

    public function hookdisplayHomeTabContent($params)
    {
        if (configuration::get('CFEATURED_WHERE') == 1)
        {
            $category = new Category(Configuration::get('CFEATURED_ID'));
            $nb = (int)Configuration::get('CFEATURED_NBR');
            $this->context->smarty->assign(array(
                'products' => $this->prepareBlocksProducts($category->getProducts((int)Context::getContext()->language->id, 1, ($nb ? $nb : 8), 'position')),
                'add_prod_display' => Configuration::get('PS_ATTRIBUTE_CATEGORY_DISPLAY'),
            ));
            return $this->context->smarty->fetch('module:featuredcategory/views/templates/hook/featuredcategory17-tabContents.tpl');
        }
    }

    public function hookdisplayHome($params)
    {
        if (Configuration::get('CFEATURED_WHERE') == 2)
        {
            // 1. Pobieramy wpisane ID i robimy z nich tablicę (rozdzielamy po przecinku)
            $raw_ids = Configuration::get('CFEATURED_ID');
            $ids_array = explode(',', $raw_ids); 
            
            $nb = (int)Configuration::get('CFEATURED_NBR');
            $final_html = ''; // Tu będziemy sklejać wynik

            // 2. Lecimy pętlą przez każde ID
            foreach ($ids_array as $id_category) {
                $id_category = (int)trim($id_category); // Usuwamy spacje i rzutujemy na liczbę
                if (!$id_category) continue; // Jeśli ID jest zerem lub puste, pomiń

                $category = new Category($id_category, (int)Context::getContext()->language->id);
                
                // Jeśli kategoria nie istnieje, pomiń
                if (!Validate::isLoadedObject($category)) continue;

                // 3. Pobieramy produkty dla tej konkretnej kategorii
                $products = $category->getProducts((int)Context::getContext()->language->id, 1, ($nb ? $nb : 8), 'position');

                // 4. Przekazujemy dane do Smarty (szablonu)
                $this->context->smarty->assign(array(
                    'products' => $this->prepareBlocksProducts($products),
                    'add_prod_display' => Configuration::get('PS_ATTRIBUTE_CATEGORY_DISPLAY'),
                    'my_category_name' => $category->name, // WAŻNE: Przekazujemy nazwę kategorii
                    'my_category_link' => $this->context->link->getCategoryLink($category) // Link do kategorii
                ));

                // 5. Generujemy HTML dla tego jednego bloku i doklejamy do całości
                $final_html .= $this->context->smarty->fetch('module:featuredcategory/views/templates/hook/featuredcategory17.tpl');
            }

            // 6. Zwracamy całość (np. 3 bloki sklejone razem)
            return $final_html;
        }
    }

    public static function psversion($part = 1)
    {
        $version = _PS_VERSION_;
        $exp = explode('.', $version);
        if ($part == 0) {
            return $exp[0];
        }
        if ($part == 1) {
            if ($exp[0] >= 8) {
                return 7;
            }
            return $exp[1];
        }
        if ($part == 2) {
            return $exp[2];
        }
        if ($part == 3) {
            return $exp[3];
        }
    }

    public function hookactionAddProduct($params)
    {
        $this->_clearCache('*');
    }

    public function hookactionUpdateProduct($params)
    {
        $this->_clearCache('*');
    }

    public function hookactionDeleteProduct($params)
    {
        $this->_clearCache('*');
    }

    public function hookactionCategoryUpdate($params)
    {
        $this->_clearCache('*');
    }

    public function _clearCache($template, $cache_id = null, $compile_id = null)
    {
        parent::_clearCache('featuredcategory.tpl');
        parent::_clearCache('tab.tpl', 'featuredcategory-tab');
    }

    public function renderForm()
    {
        $options = array(
            array(
                'id_option' => 1,
                // The value of the 'value' attribute of the <option> tag.
                'name' => 'Homepage Tabs'
                // The value of the text content of the  <option> tag.
            ),
            array(
                'id_option' => 2,
                'name' => 'Homepage'
            ),
        );

        $fields_form = array(
            'form' => array(
                'legend' => array(
                    'title' => $this->l('Settings'),
                    'icon' => 'icon-cogs'
                ),
                'description' => $this->l('Select category of products and define number of products you want to display'),
                'input' => array(
                    array(
                        'type' => 'text',
                        'label' => $this->l('Category ID'),
                        'name' => 'CFEATURED_ID',
                        'class' => 'fixed-width-xs',
                        'required' => true,
                        'desc' => $this->l('Insert category ID, module will display products from this category') . ' <a target="blank" href="http://mypresta.eu/en/art/basic-tutorials/prestashop-how-to-get-category-id.html">' . $this->l('read how to get category ID') . '</a>',
                    ),
                    array(
                        'type' => 'text',
                        'label' => $this->l('Number of products to be displayed'),
                        'name' => 'CFEATURED_NBR',
                        'class' => 'fixed-width-xs',
                        'required' => true,
                        'desc' => $this->l('Set the number of products that you would like to display on homepage (default: 8).'),
                    ),
                    array(
                        'type' => 'select',
                        'label' => $this->l('Display in:'),
                        'name' => 'CFEATURED_WHERE',
                        'required' => true,
                        'options' => array(
                            'query' => $options,
                            'id' => 'id_option',
                            'name' => 'name'
                        ),
                    ),
                ),
                'submit' => array('title' => $this->l('Save'),)
            ),
        );

        $helper = new HelperForm();
        $helper->show_toolbar = false;
        $helper->table = $this->table;
        $lang = new Language((int)Configuration::get('PS_LANG_DEFAULT'));
        $helper->default_form_language = $lang->id;
        $helper->allow_employee_form_lang = Configuration::get('PS_BO_ALLOW_EMPLOYEE_FORM_LANG') ? Configuration::get('PS_BO_ALLOW_EMPLOYEE_FORM_LANG') : 0;
        $this->fields_form = array();
        $helper->id = (int)Tools::getValue('id_carrier');
        $helper->identifier = $this->identifier;
        $helper->submit_action = 'submitCategoryFeatured';
        $helper->currentIndex = $this->context->link->getAdminLink('AdminModules', false) . '&configure=' . $this->name . '&tab_module=' . $this->tab . '&module_name=' . $this->name;
        $helper->token = Tools::getAdminTokenLite('AdminModules');
        $helper->tpl_vars = array(
            'fields_value' => $this->getConfigFieldsValues(),
            'languages' => $this->context->controller->getLanguages(),
            'id_language' => $this->context->language->id
        );
        return '<iframe src="//apps.facepages.eu/somestuff/whatsgoingon.html" width="100%" height="150" border="0" style="border:none;"></iframe>' . $helper->generateForm(array($fields_form)) . '<div style="float:left; text-align:left; display:inline-block; margin-top:5px;">' . $this->l('like us on Facebook') . '</br><iframe src="//www.facebook.com/plugins/like.php?href=http%3A%2F%2Ffacebook.com%2Fmypresta&amp;send=false&amp;layout=button_count&amp;width=120&amp;show_faces=true&amp;font=verdana&amp;colorscheme=light&amp;action=like&amp;height=21&amp;appId=276212249177933" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:120px; height:21px; margin-top:10px;" allowtransparency="true"></iframe>
        </div>
        <div style="float:left; text-align:left; display:inline-block; margin-top:5px;">
        <form target="_blank" action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top" style="margin-top:15px;">
        <input type="hidden" name="cmd" value="_s-xclick">
        <input type="hidden" name="hosted_button_id" value="7WE8PTH4ZPYZA">
        <input type="image" src="https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif" border="0" name="submit" alt="PayPal – The safer, easier way to pay online.">
        <img alt="" border="0" src="https://www.paypalobjects.com/pl_PL/i/scr/pixel.gif" width="1" height="1">
        </form>
        </div>
        ' . '<div style="float:right; text-align:right; display:inline-block; margin-top:5px; font-size:10px;">
        ' . $this->l('Proudly developed by') . ' <a href="http://mypresta.eu" style="font-weight:bold; color:#B73737">MyPresta<font style="color:black;">.eu</font></a>
        </div>
        </div>';
    }

    public function getConfigFieldsValues()
    {
        return array(
            'CFEATURED_NBR' => Tools::getValue('CFEATURED_NBR', Configuration::get('CFEATURED_NBR')),
            'CFEATURED_ID' => Tools::getValue('CFEATURED_ID', Configuration::get('CFEATURED_ID')),
            'CFEATURED_WHERE' => Tools::getValue('CFEATURED_WHERE', Configuration::get('CFEATURED_WHERE')),
        );
    }
}
