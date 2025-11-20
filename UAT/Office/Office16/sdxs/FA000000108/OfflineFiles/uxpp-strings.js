"use strict";
/* tslint:disable */ var UxppStrings = { "SpinnerLoadingLabel": "Loading...", "RaiseTestEventLabel": "Raise a test event" };
var UxppStringsEnum = UxppStrings;
var UxppStringsArray = [];
if (typeof window !== 'undefined' && (window.g_NewStringsInfra === true || window.g_NewStringsInfra === "True")) {
    UxppStringsEnum = Object.keys(UxppStrings).reduce((acc, key, index) => {
        acc[key] = index;
        return acc;
    }, {});
    UxppStringsArray = Object.values(UxppStrings);
}
var UxppStringsManager = {
    UxppStringsArray: UxppStringsArray,
    get: function (x) {
        if (typeof window !== 'undefined' && (window.g_NewStringsInfra === true || window.g_NewStringsInfra === "True")) {
            return UxppStringsArray[x];
        }
        else {
            return x;
        }
    }
};
