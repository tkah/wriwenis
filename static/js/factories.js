/*
 * factories.js
 * Creates app data factory, talks to RESTful API
 * Called from controllers.js
 * Torran Kahleck 9/10/16
 */

(function (angular) {

    'use strict';

    angular.module('factories', [])
        .factory('InputFactory', ['$document', '$rootScope', '$q', '$http',
            function ($document, $rootScope, $q, $http) {
                return {

                    // Call RESTful backend with input data
                    getResponse: function (input) {
                        var deferred = $q.defer();

                        // Get response from Flask back-end
                        $http.post('/input', input)
                            .then(function (res) {
                                // Resolve deferred response to front-end
                                deferred.resolve(res);
                            });

                        // Return promise to controller
                        return deferred.promise;
                    }
                }
            }
        ]);

})(angular);