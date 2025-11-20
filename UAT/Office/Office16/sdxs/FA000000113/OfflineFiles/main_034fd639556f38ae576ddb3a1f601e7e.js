var TypeScriptModule =
/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/index.ts");
/******/ })
/************************************************************************/
/******/ ({

/***/ "../../node_modules/@ms/oteljs/dist/Activity.js":
/*!********************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/Activity.js ***!
  \********************************************************************************/
/*! exports provided: ActivityScope */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ActivityScope", function() { return ActivityScope; });
/* harmony import */ var _CorrelationVector__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./CorrelationVector */ "../../node_modules/@ms/oteljs/dist/CorrelationVector.js");
/* harmony import */ var _OTelNotifications__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./OTelNotifications */ "../../node_modules/@ms/oteljs/dist/OTelNotifications.js");
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (undefined && undefined.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};


// Currently we only send one activity at a time
var ACTIVITY_COUNT = 1;
// Currently we do not aggregate activities in OTelJS
var ACTIVITY_AGGMODE = 0;
var getCurrentMicroseconds = function () {
    return Date.now() * 1000;
};
if (typeof window === 'object' && typeof window.performance === 'object' && 'now' in window.performance) {
    getCurrentMicroseconds = function () {
        return Math.floor(window.performance.now()) * 1000;
    };
}
/**
 * An activity scope, which automatically records duration and correlation vectors.
 * Activity scopes must have their result set with setResult or setSuccess.
 * The can be auto-ending when created with executeSync/executeAsync,
 * or their scope can be manually managed with createNew and endNow.
 * Child activities can be created with corresponding functions.
 */
var ActivityScope = /** @class */ (function () {
    function ActivityScope(telemetryLogger, activityName, parent) {
        this._optionalEventFlags = {};
        this._ended = false;
        this._telemetryLogger = telemetryLogger;
        this._activityName = activityName;
        if (parent) {
            this._cv = _CorrelationVector__WEBPACK_IMPORTED_MODULE_0__["CorrelationVector"].getNextChild(parent._cv);
        }
        else {
            this._cv = _CorrelationVector__WEBPACK_IMPORTED_MODULE_0__["CorrelationVector"].getNext();
        }
        this._dataFields = [];
        this._success = undefined;
        this._startTime = getCurrentMicroseconds();
    }
    /**
     * Creates a new Activity Scope that will be managed by the caller
     * One of setSuccess or setResult must be called on the scope, followed by endNow.
     * @param telemetryLogger - The telemetry logger that the activity belongs to
     * @param activityName - The name of the activity
     */
    ActivityScope.createNew = function (telemetryLogger, activityName) {
        return new ActivityScope(telemetryLogger, activityName);
    };
    /**
     * Creates an activity parented to the current activity. Does not start the activity.
     * @param activityName - The name of the activity
     */
    ActivityScope.prototype.createChildActivity = function (activityName) {
        var childActivity = new ActivityScope(this._telemetryLogger, activityName, this);
        return childActivity;
    };
    /**
     * Sets optional event flags.
     * @param eventFlags - Event flags to set
     */
    ActivityScope.prototype.setEventFlags = function (eventFlags) {
        this._optionalEventFlags = eventFlags;
    };
    /**
     * Adds a data field to the activity
     * @param dataField - A data field to add
     */
    ActivityScope.prototype.addDataField = function (dataField) {
        this._dataFields.push(dataField);
    };
    /**
     * Adds data fields to the activity
     * @param dataFields - Data fields to add
     */
    ActivityScope.prototype.addDataFields = function (dataFields) {
        var _a;
        (_a = this._dataFields).push.apply(_a, dataFields);
    };
    /**
     * Sets whether the activity succeeded
     * @param success - Whether the activity succeeded
     */
    ActivityScope.prototype.setSuccess = function (success) {
        this._success = success;
    };
    /**
     * Sets the result of the activity
     * @param resultCode - The result code, e.g. 0 for success
     * @param resultType - Optional: The result type, e.g. "HRESULT"
     * @param resultTag - Optional: The result tag
     */
    // tslint:disable-next-line no-reserved-keywords
    ActivityScope.prototype.setResult = function (code, type, tag) {
        this._result = { code: code, type: type, tag: tag };
    };
    /**
     * Ends the activity; records the duration and sends a telemetry event.
     */
    ActivityScope.prototype.endNow = function () {
        if (this._ended) {
            Object(_OTelNotifications__WEBPACK_IMPORTED_MODULE_1__["logNotification"])(_OTelNotifications__WEBPACK_IMPORTED_MODULE_1__["LogLevel"].Error, _OTelNotifications__WEBPACK_IMPORTED_MODULE_1__["Category"].Core, function () { return 'Activity has already ended'; });
            return;
        }
        if (this._success === undefined && this._result === undefined) {
            // The Activity dashboard shows these activities as 'unresolved'
            // but developers generally should avoid leaving activities in this state.
            Object(_OTelNotifications__WEBPACK_IMPORTED_MODULE_1__["logNotification"])(_OTelNotifications__WEBPACK_IMPORTED_MODULE_1__["LogLevel"].Warning, _OTelNotifications__WEBPACK_IMPORTED_MODULE_1__["Category"].Core, function () { return 'Activity does not have success or result set'; });
        }
        var endTime = getCurrentMicroseconds();
        var duration = endTime - this._startTime;
        this._ended = true;
        var activity = {
            duration: duration,
            count: ACTIVITY_COUNT,
            aggMode: ACTIVITY_AGGMODE,
            cV: this._cv.getString(),
            success: this._success,
            result: this._result
        };
        return this._telemetryLogger.sendActivity(this._activityName, activity, this._dataFields, this._optionalEventFlags);
    };
    /**
     * Starts an activity to execute asynchronously
     * You must call setSuccess or setResult on the activity inside the activity body.
     * When the activity body resolves or rejects, the duration is recorded and the activity is sent.
     * The promise resolution is passed through to the caller.
     * @param activityBody - The body of the activity, which should return a promise.
     */
    ActivityScope.prototype.executeAsync = function (activityBody) {
        return __awaiter(this, void 0, void 0, function () {
            var _this = this;
            return __generator(this, function (_a) {
                return [2 /*return*/, activityBody(this)
                        .then(function (result) {
                        _this.endNow();
                        return result;
                    })
                        .catch(function (e) {
                        _this.endNow();
                        throw e;
                    })];
            });
        });
    };
    /**
     * Starts an activity to execute synchronously
     * You must call setSuccess or setResult on the activity inside the activity body.
     * When the function returns, the duration is recorded and the activity is sent. The return value is passed through to the caller.
     * @param activityBody - The body of the activity, which should return a promise.
     */
    ActivityScope.prototype.executeSync = function (activityBody) {
        try {
            var ret = activityBody(this);
            this.endNow();
            return ret;
        }
        catch (e) {
            this.endNow();
            throw e;
        }
    };
    /**
     * Starts an activity to execute asynchronously, parented to the current activity.
     * @param activityName - The name of the activity
     * @param activityBody - The body of the activity
     */
    ActivityScope.prototype.executeChildActivityAsync = function (activityName, activityBody) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, this.createChildActivity(activityName).executeAsync(activityBody)];
            });
        });
    };
    /**
     * Starts an activity to execute synchronously, parented to the current activity.
     * @param activityName - The name of the activity
     * @param activityBody - The body of the activity
     */
    ActivityScope.prototype.executeChildActivitySync = function (activityName, activityBody) {
        return this.createChildActivity(activityName).executeSync(activityBody);
    };
    return ActivityScope;
}());

//# sourceMappingURL=Activity.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/Contract.js":
/*!********************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/Contract.js ***!
  \********************************************************************************/
/*! exports provided: addContractField */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "addContractField", function() { return addContractField; });
/* harmony import */ var _DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./DataFieldHelper */ "../../node_modules/@ms/oteljs/dist/DataFieldHelper.js");

/**
 * Add a metadata field to the list of data fields indicating that a specific contract has been used.
 * For example, we might add the data field zC.MySdx: Office.System.SDX, which indicates that
 * the fields under MySdx conform to the Office.System.SDX contract.
 * @param dataFields - The list of data fields, to which a contract field will be added
 * @param instanceName - The instance of the contract. Usually the same as the contract name without its namespace,
 *                       but can be different, especially if you have more than one of the same contract type in a single event.
 * @param contractName - The name of the contract, for example Office.System.SDX
 */
function addContractField(dataFields, instanceName, contractName) {
    dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])("zC." + instanceName, contractName));
}
//# sourceMappingURL=Contract.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/CorrelationVector.js":
/*!*****************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/CorrelationVector.js ***!
  \*****************************************************************************************/
