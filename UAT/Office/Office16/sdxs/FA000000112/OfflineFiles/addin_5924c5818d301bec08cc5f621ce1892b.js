// The initialize function must be run each time a new page is loaded
(function () {
    try {
        Office.initialize = function (reason) {
            $(document).ready(function () {
                OfficeFirstPartyAuth.debugging = true;
                OfficeFirstPartyAuth.delay = 5000;
                OfficeFirstPartyAuth.authFlow = "authcode";
                OfficeFirstPartyAuth.autoVersion = "flight";
                // OfficeFirstPartyAuth.autoPopup = true;

                OfficeFirstPartyAuth.load().then(
                    function () {
                        console.log("Initialized BrowserAuth.load");

                        $("#getAuthContext").prop("disabled", false);
                        $("#getAccessToken1").prop("disabled", false);
                        $("#getAccessToken2").prop("disabled", false);
                        $("#getAccessToken3").prop("disabled", false);
                        $("#getAccessToken4").prop("disabled", false);
                    },
                    function (rejected) {
                        //TODO enable them just if the host is BlueChicken
                        $("#getAuthContext").prop("disabled", false);

                        $("#tokenText").text(JSON.stringify(rejected));
                        console.log('========================================================================================================');
                    }
                );

                $("#getAuthContext").click(function (event) {
                    callGetAuthContext();
                });
                $("#getAccessToken1").click(function (event) {
                    callGetAccessToken(false, false);
                });
                $("#getAccessToken2").click(function (event) {
                    callGetAccessToken(true, false);
                });
                $("#getAccessToken3").click(function (event) {
                    callGetAccessToken(false, true);
                });
                $("#getAccessToken4").click(function (event) {
                    callGetAccessToken(true, true);
                });
            });
        }
    } catch (e) {
        console.log("Office.initialize throws exception:" + e);
    }

    function callGetAuthContext() {
        Office.context.webAuth.getAuthContextAsync(function (result) {
            $("#authText").text(JSON.stringify(result));
        });
    }

    function callGetAccessToken(popup, forceRefresh) {
        var resource = $("#resourceInput").val();

        var tokenParams = {
            'resource': resource,
            'authChallenge': '',
            'policy': ''
        };

        var behaviorParam = {
            'popup': popup,
            'forceRefresh': forceRefresh
        };

        var token = OfficeFirstPartyAuth.getAccessToken(tokenParams, behaviorParam);
        token.then(
            function (resolved) {
                console.log("resolved token");
                console.log(resolved);
                $("#tokenText").text(resolved.accessToken);
            },
            function (rejected) {
                console.log("rejected token");
                console.log(rejected);
                $("#tokenText").text(JSON.stringify(rejected));
            });
    }
})();