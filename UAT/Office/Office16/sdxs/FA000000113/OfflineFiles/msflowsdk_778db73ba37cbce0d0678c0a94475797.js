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
/******/ 	__webpack_require__.p = "./dist";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 5);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __assign = (this && this.__assign) || function () {
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
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deriveHostId = exports.Widget = exports.OAuthHandlers = exports.PathAliasesByWidgetType = exports.WidgetHostAction = exports.WidgetNotifyActions = exports.ErrorCodes = exports.WellKnownHostIds = exports.ViewContainerTypes = exports.WidgetTypes = void 0;
var SdkHelper = __webpack_require__(6);
var msFlowError_1 = __webpack_require__(4);
var utils_1 = __webpack_require__(7);
var string_1 = __webpack_require__(1);
var rpc_standalone_1 = __webpack_require__(14);
var config_1 = __webpack_require__(15);
var EnvironmentHelper = __webpack_require__(16);
var RegionalUrlHelper = __webpack_require__(18);
var SdkSettings_1 = __webpack_require__(3);
exports.WidgetTypes = {
    approvalCenter: 'approvalCenter',
    bpfActionCenter: 'bpfActionCenter',
    connectionWizard: 'connectionWizard',
    copilotPlugins: 'copilotPlugins',
    flowCreation: 'flowCreation',
    flowDetails: 'flowDetails',
    flowEdit: 'flowEdit',
    flowNew: 'flowNew',
    flowRunDetails: 'flowRunDetails',
    flowsRuntime: 'flowsRuntime',
    flows: 'flows',
    naturalLanguageToFlowWizard: 'naturalLanguageToFlowWizard',
    templates: 'templates'
};
exports.ViewContainerTypes = {
    fullPage: 'fullPage',
    modal: 'modal',
    panel: 'panel'
};
exports.WellKnownHostIds = {
    DYNAMICS_CRM: 'DynCRM',
    DYNAMICS_NAV: 'DynNAV',
    EXCEL: 'Excel',
    IOT: 'IOT',
    LOGICAPPS: 'LogicApps',
    OUTLOOKWEB: 'OWA',
    POWERAPPS: 'PowerApps',
    POWERAPPSMAKER: 'PowerAppsMaker',
    POWERAPPSSTUDIO: 'PowerappsPpux',
    POWERFLOWADDIN: 'PowerFlowAddin',
    POWERVIRTUALAGENTS: 'PowerVirtualAgents',
    SHAREPOINT: 'SPO',
    STAFFHUB: 'StaffHub',
    TEAMS: 'Teams',
    TEAMSSOLUTIONEXPLORER: 'TeamsSolutionExplorer',
    TREASURY: 'Treasury',
    WIDGETTEST: 'WidgetTest',
    ADOBE_SIGN: 'AdobeSign',
    MSCC: 'MicrosoftSupplyChainCenter',
    UNSPECIFIED: 'Unknown',
};
exports.ErrorCodes = {
    UnlistenedEventCalled: 'UnlistenedEventCalled',
    InvalidRpcEvent: 'InvalidRpcEvent'
};
exports.WidgetNotifyActions = {
    CloseInfoPane: 'closeInfoPane',
    CloseWidget: 'closeWidget',
    ConnectionsConfirmed: 'connectionsConfirmed',
    CreateFlowFromTemplate: 'createFlowFromTemplate',
    CreateFlowFromTemplateDefinition: 'createFlowFromTemplateDefinition',
    TriggerFlow: 'triggerflow',
    TriggerFlowByTemplate: 'triggerflowbytemplate',
    GetTriggerSchema: 'gettriggerschema',
    RefreshConnections: 'refreshconnections',
    RefreshApis: 'refreshapis',
    UserSelectionUpdated: 'userselectionupdated',
    ShowAlertBanner: 'showalertbanner'
};
exports.WidgetHostAction = {
    EXECUTE_TEAMS_DEEP_LINK: 'EXECUTE_TEAMS_DEEP_LINK',
    FLOW_CREATION_FAILED: 'FLOW_CREATION_FAILED',
    FLOW_CREATION_SUCCEEDED: 'FLOW_CREATION_SUCCEEDED',
    FLOW_INSTALL_FAILED: 'FLOW_INSTALL_FAILED',
    FLOW_INSTALL_SUCCEEDED: 'FLOW_INSTALL_SUCCEEDED',
    GET_ACCESS_TOKEN: 'GET_ACCESS_TOKEN',
    GET_IMPLICIT_DATA: 'GET_IMPLICIT_DATA',
    GET_STRINGS: 'GET_STRINGS',
    SIDE_PANE_VISIBILITY_SET: 'SIDE_PANE_VISIBILITY_SET',
    LAUNCH_OAUTH_POPUP: 'LAUNCH_OAUTH_POPUP',
    ON_ADD_CONNECTION_CLICKED: 'ON_ADD_CONNECTION_CLICKED',
    ON_DELETE_CUSTOM_API_CLICKED: 'ON_DELETE_CUSTOMAPI_CLICKED',
    RUN_FLOW_CANCEL_BUTTON_CLICKED: 'RUN_FLOW_CANCEL_BUTTON_CLICKED',
    RUN_FLOW_DONE_BUTTON_CLICKED: 'RUN_FLOW_DONE_BUTTON_CLICKED',
    RUN_FLOW_STARTED: 'RUN_FLOW_STARTED',
    RUN_FLOW_COMPLETED: 'RUN_FLOW_COMPLETED',
    TEMPLATE_LOAD_FAILED: 'TEMPLATE_LOAD_FAILED',
    WIDGET_CLOSE: 'WIDGET_CLOSE',
    WIDGET_READY: 'WIDGET_READY',
    WIDGET_RENDERED: 'WIDGET_RENDERED',
    RECEIVED_APPROVAL_STATUS_CHANGED: 'RECEIVED_APPROVAL_STATUS_CHANGED',
    SENT_APPROVAL_STATUS_CHANGED: 'SENT_APPROVAL_STATUS_CHANGED',
};
var PathAliasToPath = {
    connectionWizard: '/manage{environment}/connections/wizard',
    copilotPlugins: '/manage{environment}/copilotPlugins',
    myFlows: '/manage{environment}/flows',
    sharedFlows: '/manage{environment}/flows/shared',
    receivedApprovals: '/manage{environment}/approvals/received',
    sentApprovals: '/manage{environment}/approvals/sent',
    activeBpfs: '/manage{environment}/businessProcess/instances/active',
    inactiveBpfs: '/manage{environment}/businessProcess/instances/inactive',
    flowCreation: '/manage{environment}/templates/flowCreation',
    flowDetails: '/manage{environment}{solution}/flows/{flowName}/details',
    flowEdit: '/manage{environment}{solution}/flows/{flowName}',
    flowRunDetails: '/manage{environment}{solution}/flows/{flowName}/runs/{runId}',
    flowNewBlank: '/manage{environment}{solution}/flows/new',
    flowNewAutomated: '/manage{environment}{solution}/flows/new/automated',
    flowNewInstant: '/manage{environment}{solution}/flows/new/instant',
    flowNewScheduled: '/manage{environment}{solution}/flows/new/scheduled',
    flowsRuntime: '/manage{environment}/flow/run',
    naturalLanguageToFlowWizard: '/create/fromNaturalLanguage',
    templates: '/templates/' // NOTE: trailing slash required to prevent redirect
};
var MakerPathAliasToPath = __assign(__assign({}, PathAliasToPath), { receivedApprovals: '/manage{environment}/approvalcenter/received', sentApprovals: '/manage{environment}/approvalcenter/sent' });
exports.PathAliasesByWidgetType = {
    connectionWizard: ['connectionWizard'],
    copilotPlugins: ['copilotPlugins'],
    flows: ['myFlows', 'sharedFlows'],
    approvalCenter: ['receivedApprovals', 'sentApprovals'],
    bpfActionCenter: ['activeBpfs', 'inactiveBpfs'],
    flowCreation: ['flowCreation'],
    flowDetails: ['flowDetails'],
    flowEdit: ['flowEdit'],
    flowNew: ['flowNewBlank', 'flowNewAutomated', 'flowNewInstant', 'flowNewScheduled'],
    flowsRuntime: ['flowsRuntime'],
    flowRunDetails: ['flowRunDetails'],
    naturalLanguageToFlowWizard: ['naturalLanguageToFlowWizard'],
    templates: ['templates']
};
exports.OAuthHandlers = {
    oAuth: 'oAuth',
    teamsOAuth: 'teamsOAuth',
    widgetOAuth: 'widgetOAuth',
    mobileWidgetOAuth: 'mobileWidgetOAuth'
};
var SidePaneVisibilitySetName = 'SIDE_PANE_VISIBILITY_SET';
var GetAccessTokenMethodName = 'GET_ACCESS_TOKEN';
var Widget = exports.Widget = /** @class */ (function () {
    function Widget(widgetOption, sdkOption) {
        this.widgetOption = widgetOption;
        this.sdkOption = sdkOption;
        /* tslint:disable: no-any */
        this.callbacks = {};
        this.notifyCallback = 'NOTIFY';
        this.widgetReady = false;
        if (!this.widgetOption) {
            throw new msFlowError_1.MsFlowError('Widget requires a widget option.');
        }
        if (!this.sdkOption) {
            throw new msFlowError_1.MsFlowError('Widget requires a sdk option.');
        }
        if (this.widgetOption.oAuthHandler &&
            !(0, string_1.equalsIgnoreCase)(this.widgetOption.oAuthHandler, exports.OAuthHandlers.oAuth) &&
            !(0, string_1.equalsIgnoreCase)(this.widgetOption.oAuthHandler, exports.OAuthHandlers.teamsOAuth) &&
            !(0, string_1.equalsIgnoreCase)(this.widgetOption.oAuthHandler, exports.OAuthHandlers.widgetOAuth) &&
            !(0, string_1.equalsIgnoreCase)(this.widgetOption.oAuthHandler, exports.OAuthHandlers.mobileWidgetOAuth)) {
            throw new msFlowError_1.MsFlowError('Invalid OAuth handler specified: ' + this.widgetOption.oAuthHandler);
        }
        if (!this.sdkOption.hostName || this.sdkOption.hostName.length < 1) {
            throw new msFlowError_1.MsFlowError('hostName is required in sdk option.');
        }
        if (typeof this.sdkOption.hostName === 'string' && this.sdkOption.hostName.charAt(this.sdkOption.hostName.length - 1) === '/') {
            this.sdkOption.hostName = this.sdkOption.hostName.substring(0, this.sdkOption.hostName.length - 1);
        }
        // If no hostId specified, attempt to derive one from the location
        if ((0, string_1.isNullOrUndefined)(this.sdkOption.hostId)) {
            this.sdkOption.hostId = deriveHostId(document.location);
        }
        // validate option
        if ((0, string_1.isString)(this.widgetOption.container)) {
            this.widgetOption.container = document.getElementById(this.widgetOption.container);
        }
        // If the incoming flow name is of the format v1/{environmentId}/{flowName}
        // This is to support running non default flows from SPO column
        if (this.widgetOption.flowName && this.widgetOption.flowName.substring(0, 3) == 'v1/') {
            var details = this.widgetOption.flowName.split('/');
            this.widgetOption.environmentId = details[1];
            this.widgetOption.flowName = details[2];
        }
        if (!this.widgetOption.container) {
            throw new msFlowError_1.MsFlowError('Widget requires a container element.');
        }
        if ((0, string_1.isNullOrUndefined)(this.widgetOption.widgetId)) {
            this.widgetOption.widgetId = (0, utils_1.uuid)();
        }
        // allow test domain in debug mode
        if (widgetOption.debugMode) {
            Widget.allowedDomains.push(SdkSettings_1.SdkSettings.portalTestDomain, SdkSettings_1.SdkSettings.makerDevPortalDomain);
        }
        if (!this.widgetOption.enableRegionalPortal) {
            this.initializeIframe(this.widgetOption.environmentId, this.sdkOption.hostName);
        }
        else if (this.widgetOption.environmentLocation) {
            var hostName = RegionalUrlHelper.getRegionalPortalUrl(this.widgetOption.environmentLocation, this.sdkOption.hostName);
            this.initializeIframe(this.widgetOption.environmentId, hostName);
        }
    }
    /* tslint:disable: no-any */
    Widget.prototype.notify = function (methodName, actionData) {
        /* tslint:enable: no-any */
        var _this = this;
        if (!this.widgetReady) {
            return Promise.reject({ code: 'WidgetNotReady', message: 'Notify() called before widget has fired WIDGET_READY' });
        }
        /* tslint:disable: no-any */
        return new Promise(function (resolve, reject) {
            /* tslint:enable: no-any */
            var param = _this.createRequestParam();
            var requestMessage = {
                actionName: methodName,
                actionData: actionData
            };
            param.data = requestMessage;
            _this.rpcClient.call(_this.notifyCallback, [param])
                .then(function (result) {
                if (result && result.data) {
                    resolve(result.data);
                }
                else {
                    resolve(null);
                }
            })
                .catch(function (error) {
                if (error && error.innerException) {
                    if (error.innerException.data) {
                        error = error.innerException.data;
                    }
                    else {
                        error = { code: 'UnknownError', message: error.innerException.message };
                    }
                }
                reject(error);
            });
        });
    };
    /* tslint:disable: no-any */
    Widget.prototype.listen = function (methodName, callback) {
        if (!this.callbacks[methodName]) {
            /* tslint:enable: no-any */
            this.callbacks[methodName] = callback;
            if ((0, string_1.equalsIgnoreCase)(methodName, GetAccessTokenMethodName)
                && this.widgetOption.enableRegionalPortal
                && !this.widgetOption.environmentLocation) {
                this.onGetAccessTokenCallbackAdded();
            }
        }
    };
    Widget.prototype.dispose = function () {
        if (this.iframe) {
            this.widgetOption.container.removeChild(this.iframe);
            SdkHelper.removeEventListener('message', this.onReceivedMessageHandler);
        }
    };
    Widget.prototype.onGetAccessTokenCallbackAdded = function () {
        var _this = this;
        // get access token
        var callback = this.callbacks[GetAccessTokenMethodName];
        var authResource = SdkSettings_1.SdkSettings.authResource;
        if ((0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.govHostName, 0) || (0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.makerGovPortalDomain, 0)) {
            authResource = SdkSettings_1.SdkSettings.govAuthResource;
        }
        else if ((0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.highHostName, 0) || (0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.makerHighPortalDomain, 0)) {
            authResource = SdkSettings_1.SdkSettings.highAuthResource;
        }
        else if ((0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.dodPortalDomain, 0) || (0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.makerDodPortalDomain, 0)) {
            authResource = SdkSettings_1.SdkSettings.dodAuthResource;
        }
        else if ((0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.chinaPortalDomain, 0) || (0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.makerChinaPortalDomain, 0)) {
            authResource = SdkSettings_1.SdkSettings.chinaAuthResource;
        }
        else if ((0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.usnatPortalDomain, 0) || (0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.makerUssecPortalDomain, 0)) {
            authResource = SdkSettings_1.SdkSettings.usnatAuthResource;
        }
        else if ((0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.ussecPortalDomain, 0) || (0, string_1.stringIncludes)(this.sdkOption.hostName, SdkSettings_1.SdkSettings.makerUsnatPortalDomain, 0)) {
            authResource = SdkSettings_1.SdkSettings.ussecAuthResource;
        }
        if (callback) {
            var requestParam = {
                data: {
                    resource: authResource
                },
                callInfo: {
                    widgetId: this.widgetOption.widgetId
                }
            };
            var doneCallback = function (errorResult, successResult) {
                var accessToken = successResult.token;
                _this.lookupRegionalPortalUrlAndInitializeIframe(accessToken);
            };
            try {
                callback(requestParam, doneCallback);
            }
            catch (e) {
                throw e instanceof msFlowError_1.MsFlowError ? e : new Error('failed to get access token');
            }
        }
    };
    Widget.prototype.lookupRegionalPortalUrlAndInitializeIframe = function (accessToken) {
        var _this = this;
        if (!accessToken) {
            throw new msFlowError_1.MsFlowError('Flow widget received a null token from the host');
        }
        EnvironmentHelper.getEnvironmentInfo(this.sdkOption.hostName, this.widgetOption.environmentId, accessToken)
            .then(function (environmentInfo) {
            var regionalPortalUrl = RegionalUrlHelper.getRegionalPortalUrl(environmentInfo.location, _this.sdkOption.hostName);
            _this.initializeIframe(environmentInfo.name, regionalPortalUrl);
        })
            .catch(function (error) {
            // Fallback to initialization using widget options
            _this.regionalPortalInitFailed = true;
            _this.initializeIframe(_this.widgetOption.environmentId, _this.sdkOption.hostName);
        });
    };
    Widget.prototype.initializeIframe = function (environmentName, hostName) {
        this.sdkOption.hostName = hostName;
        // update environment only if not passed by the host
        this.widgetOption.environmentId = this.widgetOption.environmentId || environmentName;
        this.url = this.constructUrl();
        this.renderIframe();
        this.rpcClient = new rpc_standalone_1.Rpc({
            signature: this.widgetOption.widgetId,
            targetOrigin: '*',
            rpcMessageHandler: new rpc_standalone_1.WindowPostMessageRpcHandler({
                targetWindow: this.iframe.contentWindow
            })
        });
    };
    Widget.prototype.createRequestParam = function () {
        var callInfo = {
            widgetId: this.widgetOption.widgetId
        };
        return {
            callInfo: callInfo
        };
    };
    Widget.prototype.renderIframe = function () {
        var _this = this;
        this.iframe = document.createElement('iframe');
        this.iframe.setAttribute('src', this.url);
        this.iframe.setAttribute('id', this.widgetOption.widgetId);
        this.iframe.setAttribute('name', 'widgetIFrame');
        this.iframe.setAttribute('allow', 'geolocation');
        this.iframe.setAttribute('title', this.widgetOption.iframeTitle || 'Microsoft Power Automate');
        this.iframe.setAttribute('role', 'presentation');
        var container = this.widgetOption.container;
        this.iframe.scrolling = container.getAttribute('data-mswidget-scrolling') || 'yes';
        container.appendChild(this.iframe);
        this.onReceivedMessageHandler = function (event) { return _this.onMessageReceived(event); };
        SdkHelper.addEventListener('message', this.onReceivedMessageHandler, true);
        this.listen(SidePaneVisibilitySetName, function (event) {
            _this.iframe.scrolling = event.data && event.data['visible'] ? 'no' : 'auto';
        });
        this.listen('CONNECTION_REFERENCES_CONFIRMED', function (requestParam) {
            if (_this.getWidgetType() === exports.WidgetTypes.connectionWizard ||
                (_this.widgetOption.connectionWizardSettings && _this.widgetOption.connectionWizardSettings.onConnectionReferencesConfirmed)) {
                _this.widgetOption.connectionWizardSettings.onConnectionReferencesConfirmed(requestParam.data);
            }
        });
        this.listen('CONNECTION_WIZARD_CONFIRMATIONBUTTONDETAILS', function (requestParam) {
            if (_this.getWidgetType() === exports.WidgetTypes.connectionWizard ||
                (_this.widgetOption.connectionWizardSettings && _this.widgetOption.connectionWizardSettings.onConnectionWizardConfirmationButtonDetailsChanged)) {
                _this.widgetOption.connectionWizardSettings.onConnectionWizardConfirmationButtonDetailsChanged(requestParam.data);
            }
        });
        this.listen('CONNECTION_WIZARD_ERROR', function (requestParam) {
            if (_this.widgetOption.connectionWizardSettings && _this.widgetOption.connectionWizardSettings.onConnectionWizardError) {
                _this.widgetOption.connectionWizardSettings.onConnectionWizardError(requestParam.data);
            }
        });
        this.listen('GET_WIDGET_OPTIONS', function (_requestParam, doneCallback) {
            var _a;
            var connectionWizardSettings = (_a = _this.widgetOption, _a.connectionWizardSettings), flowDetailsSettings = _a.flowDetailsSettings, flowsSettings = _a.flowsSettings, runtimeSettings = _a.runtimeSettings, templatesSettings = _a.templatesSettings;
            doneCallback(null, {
                connectionReferences: connectionWizardSettings && connectionWizardSettings.connectionReferences,
                flowsFilter: flowsSettings && flowsSettings.flowsFilter,
                waitAfterInstallingFlow: runtimeSettings && runtimeSettings.waitAfterInstallingFlow,
                additionalOwners: _this.widgetOption.additionalOwners,
                embeddedIn: _this.widgetOption.embeddedIn,
                exitWidgetToEditInAdvancedMode: templatesSettings && templatesSettings.exitWidgetToEditInAdvancedMode,
                hideFlowCreationCloseButton: templatesSettings && templatesSettings.hideFlowCreationCloseButton,
                hideFlowCreationHeader: templatesSettings && templatesSettings.hideFlowCreationHeader,
                hideTemplateTitleDietDesigner: templatesSettings && templatesSettings.hideTemplateTitleDietDesigner,
                hideTemplateTypeDietDesigner: templatesSettings && templatesSettings.hideTemplateTypeDietDesigner,
                useFlowCreatorSurfaceFromTemplateGallery: templatesSettings && templatesSettings.useFlowCreatorSurfaceFromTemplateGallery,
                flowDetailsBreadcrumbItems: flowDetailsSettings && flowDetailsSettings.breadcrumbItems,
                enableDynamicSchemaCallback: _this.widgetOption.enableDynamicSchemaCallback,
                flowDetailsEnableDefaultBreadcrumbs: flowDetailsSettings && flowDetailsSettings.enableDefaultBreadcrumbs,
                teamsDeepLinkScenariosEnabled: _this.widgetOption.teamsDeepLinkScenariosEnabled,
                exitWidgetToViewCreatedFlow: templatesSettings && templatesSettings.exitWidgetToViewCreatedFlow,
                pathAliasOverrides: _this.widgetOption.pathAliasOverrides,
                preventCloseOnFlowCreationDoneClicked: templatesSettings && templatesSettings.preventCloseOnFlowCreationDoneClicked,
                hideDesignerBackButton: flowsSettings && flowsSettings.hideDesignerBackButton,
                hideDesignerTestButton: flowsSettings && flowsSettings.hideDesignerTestButton
            });
        });
    };
    Widget.prototype.onMessageReceived = function (event) {
        if (!this.isValidRpcEvent(event)) {
            var errorObj = {
                name: exports.ErrorCodes.InvalidRpcEvent,
                message: 'Widget dropping received message because its RPC event is invalid, event originated from ' + event.origin
            };
            if (this.widgetOption.errorHandler) {
                this.widgetOption.errorHandler(errorObj);
            }
            if (this.widgetOption.debugMode) {
                console.warn(errorObj);
            }
            return;
        }
        if (!event.data.method) {
            return;
        }
        switch (event.data.method) {
            case '__PING__':
                this.rpcAckHandler(event);
                break;
            default:
                this.invokeCallbackHandler(event.data.method, event);
                break;
        }
    };
    Widget.prototype.isValidRpcEvent = function (event) {
        var iframeHostName = (0, string_1.endsWithIgnoreCase)(event.origin, '/') ? event.origin.replace('/', '') : event.origin;
        return (0, string_1.equalsIgnoreCase)(event.data.signature, this.widgetOption.widgetId) && Widget.allowedDomains.some(function (domain) { return (0, string_1.endsWithIgnoreCase)(iframeHostName, domain); });
    };
    Widget.prototype.rpcAckHandler = function (event) {
        var response = {
            id: event.data.id,
            signature: event.data.signature,
            result: '__PONG__',
            error: null,
        };
        event.source && event.source.postMessage(response, event.origin);
    };
    Widget.prototype.invokeCallbackHandler = function (methodName, event) {
        var requestParam;
        if (event && event.data && event.data.params && event.data.params.length > 0) {
            requestParam = event.data.params[0];
        }
        // If handling WIDGET_READY, mark the widget as ready prior
        // to making any callback to the host
        if (methodName === exports.WidgetHostAction.WIDGET_READY) {
            this.setIsReady();
        }
        var callback = this.callbacks[methodName];
        var response = {
            id: event.data.id,
            signature: event.data.signature,
        };
        if (callback) {
            var doneCallback = function (errorResult, successResult) {
                response.result = successResult;
                response.error = errorResult;
                event.source && event.source.postMessage(response, event.origin);
            };
            try {
                callback(requestParam, doneCallback);
            }
            catch (e) {
                // if client throw an error
                response.error = e;
                event.source && event.source.postMessage(response, event.origin);
            }
        }
        else {
            // the host is not listening for this event so we must throw an error to allow widget's promise to complete
            response.error = {
                value: {
                    name: exports.ErrorCodes.UnlistenedEventCalled,
                    message: "Event '".concat(methodName, "' is not being listened for by the host")
                }
            };
            event.source && event.source.postMessage(response, event.origin);
        }
    };
    Widget.prototype.constructUrl = function () {
        return "".concat(this.constructBaseUrl()).concat(this.getWidgetPath()).concat(this.constructWidgetQueryString())
            .replace('{environment}', !this.widgetOption.environmentId ? '' : "/environments/".concat(this.widgetOption.environmentId))
            .replace('{solution}', !this.widgetOption.solutionId ? '' : "/solutions/".concat(this.widgetOption.solutionId))
            .replace('{flowName}', !this.widgetOption.flowName ? '' : this.widgetOption.flowName)
            .replace('{runId}', !this.widgetOption.runId ? '' : this.widgetOption.runId);
    };
    Widget.prototype.setIsReady = function () {
        this.widgetReady = true;
    };
    /* tslint:disable: no-any */
    Widget.prototype.getRpcClient = function () {
        /* tslint:enable: no-any */
        return this.rpcClient;
    };
    Widget.prototype.constructBaseUrl = function () {
        if (typeof this.sdkOption.hostName === 'string') {
            return "".concat(this.sdkOption.hostName, "/").concat(this.sdkOption.locale, "/widgets");
        }
        else {
            return "".concat(this.sdkOption.hostName[0], "/").concat(this.sdkOption.locale, "/widgets");
        }
    };
    Widget.prototype.constructBaseQueryString = function () {
        var queryString = "?widgetId=".concat(this.widgetOption.widgetId) +
            "&sdkVersion=".concat(config_1.config.version) +
            "&widgetType=".concat(this.getWidgetType()) +
            "&utm_medium=widget" +
            "&utm_source=".concat(this.sdkOption.hostId);
        if (this.sdkOption.hostLocale) {
            queryString += "&utm_locale=".concat(this.sdkOption.hostLocale);
        }
        if (this.sdkOption.hostPlatform) {
            queryString += "&utm_platform=".concat(this.sdkOption.hostPlatform);
        }
        if (this.sdkOption.hostVersion) {
            queryString += "&utm_version=".concat(this.sdkOption.hostVersion);
        }
        if (this.widgetOption.sessionId) {
            queryString += "&sessionId=".concat(this.widgetOption.sessionId);
        }
        if (this.widgetOption.campaign) {
            queryString += "&utm_campaign=".concat(this.widgetOption.campaign);
        }
        if (this.widgetOption.visibleHideKeys) {
            queryString += "&visibleHideKeys=".concat(this.widgetOption.visibleHideKeys);
        }
        if (!!this.widgetOption.environmentId) {
            queryString += "&environment=".concat(this.widgetOption.environmentId);
        }
        if (!!this.widgetOption.solutionId) {
            queryString += "&solutionId=".concat(this.widgetOption.solutionId);
        }
        // only put the switch into the query string if the user explicitly specified it, thus deferring to flow portal
        // (server or client) on the decision of what the default should be if it was not specified
        if (!(0, string_1.isNullOrUndefined)(this.widgetOption.enableOnBehalfOfTokens)) {
            queryString += "&enableOnBehalfOfTokens=".concat(this.widgetOption.enableOnBehalfOfTokens);
        }
        if (!(0, string_1.isNullOrUndefined)(this.widgetOption.groupId)) {
            queryString += "&groupId=".concat(this.widgetOption.groupId);
        }
        if (!(0, string_1.isNullOrUndefined)(this.widgetOption.enableRegionalPortal)) {
            queryString += "&enableRegionalPortal=".concat(this.widgetOption.enableRegionalPortal);
        }
        if (!(0, string_1.isNullOrUndefined)(this.widgetOption.enableWidgetV2)) {
            queryString += "&enableWidgetV2=".concat(this.widgetOption.enableWidgetV2);
        }
        if ((0, string_1.isNullOrUndefined)(this.widgetOption.oAuthHandler)) {
            this.widgetOption.oAuthHandler = exports.OAuthHandlers.oAuth;
        }
        queryString += "&oAuthHandler=".concat(this.widgetOption.oAuthHandler);
        return queryString;
    };
    Widget.prototype.constructHideTabsQueryParam = function (hideTabsWidgetOption) {
        // if the caller did not specify this value we are intentionally setting it false in order to provide the client
        // with a guarantee that the default value remain constant unless they take on a new version of jssdk
        return (hideTabsWidgetOption === true)
            ? "&hideTabs=".concat(hideTabsWidgetOption)
            : "&hideTabs=false";
    };
    Widget.prototype.constructWidgetQueryString = function () {
        var _this = this;
        var queryString = this.constructBaseQueryString();
        if (this.widgetOption.widgetStyleSettings) {
            queryString += this.getDynamicParamsUrl(this.widgetOption.widgetStyleSettings);
        }
        // For runtime widget, if flowname is provided at render time, we use this to load the flow instead of the one coming from TriggerFlow callback
        if (this.getWidgetType() === exports.WidgetTypes.flowsRuntime && this.widgetOption.flowName) {
            queryString += "&flowName=".concat(this.widgetOption.flowName);
        }
        if (this.widgetOption.flowsSettings) {
            if (this.widgetOption.flowsSettings.createFromBlankTemplateId) {
                queryString += "&defaultTemplate=".concat(this.widgetOption.flowsSettings.createFromBlankTemplateId);
            }
            queryString += this.constructHideTabsQueryParam(this.widgetOption.flowsSettings.hideTabs);
            if (this.widgetOption.flowsSettings.isMini) {
                queryString += "&isMini=true";
            }
            if (this.widgetOption.flowsSettings.hideFlowCreation) {
                queryString += "&hideFlowCreation=true";
            }
            if (this.widgetOption.flowsSettings.enableBusinessProcessFlow) {
                queryString += "&enableBusinessProcessFlow=true";
            }
            if (this.widgetOption.flowsSettings.allowImplicitConsent) {
                queryString += "&allowImplicitConsent=true";
            }
            if (this.widgetOption.flowsSettings.enableTeamsHomePage) {
                queryString += '&teamsHome=true';
            }
            if (this.widgetOption.flowsSettings.widgetFlowListDisplaySettings) {
                queryString += this.getDynamicParamsUrl(this.widgetOption.flowsSettings.widgetFlowListDisplaySettings);
            }
        }
        if (this.widgetOption.flowNewSettings) {
            if (this.widgetOption.flowNewSettings.templateName) {
                queryString += "&template=".concat(this.widgetOption.flowNewSettings.templateName);
            }
            if (this.widgetOption.flowNewSettings.galleryName) {
                queryString += "&gallery=".concat(this.widgetOption.flowNewSettings.galleryName);
            }
            if (this.widgetOption.flowNewSettings.connectionReferences) {
                Object.keys(this.widgetOption.flowNewSettings.connectionReferences || {}).map(function (referenceName) {
                    var connectionReference = _this.widgetOption.flowNewSettings.connectionReferences[referenceName];
                    queryString += "&connection.".concat(referenceName, "=").concat(connectionReference.selectedConnectionName);
                });
            }
        }
        if (this.widgetOption.approvalCenterSettings) {
            queryString += this.constructHideTabsQueryParam(this.widgetOption.approvalCenterSettings.hideTabs);
            if (this.widgetOption.approvalCenterSettings.approvalsFilter) {
                var encodedApprovalsFilter = "&approvalsFilter=".concat(encodeURIComponent(this.widgetOption.approvalCenterSettings.approvalsFilter));
                queryString += encodedApprovalsFilter;
            }
            if (this.widgetOption.approvalCenterSettings.autoNavigateToDetails) {
                queryString += "&autoNavigateToDetails=true";
            }
            if (this.widgetOption.approvalCenterSettings.hideInfoPaneCloseButton) {
                queryString += "&hideInfoPaneCloseButton=true";
            }
            if (this.widgetOption.approvalCenterSettings.hideFlowCreation) {
                queryString += "&hideFlowCreation=true";
            }
            if (this.widgetOption.approvalCenterSettings.showSimpleEmptyPage) {
                queryString += "&showSimpleEmptyPage=true";
            }
            if (this.widgetOption.approvalCenterSettings.hideLink) {
                queryString += "&hideLink=true";
            }
            if (this.widgetOption.approvalCenterSettings.showApprovalHistory) {
                queryString += "&showApprovalHistory=true";
            }
        }
        if (this.widgetOption.flowCreationSettings) {
            if (this.widgetOption.flowCreationSettings.hideEditAdvancedModeButton) {
                queryString += "&hideEditAdvancedModeButton=".concat(this.widgetOption.flowCreationSettings.hideEditAdvancedModeButton);
            }
        }
        if (this.widgetOption.templatesSettings) {
            if (this.widgetOption.templatesSettings.defaultParams) {
                queryString += this.getDynamicParamsUrl(this.widgetOption.templatesSettings.defaultParams);
            }
            ;
            if (this.widgetOption.templatesSettings.destination) {
                queryString += "&destination=".concat(this.widgetOption.templatesSettings.destination);
            }
            if (this.widgetOption.templatesSettings.templateCategory) {
                queryString += "&category=".concat(this.widgetOption.templatesSettings.templateCategory);
            }
            if (this.widgetOption.templatesSettings.metadataSortProperty) {
                queryString += "&metadataSortProperty=".concat(this.widgetOption.templatesSettings.metadataSortProperty);
            }
            if (this.widgetOption.templatesSettings.pageSize) {
                queryString += "&pageSize=".concat(this.widgetOption.templatesSettings.pageSize);
            }
            if (this.widgetOption.templatesSettings.useServerSideProvisioning) {
                queryString += "&useServerSideProvisioning=".concat(this.widgetOption.templatesSettings.useServerSideProvisioning);
            }
            if (this.widgetOption.templatesSettings.searchTerm) {
                queryString += "&q=".concat(this.widgetOption.templatesSettings.searchTerm);
            }
            if (this.widgetOption.templatesSettings.enableTemplatesPageShell) {
                queryString += "&templatesShell=".concat(this.widgetOption.templatesSettings.enableTemplatesPageShell);
            }
            if (this.widgetOption.templatesSettings.hideSidePanel) {
                queryString += "&hideSidePanel=".concat(this.widgetOption.templatesSettings.hideSidePanel);
            }
            if (this.widgetOption.templatesSettings.hideStartWithDescription) {
                queryString += "&hideStartWithDescription=".concat(this.widgetOption.templatesSettings.hideStartWithDescription);
            }
            if (this.widgetOption.templatesSettings.showCreateButtonOnLeft) {
                queryString += "&showCreateButtonOnLeft=".concat(this.widgetOption.templatesSettings.showCreateButtonOnLeft);
            }
            if (this.widgetOption.templatesSettings.showGoBack) {
                queryString += "&showGoBack=true";
            }
            if (this.widgetOption.templatesSettings.enableWidgetCloseOnFlowSave) {
                queryString += "&enableWidgetCloseOnFlowSave=".concat(this.widgetOption.templatesSettings.enableWidgetCloseOnFlowSave);
            }
            if (this.widgetOption.templatesSettings.enableDietDesigner) {
                queryString += "&enableDietDesigner=".concat(this.widgetOption.templatesSettings.enableDietDesigner);
            }
            if (this.widgetOption.templatesSettings.disableNavigationAfterAutoCreation) {
                queryString += "&disableNavigationAfterAutoCreation=".concat(this.widgetOption.templatesSettings.disableNavigationAfterAutoCreation);
            }
            if (this.widgetOption.templatesSettings.allowCustomFlowName) {
                queryString += "&allowCustomFlowName=".concat(this.widgetOption.templatesSettings.allowCustomFlowName);
            }
            if (this.widgetOption.templatesSettings.showCreateFromBlank) {
                queryString += "&showCreateFromBlank=true";
            }
            if (this.widgetOption.templatesSettings.showHiddenTemplates) {
                queryString += "&showHiddenTemplates=true";
            }
            if (this.widgetOption.templatesSettings.oneClickCategory) {
                queryString += "&oneClickCategory=".concat(this.widgetOption.templatesSettings.oneClickCategory);
            }
            if (this.widgetOption.templatesSettings.dietCategory) {
                queryString += "&dietCategory=".concat(this.widgetOption.templatesSettings.dietCategory);
            }
            if (this.widgetOption.templatesSettings.waitAfterSavingFlow) {
                queryString += "&waitAfterSavingFlow=".concat(this.widgetOption.templatesSettings.waitAfterSavingFlow);
            }
        }
        if (this.widgetOption.runtimeSettings) {
            queryString += this.getDynamicParamsUrl(this.widgetOption.runtimeSettings);
        }
        queryString += "&pathAlias=".concat(this.getWidgetPathAlias());
        if (this.regionalPortalInitFailed) {
            queryString += '&regionalPortalInitFailed=true';
        }
        if (this.widgetOption.historyDisabled) {
            queryString += '&historyDisabled=true';
        }
        if (this.widgetOption.naturalLanguageToFlowWizardSettings) {
            if (this.widgetOption.naturalLanguageToFlowWizardSettings.initialPrompt) {
                queryString += "&prompt=".concat(this.widgetOption.naturalLanguageToFlowWizardSettings.initialPrompt);
            }
        }
        /** This must always be true going forward. Need the flag to allow the widget to decide whether or not to call
         *  events which may or may not be listened for by the host. Without this branching logic on the widget side,
         *  the widget would block indefinitely for hosts which are not listening for the optional event and are using an old sdk version.
         */
        queryString += '&allowOptionalEvents=true';
        return queryString;
    };
    Widget.prototype.getWidgetPathAlias = function () {
        var widgetTab;
        switch (this.getWidgetType()) {
            case exports.WidgetTypes.flows:
                widgetTab = this.widgetOption.flowsSettings ? this.widgetOption.flowsSettings.tab : null;
                break;
            case exports.WidgetTypes.flowNew:
                widgetTab = this.widgetOption.flowNewSettings ? this.widgetOption.flowNewSettings.tab : null;
                break;
            case exports.WidgetTypes.approvalCenter:
                widgetTab = this.widgetOption.approvalCenterSettings ? this.widgetOption.approvalCenterSettings.tab : null;
                break;
            case exports.WidgetTypes.bpfActionCenter:
                widgetTab = this.widgetOption.bpfActionCenterSettings ? this.widgetOption.bpfActionCenterSettings.tab : null;
                break;
            default:
                break;
        }
        // note widget type has already been validated, so if tabPathsForType comes back null it is a bug in our code for which it is appropriate to null ref
        var pathAliases = exports.PathAliasesByWidgetType[this.getWidgetType()];
        if (widgetTab && pathAliases.indexOf(widgetTab) === -1) {
            throw new msFlowError_1.MsFlowError("Please provide a valid widget tab identifier for the specified widget type. "
                + "Widget type '".concat(this.getWidgetType(), "' does not support tab '").concat(widgetTab, "'. Supported tabs for ")
                + "this widget type are: '".concat(JSON.stringify(pathAliases), "'."));
        }
        return !widgetTab ? pathAliases[0] : widgetTab;
    };
    Widget.prototype.getWidgetPath = function () {
        var _this = this;
        // For some maker scenarios (like approvals) the path alias varies slightly
        if (SdkSettings_1.MakerShellAllowedDomains.some(function (domain) { return (0, string_1.endsWithIgnoreCase)(_this.sdkOption.hostName, domain); })) {
            return MakerPathAliasToPath[this.getWidgetPathAlias()];
        }
        return PathAliasToPath[this.getWidgetPathAlias()];
    };
    /* tslint:disable: no-any */
    Widget.prototype.getDynamicParamsUrl = function (dynamicParams) {
        /* tslint:enable: no-any */
        var dynamicParamsUrl = '';
        if (Object.keys(dynamicParams).length > 0) {
            try {
                var keys = Object.keys(dynamicParams).filter(function (key) { return !(0, string_1.isNullOrUndefined)(dynamicParams[key]); });
                dynamicParamsUrl = '&' + keys.map(function (k) {
                    return encodeURIComponent(k) + '=' + encodeURIComponent(dynamicParams[k]);
                }).join('&');
            }
            catch (e) {
                throw new Error('Failed to create url params out of dynamic params data. Exception: ' + e);
            }
        }
        return dynamicParamsUrl;
    };
    Widget.widgetPrefix = 'msflowsdk';
    Widget.allowedDomains = __spreadArray(__spreadArray([], SdkSettings_1.DefaultAllowedDomains, true), SdkSettings_1.MakerShellAllowedDomains, true);
    return Widget;
}());
function deriveHostId(location) {
    if ((0, string_1.isNullOrUndefined)(location) ||
        (0, string_1.isNullOrUndefined)(location.pathname) ||
        (0, string_1.isNullOrUndefined)(location.hostname)) {
        return exports.WellKnownHostIds.UNSPECIFIED;
    }
    var pathname = location.pathname.toLowerCase();
    var hostname = location.hostname.toLowerCase();
    var crmRegex = /crm[\d]+\.dynamics.com/;
    if ((0, string_1.endsWithIgnoreCase)(hostname, '.powerapps.com') && (0, string_1.startsWithIgnoreCase)(hostname, 'make.')) {
        return exports.WellKnownHostIds.POWERAPPSMAKER;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, '.powerapps.com')) {
        return exports.WellKnownHostIds.POWERAPPS;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, '.sharepoint.com') || (0, string_1.endsWithIgnoreCase)(hostname, '.sharepoint-df.com') || (0, string_1.endsWithIgnoreCase)(hostname, 'msft.spoppe.com')) {
        return exports.WellKnownHostIds.SHAREPOINT;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, '.financials.dynamics.com')) {
        return exports.WellKnownHostIds.DYNAMICS_NAV;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, '.crm.dynamics.com') || (0, string_1.endsWithIgnoreCase)(hostname, 'crmdynint.com') || crmRegex.exec(hostname)) {
        return exports.WellKnownHostIds.DYNAMICS_CRM;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, 'outlook.office.com') || (0, string_1.endsWithIgnoreCase)(hostname, 'outlook-sdf.office.com')) {
        return exports.WellKnownHostIds.OUTLOOKWEB;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, '.flow.microsoft.com') || (0, string_1.endsWithIgnoreCase)(hostname, 'dev.azure-flows.net') || (0, string_1.endsWithIgnoreCase)(hostname, SdkSettings_1.SdkSettings.makerPortalDomain)) {
        return exports.WellKnownHostIds.WIDGETTEST;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, '.hosting.portal.azure.net')) {
        return exports.WellKnownHostIds.LOGICAPPS;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, '.azureiotcentral-dev.com') || (0, string_1.endsWithIgnoreCase)(hostname, 'azureiotcentral.com')) {
        return exports.WellKnownHostIds.IOT;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, 'staffhub.office.com') || (0, string_1.endsWithIgnoreCase)(hostname, 'staffhub.ms')) {
        return exports.WellKnownHostIds.STAFFHUB;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, 'bankadmin.azurewebsites.net') ||
        (0, string_1.endsWithIgnoreCase)(hostname, 'maui-uat.azurewebsites.net') ||
        (0, string_1.endsWithIgnoreCase)(hostname, 'maui-int.azurewebsites.net')) {
        return exports.WellKnownHostIds.TREASURY;
    }
    else if (pathname.indexOf('widgethosts/teams') >= 0) {
        return exports.WellKnownHostIds.TEAMS;
    }
    else if (pathname.indexOf('widgethosts/excel') >= 0) {
        return exports.WellKnownHostIds.EXCEL;
    }
    else if ((0, string_1.endsWithIgnoreCase)(hostname, '.customercareintelligence.net') || (0, string_1.endsWithIgnoreCase)(hostname, 'powerva.microsoft.com')) {
        return exports.WellKnownHostIds.POWERVIRTUALAGENTS;
    }
    return exports.WellKnownHostIds.UNSPECIFIED;
}
exports.deriveHostId = deriveHostId;