/*! exports provided: CorrelationVector */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CorrelationVector", function() { return CorrelationVector; });
var CorrelationVector;
(function (CorrelationVector) {
    var baseHash;
    var baseId = 0;
    /**
     * Get a new correlation vector representing the next event in sequence
     */
    function getNext() {
        if (baseHash === undefined) {
            baseHash = generatePseudoHash();
        }
        return new CV(baseHash, ++baseId);
    }
    CorrelationVector.getNext = getNext;
    /**
     * Get a new correlation vector parented to this one
     * @param parent
     */
    function getNextChild(parent) {
        return new CV(parent.getString(), ++parent.nextChild);
    }
    CorrelationVector.getNextChild = getNextChild;
    var CV = /** @class */ (function () {
        function CV(base, id) {
            this.base = base;
            this.id = id;
            this.nextChild = 0;
        }
        CV.prototype.getString = function () {
            return this.base + "." + this.id;
        };
        return CV;
    }());
    CorrelationVector.CV = CV;
    function generatePseudoHash() {
        var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        var hashLength = 22;
        var result = [];
        for (var i = 0; i < hashLength; i++) {
            // tslint:disable: insecure-random (security is not a concern here and secure crypto function is not available on all platform)
            result.push(characters.charAt(Math.floor(Math.random() * characters.length)));
        }
        return result.join('');
    }
})(CorrelationVector || (CorrelationVector = {}));
//# sourceMappingURL=CorrelationVector.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/CustomContract.js":
/*!**************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/CustomContract.js ***!
  \**************************************************************************************/
/*! exports provided: getFieldsForContract */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getFieldsForContract", function() { return getFieldsForContract; });
/* harmony import */ var _Contract__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./Contract */ "../../node_modules/@ms/oteljs/dist/Contract.js");

/**
 * Get fields for a 'custom' contract that doesn't ship with OTel.js
 * You pass in the parameters for a contract, and this function returns the data fields in TelemetryEvent.dataFields format.
 * @param instanceName - The instance of the contract. Usually the same as the contract name without its namespace,
 *                       but can be different, especially if you have more than one of the same contract type in a single event.
 * @param contractName - The name of the contract, for example Office.System.SDX
 * @param contractFields - The data fields in the contract.
 */
function getFieldsForContract(instanceName, contractName, contractFields) {
    var dataFields = contractFields.map(function (contractField) {
        return {
            name: instanceName + "." + contractField.name,
            value: contractField.value,
            dataType: contractField.dataType
        };
    });
    Object(_Contract__WEBPACK_IMPORTED_MODULE_0__["addContractField"])(dataFields, instanceName, contractName);
    return dataFields;
}
//# sourceMappingURL=CustomContract.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/DataClassification.js":
/*!******************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/DataClassification.js ***!
  \******************************************************************************************/
/*! exports provided: DataClassification */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "DataClassification", function() { return DataClassification; });
var DataClassification;
(function (DataClassification) {
    // tslint:disable:no-bitwise
    DataClassification[DataClassification["EssentialServiceMetadata"] = 1] = "EssentialServiceMetadata";
    DataClassification[DataClassification["AccountData"] = 2] = "AccountData";
    DataClassification[DataClassification["SystemMetadata"] = 4] = "SystemMetadata";
    DataClassification[DataClassification["OrganizationIdentifiableInformation"] = 8] = "OrganizationIdentifiableInformation";
    DataClassification[DataClassification["EndUserIdentifiableInformation"] = 16] = "EndUserIdentifiableInformation";
    DataClassification[DataClassification["CustomerContent"] = 32] = "CustomerContent";
    DataClassification[DataClassification["AccessControl"] = 64] = "AccessControl";
})(DataClassification || (DataClassification = {}));
//# sourceMappingURL=DataClassification.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/DataField.js":
/*!*********************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/DataField.js ***!
  \*********************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

//# sourceMappingURL=DataField.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/DataFieldHelper.js":
/*!***************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/DataFieldHelper.js ***!
  \***************************************************************************************/
/*! exports provided: makeBooleanDataField, makeInt64DataField, makeDoubleDataField, makeStringDataField, makeGuidDataField */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "makeBooleanDataField", function() { return makeBooleanDataField; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "makeInt64DataField", function() { return makeInt64DataField; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "makeDoubleDataField", function() { return makeDoubleDataField; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "makeStringDataField", function() { return makeStringDataField; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "makeGuidDataField", function() { return makeGuidDataField; });
/* harmony import */ var _DataFieldType__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./DataFieldType */ "../../node_modules/@ms/oteljs/dist/DataFieldType.js");
/* harmony import */ var _DataClassification__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./DataClassification */ "../../node_modules/@ms/oteljs/dist/DataClassification.js");


/**
 * Make a boolean data field.
 * @param name - The name of the data field
 * @param value - The value of the data field
 */
function makeBooleanDataField(name, value) {
    return {
        name: name,
        dataType: _DataFieldType__WEBPACK_IMPORTED_MODULE_0__["DataFieldType"].Boolean,
        value: value,
        classification: _DataClassification__WEBPACK_IMPORTED_MODULE_1__["DataClassification"].SystemMetadata
    };
}
/**
 * Make a data field corresponding to the Aria Int64 data type. Note that
 * JavaScript doesn't actually support Int64 precision on large numbers.
 * @param name - The name of the data field
 * @param value - The value of the data field
 */
function makeInt64DataField(name, value) {
    return {
        name: name,
        dataType: _DataFieldType__WEBPACK_IMPORTED_MODULE_0__["DataFieldType"].Int64,
        value: value,
        classification: _DataClassification__WEBPACK_IMPORTED_MODULE_1__["DataClassification"].SystemMetadata
    };
}
/**
 * Make a double data field
 * @param name - The name of the data field
 * @param value - The value of the data field
 */
function makeDoubleDataField(name, value) {
    return {
        name: name,
        dataType: _DataFieldType__WEBPACK_IMPORTED_MODULE_0__["DataFieldType"].Double,
        value: value,
        classification: _DataClassification__WEBPACK_IMPORTED_MODULE_1__["DataClassification"].SystemMetadata
    };
}
/**
 * Make a string data field
 * @param name - The name of the data field
 * @param value - The value of the data field
 */
function makeStringDataField(name, value) {
    return {
        name: name,
        dataType: _DataFieldType__WEBPACK_IMPORTED_MODULE_0__["DataFieldType"].String,
        value: value,
        classification: _DataClassification__WEBPACK_IMPORTED_MODULE_1__["DataClassification"].SystemMetadata
    };
}
/**
 * Make a GUID data field
 * !!!WARNING: Only the 1DS Sink has support for Guid types.
 * @param name - The name of the data field
 * @param value - The value of the data field
 */
function makeGuidDataField(name, value) {
    return {
        name: name,
        dataType: _DataFieldType__WEBPACK_IMPORTED_MODULE_0__["DataFieldType"].Guid,
        value: value,
        classification: _DataClassification__WEBPACK_IMPORTED_MODULE_1__["DataClassification"].SystemMetadata
    };
}
//# sourceMappingURL=DataFieldHelper.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/DataFieldType.js":
/*!*************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/DataFieldType.js ***!
  \*************************************************************************************/
/*! exports provided: DataFieldType */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "DataFieldType", function() { return DataFieldType; });
var DataFieldType;
(function (DataFieldType) {
    DataFieldType[DataFieldType["String"] = 0] = "String";
    DataFieldType[DataFieldType["Boolean"] = 1] = "Boolean";
    DataFieldType[DataFieldType["Int64"] = 2] = "Int64";
    DataFieldType[DataFieldType["Double"] = 3] = "Double";
    DataFieldType[DataFieldType["Guid"] = 4] = "Guid";
})(DataFieldType || (DataFieldType = {}));
//# sourceMappingURL=DataFieldType.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/Event.js":
/*!*****************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/Event.js ***!
  \*****************************************************************************/
/*! exports provided: Event */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Event", function() { return Event; });
/* tslint:disable */
// Event implementation.  Allows an object to notify subscribed listeners of an event, passing
// a typed payload for event arguments.  Users of this class should keep the Event<T> private,
// and instead expose the object to the outside via the IEventListeners<T> interface to
// prevent other classes from firing the event.
var Event = /** @class */ (function () {
    function Event() {
        this._listeners = [];
    }
    /**
     * Fires an event to its listeners
     * @param args - The parameters of the event
     */
    Event.prototype.fireEvent = function (args) {
        this._listeners.forEach(function (listener) { return listener(args); });
    };
    /**
     * Add an event listener
     * @param listener - The listener that can process events
     */
    Event.prototype.addListener = function (listener) {
        if (listener) {
            this._listeners.push(listener);
        }
    };
    /**
     * Remove an event listener
     * @param listener - The listener to remove
     */
    Event.prototype.removeListener = function (listener) {
        this._listeners = this._listeners.filter(function (h) { return h !== listener; });
    };
    /**
     * Get the count of event listeners
     */
    Event.prototype.getListenerCount = function () {
        return this._listeners.length;
    };
    return Event;
}());

//# sourceMappingURL=Event.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/EventFlagFiller.js":
/*!***************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/EventFlagFiller.js ***!
  \***************************************************************************************/
/*! exports provided: getEffectiveEventFlags */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "getEffectiveEventFlags", function() { return getEffectiveEventFlags; });
/* harmony import */ var _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./EventFlagsProperties */ "../../node_modules/@ms/oteljs/dist/EventFlagsProperties.js");
/* harmony import */ var ___WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! . */ "../../node_modules/@ms/oteljs/dist/index.js");


/**
 * Gets EventFlags from a STE.TelemetryEvent, filling them with default values if they don't exist
 * Note that the passed telemetry event is not changed
 * @param telemetryEvent - The telemetry event
 */
