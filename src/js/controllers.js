/*
 * controllers.js
 * Controls the majority of the web app's functionality
 * Acts as intermediary between model and views
 * Some smaller state controllers defined in app.js
 * Torran Kahleck 9/10/16
 */

(function (angular) {

    'use strict';

    angular.module('controllers', [])
    /*
            Code to executre before,during, after state changes goes here
         */
        .run(['$rootScope', '$state', '$stateParams',
            function ($rootScope, $state, $stateParams) {
                $rootScope.$on('$stateChangeStart', function (event, next) {

                });

                $rootScope.$on('$stateChangeSuccess',
                    function(event, toState, toParams, fromState, fromParams) {

                    }
                )
            }
        ])

        /*
            Web app client logic
         */
        .controller('TopCtrl', ['$rootScope', '$scope', 'InputFactory', '$timeout',
            function ($rootScope, $scope, InputFactory, $timeout) {
                $scope.user = {};
                $scope.messages = [];
                $scope.resp = false;
                $scope.chatStarted = false;
                $scope.genderChosen = false;

                // Variables used to track user name and other bookkeeping for back end
                var since_name_check = 15;
                var since_profession_check = 0;
                var lastOutput = "";
                var lastInput = "";
                var location = "";
                var author = "You";

                var userAvatar = "";
                var acolytes = [{name: "Turner", avatar: "supportmale.svg"},{name: "Howard", avatar: "supportmale.svg"},{name: "Stacy", avatar: "supportfemale.svg"},{name: "Donna", avatar: "supportfemale.svg"}];

                $scope.acolyte = acolytes[Math.floor(Math.random()*acolytes.length)];
                
                var femaleAvatars = ["female.svg","maturewoman.svg"];
                var maleAvatars = ["matureman1.svg","matureman2.svg"];

                $scope.countDownStart = Math.floor(Math.random() * 10) + 5;

                // Gender determines the avatar class used
                $scope.setGender = function(gender) {


                    if (gender == 'm') {
                        userAvatar = maleAvatars[Math.floor(Math.random() * maleAvatars.length)];
                    }
                    else {
                        userAvatar = femaleAvatars[Math.floor(Math.random() * femaleAvatars.length)];
                    } 

                    // Display text prompt
                    $scope.genderChosen = true;

                    var countDownFunction = function() {
                        if ($scope.countDownStart == 0) {
                            $scope.submitInput("Hello");
                        }
                        else {
                            $scope.countDownStart --;
                            countDown = $timeout(countDownFunction, 1000);
                        }
                    };

                    var countDown = $timeout(countDownFunction, 1000);

                };

                // Submit user input to backend for response
                $scope.submitInput = function(input) {
                    $scope.resp = true;
                    var newMsg = {author: author, text: input, avatar: "/static/img/" + userAvatar, lastOutput: lastOutput, lastInput: lastInput, since_name_check: since_name_check, since_profession_check: since_profession_check, location: location, acolyte: $scope.acolyte.name};
                    if ($scope.messages.length > 0) $scope.messages.push(newMsg);

                    lastInput = input;
                    $scope.user.msg = null;

                    // Get response from server -- InputFactory is in js/factories.js
                    InputFactory.getResponse(newMsg)
                        .then(function(res) {
                            $scope.resp = false;
                            lastOutput = res.data.output;
                            author = res.data.author;
                            since_name_check = res.data.since_name_check;
                            since_profession_check = res.data.since_profession_check;
                            location = res.data.location;
                            $scope.chatStarted = true;

                            $scope.messages.push({author: "Acolyte " + $scope.acolyte.name, text: res.data.output, avatar: "/static/img/" + $scope.acolyte.avatar});
                        });
                }
            }
        ]);

})(angular);