/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
__exportStar(__webpack_require__(9), exports);
__exportStar(__webpack_require__(2), exports);
__exportStar(__webpack_require__(10), exports);
__exportStar(__webpack_require__(11), exports);
__exportStar(__webpack_require__(12), exports);
__exportStar(__webpack_require__(13), exports);


/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.equalsIgnoreCase = void 0;
function equalsIgnoreCase(str, otherStr) {
    str = ('' + str).toUpperCase();
    otherStr = ('' + otherStr).toUpperCase();
    return str === otherStr;
}
exports.equalsIgnoreCase = equalsIgnoreCase;


/***/ }),
/* 3 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.MakerShellAllowedDomains = exports.DefaultAllowedDomains = exports.SdkSettings = void 0;
exports.SdkSettings = {
    authResource: 'https://management.core.windows.net/',
    govAuthResource: 'https://gov.service.flow.microsoft.us/',
    highAuthResource: 'https://high.service.flow.microsoft.us/',
    dodAuthResource: 'https://service.flow.appsplatform.us/',
    chinaAuthResource: 'https://service.powerautomate.cn/',
    usnatAuthResource: 'https://service.flow.eaglex.ic.gov/',
    ussecAuthResource: 'https://service.flow.microsoft.scloud/',
    apiVersion: '2016-11-01',
    portalDomain: 'flow.microsoft.com',
    providerName: 'microsoft.processsimple',
    apiUrl: 'https://api.flow.microsoft.com',
    govApiUrl: 'https://gov.api.flow.microsoft.us',
    highApiUrl: 'https://high.api.flow.microsoft.us',
    dodApiUrl: 'https://api.flow.appsplatform.us',
    chinaApiUrl: 'https://api.powerautomate.cn',
    usnatApiUrl: 'https://api.flow.eaglex.ic.gov',
    ussecApiUrl: 'https://api.flow.microsoft.scloud',
    tip1ApiUrl: 'https://tip1.api.flow.microsoft.com',
    tip1ApiVersion: '2016-11-01-beta',
    tip1PortalDomain: 'tip1.flow.microsoft.com',
    tip2ApiUrl: 'https://tip2.api.flow.microsoft.com',
    tip2ApiVersion: '2016-11-01-alpha',
    tip2PortalDomain: 'tip2.flow.microsoft.com',
    portalTestDomain: 'flows.azure-test.net',
    govPortalDomain: 'flow.microsoft.us',
    govHostName: 'gov.flow.microsoft.us',
    highHostName: 'high.flow.microsoft.us',
    dodPortalDomain: 'flow.appsplatform.us',
    chinaPortalDomain: 'www.powerautomate.cn',
    usnatPortalDomain: 'portal.flow.eaglex.ic.gov',
    ussecPortalDomain: 'portal.flow.microsoft.scloud',
    makerChinaPortalDomain: 'make.powerautomate.cn',
    makerDevPortalDomain: 'local.flow.microsoft.com:44300',
    makerPortalDomain: 'powerautomate.com',
    makerGovPortalDomain: 'gov.powerautomate.us',
    makerHighPortalDomain: 'high.powerautomate.us',
    makerDodPortalDomain: 'powerautomate.appsplatform.us',
    makerUsnatPortalDomain: 'powerautomate.eaglex.ic.gov',
    makerUssecPortalDomain: 'powerautomate.microsoft.scloud',
    makerTestPortalDomain: 'test.powerautomate.com',
    makerPreprodPortalDomain: 'preprod.powerautomate.com',
    makerPreviewPortalDomain: 'preview.powerautomate.com'
};
exports.DefaultAllowedDomains = [exports.SdkSettings.portalDomain, exports.SdkSettings.govPortalDomain, exports.SdkSettings.dodPortalDomain, exports.SdkSettings.chinaPortalDomain, exports.SdkSettings.usnatPortalDomain, exports.SdkSettings.ussecPortalDomain];
exports.MakerShellAllowedDomains = [
    exports.SdkSettings.makerPortalDomain,
    exports.SdkSettings.makerGovPortalDomain,
    exports.SdkSettings.makerHighPortalDomain,
    exports.SdkSettings.makerChinaPortalDomain,
    exports.SdkSettings.makerDodPortalDomain,
    exports.SdkSettings.makerPreviewPortalDomain,
    exports.SdkSettings.makerPreprodPortalDomain,
    exports.SdkSettings.makerUsnatPortalDomain,
    exports.SdkSettings.makerUssecPortalDomain
];


/***/ }),
/* 4 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.MsFlowError = void 0;
var MsFlowError = exports.MsFlowError = /** @class */ (function (_super) {
    __extends(MsFlowError, _super);
    function MsFlowError(message) {
        var _this = _super.call(this, "".concat(MsFlowError.errorName, ": message")) || this;
        _this.message = message;
        _this.name = MsFlowError.errorName;
        return _this;
    }
    MsFlowError.errorName = 'MsFlowSdk';
    return MsFlowError;
}(Error));