function getEffectiveEventFlags(telemetryEvent) {
    var eventFlags = {
        costPriority: _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_0__["CostPriority"].Normal,
        samplingPolicy: _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_0__["SamplingPolicy"].Measure,
        persistencePriority: _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_0__["PersistencePriority"].Normal,
        dataCategories: _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_0__["DataCategories"].NotSet,
        diagnosticLevel: _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_0__["DiagnosticLevel"].FullEvent
    };
    if (!telemetryEvent.eventFlags || !telemetryEvent.eventFlags.dataCategories) {
        Object(___WEBPACK_IMPORTED_MODULE_1__["logNotification"])(___WEBPACK_IMPORTED_MODULE_1__["LogLevel"].Error, ___WEBPACK_IMPORTED_MODULE_1__["Category"].Core, function () { return 'Event is missing DataCategories event flag'; });
    }
    if (!telemetryEvent.eventFlags) {
        return eventFlags;
    }
    if (telemetryEvent.eventFlags.costPriority) {
        eventFlags.costPriority = telemetryEvent.eventFlags.costPriority;
    }
    if (telemetryEvent.eventFlags.samplingPolicy) {
        eventFlags.samplingPolicy = telemetryEvent.eventFlags.samplingPolicy;
    }
    if (telemetryEvent.eventFlags.persistencePriority) {
        eventFlags.persistencePriority = telemetryEvent.eventFlags.persistencePriority;
    }
    if (telemetryEvent.eventFlags.dataCategories) {
        eventFlags.dataCategories = telemetryEvent.eventFlags.dataCategories;
    }
    if (telemetryEvent.eventFlags.diagnosticLevel) {
        eventFlags.diagnosticLevel = telemetryEvent.eventFlags.diagnosticLevel;
    }
    return eventFlags;
}
//# sourceMappingURL=EventFlagFiller.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/EventFlagsProperties.js":
/*!********************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/EventFlagsProperties.js ***!
  \********************************************************************************************/
/*! exports provided: SamplingPolicy, PersistencePriority, CostPriority, DataCategories, DiagnosticLevel */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SamplingPolicy", function() { return SamplingPolicy; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "PersistencePriority", function() { return PersistencePriority; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CostPriority", function() { return CostPriority; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "DataCategories", function() { return DataCategories; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "DiagnosticLevel", function() { return DiagnosticLevel; });
var SamplingPolicy;
(function (SamplingPolicy) {
    SamplingPolicy[SamplingPolicy["NotSet"] = 0] = "NotSet";
    SamplingPolicy[SamplingPolicy["Measure"] = 1] = "Measure";
    SamplingPolicy[SamplingPolicy["Diagnostics"] = 2] = "Diagnostics";
    SamplingPolicy[SamplingPolicy["CriticalBusinessImpact"] = 191] = "CriticalBusinessImpact";
    SamplingPolicy[SamplingPolicy["CriticalCensus"] = 192] = "CriticalCensus";
    SamplingPolicy[SamplingPolicy["CriticalExperimentation"] = 193] = "CriticalExperimentation";
    SamplingPolicy[SamplingPolicy["CriticalUsage"] = 194] = "CriticalUsage";
})(SamplingPolicy || (SamplingPolicy = {}));
var PersistencePriority;
(function (PersistencePriority) {
    PersistencePriority[PersistencePriority["NotSet"] = 0] = "NotSet";
    PersistencePriority[PersistencePriority["Normal"] = 1] = "Normal";
    PersistencePriority[PersistencePriority["High"] = 2] = "High";
})(PersistencePriority || (PersistencePriority = {}));
var CostPriority;
(function (CostPriority) {
    CostPriority[CostPriority["NotSet"] = 0] = "NotSet";
    CostPriority[CostPriority["Normal"] = 1] = "Normal";
    CostPriority[CostPriority["High"] = 2] = "High";
})(CostPriority || (CostPriority = {}));
/**
 * DataCategories
 * These can be combined with | as appropriate
 */
var DataCategories;
(function (DataCategories) {
    DataCategories[DataCategories["NotSet"] = 0] = "NotSet";
    DataCategories[DataCategories["SoftwareSetup"] = 1] = "SoftwareSetup";
    DataCategories[DataCategories["ProductServiceUsage"] = 2] = "ProductServiceUsage";
    DataCategories[DataCategories["ProductServicePerformance"] = 4] = "ProductServicePerformance";
    DataCategories[DataCategories["DeviceConfiguration"] = 8] = "DeviceConfiguration";
    DataCategories[DataCategories["InkingTypingSpeech"] = 16] = "InkingTypingSpeech";
})(DataCategories || (DataCategories = {}));
/**
 * The diagnostic level of the event
 * For generic events, a user can be set to send no events, only basic events, or all (full and basic) events.
 * Services can also send events that are necessary for them to function; these are not affected by the above setting.
 * Instead, if the service is turned off, then it will stop functioning and no NecessaryServiceDataEvents will be sent.
 * AlwaysOnNecessaryServiceDataEvents are always on.
 */
var DiagnosticLevel;
(function (DiagnosticLevel) {
    DiagnosticLevel[DiagnosticLevel["ReservedDoNotUse"] = 0] = "ReservedDoNotUse";
    DiagnosticLevel[DiagnosticLevel["BasicEvent"] = 10] = "BasicEvent";
    DiagnosticLevel[DiagnosticLevel["FullEvent"] = 100] = "FullEvent";
    DiagnosticLevel[DiagnosticLevel["NecessaryServiceDataEvent"] = 110] = "NecessaryServiceDataEvent";
    DiagnosticLevel[DiagnosticLevel["AlwaysOnNecessaryServiceDataEvent"] = 120] = "AlwaysOnNecessaryServiceDataEvent";
})(DiagnosticLevel || (DiagnosticLevel = {}));
//# sourceMappingURL=EventFlagsProperties.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/OTelNotifications.js":
/*!*****************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/OTelNotifications.js ***!
  \*****************************************************************************************/
/*! exports provided: LogLevel, Category, onNotification, logNotification, logError */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "LogLevel", function() { return LogLevel; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Category", function() { return Category; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "onNotification", function() { return onNotification; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "logNotification", function() { return logNotification; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "logError", function() { return logError; });
/* harmony import */ var _Event__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./Event */ "../../node_modules/@ms/oteljs/dist/Event.js");

var onNotificationEvent = new _Event__WEBPACK_IMPORTED_MODULE_0__["Event"]();
var LogLevel;
(function (LogLevel) {
    LogLevel[LogLevel["Error"] = 0] = "Error";
    LogLevel[LogLevel["Warning"] = 1] = "Warning";
    LogLevel[LogLevel["Info"] = 2] = "Info";
    LogLevel[LogLevel["Verbose"] = 3] = "Verbose";
})(LogLevel || (LogLevel = {}));
var Category;
(function (Category) {
    Category[Category["Core"] = 0] = "Core";
    Category[Category["Sink"] = 1] = "Sink";
    Category[Category["Transport"] = 2] = "Transport";
})(Category || (Category = {}));
/**
 * Returns a list of notification event listeners. You can add an event listener:
 *    onNotification().addListener(event =\> \{
 *      console.log(event!.message + ' ' + event!.level); \});
 *
 * DO NOT trigger telemetry events on these notifications, as doing so may
 * create an infinite loop of telemetry events.
 */
function onNotification() {
    return onNotificationEvent;
}
/**
 * Internal function: log a notification
 * @param level - The level of notification to log
 * @param category - The category of the notification
 * @param message - A function that returns a message to log
 */
function logNotification(level, category, message) {
    onNotificationEvent.fireEvent({ level: level, category: category, message: message });
}
/**
 * Internal function: log an error
 * @param category - The category of the notification
 * @param message - A message that will preceed the message from error object
 * @param error - An error object, from which an error message might be obtained
 */
function logError(category, message, error) {
    logNotification(LogLevel.Error, category, function () {
        var errorMessage = error instanceof Error ? error.message : '';
        return message + ": " + errorMessage;
    });
}
//# sourceMappingURL=OTelNotifications.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/OptionalEventFlags.js":
/*!******************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/OptionalEventFlags.js ***!
  \******************************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

//# sourceMappingURL=OptionalEventFlags.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/SimpleTelemetryLogger.js":
/*!*********************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/SimpleTelemetryLogger.js ***!
  \*********************************************************************************************/
/*! exports provided: SuppressNexus, SimpleTelemetryLogger */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SuppressNexus", function() { return SuppressNexus; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SimpleTelemetryLogger", function() { return SimpleTelemetryLogger; });
/* harmony import */ var _TelemetryEvent__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./TelemetryEvent */ "../../node_modules/@ms/oteljs/dist/TelemetryEvent.js");
/* harmony import */ var _TenantTokenManager__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./TenantTokenManager */ "../../node_modules/@ms/oteljs/dist/TenantTokenManager.js");
/* harmony import */ var _TelemetryEventValidator__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./TelemetryEventValidator */ "../../node_modules/@ms/oteljs/dist/TelemetryEventValidator.js");
/* harmony import */ var _Event__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./Event */ "../../node_modules/@ms/oteljs/dist/Event.js");
/* harmony import */ var _OTelNotifications__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./OTelNotifications */ "../../node_modules/@ms/oteljs/dist/OTelNotifications.js");
/* harmony import */ var ___WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! . */ "../../node_modules/@ms/oteljs/dist/index.js");
/* harmony import */ var _Version__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./Version */ "../../node_modules/@ms/oteljs/dist/Version.js");
var __assign = (undefined && undefined.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};







