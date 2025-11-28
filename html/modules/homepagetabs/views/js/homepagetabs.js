/**
 * PrestaShop module created by VEKIA, a guy from official PrestaShop community ;-)
 *
 * @author    VEKIA PL MILOSZ MYSZCZUK VATEU: PL9730945634
 * @copyright 2010-2025 VEKIA
 * @license   This program is not free software and you can't resell and redistribute it
 *
 * CONTACT WITH DEVELOPER http://mypresta.eu
 * support@mypresta.eu
 */

$(document).ready(function () {
    $('#home-page-tabs li a, #index .tab-content .tab-pane').removeClass('active in');
    $('#home-page-tabs li:first a, #index .tab-content .tab-pane:first').addClass('active in');
    homepageTabsMiniature();
    $('#home-page-tabs li a').click(function () {
        setTimeout(
            function () {
                homepageTabsMiniature()
            }, 400);
    });
});

function homepageTabsMiniature(){

}