/***/ }),
/* 5 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.MsFlowSdk = void 0;
var widget_1 = __webpack_require__(0);
var msFlowError_1 = __webpack_require__(4);
var approvalCenterWidget_1 = __webpack_require__(19);
var bpfActionCenterWidget_1 = __webpack_require__(20);
var flowsWidget_1 = __webpack_require__(21);
var flowsRuntimeWidget_1 = __webpack_require__(22);
var flowCreationWidget_1 = __webpack_require__(23);
var templatesWidget_1 = __webpack_require__(24);
var widget_2 = __webpack_require__(0);
var flowNewWidget_1 = __webpack_require__(25);
var flowEditWidget_1 = __webpack_require__(26);
var flowDetailsWidget_1 = __webpack_require__(27);
var flowRunDetailsWidget_1 = __webpack_require__(28);
var connectionWizardWidget_1 = __webpack_require__(29);
var copilotPluginsWidget_1 = __webpack_require__(30);
var naturalLanguageToFlowWizardWidget_1 = __webpack_require__(31);
var MsFlowSdk = /** @class */ (function () {
    function MsFlowSdk(sdkOption) {
        this.sdkOption = sdkOption;
        // validate options
        if (!this.sdkOption) {
            throw new msFlowError_1.MsFlowError('Sdk options are required');
        }
        if (this.sdkOption.hostName && typeof this.sdkOption.hostName !== 'string') {
            throw new msFlowError_1.MsFlowError('The host name can only be of type string');
        }
        // default value
        this.sdkOption.hostName = this.sdkOption.hostName || 'https://flow.microsoft.com';
        this.sdkOption.locale = this.sdkOption.locale || 'en-us';
    }
    MsFlowSdk.prototype.renderWidget = function (widgetType, widgetOption) {
        var widget;
        switch (widgetType) {
            case approvalCenterWidget_1.ApprovalCenterWidget.widgetType:
                widget = new approvalCenterWidget_1.ApprovalCenterWidget(widgetOption, this.sdkOption);
                break;
            case bpfActionCenterWidget_1.BpfActionCenterWidget.widgetType:
                widget = new bpfActionCenterWidget_1.BpfActionCenterWidget(widgetOption, this.sdkOption);
                break;
            case connectionWizardWidget_1.ConnectionWizardWidget.widgetType:
                widget = new connectionWizardWidget_1.ConnectionWizardWidget(widgetOption, this.sdkOption);
                break;
            case copilotPluginsWidget_1.CopilotPluginsWidget.widgetType:
                widget = new copilotPluginsWidget_1.CopilotPluginsWidget(widgetOption, this.sdkOption);
                break;
            case flowsRuntimeWidget_1.FlowsRuntimeWidget.widgetType:
                widget = new flowsRuntimeWidget_1.FlowsRuntimeWidget(widgetOption, this.sdkOption);
                break;
            case flowsWidget_1.FlowsWidget.widgetType:
                widget = new flowsWidget_1.FlowsWidget(widgetOption, this.sdkOption);
                break;
            case flowCreationWidget_1.FlowCreationWidget.widgetType:
                widget = new flowCreationWidget_1.FlowCreationWidget(widgetOption, this.sdkOption);
                break;
            case flowDetailsWidget_1.FlowDetailsWidget.widgetType:
                widget = new flowDetailsWidget_1.FlowDetailsWidget(widgetOption, this.sdkOption);
                break;
            case flowEditWidget_1.FlowEditWidget.widgetType:
                widget = new flowEditWidget_1.FlowEditWidget(widgetOption, this.sdkOption);
                break;
            case flowNewWidget_1.FlowNewWidget.widgetType:
                widget = new flowNewWidget_1.FlowNewWidget(widgetOption, this.sdkOption);
                break;
            case flowRunDetailsWidget_1.FlowRunDetailsWidget.widgetType:
                widget = new flowRunDetailsWidget_1.FlowRunDetailsWidget(widgetOption, this.sdkOption);
                break;
            case naturalLanguageToFlowWizardWidget_1.NaturalLanguageToFlowWizardWidget.widgetType:
                widget = new naturalLanguageToFlowWizardWidget_1.NaturalLanguageToFlowWizardWidget(widgetOption, this.sdkOption);
                break;
            case templatesWidget_1.TemplatesWidget.widgetType:
                widget = new templatesWidget_1.TemplatesWidget(widgetOption, this.sdkOption);
                break;
            default:
                break;
        }
        if (!widget) {
            throw new msFlowError_1.MsFlowError('please provide a valid supported widget type.');
        }
        return widget;
    };
    return MsFlowSdk;
}());
exports.MsFlowSdk = MsFlowSdk;
/* tslint:disable: no-any */
window.MsFlowSdk = MsFlowSdk;
window.WidgetTypes = widget_2.WidgetTypes;
window.OAuthHandlers = widget_2.OAuthHandlers;
window.WellKnownHostIds = widget_2.WellKnownHostIds;
window.WidgetHostAction = widget_1.WidgetHostAction;
window.WidgetNotifyActions = widget_1.WidgetNotifyActions;
if (window.msFlowSdkLoaded) {
    window.msFlowSdkLoaded();
}
/* tslint:enable: no-any */


