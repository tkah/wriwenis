/*
 * app.js
 * Creates app module
 * Configures what urls and states reference which partials (stateProvider, urlProvider)
 * Torran Kahleck 9/10/16
 */

(function (angular) {

    'use strict';

    var app = angular.module('app',
        [
            'controllers',
            'luegg.directives',
            'factories',
            'ui.router',
            'ngMaterial',
            'ngMessages',
            'ngAnimate',
            'picardy.fontawesome'
        ])

        // App configuration
        .config(['$compileProvider', '$stateProvider', '$urlRouterProvider',
                function ($compileProvider, $stateProvider, $urlRouterProvider) {

                    $urlRouterProvider
                        .otherwise('/home/');

                    // Match state names to urls and partials
                    $stateProvider
                        .state("home", {
                            url: "/home",
                            templateUrl: 'templates/home.html',
                            controller: "HomeCtrl"
                        });
                }
            ]
        );

})(angular);
