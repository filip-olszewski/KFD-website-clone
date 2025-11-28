{**
* PrestaShop module created by VEKIA, a guy from official PrestaShop community ;-)
*
* @author    VEKIA PL MILOSZ MYSZCZUK VATEU: PL9730945634
* @copyright 2010-2025 VEKIA
* @license   This program is not free software and you can't resell and redistribute it
*
* CONTACT WITH DEVELOPER http://mypresta.eu
* support@mypresta.eu
*}

{assign var='HOOK_HOME_TAB_CONTENT' value=Hook::exec('displayHomeTabContent')}
{assign var='HOOK_HOME_TAB' value=Hook::exec('displayHomeTab')}
{if isset($HOOK_HOME_TAB_CONTENT) && $HOOK_HOME_TAB_CONTENT|trim}
    <div class="tabs">
        {if isset($HOOK_HOME_TAB) && $HOOK_HOME_TAB|trim}
            <ul id="home-page-tabs" class="nav nav-tabs clearfix">
                {$HOOK_HOME_TAB nofilter}
            </ul>
        {/if}
        <div class="tab-content" id="tab-content">{$HOOK_HOME_TAB_CONTENT nofilter}</div>
    </div>
{/if}