/***/ }),
/* 6 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.removeEventListener = exports.addEventListener = void 0;
function addEventListener(eventName, callback, capture) {
    if (window.addEventListener) {
        window.addEventListener(eventName, callback, capture);
    }
    else {
        // to support other browser
        /* tslint:disable: no-any */
        window.attachEvent(eventName, callback);
        /* tslint:enable: no-any */
    }
}
exports.addEventListener = addEventListener;
function removeEventListener(eventName, callback, capture) {
    if (window.removeEventListener) {
        window.removeEventListener(eventName, callback, capture);
    }
    else {
        // to support other browser
        /* tslint:disable: no-any */
        window.detactEvent(eventName, callback);
        /* tslint:enable: no-any */
    }
}
exports.removeEventListener = removeEventListener;


/***/ }),
/* 7 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
__exportStar(__webpack_require__(8), exports);
__exportStar(__webpack_require__(1), exports);


/***/ }),
/* 8 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.uuid = void 0;
var lookup = [];
for (var i = 0; i < 256; i++) {
    lookup[i] = (i < 16 ? '0' : '') + (i).toString(16);
}
function uuid() {
    var random0 = Math.random() * 0xffffffff | 0;
    var random1 = Math.random() * 0xffffffff | 0;
    var random2 = Math.random() * 0xffffffff | 0;
    var random3 = Math.random() * 0xffffffff | 0;
    var segment0 = lookup[random0 & 0xff] + lookup[random0 >> 8 & 0xff] + lookup[random0 >> 16 & 0xff] + lookup[random0 >> 24 & 0xff];
    var segment1 = lookup[random1 & 0xff] + lookup[random1 >> 8 & 0xff] + '-' + lookup[random1 >> 16 & 0x0f | 0x40] + lookup[random1 >> 24 & 0xff];
    var segment2 = lookup[random2 & 0x3f | 0x80] + lookup[random2 >> 8 & 0xff] + '-' + lookup[random2 >> 16 & 0xff] + lookup[random2 >> 24 & 0xff];
    var segment3 = lookup[random3 & 0xff] + lookup[random3 >> 8 & 0xff] + lookup[random3 >> 16 & 0xff] + lookup[random3 >> 24 & 0xff];
    return segment0 + "-" + segment1 + "-" + segment2 + "-" + segment3;
}
exports.uuid = uuid;


/***/ }),
/* 9 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.endsWithIgnoreCase = void 0;
var equalsIgnoreCase_1 = __webpack_require__(2);
function endsWithIgnoreCase(value, suffixString) {
    var result, testString = "" + value;
    if (testString && suffixString) {
        result = equalsIgnoreCase_1.equalsIgnoreCase(testString.substr(testString.length - suffixString.length), suffixString);
    }
    return result;
}
exports.endsWithIgnoreCase = endsWithIgnoreCase;


/***/ }),
/* 10 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.isNullOrUndefined = void 0;
/**
 * Returns true if a value is null or undefined.
 * @arg value {any} - The value to check if null or undefined.
 * @return {boolean} - True if the value is null or undefined.
 */