/**
 * Use this as the Nexus tenant token when Nexus logging is not needed or relevant
 */
var SuppressNexus = -1;
/**
 * SimpleTelemetryLogger is the base implementation of a telemetry logger.
 * It exposes sendTelemetryEvent, which is used to log a telemetry event.
 */
var SimpleTelemetryLogger = /** @class */ (function () {
    /**
     * Creates a telemetry logger
     * @param parent - A parent telemetry logger that this telemetry logger should inherit from
     *                 This telemetry logger will send telemetry to the same sinks
     *                 and will send the same persistent data fields as the parent logger
     * @param persistentDataFields - Data fields to send with every event
     */
    function SimpleTelemetryLogger(parent, persistentDataFields, config) {
        var _a, _b;
        /**
         * A list of sinks that telemetry events will be forwarded to
         */
        this.onSendEvent = new _Event__WEBPACK_IMPORTED_MODULE_3__["Event"]();
        /**
         * @internal Internal variable; do not use publicly.
         */
        this.persistentDataFields = [];
        this.config = config || {};
        if (parent) {
            this.onSendEvent = parent.onSendEvent;
            (_a = this.persistentDataFields).push.apply(_a, parent.persistentDataFields);
            this.config = __assign(__assign({}, parent.getConfig()), this.config);
        }
        if (persistentDataFields) {
            (_b = this.persistentDataFields).push.apply(_b, persistentDataFields);
        }
    }
    /**
     * SendTelemetryEvent is the basic way to send a telemetry event.
     * This should be used for sending telemetry about discrete events that happened
     * For telemetry that includes duration and/or success/failure, the Activity API may be more appropriate.
     * @param event - The telemetry event to send
     */
    SimpleTelemetryLogger.prototype.sendTelemetryEvent = function (event) {
        var localEvent;
        try {
            if (this.onSendEvent.getListenerCount() === 0) {
                Object(_OTelNotifications__WEBPACK_IMPORTED_MODULE_4__["logNotification"])(_OTelNotifications__WEBPACK_IMPORTED_MODULE_4__["LogLevel"].Warning, _OTelNotifications__WEBPACK_IMPORTED_MODULE_4__["Category"].Core, function () { return 'No telemetry sinks are attached.'; });
                return;
            }
            // Don't modify the event that got passed in; we create our own.
            localEvent = this.cloneEvent(event);
            this.processTelemetryEvent(localEvent);
        }
        catch (error) {
            Object(_OTelNotifications__WEBPACK_IMPORTED_MODULE_4__["logError"])(_OTelNotifications__WEBPACK_IMPORTED_MODULE_4__["Category"].Core, 'SendTelemetryEvent', error);
            return;
        }
        try {
            this.onSendEvent.fireEvent(localEvent);
        }
        catch (_e) {
            // Sinks should handle their own errors;
        }
    };
    /**
     * Processes a telemetry event, but does not send it
     *   Determines the tenant tokens
     *   Adds persistent data fields
     *   Validates the event
     * Throws if the event is invalid
     * @param event - The telemetry event to process
     */
    SimpleTelemetryLogger.prototype.processTelemetryEvent = function (event) {
        var _a;
        if (!event.telemetryProperties) {
            event.telemetryProperties = _TenantTokenManager__WEBPACK_IMPORTED_MODULE_1__["TenantTokenManager"].getTenantTokens(event.eventName);
        }
        if (event.dataFields) {
            event.dataFields.unshift(Object(___WEBPACK_IMPORTED_MODULE_5__["makeStringDataField"])('OTelJS.Version', _Version__WEBPACK_IMPORTED_MODULE_6__["oteljsVersion"]));
            if (this.persistentDataFields) {
                // The last-added data field wins, if the same-named data field is added more than once.
                // Persistent data fields should have lower priority than per-event data fields
                (_a = event.dataFields).unshift.apply(_a, this.persistentDataFields);
            }
        }
        if (!this.config.disableValidation) {
            _TelemetryEventValidator__WEBPACK_IMPORTED_MODULE_2__["TelemetryEventValidator"].validateTelemetryEvent(event);
        }
    };
    /**
     * Adds a telemetry sink, to which events will be sent
     * @param sink - The telemetry sink to add
     */
    SimpleTelemetryLogger.prototype.addSink = function (sink) {
        this.onSendEvent.addListener(function (event) { return sink.sendTelemetryEvent(event); });
    };
    /**
     * Sets a tenant token for a single namespace. Events within the namespace will be sent to the corresponding tenant.
     * @param namespace - The namespace to which the tokens apply, such as Office.System.
     * @param ariaTenantToken - The Aria tenant token
     * @param nexusTenantToken - The Nexus tenant token
     */
    SimpleTelemetryLogger.prototype.setTenantToken = function (namespace, ariaTenantToken, nexusTenantToken) {
        _TenantTokenManager__WEBPACK_IMPORTED_MODULE_1__["TenantTokenManager"].setTenantToken(namespace, ariaTenantToken, nexusTenantToken);
    };
    /**
     * Sets tenant tokens for multiple namespaces.
     * @param tokenTree - An that represents namespaces and which tenants to send corresponding tokens to
     *   For example, the following tree identifies where to send events under the Office.System and Office.Word namespaces.
     *                \{ Office: \{
     *                    System: \{
     *                      ariaTenantToken: 'foo',
     *                      nexusTenantToken: 100
     *                    \},
     *                    Word: \{
     *                      ariaTenantToken: 'bar',
     *                      nexusTenantToken: 200
     *                    \}
     *                \}\}
     */
    SimpleTelemetryLogger.prototype.setTenantTokens = function (tokenTree) {
        _TenantTokenManager__WEBPACK_IMPORTED_MODULE_1__["TenantTokenManager"].setTenantTokens(tokenTree);
    };
    /**
     * Clone a telemetry event; generally so we don't modify the input telemetry event
     * Also sets dataFields to [] if it isn't already set
     * @param event - The event to clone
     */
    SimpleTelemetryLogger.prototype.cloneEvent = function (event) {
        return Object(_TelemetryEvent__WEBPACK_IMPORTED_MODULE_0__["cloneEvent"])(event);
    };
    /**
     * Gets the currently applied configuration
     */
    SimpleTelemetryLogger.prototype.getConfig = function () {
        return this.config;
    };
    return SimpleTelemetryLogger;
}());

//# sourceMappingURL=SimpleTelemetryLogger.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/TelemetryEvent.js":
/*!**************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/TelemetryEvent.js ***!
  \**************************************************************************************/
/*! exports provided: cloneEvent */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "cloneEvent", function() { return cloneEvent; });
/**
 * Clone a telemetry event; generally so we don't modify the input telemetry event
 * Also sets dataFields to [] if it isn't already set
 * @param event - The event to clone
 */
function cloneEvent(event) {
    var localEvent = { eventName: event.eventName, eventFlags: event.eventFlags };
    if (!!event.telemetryProperties) {
        localEvent.telemetryProperties = {
            ariaTenantToken: event.telemetryProperties.ariaTenantToken,
            nexusTenantToken: event.telemetryProperties.nexusTenantToken
        };
    }
    if (!!event.eventContract) {
        localEvent.eventContract = { name: event.eventContract.name, dataFields: event.eventContract.dataFields.slice() };
    }
    localEvent.dataFields = !!event.dataFields ? event.dataFields.slice() : [];
    return localEvent;
}
//# sourceMappingURL=TelemetryEvent.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/TelemetryEventValidator.js":
/*!***********************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/TelemetryEventValidator.js ***!
  \***********************************************************************************************/
/*! exports provided: TelemetryEventValidator */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TelemetryEventValidator", function() { return TelemetryEventValidator; });
/* harmony import */ var _DataFieldType__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./DataFieldType */ "../../node_modules/@ms/oteljs/dist/DataFieldType.js");