/* tslint:disable: no-any */
function isNullOrUndefined(value) {
    /* tslint:enable: no-any */
    return value === null || value === undefined;
}
exports.isNullOrUndefined = isNullOrUndefined;


/***/ }),
/* 11 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.isString = void 0;
/* tslint:disable: no-any */
function isString(s) {
    /* tslint:enable: no-any */
    return typeof s === 'string' || s instanceof String;
}
exports.isString = isString;


/***/ }),
/* 12 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.startsWithIgnoreCase = void 0;
var equalsIgnoreCase_1 = __webpack_require__(2);
function startsWithIgnoreCase(value, prefixString) {
    var result, testString = "" + value;
    if (testString && prefixString) {
        result = equalsIgnoreCase_1.equalsIgnoreCase(testString.substring(0, prefixString.length), prefixString);
    }
    return result;
}
exports.startsWithIgnoreCase = startsWithIgnoreCase;


/***/ }),
/* 13 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.stringIncludes = void 0;
function stringIncludes(subjectString, searchString, position) {
    if (typeof position === 'undefined') {
        position = 0;
    }
    return String.prototype.indexOf.call(subjectString, searchString, position) >= 0;
}
exports.stringIncludes = stringIncludes;


/***/ }),
/* 14 */
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = (function() { return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;
/******/
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
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
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/// <reference path="../../typings/es6-promise/es6-promise.d.ts" />
	!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__, exports, __webpack_require__(1), __webpack_require__(2)], __WEBPACK_AMD_DEFINE_RESULT__ = function (require, exports, exception_1, guid_1) {
	    'use strict';
	    var PING = '__PING__';
	    var PONG = '__PONG__';
	    function defer() {
	        'use strict';
	        /* tslint:disable: no-any */
	        var deferred = {};
	        /* tslint:enable: no-any */
	        deferred.promise = new Promise(function (resolve, reject) {
	            deferred.resolve = resolve;
	            deferred.reject = reject;
	        });
	        return deferred;
	    }
	    var Rpc = (function () {
	        function Rpc(rpcOptions) {
	            var _this = this;
	            /* tslint:disable: no-any */
	            this._deferredResponses = {};
	            /* tslint:enable: no-any */
	            this._rpcMethods = {};
	            this._ready = false;
	            this._queuedRequestMessages = [];
	            this._onRpcMessageRecieved = function (message) {
	                if (!message || message.signature !== _this._rpcOptions.signature) {
	                    return;
	                }
	                var rpcRequestMessage = message;
	                if (rpcRequestMessage.method) {
	                    _this._onRpcRequestMessageReceived(rpcRequestMessage);
	                }
	                else {
	                    _this._onRpcResponseMessageReceived(message);
	                }
	            };
	            this._onRpcRequestMessageReceived = function (rpcRequestMessage) {
	                var rpcMethod = _this._rpcMethods[rpcRequestMessage.method];
	                if (!rpcMethod) {
	                    return;
	                }
	                var rpcResponseMessage = {
	                    signature: rpcRequestMessage.signature,
	                    id: rpcRequestMessage.id,
	                    error: null
	                };
	                try {
	                    var result = rpcMethod.apply(_this, rpcRequestMessage.params);
	                    // NOTE: rather then checking if result is a Promise or not,
	                    // always use Promise.resolve(result) so that if the result is a Promise,
	                    // 'then/catch callback' will only be called after the result promise is completed.
	                    _this._rpcOptions.Promise.resolve(result)
	                        .then(function (result) {
	                        rpcResponseMessage.result = result;
	                        _this._rpcOptions.rpcMessageHandler.postMessage(rpcResponseMessage, _this._rpcOptions.targetOrigin);
	                    })
	                        .catch(function (ex) {
	                        rpcResponseMessage.error = _this._serializeError(ex);
	                        _this._rpcOptions.rpcMessageHandler.postMessage(rpcResponseMessage, _this._rpcOptions.targetOrigin);
	                    });
	                }
	                catch (ex) {
	                    // propagate the error correctly to the caller incase there was a synchronous error thrown by the rpcMethod implementation
	                    rpcResponseMessage.error = _this._serializeError(ex);
	                    _this._rpcOptions.rpcMessageHandler.postMessage(rpcResponseMessage, _this._rpcOptions.targetOrigin);
	                }
	            };
	            this._onRpcResponseMessageReceived = function (rpcResponseMessage) {
	                var deferred = _this._deferredResponses[rpcResponseMessage.id];
	                if (deferred) {
	                    if (rpcResponseMessage.error) {
	                        deferred.reject(_this._deserializeError(rpcResponseMessage.error));
	                    }
	                    else {
	                        deferred.resolve(rpcResponseMessage.result);
	                    }
	                    delete _this._deferredResponses[rpcResponseMessage.id];
	                }
	            };
	            if (!rpcOptions) {
	                throw new Error('rpcOptions required');
	            }
	            if (!rpcOptions.Promise) {
	                rpcOptions.Promise = {
	                    defer: defer,
	                    /* tslint:disable: no-any */
	                    resolve: function (value) { return Promise.resolve(value); },
	                    reject: function (value) { return Promise.reject(value); }
	                };
	            }
	            this._rpcOptions = rpcOptions;
	            this._rpcOptions.rpcMessageHandler.addListener(this._onRpcMessageRecieved);
	            this.register(PING, this._onPing);
	        }
	        Rpc.prototype.ack = function () {
	            // only iframe (child) calls this method
	            var _this = this;
	            // unregister ping since we are not the shell
	            this.unregister(PING);
	            return this.call(PING)
	                .then(function (message) {
	                if (message === PONG) {
	                    // shell notified that the shell is ready
	                    _this._ready = true;
	                    _this._processQueue();
	                }
	                else {
	                    return Promise.reject(new Error('Invalid PONG message' + message));
	                }
	            })
	                .catch(function (ex) {
	                // ping failed
	                _this.register(PING, _this._onPing);
	                console.error('PING failed to receive PONG message', ex);
	                return Promise.reject(ex);
	            });
	        };
	        /* tslint:disable: no-any */
	        Rpc.prototype.call = function (method, params) {
	            var id = guid_1.default(), rpcRequestMessage = {
	                signature: this._rpcOptions.signature,
	                id: id,
	                method: this._normalizeMethodName(method),
	                params: params
	            };
	            var deferred = this._rpcOptions.Promise.defer();
	            this._deferredResponses[id] = deferred;
	            if (this._ready || method === PING) {
	                this._call(rpcRequestMessage);
	            }
	            else {
	                this._queuedRequestMessages.push(rpcRequestMessage);
	            }
	            return deferred.promise;
	        };
	        /* tslint:disable: no-any */
	        Rpc.prototype.register = function (method, func) {
	            var normalizedMethod = this._normalizeMethodName(method);
	            if (this._rpcMethods[normalizedMethod]) {
	                throw new Error("Rpc method with name '" + method + "' already registered.");
	            }
	            this._rpcMethods[normalizedMethod] = func;
	        };
	        Rpc.prototype.unregister = function (method) {
	            var normalizedMethod = this._normalizeMethodName(method);
	            if (!this._rpcMethods[normalizedMethod]) {
	                throw new Error("Rpc method with name " + method + " failed to unregister. Method not found");
	            }
	            delete this._rpcMethods[normalizedMethod];
	        };
	        Rpc.prototype.dispose = function () {
	            var _this = this;
	            this._rpcMethods = {};
	            Object.keys(this._deferredResponses).forEach(function (key) { return _this._deferredResponses[key].reject(new Error('rpc disposed')); });
	            this._deferredResponses = {};
	            this._rpcOptions.rpcMessageHandler.removeListener(this._onRpcMessageRecieved);
	        };
	        Rpc.prototype._call = function (rpcRequestMessage) {
	            try {
	                this._rpcOptions.rpcMessageHandler.postMessage(rpcRequestMessage, this._rpcOptions.targetOrigin);
	            }
	            catch (ex) {
	                this._deferredResponses[rpcRequestMessage.id].reject(ex);
	                delete this._deferredResponses[rpcRequestMessage.id];
	            }
	        };
	        Rpc.prototype._onPing = function () {
	            // iframe notified the shell that iframe is ready
	            this.unregister(PING);
	            this._ready = true;
	            this._processQueue();
	            return PONG;
	        };
	        Rpc.prototype._processQueue = function () {
	            var _this = this;
	            this._queuedRequestMessages.forEach(function (rpcRequestMessage) { return _this._call(rpcRequestMessage); });
	            this._queuedRequestMessages = [];
	        };
	        Rpc.prototype._normalizeMethodName = function (method) {
	            return method.toUpperCase();
	        };
	        Rpc.prototype._serializeError = function (ex) {
	            if (ex instanceof Error) {
	                var value_1 = {
	                    name: ex.name,
	                    message: ex.message,
	                    _stack: ex.stack
	                };
	                Object.keys(ex).forEach(function (key) {
	                    value_1[key] = ex[key];
	                });
	                return {
	                    value: value_1
	                };
	            }
	            else {
	                return {
	                    value: ex
	                };
	            }
	        };
	        Rpc.prototype._deserializeError = function (error) {
	            return new exception_1.RpcException('ReceiverFailed', 'Receiver failed', exception_1.convertToException(error.value));
	        };
	        return Rpc;
	    }());
	    exports.Rpc = Rpc;
	    var WindowPostMessageRpcHandler = (function () {
	        function WindowPostMessageRpcHandler(options) {
	            /* tslint:disable: no-any */
	            this._listeners = {};
	            if (!options) {
	                throw new Error('options required');
	            }
	            if (!options.targetWindow) {
	                throw new Error('targetWindow required');
	            }
	            options.sourceWindow = options.sourceWindow || window;
	            options.messageSerializer = options.messageSerializer || (function (rpcMessage) { return rpcMessage; });
	            options.messageDeserializer = options.messageDeserializer || (function (data) { return data; });
	            this._options = options;
	        }
	        WindowPostMessageRpcHandler.prototype.postMessage = function (rpcMessage, targetOrigin) {
	            this._options.targetWindow.postMessage(this._options.messageSerializer(rpcMessage), targetOrigin);
	        };
	        WindowPostMessageRpcHandler.prototype.addListener = function (listener) {
	            var _this = this;
	            /* tslint:disable: no-any */
	            if (this._listeners[listener]) {
	                console.error('duplicate rpc listener added');
	            }
	            this._listeners[listener] = function (e) {
	                var data = _this._options.messageDeserializer(e.data);
	                /* tslint:enable: no-any */
	                if (!data) {
	                    return;
	                }
	                else if (data.method) {
	                    listener({
	                        signature: data.signature,
	                        id: data.id,
	                        method: data.method,
	                        params: data.params
	                    });
	                }
	                else {
	                    listener({
	                        signature: data.signature,
	                        id: data.id,
	                        result: data.result,
	                        error: data.error
	                    });
	                }
	            };
	            /* tslint:disable: no-any */
	            this._options.sourceWindow.addEventListener('message', this._listeners[listener]);
	            /* tslint:enable: no-any */
	        };
	        WindowPostMessageRpcHandler.prototype.removeListener = function (listener) {
	            /* tslint:disable: no-any */
	            this._options.sourceWindow.removeEventListener('message', this._listeners[listener]);
	            delete this._listeners[listener];
	            /* tslint:enable: no-any */
	        };
	        return WindowPostMessageRpcHandler;
	    }());
	    exports.WindowPostMessageRpcHandler = WindowPostMessageRpcHandler;
	}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
	//# sourceMappingURL=rpc.js.map

/***/ },
/* 1 */
/***/ function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;var __extends = (this && this.__extends) || function (d, b) {
	    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
	    function __() { this.constructor = d; }
	    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
	};
	!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__, exports], __WEBPACK_AMD_DEFINE_RESULT__ = function (require, exports) {
	    'use strict';
	    /* tslint:disable: no-any */
	    var Exception = (function () {
	        function Exception(type, code, message, data, innerException) {
	            if (data === void 0) { data = null; }
	            if (innerException === void 0) { innerException = null; }
	            var error = data && data instanceof Error ? data : new Error(message);
	            if (!type) {
	                throw new ArgumentException('Type cannot be empty for exception');
	            }
	            this._type = type;
	            if (!code) {
	                throw new ArgumentException('Code cannot be empty for exception');
	            }
	            this._code = code;
	            if (!message) {
	                throw new ArgumentException('Message cannot be empty for exception');
	            }
	            this._message = message;
	            this._data = data;
	            this._stackTrace = error.stack;
	            this._innerException = innerException;
	        }
	        Object.defineProperty(Exception.prototype, "type", {
	            get: function () {
	                return this._type;
	            },
	            enumerable: true,
	            configurable: true
	        });
	        Object.defineProperty(Exception.prototype, "code", {
	            get: function () {
	                return this._code;
	            },
	            enumerable: true,
	            configurable: true
	        });
	        Object.defineProperty(Exception.prototype, "stackTrace", {
	            get: function () {
	                return this._stackTrace;
	            },
	            enumerable: true,
	            configurable: true
	        });
	        Object.defineProperty(Exception.prototype, "message", {
	            get: function () {
	                return this._message;
	            },
	            enumerable: true,
	            configurable: true
	        });
	        Object.defineProperty(Exception.prototype, "data", {
	            get: function () {
	                return this._data;
	            },
	            enumerable: true,
	            configurable: true
	        });
	        Object.defineProperty(Exception.prototype, "innerException", {
	            get: function () {
	                return this._innerException;
	            },
	            enumerable: true,
	            configurable: true
	        });
	        return Exception;
	    }());
	    exports.Exception = Exception;
	    var UnknownException = (function (_super) {
	        __extends(UnknownException, _super);
	        function UnknownException(data) {
	            return _super.call(this, 'UnknownException', 'UnknownException', 'Unknown error.', data) || this;
	        }
	        return UnknownException;
	    }(Exception));
	    exports.UnknownException = UnknownException;
	    var RpcException = (function (_super) {
	        __extends(RpcException, _super);
	        function RpcException(code, message, innerException) {
	            if (innerException === void 0) { innerException = null; }
	            return _super.call(this, 'RpcException', code, message, null, innerException) || this;
	        }
	        return RpcException;
	    }(Exception));
	    exports.RpcException = RpcException;
	    var ArgumentException = (function (_super) {
	        __extends(ArgumentException, _super);
	        function ArgumentException(message) {
	            return _super.call(this, 'ArgumentException', 'ArgumentException', message, null, null) || this;
	        }
	        return ArgumentException;
	    }(Exception));
	    exports.ArgumentException = ArgumentException;
	    function convertToException(error) {
	        'use strict';
	        if (error instanceof Error || (error.name && error.message && !error.hasOwnProperty('_stackTrace'))) {
	            return new Exception('ErrorException', 'Error', error.message, error);
	        }
	        else if (error.type && error.code && error.message && error.hasOwnProperty('_stackTrace')) {
	            return error;
	        }
	        else {
	            return new UnknownException(error);
	        }
	    }
	    exports.convertToException = convertToException;
	}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
	//# sourceMappingURL=exception.js.map

/***/ },
/* 2 */
/***/ function(module, exports, __webpack_require__) {

	var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__, exports], __WEBPACK_AMD_DEFINE_RESULT__ = function (require, exports) {
	    'use strict';
	    var hexValues = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'];
	    var separator = '-';
	    /**
	     * Returns a GUID such as xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx.
	     *
	     * @return New GUID.
	     */
	    function guid() {
	        'use strict';
	        // c.f. rfc4122 (UUID version 4 = xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx)
	        var oct = '', tmp;
	        for (var a = 0; a < 4; a++) {
	            tmp = (4294967296 * Math.random()) | 0;
	            oct += hexValues[tmp & 0xF]
	                + hexValues[tmp >> 4 & 0xF]
	                + hexValues[tmp >> 8 & 0xF]
	                + hexValues[tmp >> 12 & 0xF]
	                + hexValues[tmp >> 16 & 0xF]
	                + hexValues[tmp >> 20 & 0xF]
	                + hexValues[tmp >> 24 & 0xF]
	                + hexValues[tmp >> 28 & 0xF];
	        }
	        // 'Set the two most significant bits (bits 6 and 7) of the clock_seq_hi_and_reserved to zero and one, respectively'
	        var clockSequenceHi = hexValues[8 + (Math.random() * 4) | 0];
	        return oct.substr(0, 8) + separator + oct.substr(9, 4) + separator + '4' + oct.substr(13, 3) + separator + clockSequenceHi + oct.substr(16, 3) + separator + oct.substr(19, 12);
	    }
	    Object.defineProperty(exports, "__esModule", { value: true });
	    exports.default = guid;
	}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__), __WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
	//# sourceMappingURL=guid.js.map