var TelemetryEventValidator;
(function (TelemetryEventValidator) {
    var INT64_MIN = -9007199254740991;
    var INT64_MAX = 9007199254740991;
    // Starts with A-Z, and then contains only alphanumerics
    var StartsWithCapitalRegex = /^[A-Z][a-zA-Z0-9]*$/;
    // Contains alphanumeric or _ or .
    var AlphanumericRegex = /^[a-zA-Z0-9_\.]*$/;
    function validateTelemetryEvent(event) {
        if (!isEventNameValid(event.eventName)) {
            throw new Error('Invalid eventName');
        }
        if (event.eventContract && !isEventContractValid(event.eventContract)) {
            throw new Error('Invalid eventContract');
        }
        if (event.dataFields != null) {
            for (var i = 0; i < event.dataFields.length; i++) {
                validateDataField(event.dataFields[i]);
            }
        }
    }
    TelemetryEventValidator.validateTelemetryEvent = validateTelemetryEvent;
    function isNamespaceValid(eventNamePieces) {
        // Min 3 pieces: Office.(Namespace).EventName)
        return !!eventNamePieces && eventNamePieces.length >= 3 && eventNamePieces[0] === 'Office';
    }
    function isEventNodeValid(eventNode) {
        return eventNode !== undefined && StartsWithCapitalRegex.test(eventNode);
    }
    function isEventNameValid(eventName) {
        var maxEventNameLength = 98; // Client Code = 100 limit; Aria Compact SDK = 98 limit.
        if (!eventName || eventName.length > maxEventNameLength) {
            return false;
        }
        var eventNamePieces = eventName.split('.');
        var eventNodeName = eventNamePieces[eventNamePieces.length - 1];
        return isNamespaceValid(eventNamePieces) && isEventNodeValid(eventNodeName);
    }
    function isEventContractValid(eventContract) {
        return isNameValid(eventContract.name);
    }
    function isDataFieldNameValid(dataFieldName) {
        var maxDataFieldNameLength = 100;
        var dataFieldPrefixLength = 5;
        return !!dataFieldName && isNameValid(dataFieldName) && dataFieldName.length + dataFieldPrefixLength < maxDataFieldNameLength;
    }
    function isNameValid(name) {
        return name !== undefined && AlphanumericRegex.test(name);
    }
    function validateDataField(dataField) {
        if (!isDataFieldNameValid(dataField.name)) {
            throw new Error('Invalid dataField name');
        }
        if (dataField.dataType === _DataFieldType__WEBPACK_IMPORTED_MODULE_0__["DataFieldType"].Int64) {
            validateInt(dataField.value);
        }
    }
    function validateInt(value) {
        if (typeof value !== 'number' || !isFinite(value) || Math.floor(value) !== value || value < INT64_MIN || value > INT64_MAX) {
            throw new Error("Invalid integer " + JSON.stringify(value));
        }
    }
    TelemetryEventValidator.validateInt = validateInt;
})(TelemetryEventValidator || (TelemetryEventValidator = {}));
//# sourceMappingURL=TelemetryEventValidator.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/TelemetryLogger.js":
/*!***************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/TelemetryLogger.js ***!
  \***************************************************************************************/
/*! exports provided: TelemetryLogger */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TelemetryLogger", function() { return TelemetryLogger; });
/* harmony import */ var _SimpleTelemetryLogger__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./SimpleTelemetryLogger */ "../../node_modules/@ms/oteljs/dist/SimpleTelemetryLogger.js");
/* harmony import */ var _Activity__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./Activity */ "../../node_modules/@ms/oteljs/dist/Activity.js");
/* harmony import */ var _contracts_Contracts__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./contracts/Contracts */ "../../node_modules/@ms/oteljs/dist/contracts/Contracts.js");
var __extends = (undefined && undefined.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (undefined && undefined.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (undefined && undefined.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};



/**
 * A TelemetryLogger that includes more advanced functions than the SimpleTelemetryLogger,
 * specifically activities and errors.
 */
var TelemetryLogger = /** @class */ (function (_super) {
    __extends(TelemetryLogger, _super);
    function TelemetryLogger() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    /**
     * Starts an unparented activity to execute asynchronously
     * The caller must call setResult or setSuccess
     * Returns the result of the activityBody
     * @param activityName - The name of the activity
     * @param activityBody - The body of the activity
     */
    TelemetryLogger.prototype.executeActivityAsync = function (activityName, activityBody) {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                return [2 /*return*/, this.createNewActivity(activityName).executeAsync(activityBody)];
            });
        });
    };
    /**
     * Starts an unparented activity to execute synchronously
     * The caller must call setResult or setSuccess
     * Returns the result of the activityBody
     * @param activityName - The name of the activity
     * @param activityBody - The body of the activity
     */
    TelemetryLogger.prototype.executeActivitySync = function (activityName, activityBody) {
        return this.createNewActivity(activityName).executeSync(activityBody);
    };
    /**
     * Creates a new activity. The caller is responsible for setting the result and calling endNow.
     * @param activityName - The name of the activity
     */
    TelemetryLogger.prototype.createNewActivity = function (activityName) {
        return _Activity__WEBPACK_IMPORTED_MODULE_1__["ActivityScope"].createNew(this, activityName);
    };
    /**
     * Advanced usage: Sends an activity. The caller is responsible for setting all of the activity parameters.
     * @param activityName - The name of the activity
     * @param activity - The activity contract
     * @param dataFields - Optional additional data fields
     * @param optionalEventFlags - Optional event flags
     */
    TelemetryLogger.prototype.sendActivity = function (activityName, activity, dataFields, optionalEventFlags) {
        return this.sendTelemetryEvent({
            eventName: activityName,
            eventContract: {
                name: _contracts_Contracts__WEBPACK_IMPORTED_MODULE_2__["Contracts"].Office.System.Activity.contractName,
                dataFields: _contracts_Contracts__WEBPACK_IMPORTED_MODULE_2__["Contracts"].Office.System.Activity.getFields(activity)
            },
            dataFields: dataFields,
            eventFlags: optionalEventFlags
        });
    };
    /**
     * Sends an event with the Error data contract. A convenience wrapper around sendTelemetryEvent, with
     * an Error as a data field.
     * @param error - an ErrorEvent that represents the error
     */
    TelemetryLogger.prototype.sendError = function (error) {
        var dataFields = _contracts_Contracts__WEBPACK_IMPORTED_MODULE_2__["Contracts"].Office.System.Error.getFields('Error', error.error);
        if (error.dataFields != null) {
            dataFields.push.apply(dataFields, error.dataFields);
        }
        return this.sendTelemetryEvent({
            eventName: error.eventName,
            dataFields: dataFields,
            eventFlags: error.eventFlags
        });
    };
    return TelemetryLogger;
}(_SimpleTelemetryLogger__WEBPACK_IMPORTED_MODULE_0__["SimpleTelemetryLogger"]));

//# sourceMappingURL=TelemetryLogger.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/TelemetryProperties.js":
/*!*******************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/TelemetryProperties.js ***!
  \*******************************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

//# sourceMappingURL=TelemetryProperties.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/TelemetrySink.js":
/*!*************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/TelemetrySink.js ***!
  \*************************************************************************************/
/*! no static exports found */
/***/ (function(module, exports) {

//# sourceMappingURL=TelemetrySink.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/TenantTokenManager.js":
/*!******************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/TenantTokenManager.js ***!
  \******************************************************************************************/
/*! exports provided: TenantTokenManager */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "TenantTokenManager", function() { return TenantTokenManager; });
/* harmony import */ var _OTelNotifications__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./OTelNotifications */ "../../node_modules/@ms/oteljs/dist/OTelNotifications.js");

var TokenType;
(function (TokenType) {
    TokenType[TokenType["Aria"] = 0] = "Aria";
    TokenType[TokenType["Nexus"] = 1] = "Nexus";
})(TokenType || (TokenType = {}));
var TenantTokenManager;
(function (TenantTokenManager) {
    var ariaTokenMap = {};
    var nexusTokenMap = {};
    // tslint:disable-next-line:no-any
    var tenantTokens = {};
    function setTenantToken(namespace, ariaTenantToken, nexusTenantToken) {
        var parts = namespace.split('.');
        // Ensure that the provided namespace is valid
        if (parts.length < 2 || parts[0] !== 'Office') {
            Object(_OTelNotifications__WEBPACK_IMPORTED_MODULE_0__["logNotification"])(_OTelNotifications__WEBPACK_IMPORTED_MODULE_0__["LogLevel"].Error, _OTelNotifications__WEBPACK_IMPORTED_MODULE_0__["Category"].Core, function () {
                return "Invalid namespace: " + namespace;
            });
            return;
        }
        // Create the leaf node first
        var leaf = Object.create(Object.prototype);
        if (ariaTenantToken) {
            leaf['ariaTenantToken'] = ariaTenantToken;
        }
        if (nexusTenantToken) {
            leaf['nexusTenantToken'] = nexusTenantToken;
        }
        // Then walk backwards adding the path to the root
        var node = leaf;
        var index;
        for (index = parts.length - 1; index >= 0; --index) {
            var parentNode = Object.create(Object.prototype);
            parentNode[parts[index]] = node;
            node = parentNode;
        }
        setTenantTokens(node);
    }
    TenantTokenManager.setTenantToken = setTenantToken;
    function setTenantTokens(tokenTree) {
        if (typeof tokenTree !== 'object') {
            throw new Error('tokenTree must be an object');
        }
        tenantTokens = mergeTenantTokens(tenantTokens, tokenTree);
    }
    TenantTokenManager.setTenantTokens = setTenantTokens;
    function getTenantTokens(eventName) {
        var ariaTenantToken = getAriaTenantToken(eventName);
        var nexusTenantToken = getNexusTenantToken(eventName);
        if (!nexusTenantToken || !ariaTenantToken) {
            throw new Error('Could not find tenant token for ' + eventName);
        }
        return {
            ariaTenantToken: ariaTenantToken,
            nexusTenantToken: nexusTenantToken
        };
    }
    TenantTokenManager.getTenantTokens = getTenantTokens;
    function getAriaTenantToken(eventName) {
        // Return cached token if it exists for eventName
        if (ariaTokenMap[eventName]) {
            return ariaTokenMap[eventName];
        }
        var ariaToken = getTenantToken(eventName, TokenType.Aria);
        if (typeof ariaToken === 'string') {
            ariaTokenMap[eventName] = ariaToken;
            return ariaToken;
        }
        return undefined;
    }
    TenantTokenManager.getAriaTenantToken = getAriaTenantToken;
    function getNexusTenantToken(eventName) {
        // Return cached token if it exists for eventName
        if (nexusTokenMap[eventName]) {
            return nexusTokenMap[eventName];
        }
        var nexusToken = getTenantToken(eventName, TokenType.Nexus);
        if (typeof nexusToken === 'number') {
            nexusTokenMap[eventName] = nexusToken;
            return nexusToken;
        }
        return undefined;
    }
    TenantTokenManager.getNexusTenantToken = getNexusTenantToken;
    function getTenantToken(eventName, tokenType) {
        // Find token
        var pieces = eventName.split('.');
        var node = tenantTokens;
        var token = undefined;
        if (!node) {
            return undefined;
        }
        for (var i = 0; i < pieces.length - 1; i++) {
            if (node[pieces[i]]) {
                node = node[pieces[i]];
                if (tokenType === TokenType.Aria && typeof node.ariaTenantToken === 'string') {
                    // set token if one is available
                    token = node.ariaTenantToken;
                }
                else if (tokenType === TokenType.Nexus && typeof node.nexusTenantToken === 'number') {
                    token = node.nexusTenantToken;
                }
            }
        }
        return token;
    }
    // tslint:disable-next-line:no-any
    function mergeTenantTokens(existingTokenTree, newTokenTree) {
        if (typeof newTokenTree !== 'object') {
            return newTokenTree;
        }
        for (var _i = 0, _a = Object.keys(newTokenTree); _i < _a.length; _i++) {
            var key = _a[_i];
            if (key in existingTokenTree && typeof (existingTokenTree[key] === 'object')) {
                existingTokenTree[key] = mergeTenantTokens(existingTokenTree[key], newTokenTree[key]);
            }
            else {
                existingTokenTree[key] = newTokenTree[key];
            }
        }
        return existingTokenTree;
    }
    function clear() {
        ariaTokenMap = {};
        nexusTokenMap = {};
        tenantTokens = {};
    }
    TenantTokenManager.clear = clear;
})(TenantTokenManager || (TenantTokenManager = {}));
//# sourceMappingURL=TenantTokenManager.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/Version.js":
/*!*******************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/Version.js ***!
  \*******************************************************************************/
/*! exports provided: oteljsVersion */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "oteljsVersion", function() { return oteljsVersion; });
var oteljsVersion = '3.1.74';
//# sourceMappingURL=Version.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/contracts/Contracts.js":
/*!*******************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/contracts/Contracts.js ***!
  \*******************************************************************************************/
/*! exports provided: Contracts */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Contracts", function() { return Contracts; });
/* harmony import */ var _officeeventschema_tml__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./officeeventschema.tml */ "../../node_modules/@ms/oteljs/dist/contracts/officeeventschema.tml.js");
/* harmony import */ var _Office_System_Error__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./Office.System.Error */ "../../node_modules/@ms/oteljs/dist/contracts/Office.System.Error.js");


var _Activity = _officeeventschema_tml__WEBPACK_IMPORTED_MODULE_0__["Activity"];
var _Result = _officeeventschema_tml__WEBPACK_IMPORTED_MODULE_0__["Result"];
var _Error = _Office_System_Error__WEBPACK_IMPORTED_MODULE_1__["Error"];
var _Funnel = _officeeventschema_tml__WEBPACK_IMPORTED_MODULE_0__["Funnel"];
var _Host = _officeeventschema_tml__WEBPACK_IMPORTED_MODULE_0__["Host"];
var _SDX = _officeeventschema_tml__WEBPACK_IMPORTED_MODULE_0__["SDX"];
var _UserAction = _officeeventschema_tml__WEBPACK_IMPORTED_MODULE_0__["UserAction"];
var _User = _officeeventschema_tml__WEBPACK_IMPORTED_MODULE_0__["User"];
var Contracts;
(function (Contracts) {
    var Office;
    (function (Office) {
        var System;
        (function (System) {
            System.Activity = _Activity;
            System.Result = _Result;
            System.Error = _Error;
            System.Funnel = _Funnel;
            System.Host = _Host;
            System.SDX = _SDX;
            System.User = _User;
            System.UserAction = _UserAction;
        })(System = Office.System || (Office.System = {}));
    })(Office = Contracts.Office || (Contracts.Office = {}));
})(Contracts || (Contracts = {}));
//# sourceMappingURL=Contracts.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/contracts/Office.System.Error.js":
/*!*****************************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/contracts/Office.System.Error.js ***!
  \*****************************************************************************************************/
/*! exports provided: Error */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Error", function() { return Error; });
/* harmony import */ var _DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../DataFieldHelper */ "../../node_modules/@ms/oteljs/dist/DataFieldHelper.js");
/* harmony import */ var _Contract__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../Contract */ "../../node_modules/@ms/oteljs/dist/Contract.js");


var Error;
(function (Error) {
    var contractName = 'Office.System.Error';
    /**
     * Gets data fields for the Error Contract
     * @param instanceName - The instance name of this Error Contract
     * @param contract - The object containing data fields pertaining to the Error Contract
     */
    function getFields(instanceName, contract) {
        var dataFields = [];
        dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".ErrorGroup", contract.errorGroup));
        dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Tag", contract.tag));
        if (contract.code !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Code", contract.code));
        }
        if (contract.id !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Id", contract.id));
        }
        if (contract.count !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Count", contract.count));
        }
        Object(_Contract__WEBPACK_IMPORTED_MODULE_1__["addContractField"])(dataFields, instanceName, contractName);
        return dataFields;
    }
    Error.getFields = getFields;
})(Error || (Error = {})); // Error
//# sourceMappingURL=Office.System.Error.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/contracts/officeeventschema.tml.js":
/*!*******************************************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/contracts/officeeventschema.tml.js ***!
  \*******************************************************************************************************/
/*! exports provided: Result, Activity, Host, User, SDX, Funnel, UserAction */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Result", function() { return Result; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Activity", function() { return Activity; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Host", function() { return Host; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "User", function() { return User; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SDX", function() { return SDX; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Funnel", function() { return Funnel; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "UserAction", function() { return UserAction; });
/* harmony import */ var _DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../DataFieldHelper */ "../../node_modules/@ms/oteljs/dist/DataFieldHelper.js");
/* harmony import */ var _Contract__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../Contract */ "../../node_modules/@ms/oteljs/dist/Contract.js");
/*
    This code was automatically generated.
    Changes to this file may cause incorrect behavior and will be lost if the code is regenerated.
*/