/***/ }
/******/ ])}).call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));;
//# sourceMappingURL=rpc.standalone.js.map

/***/ }),
/* 15 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.config = void 0;
exports.config = {
    version: '2.2.0'
};


/***/ }),
/* 16 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.getEnvironmentInfo = exports.getEnvironmentUrl = void 0;
var SdkSettings_1 = __webpack_require__(3);
var string_1 = __webpack_require__(1);
var httpHelper_1 = __webpack_require__(17);
function getEnvironmentUrl(hostName, environmentName) {
    if ((0, string_1.isNullOrUndefined)(environmentName) || environmentName.trim() === '') {
        environmentName = '~default';
    }
    var apiVersion = SdkSettings_1.SdkSettings.apiVersion;
    var flowApiUrl = SdkSettings_1.SdkSettings.apiUrl;
    // ignore host case
    hostName = hostName.toLowerCase();
    if (hostName &&
        ((0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.tip1PortalDomain, 0) ||
            (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.makerPreprodPortalDomain, 0))) {
        apiVersion = SdkSettings_1.SdkSettings.tip1ApiVersion;
        flowApiUrl = SdkSettings_1.SdkSettings.tip1ApiUrl;
    }
    else if (hostName &&
        ((0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.tip2PortalDomain, 0) ||
            (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.portalTestDomain, 0) ||
            (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.makerTestPortalDomain, 0))) {
        apiVersion = SdkSettings_1.SdkSettings.tip2ApiVersion;
        flowApiUrl = SdkSettings_1.SdkSettings.tip2ApiUrl;
    }
    if (hostName && ((0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.govHostName, 0) || (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.makerGovPortalDomain, 0))) {
        flowApiUrl = SdkSettings_1.SdkSettings.govApiUrl;
    }
    else if (hostName && ((0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.highHostName, 0) || (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.makerHighPortalDomain, 0))) {
        flowApiUrl = SdkSettings_1.SdkSettings.highApiUrl;
    }
    else if (hostName && ((0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.dodPortalDomain, 0) || (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.makerDodPortalDomain, 0))) {
        flowApiUrl = SdkSettings_1.SdkSettings.dodApiUrl;
    }
    else if (hostName && ((0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.chinaPortalDomain, 0) || (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.makerChinaPortalDomain, 0))) {
        flowApiUrl = SdkSettings_1.SdkSettings.chinaApiUrl;
    }
    else if (hostName && ((0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.usnatPortalDomain, 0) || (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.makerUsnatPortalDomain, 0))) {
        flowApiUrl = SdkSettings_1.SdkSettings.usnatApiUrl;
    }
    else if (hostName && ((0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.ussecPortalDomain, 0) || (0, string_1.stringIncludes)(hostName, SdkSettings_1.SdkSettings.makerUssecPortalDomain, 0))) {
        flowApiUrl = SdkSettings_1.SdkSettings.ussecApiUrl;
    }
    return "".concat(flowApiUrl, "/providers/").concat(SdkSettings_1.SdkSettings.providerName, "/environments/").concat(environmentName, "?api-version=").concat(apiVersion);
}
exports.getEnvironmentUrl = getEnvironmentUrl;
function getEnvironmentInfo(hostName, environmentName, accessToken) {
    var enviromentUrl = getEnvironmentUrl(hostName, environmentName);
    return (0, httpHelper_1.getJson)(enviromentUrl, accessToken)
        .then(function (result) {
        return { name: result.name, location: result.location };
    });
}
exports.getEnvironmentInfo = getEnvironmentInfo;


/***/ }),
/* 17 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.getJson = void 0;
/* tslint:disable: no-any */
function getJson(url, accessToken) {
    /* tslint:enable: no-any */
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url);
        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    resolve(JSON.parse(xhr.responseText));
                }
                catch (e) {
                    reject({
                        status: xhr.status,
                        statusText: e
                    });
                }
            }
            else {
                reject({
                    status: xhr.status,
                    statusText: xhr.statusText
                });
            }
        };
        xhr.onerror = function () {
            reject({
                status: xhr.status,
                statusText: xhr.statusText
            });
        };
        xhr.open('GET', url);
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('Authorization', "Bearer ".concat(accessToken));
        xhr.send();
    });
}
exports.getJson = getJson;