var Result;
(function (Result) {
    var contractName = 'Office.System.Result';
    /* Gets data fields for the Office.System.Result contract */
    function getFields(instanceName, contract) {
        var dataFields = [];
        dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Code", contract.code));
        if (contract.type !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Type", contract.type));
        }
        if (contract.tag !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Tag", contract.tag));
        }
        if (contract.isExpected !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeBooleanDataField"])(instanceName + ".IsExpected", contract.isExpected));
        }
        Object(_Contract__WEBPACK_IMPORTED_MODULE_1__["addContractField"])(dataFields, instanceName, contractName);
        return dataFields;
    }
    Result.getFields = getFields;
})(Result || (Result = {})); // Result
var Activity;
(function (Activity) {
    Activity.contractName = 'Office.System.Activity';
    /* Gets data fields for the Office.System.Activity contract */
    function getFields(contract) {
        var instanceName = 'Activity';
        var dataFields = [];
        if (contract.cV !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".CV", contract.cV));
        }
        dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Duration", contract.duration));
        dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Count", contract.count));
        dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".AggMode", contract.aggMode));
        if (contract.success !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeBooleanDataField"])(instanceName + ".Success", contract.success));
        }
        if (contract.result !== undefined) {
            dataFields.push.apply(dataFields, Result.getFields(instanceName + ".Result", contract.result));
        }
        Object(_Contract__WEBPACK_IMPORTED_MODULE_1__["addContractField"])(dataFields, instanceName, Activity.contractName);
        return dataFields;
    }
    Activity.getFields = getFields;
})(Activity || (Activity = {})); // Activity
var Host;
(function (Host) {
    var contractName = 'Office.System.Host';
    /* Gets data fields for the Office.System.Host contract */
    function getFields(instanceName, contract) {
        var dataFields = [];
        if (contract.id !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Id", contract.id));
        }
        if (contract.version !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Version", contract.version));
        }
        if (contract.sessionId !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".SessionId", contract.sessionId));
        }
        Object(_Contract__WEBPACK_IMPORTED_MODULE_1__["addContractField"])(dataFields, instanceName, contractName);
        return dataFields;
    }
    Host.getFields = getFields;
})(Host || (Host = {})); // Host
var User;
(function (User) {
    var contractName = 'Office.System.User';
    /* Gets data fields for the Office.System.User contract */
    function getFields(instanceName, contract) {
        var dataFields = [];
        if (contract.alias !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Alias", contract.alias));
        }
        if (contract.primaryIdentityHash !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".PrimaryIdentityHash", contract.primaryIdentityHash));
        }
        if (contract.primaryIdentitySpace !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".PrimaryIdentitySpace", contract.primaryIdentitySpace));
        }
        if (contract.tenantId !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".TenantId", contract.tenantId));
        }
        if (contract.tenantGroup !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".TenantGroup", contract.tenantGroup));
        }
        if (contract.isAnonymous !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeBooleanDataField"])(instanceName + ".IsAnonymous", contract.isAnonymous));
        }
        Object(_Contract__WEBPACK_IMPORTED_MODULE_1__["addContractField"])(dataFields, instanceName, contractName);
        return dataFields;
    }
    User.getFields = getFields;
})(User || (User = {})); // User
var SDX;
(function (SDX) {
    var contractName = 'Office.System.SDX';
    /* Gets data fields for the Office.System.SDX contract */
    function getFields(instanceName, contract) {
        var dataFields = [];
        if (contract.id !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Id", contract.id));
        }
        if (contract.version !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Version", contract.version));
        }
        if (contract.instanceId !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".InstanceId", contract.instanceId));
        }
        if (contract.name !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Name", contract.name));
        }
        if (contract.marketplaceType !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".MarketplaceType", contract.marketplaceType));
        }
        if (contract.sessionId !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".SessionId", contract.sessionId));
        }
        if (contract.browserToken !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".BrowserToken", contract.browserToken));
        }
        if (contract.osfRuntimeVersion !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".OsfRuntimeVersion", contract.osfRuntimeVersion));
        }
        if (contract.officeJsVersion !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".OfficeJsVersion", contract.officeJsVersion));
        }
        if (contract.hostJsVersion !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".HostJsVersion", contract.hostJsVersion));
        }
        if (contract.assetId !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".AssetId", contract.assetId));
        }
        if (contract.providerName !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".ProviderName", contract.providerName));
        }
        if (contract.type !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Type", contract.type));
        }
        Object(_Contract__WEBPACK_IMPORTED_MODULE_1__["addContractField"])(dataFields, instanceName, contractName);
        return dataFields;
    }
    SDX.getFields = getFields;
})(SDX || (SDX = {})); // SDX
var Funnel;
(function (Funnel) {
    var contractName = 'Office.System.Funnel';
    /* Gets data fields for the Office.System.Funnel contract */
    function getFields(instanceName, contract) {
        var dataFields = [];
        if (contract.name !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Name", contract.name));
        }
        if (contract.state !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".State", contract.state));
        }
        Object(_Contract__WEBPACK_IMPORTED_MODULE_1__["addContractField"])(dataFields, instanceName, contractName);
        return dataFields;
    }
    Funnel.getFields = getFields;
})(Funnel || (Funnel = {})); // Funnel
var UserAction;
(function (UserAction) {
    var contractName = 'Office.System.UserAction';
    /* Gets data fields for the Office.System.UserAction contract */
    function getFields(instanceName, contract) {
        var dataFields = [];
        if (contract.id !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".Id", contract.id));
        }
        if (contract.name !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".Name", contract.name));
        }
        if (contract.commandSurface !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".CommandSurface", contract.commandSurface));
        }
        if (contract.parentName !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".ParentName", contract.parentName));
        }
        if (contract.triggerMethod !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeStringDataField"])(instanceName + ".TriggerMethod", contract.triggerMethod));
        }
        if (contract.timeOffsetMs !== undefined) {
            dataFields.push(Object(_DataFieldHelper__WEBPACK_IMPORTED_MODULE_0__["makeInt64DataField"])(instanceName + ".TimeOffsetMs", contract.timeOffsetMs));
        }
        Object(_Contract__WEBPACK_IMPORTED_MODULE_1__["addContractField"])(dataFields, instanceName, contractName);
        return dataFields;
    }
    UserAction.getFields = getFields;
})(UserAction || (UserAction = {})); // UserAction
//# sourceMappingURL=officeeventschema.tml.js.map

/***/ }),

/***/ "../../node_modules/@ms/oteljs/dist/index.js":
/*!*****************************************************************************!*\
  !*** C:/Office/src/sdx/powerautomate/node_modules/@ms/oteljs/dist/index.js ***!
  \*****************************************************************************/
/*! no static exports found */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _contracts_Contracts__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./contracts/Contracts */ "../../node_modules/@ms/oteljs/dist/contracts/Contracts.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "Contracts", function() { return _contracts_Contracts__WEBPACK_IMPORTED_MODULE_0__["Contracts"]; });

/* harmony import */ var _Activity__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./Activity */ "../../node_modules/@ms/oteljs/dist/Activity.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "ActivityScope", function() { return _Activity__WEBPACK_IMPORTED_MODULE_1__["ActivityScope"]; });

/* harmony import */ var _Contract__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./Contract */ "../../node_modules/@ms/oteljs/dist/Contract.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "addContractField", function() { return _Contract__WEBPACK_IMPORTED_MODULE_2__["addContractField"]; });

/* harmony import */ var _CustomContract__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./CustomContract */ "../../node_modules/@ms/oteljs/dist/CustomContract.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "getFieldsForContract", function() { return _CustomContract__WEBPACK_IMPORTED_MODULE_3__["getFieldsForContract"]; });

/* harmony import */ var _DataClassification__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./DataClassification */ "../../node_modules/@ms/oteljs/dist/DataClassification.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "DataClassification", function() { return _DataClassification__WEBPACK_IMPORTED_MODULE_4__["DataClassification"]; });

/* harmony import */ var _DataField__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./DataField */ "../../node_modules/@ms/oteljs/dist/DataField.js");
/* harmony import */ var _DataField__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_DataField__WEBPACK_IMPORTED_MODULE_5__);
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _DataField__WEBPACK_IMPORTED_MODULE_5__) if(["default","Contracts","ActivityScope","addContractField","getFieldsForContract","DataClassification"].indexOf(__WEBPACK_IMPORT_KEY__) < 0) (function(key) { __webpack_require__.d(__webpack_exports__, key, function() { return _DataField__WEBPACK_IMPORTED_MODULE_5__[key]; }) }(__WEBPACK_IMPORT_KEY__));
/* harmony import */ var _DataFieldHelper__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./DataFieldHelper */ "../../node_modules/@ms/oteljs/dist/DataFieldHelper.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "makeBooleanDataField", function() { return _DataFieldHelper__WEBPACK_IMPORTED_MODULE_6__["makeBooleanDataField"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "makeInt64DataField", function() { return _DataFieldHelper__WEBPACK_IMPORTED_MODULE_6__["makeInt64DataField"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "makeDoubleDataField", function() { return _DataFieldHelper__WEBPACK_IMPORTED_MODULE_6__["makeDoubleDataField"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "makeStringDataField", function() { return _DataFieldHelper__WEBPACK_IMPORTED_MODULE_6__["makeStringDataField"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "makeGuidDataField", function() { return _DataFieldHelper__WEBPACK_IMPORTED_MODULE_6__["makeGuidDataField"]; });

/* harmony import */ var _DataFieldType__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./DataFieldType */ "../../node_modules/@ms/oteljs/dist/DataFieldType.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "DataFieldType", function() { return _DataFieldType__WEBPACK_IMPORTED_MODULE_7__["DataFieldType"]; });

/* harmony import */ var _EventFlagFiller__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./EventFlagFiller */ "../../node_modules/@ms/oteljs/dist/EventFlagFiller.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "getEffectiveEventFlags", function() { return _EventFlagFiller__WEBPACK_IMPORTED_MODULE_8__["getEffectiveEventFlags"]; });

/* harmony import */ var _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./EventFlagsProperties */ "../../node_modules/@ms/oteljs/dist/EventFlagsProperties.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "SamplingPolicy", function() { return _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_9__["SamplingPolicy"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "PersistencePriority", function() { return _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_9__["PersistencePriority"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "CostPriority", function() { return _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_9__["CostPriority"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "DataCategories", function() { return _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_9__["DataCategories"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "DiagnosticLevel", function() { return _EventFlagsProperties__WEBPACK_IMPORTED_MODULE_9__["DiagnosticLevel"]; });

/* harmony import */ var _OptionalEventFlags__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./OptionalEventFlags */ "../../node_modules/@ms/oteljs/dist/OptionalEventFlags.js");
/* harmony import */ var _OptionalEventFlags__WEBPACK_IMPORTED_MODULE_10___default = /*#__PURE__*/__webpack_require__.n(_OptionalEventFlags__WEBPACK_IMPORTED_MODULE_10__);
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _OptionalEventFlags__WEBPACK_IMPORTED_MODULE_10__) if(["default","Contracts","ActivityScope","addContractField","getFieldsForContract","DataClassification","makeBooleanDataField","makeInt64DataField","makeDoubleDataField","makeStringDataField","makeGuidDataField","DataFieldType","getEffectiveEventFlags","SamplingPolicy","PersistencePriority","CostPriority","DataCategories","DiagnosticLevel"].indexOf(__WEBPACK_IMPORT_KEY__) < 0) (function(key) { __webpack_require__.d(__webpack_exports__, key, function() { return _OptionalEventFlags__WEBPACK_IMPORTED_MODULE_10__[key]; }) }(__WEBPACK_IMPORT_KEY__));
/* harmony import */ var _OTelNotifications__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./OTelNotifications */ "../../node_modules/@ms/oteljs/dist/OTelNotifications.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "LogLevel", function() { return _OTelNotifications__WEBPACK_IMPORTED_MODULE_11__["LogLevel"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "Category", function() { return _OTelNotifications__WEBPACK_IMPORTED_MODULE_11__["Category"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "onNotification", function() { return _OTelNotifications__WEBPACK_IMPORTED_MODULE_11__["onNotification"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "logNotification", function() { return _OTelNotifications__WEBPACK_IMPORTED_MODULE_11__["logNotification"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "logError", function() { return _OTelNotifications__WEBPACK_IMPORTED_MODULE_11__["logError"]; });