/***/ }),
/* 18 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

Object.defineProperty(exports, "__esModule", { value: true });
exports.getRegionalPortalUrl = exports.getHostNamePrefixFromGeoLocation = void 0;
var string_1 = __webpack_require__(1);
var SdkSettings_1 = __webpack_require__(3);
function getHostNamePrefixFromGeoLocation(location) {
    if (!location) {
        return null;
    }
    var lowerCaseLocation = location.toLowerCase();
    switch (lowerCaseLocation) {
        case 'unitedstatesfirstrelease':
            return 'preview';
        case 'unitedstates':
            return 'us';
        case 'unitedkingdom':
            return 'uk';
        case 'europe':
            return 'emea';
        case 'usgov':
            return 'gov';
        case 'usgovhigh':
            return 'high';
        case 'china':
            return '';
        case 'dod':
        case 'usdod':
        case 'usnat':
        case 'ussec':
            return '';
        default:
            return lowerCaseLocation;
    }
}
exports.getHostNamePrefixFromGeoLocation = getHostNamePrefixFromGeoLocation;
function getRegionalPortalUrl(environmentLocation, originalHostUrl) {
    if ((0, string_1.isNullOrUndefined)(environmentLocation) || environmentLocation.trim() === '') {
        return originalHostUrl;
    }
    var hostNamePrefix = getHostNamePrefixFromGeoLocation(environmentLocation);
    var portalDomain;
    // ignore case
    originalHostUrl = originalHostUrl.toLowerCase();
    hostNamePrefix = 'make';
    if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerDodPortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.dodPortalDomain, 0)) {
        portalDomain = SdkSettings_1.SdkSettings.makerDodPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerHighPortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.highHostName, 0)) {
        portalDomain = SdkSettings_1.SdkSettings.makerHighPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerGovPortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.govPortalDomain, 0)) {
        portalDomain = SdkSettings_1.SdkSettings.makerGovPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerDevPortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.portalTestDomain, 0)) {
        hostNamePrefix = ''; // Maker dev portal doesn't follow the https://make.powerautomate.com structure
        portalDomain = SdkSettings_1.SdkSettings.makerDevPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerTestPortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.tip1PortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.tip2PortalDomain, 0)) {
        portalDomain = SdkSettings_1.SdkSettings.makerTestPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerPreprodPortalDomain, 0)) {
        portalDomain = SdkSettings_1.SdkSettings.makerPreprodPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerPreviewPortalDomain, 0) || hostNamePrefix == 'preview') {
        portalDomain = SdkSettings_1.SdkSettings.makerPreviewPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerUsnatPortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.usnatPortalDomain, 0)) {
        portalDomain = SdkSettings_1.SdkSettings.makerUsnatPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerUssecPortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.ussecPortalDomain, 0)) {
        portalDomain = SdkSettings_1.SdkSettings.makerUssecPortalDomain;
    }
    else if ((0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.makerChinaPortalDomain, 0) || (0, string_1.stringIncludes)(originalHostUrl, SdkSettings_1.SdkSettings.chinaPortalDomain, 0)) {
        // Removing prefix as it will be part of the domain in SdkSettings,
        // Keeping it for differentiation between Maker and non-Maker scenarios
        hostNamePrefix = '';
        portalDomain = SdkSettings_1.SdkSettings.makerChinaPortalDomain;
    }
    else {
        portalDomain = SdkSettings_1.SdkSettings.makerPortalDomain;
    }
    return (hostNamePrefix === '') ? "https://".concat(portalDomain) : "https://".concat(hostNamePrefix, ".").concat(portalDomain);
}
exports.getRegionalPortalUrl = getRegionalPortalUrl;


/***/ }),
/* 19 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApprovalCenterWidget = void 0;
var widget_1 = __webpack_require__(0);
var ApprovalCenterWidget = exports.ApprovalCenterWidget = /** @class */ (function (_super) {
    __extends(ApprovalCenterWidget, _super);
    function ApprovalCenterWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    ApprovalCenterWidget.prototype.getWidgetType = function () {
        return ApprovalCenterWidget.widgetType;
    };
    ApprovalCenterWidget.widgetType = widget_1.WidgetTypes.approvalCenter;
    return ApprovalCenterWidget;
}(widget_1.Widget));


/***/ }),
/* 20 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.BpfActionCenterWidget = void 0;
var widget_1 = __webpack_require__(0);
var BpfActionCenterWidget = exports.BpfActionCenterWidget = /** @class */ (function (_super) {
    __extends(BpfActionCenterWidget, _super);
    function BpfActionCenterWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    BpfActionCenterWidget.prototype.getWidgetType = function () {
        return BpfActionCenterWidget.widgetType;
    };
    BpfActionCenterWidget.widgetType = widget_1.WidgetTypes.bpfActionCenter;
    return BpfActionCenterWidget;
}(widget_1.Widget));


/***/ }),
/* 21 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowsWidget = void 0;
var widget_1 = __webpack_require__(0);
var FlowsWidget = exports.FlowsWidget = /** @class */ (function (_super) {
    __extends(FlowsWidget, _super);
    function FlowsWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    FlowsWidget.prototype.getWidgetType = function () {
        return FlowsWidget.widgetType;
    };
    FlowsWidget.widgetType = widget_1.WidgetTypes.flows;
    return FlowsWidget;
}(widget_1.Widget));


/***/ }),
/* 22 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowsRuntimeWidget = void 0;
var widget_1 = __webpack_require__(0);
var FlowsRuntimeWidget = exports.FlowsRuntimeWidget = /** @class */ (function (_super) {
    __extends(FlowsRuntimeWidget, _super);
    function FlowsRuntimeWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    FlowsRuntimeWidget.prototype.getWidgetType = function () {
        return FlowsRuntimeWidget.widgetType;
    };
    FlowsRuntimeWidget.widgetType = widget_1.WidgetTypes.flowsRuntime;
    return FlowsRuntimeWidget;
}(widget_1.Widget));


/***/ }),
/* 23 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowCreationWidget = void 0;
var widget_1 = __webpack_require__(0);
var FlowCreationWidget = exports.FlowCreationWidget = /** @class */ (function (_super) {
    __extends(FlowCreationWidget, _super);
    function FlowCreationWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    FlowCreationWidget.prototype.getWidgetType = function () {
        return FlowCreationWidget.widgetType;
    };
    FlowCreationWidget.widgetType = widget_1.WidgetTypes.flowCreation;
    return FlowCreationWidget;
}(widget_1.Widget));


/***/ }),
/* 24 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.TemplatesWidget = void 0;
var widget_1 = __webpack_require__(0);
var TemplatesWidget = exports.TemplatesWidget = /** @class */ (function (_super) {
    __extends(TemplatesWidget, _super);
    function TemplatesWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    TemplatesWidget.prototype.getWidgetType = function () {
        return TemplatesWidget.widgetType;
    };
    TemplatesWidget.widgetType = widget_1.WidgetTypes.templates;
    return TemplatesWidget;
}(widget_1.Widget));


/***/ }),
/* 25 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowNewWidget = void 0;
var widget_1 = __webpack_require__(0);
var FlowNewWidget = exports.FlowNewWidget = /** @class */ (function (_super) {
    __extends(FlowNewWidget, _super);
    function FlowNewWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    FlowNewWidget.prototype.getWidgetType = function () {
        return FlowNewWidget.widgetType;
    };
    FlowNewWidget.widgetType = widget_1.WidgetTypes.flowNew;
    return FlowNewWidget;
}(widget_1.Widget));


/***/ }),
/* 26 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowEditWidget = void 0;
var widget_1 = __webpack_require__(0);
var FlowEditWidget = exports.FlowEditWidget = /** @class */ (function (_super) {
    __extends(FlowEditWidget, _super);
    function FlowEditWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    FlowEditWidget.prototype.getWidgetType = function () {
        return FlowEditWidget.widgetType;
    };
    FlowEditWidget.widgetType = widget_1.WidgetTypes.flowEdit;
    return FlowEditWidget;
}(widget_1.Widget));


/***/ }),
/* 27 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowDetailsWidget = void 0;
var widget_1 = __webpack_require__(0);
var FlowDetailsWidget = exports.FlowDetailsWidget = /** @class */ (function (_super) {
    __extends(FlowDetailsWidget, _super);
    function FlowDetailsWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    FlowDetailsWidget.prototype.getWidgetType = function () {
        return FlowDetailsWidget.widgetType;
    };
    FlowDetailsWidget.widgetType = widget_1.WidgetTypes.flowDetails;
    return FlowDetailsWidget;
}(widget_1.Widget));


/***/ }),
/* 28 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FlowRunDetailsWidget = void 0;
var widget_1 = __webpack_require__(0);
var FlowRunDetailsWidget = exports.FlowRunDetailsWidget = /** @class */ (function (_super) {
    __extends(FlowRunDetailsWidget, _super);
    function FlowRunDetailsWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    FlowRunDetailsWidget.prototype.getWidgetType = function () {
        return FlowRunDetailsWidget.widgetType;
    };
    FlowRunDetailsWidget.widgetType = widget_1.WidgetTypes.flowRunDetails;
    return FlowRunDetailsWidget;
}(widget_1.Widget));


/***/ }),
/* 29 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConnectionWizardWidget = void 0;
var widget_1 = __webpack_require__(0);
var ConnectionWizardWidget = exports.ConnectionWizardWidget = /** @class */ (function (_super) {
    __extends(ConnectionWizardWidget, _super);
    function ConnectionWizardWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    ConnectionWizardWidget.prototype.getWidgetType = function () {
        return ConnectionWizardWidget.widgetType;
    };
    ConnectionWizardWidget.widgetType = widget_1.WidgetTypes.connectionWizard;
    return ConnectionWizardWidget;
}(widget_1.Widget));


/***/ }),
/* 30 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.CopilotPluginsWidget = void 0;
var widget_1 = __webpack_require__(0);
var CopilotPluginsWidget = exports.CopilotPluginsWidget = /** @class */ (function (_super) {
    __extends(CopilotPluginsWidget, _super);
    function CopilotPluginsWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    CopilotPluginsWidget.prototype.getWidgetType = function () {
        return CopilotPluginsWidget.widgetType;
    };
    CopilotPluginsWidget.widgetType = widget_1.WidgetTypes.copilotPlugins;
    return CopilotPluginsWidget;
}(widget_1.Widget));


/***/ }),
/* 31 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.NaturalLanguageToFlowWizardWidget = void 0;
var widget_1 = __webpack_require__(0);
var NaturalLanguageToFlowWizardWidget = exports.NaturalLanguageToFlowWizardWidget = /** @class */ (function (_super) {
    __extends(NaturalLanguageToFlowWizardWidget, _super);
    function NaturalLanguageToFlowWizardWidget(widgetOption, sdkOption) {
        var _this = _super.call(this, widgetOption, sdkOption) || this;
        _this.widgetOption = widgetOption;
        _this.sdkOption = sdkOption;
        return _this;
    }
    NaturalLanguageToFlowWizardWidget.prototype.getWidgetType = function () {
        return NaturalLanguageToFlowWizardWidget.widgetType;
    };
    NaturalLanguageToFlowWizardWidget.widgetType = widget_1.WidgetTypes.naturalLanguageToFlowWizard;
    return NaturalLanguageToFlowWizardWidget;
}(widget_1.Widget));


/***/ })
/******/ ]);
//# sourceMappingURL=msflowsdk.js.map