/* harmony import */ var _SimpleTelemetryLogger__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./SimpleTelemetryLogger */ "../../node_modules/@ms/oteljs/dist/SimpleTelemetryLogger.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "SuppressNexus", function() { return _SimpleTelemetryLogger__WEBPACK_IMPORTED_MODULE_12__["SuppressNexus"]; });

/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "SimpleTelemetryLogger", function() { return _SimpleTelemetryLogger__WEBPACK_IMPORTED_MODULE_12__["SimpleTelemetryLogger"]; });

/* harmony import */ var _TelemetryLogger__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./TelemetryLogger */ "../../node_modules/@ms/oteljs/dist/TelemetryLogger.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "TelemetryLogger", function() { return _TelemetryLogger__WEBPACK_IMPORTED_MODULE_13__["TelemetryLogger"]; });

/* harmony import */ var _TelemetryEvent__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ./TelemetryEvent */ "../../node_modules/@ms/oteljs/dist/TelemetryEvent.js");
/* harmony reexport (safe) */ __webpack_require__.d(__webpack_exports__, "cloneEvent", function() { return _TelemetryEvent__WEBPACK_IMPORTED_MODULE_14__["cloneEvent"]; });

/* harmony import */ var _TelemetryProperties__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! ./TelemetryProperties */ "../../node_modules/@ms/oteljs/dist/TelemetryProperties.js");
/* harmony import */ var _TelemetryProperties__WEBPACK_IMPORTED_MODULE_15___default = /*#__PURE__*/__webpack_require__.n(_TelemetryProperties__WEBPACK_IMPORTED_MODULE_15__);
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _TelemetryProperties__WEBPACK_IMPORTED_MODULE_15__) if(["default","Contracts","ActivityScope","addContractField","getFieldsForContract","DataClassification","makeBooleanDataField","makeInt64DataField","makeDoubleDataField","makeStringDataField","makeGuidDataField","DataFieldType","getEffectiveEventFlags","SamplingPolicy","PersistencePriority","CostPriority","DataCategories","DiagnosticLevel","LogLevel","Category","onNotification","logNotification","logError","SuppressNexus","SimpleTelemetryLogger","TelemetryLogger","cloneEvent"].indexOf(__WEBPACK_IMPORT_KEY__) < 0) (function(key) { __webpack_require__.d(__webpack_exports__, key, function() { return _TelemetryProperties__WEBPACK_IMPORTED_MODULE_15__[key]; }) }(__WEBPACK_IMPORT_KEY__));
/* harmony import */ var _TelemetrySink__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! ./TelemetrySink */ "../../node_modules/@ms/oteljs/dist/TelemetrySink.js");
/* harmony import */ var _TelemetrySink__WEBPACK_IMPORTED_MODULE_16___default = /*#__PURE__*/__webpack_require__.n(_TelemetrySink__WEBPACK_IMPORTED_MODULE_16__);
/* harmony reexport (unknown) */ for(var __WEBPACK_IMPORT_KEY__ in _TelemetrySink__WEBPACK_IMPORTED_MODULE_16__) if(["default","Contracts","ActivityScope","addContractField","getFieldsForContract","DataClassification","makeBooleanDataField","makeInt64DataField","makeDoubleDataField","makeStringDataField","makeGuidDataField","DataFieldType","getEffectiveEventFlags","SamplingPolicy","PersistencePriority","CostPriority","DataCategories","DiagnosticLevel","LogLevel","Category","onNotification","logNotification","logError","SuppressNexus","SimpleTelemetryLogger","TelemetryLogger","cloneEvent"].indexOf(__WEBPACK_IMPORT_KEY__) < 0) (function(key) { __webpack_require__.d(__webpack_exports__, key, function() { return _TelemetrySink__WEBPACK_IMPORTED_MODULE_16__[key]; }) }(__WEBPACK_IMPORT_KEY__));

















//# sourceMappingURL=index.js.map

/***/ }),

/***/ "./src/index.ts":
/*!**********************!*\
  !*** ./src/index.ts ***!
  \**********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.telemetryLogger = void 0;
var OTel = __importStar(__webpack_require__(/*! @ms/oteljs */ "../../node_modules/@ms/oteljs/dist/index.js"));
var OfficeJsSink = /** @class */ (function () {
    function OfficeJsSink() {
    }
    OfficeJsSink.prototype.sendTelemetryEvent = function (event) {
        Office.sendTelemetryEvent(event);
    };
    return OfficeJsSink;
}());
// Expose global variables
window.telemetryLogger = {};
var dLE;
var sWE;
var officeOnReadyCallback = function () {
    var onReadyTimeStampDate = Date.now();
    var onReadyTimeStamp = -1;
    var performanceTimingData = {};
    if (window.performance !== undefined) {
        if (window.performance.now !== undefined) {
            onReadyTimeStamp = performance.now();
        }
        if (window.performance.getEntries !== undefined) {
            // PerformanceObserver is not supported by IE11 and for TestSDX we don't lose any buffered data without it.
            performanceTimingData.navigation = performance.getEntriesByType('navigation');
            performanceTimingData.resource = performance.getEntriesByType('resource');
            performanceTimingData.paint = performance.getEntriesByType('paint');
            performanceTimingData.frame = performance.getEntriesByType('frame');
        }
    }
    exports.telemetryLogger = new OTel.TelemetryLogger();
    exports.telemetryLogger.addSink(new OfficeJsSink());
    exports.telemetryLogger.setTenantTokens({
        Office: {
            Extensibility: {
                ariaTenantToken: 'db334b301e7b474db5e0f02f07c51a47-a1b5bc36-1bbe-482f-a64a-c2d9cb606706-7439',
                nexusTenantToken: 1755
            }
        }
    });
    window.telemetryLogger = exports.telemetryLogger;
    // SeviceWorker related telemetry is available in window.OnLoad().
    // To avoid race between window.load and office.onReady, we add 10s delay for service worker case.
    var delay;
    try {
        if (serviceWorkerExperiment.isServiceWorkerUsed) {
            delay = 10000;
        }
    }
    catch (e) {
        delay = 0;
    }
    setTimeout(function () {
        try {
            sWE = serviceWorkerExperiment;
        }
        catch (e) {
            sWE = {
                registered: false,
                registerTS: -1,
                supported: false,
                registerScope: '',
                isServiceWorkerUsed: false,
                resourcesFromCache: '',
                resourcesFromNetwork: ''
            };
        }
        exports.telemetryLogger.sendTelemetryEvent({
            eventName: 'Office.Extensibility.SDX.Experimentation',
            eventFlags: {
                samplingPolicy: OTel.SamplingPolicy.Diagnostics,
                // tslint:disable-next-line:no-bitwise
                dataCategories: OTel.DataCategories.ProductServiceUsage | OTel.DataCategories.ProductServicePerformance
            },
            dataFields: [
                OTel.makeBooleanDataField('Loaded', true),
                OTel.makeDoubleDataField('onReadyTimeStamp', onReadyTimeStamp),
                OTel.makeStringDataField('URL', window.location.href),
                OTel.makeDoubleDataField('onReadyTimeStamp_Date', onReadyTimeStampDate),
                OTel.makeDoubleDataField('contentLoadedTimeStamp', dLE.contentLoadedTS),
                OTel.makeDoubleDataField('scriptFetchedTimeStamp', dLE.scriptFetchedTS),
                OTel.makeDoubleDataField('scriptAddedTimeStamp', dLE.scriptAddedTS),
                OTel.makeDoubleDataField('scriptLoadedTimeStamp', dLE.scriptLoadedTS),
                OTel.makeStringDataField('performanceTimingData', JSON.stringify(performanceTimingData)),
                OTel.makeBooleanDataField('swRegistered', sWE.registered),
                OTel.makeDoubleDataField('swRegisteredTS', sWE.registerTS),
                OTel.makeBooleanDataField('swSupported', sWE.supported),
                OTel.makeStringDataField('swRegisterScope', sWE.registerScope),
                OTel.makeStringDataField('swResourcesFromCache', sWE.resourcesFromCache),
                OTel.makeStringDataField('swResourcesFromNetwork', sWE.resourcesFromNetwork)
            ]
        });
    }, delay);
};
try {
    dLE = dynamicLoadExperiment;
}
catch (e) {
    dLE = {
        dynamic: false,
        scriptLoaded: false,
        contentLoadedTS: -1,
        scriptFetchedTS: -1,
        scriptAddedTS: -1,
        scriptLoadedTS: -1
    };
}
if (dLE.dynamic && !dLE.scriptLoaded) {
    window.addEventListener('WordJSLoaded', function () { return Office.onReady().then(officeOnReadyCallback); }, false);
}
else {
    debugger;
    Office.onReady()
        .then(officeOnReadyCallback);
}


/***/ })

/******/ });
//# sourceMappingURL=main.js.map