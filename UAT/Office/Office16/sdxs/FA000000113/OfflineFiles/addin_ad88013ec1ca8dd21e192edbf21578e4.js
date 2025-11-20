// The initialize function must be run each time a new page is loaded
(function () {
    try {
        Office.initialize = function (reason) {
            $(document).ready(function () {
                document.getElementById('spinner').style.display = 'block';
                document.getElementById('spinner-container').style.display = 'block';
                document.getElementById('flow-div').style.display = 'none';

                OfficeFirstPartyAuth.delay = 5000;
                OfficeFirstPartyAuth.delayMsal = 5000;
                OfficeFirstPartyAuth.authVersion = "flight";

                const powerAutomateTheme = getWidgetTheme();

                // Needs to be changed if login.html is updated.
                // The change should be replacing it with the build number pertaining to the build containing the new login.html bits.
                // Only make the change once the login.html change has been deployed to at least fast food.
                const BUILD_NUMBER = '1.0.2301.17006';
                // Reply urls need to match exactly with the urls registered on the first-party registration page.
                // The build url changes with every build, thus the reply url we automatically send would change as well.
                // Urls registered on the first-party registration page are registered manually.
                // This is a workaround so that we do not have to manually register a new url with every new build.
                // Since pages on the CDN live indefinitely, we just send an old page containing an up to date login.html page.
                const WORKAROUND_REPLY_URL = window.location.origin.startsWith("https://localhost") ?
                    'https://localhost:3000/login.html' :
                    `https://fa000000113.resources.office.net/f7024bdc-7caf-4ca8-807d-2908f09640d6/${BUILD_NUMBER}/en-us_web/login.html`;


                const loadFlowWidget = (makeEndpoint, exelHostDriveid, excelFileId, autoFillParams) => {
                    sdk = new MsFlowSdk({
                        hostName: makeEndpoint,
                        locale: "en-us",
                        hostId: "ExcelSDX",
                        enableWidgetV2: true,
                    });

                    const widgetRenderParams = {
                        container: 'flow-div',
                        flowsSettings: {
                            allowImplicitConsent: true,
                            hideTabs: true,
                            isMini: true,
                            flowsFilter: `operations/any(operation: operation/excel.fileId eq '${exelHostDriveid}/${excelFileId}')`,
                            widgetFlowListDisplaySettings: {
                                actionMenuOverFlowItems: true,
                                actionMenuClassName: 'fl-ActionMenu-ExcelWidget',
                                triggerOperationKey: 'SHARED_EXCELONLINEBUSINESS-ONROWSELECTED',
                                triggerOperationName: 'OnRowSelected',
                                triggerOperationGroupName: 'shared_excelonlinebusiness',
                                hideTemplateTitleDietDesigner: true,
                                hideTemplateTypeDietDesigner: true,
                            },
                        },
                        templatesSettings: {
                            allowCustomFlowName: true,
                            metadataSortProperty: 'ExcelTablesPriority',
                            templateCategory: 'microsoftexcel_sdx_nativem2',
                            useFlowCreatorSurfaceFromTemplateGallery: true,
                            enableDietDesigner: true,
                            showHiddenTemplates: true,
                            enableTemplatesPageShell: true,
                            defaultParams: autoFillParams,
                        },
                        enableOnBehalfOfTokens: true,
                        widgetStyleSettings: {
                            themeName: powerAutomateTheme,
                        }
                    };

                    widget = sdk.renderWidget('flows', widgetRenderParams);

                    widget.listen('GET_ACCESS_TOKEN', (_requestParam, widgetDoneCallback) => {
                        var tokenParams = {
                            'resource': 'https://service.flow.microsoft.com/',
                            'authChallenge': '',
                            'policy': ''
                        };

                        var behaviorParam = {
                            'popup': false,
                            'forceRefresh': false
                        };

                        OfficeFirstPartyAuth.getAccessToken(tokenParams, behaviorParam).then((tokenResult) => {
                            widgetDoneCallback(null, { token: tokenResult.accessToken });

                            document.getElementById('spinner').style.display = 'none';
                            document.getElementById('spinner-container').style.display = 'none';
                            document.getElementById('flow-div').style.display = 'block';
                        });
                    })
                };

                const graphEndpoint = "https://graph.microsoft.com";

                OfficeFirstPartyAuth.load(WORKAROUND_REPLY_URL, ["https://service.flow.microsoft.com/"]).then(
                    function () {
                        OfficeFirstPartyAuth.getAccessToken({ resource: graphEndpoint }, false).then((tokenResult) => {
                            Office.context.document.getFilePropertiesAsync(fileResult => {

                                // Step 1: Get the shared file id to call graph.
                                if (fileResult?.value?.url?.startsWith('https')) {

                                    //getGraphSharesApiPathFromUrl
                                    // Encode the url to onedrive item-id
                                    // https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/shares_get
                                    const workbookUrlInBase64 = btoa(encodeURI(fileResult.value.url));
                                    const encodedUrl =
                                        'u!' + workbookUrlInBase64.replace('/(^=)/g', '').replace('/', '_').replace('+', '-');
                                    const sharedApiPath = `/shares/${encodedUrl}/driveItem`;
                                    // Step 2: Get the file id and drive id.
                                    const graphToken = tokenResult.accessToken;
                                    const graphAuthHeader = `Bearer ${graphToken}`;
                                    const graphApplicationHeader = "WACPowerAutomateSDX, WANPowerAutomateSDX";
                                    const graphScenarioHeader = "GetExcelFileMetadata";
                                    const graphHeaders = {
                                        'Authorization': graphAuthHeader,
                                        'Accept': 'application/json',
                                        'Application': graphApplicationHeader,
                                        'Scenario': graphScenarioHeader
                                    }

                                    // Parameters for flow list and template
                                    let autoFillParams = {};
                                    let fileId = "nothing";
                                    let hostDriveId = "nothing";

                                    fetch(`${graphEndpoint}/v1.0${sharedApiPath}`, {
                                        headers: graphHeaders
                                    })
                                        .then(response => response.json())
                                        .then(async result => {
                                            if (result?.id?.length > 0 &&
                                                result?.parentReference?.driveId?.length > 0
                                            ) {
                                                const tag = "/root:/";
                                                const path = result.parentReference?.path;
                                                const pathIndex = path?.indexOf(tag);
                                                const relativePath = pathIndex > 0 ? `${path.substr(pathIndex + tag.length - 1)}` : '';
                                                fileId = result.id;
                                                hostDriveId = result.parentReference.driveId;
                                                const fileName = `${relativePath}/${result.name}`;
                                                const driveType = result?.parentReference?.driveType;
                                                const siteId = result?.parentReference?.siteId;

                                                const excelSource = await getExcelSource(graphEndpoint, graphHeaders, driveType, siteId);
                                                if (excelSource !== null) {
                                                    autoFillParams = {
                                                        'parameters.officescripts.drive': hostDriveId,
                                                        'parameters.officescripts.fileId': fileId,
                                                        'parameters.officescripts.fileName': fileName,
                                                        'parameters.officescripts.source': excelSource,
                                                    };
                                                }
                                            }

                                            // Step 3: Load flow widget
                                            const makeEndpoint = getMakeEndpointForToken(tokenResult.accessToken);
                                            loadFlowWidget(makeEndpoint, hostDriveId, fileId, autoFillParams);
                                        })
                                        .catch(e => {
                                            // TODO: add logging for exception
                                        });
                                }
                            });
                        });
                    });
            },
                function () {
                    //TODO enable them just if the host is BlueChicken
                    console.log("idk something broke");
                },
            )
        }
    } catch (e) {
        console.log("Office.initialize throws exception:" + e);
    }
})();

function getWidgetTheme() {
    const lightTheme = 'excel_sdx';
    const grayTheme = 'excel_sdx_gray';
    const darkTheme = 'excel_sdx_dark';

    try {
        // The Office.OfficeTheme API is not supported on these platforms, so fallback to
        // to light theme
        switch (Office.context.platform) {
            case Office.PlatformType.Mac:
            case Office.PlatformType.OfficeOnline:
                return lightTheme;
            default:
            // Intentionally empty to fallback to below logic.
        }

        const officeTheme = Office.context.officeTheme;
        const bodyBackgroundColor = officeTheme
            ? officeTheme.bodyBackgroundColor.toUpperCase()
            : "";

        switch (bodyBackgroundColor) {
            case '#E6E6E6': //OfficeTheme Colorful:
            case '#FFFFFF': //OfficeTheme White
                return lightTheme;
            case '#666666': //OfficeTheme DarkGray
                return grayTheme;
            case '#262626': //OfficeTheme Black
                return darkTheme;

            // If the office theme API does not exist or we receive an unrecognized color,
            // use the light theme.
            default:
                return lightTheme;
        }
    } catch {
        // In case of any other exception, use light theme
        return lightTheme;
    }
}

function getMakeEndpointForToken(token) {
    // Tenant whitelist
    const tenantsForPreview = ["72f988bf-86f1-41af-91ab-2d7cd011db47", "23dc67c7-c437-4c8c-b17d-a8eb749e2ad7"];
    const tenantsForTest = ["0aa46ef4-f834-4456-bcaf-c823c9cdfffd", "48619c59-dbe9-4218-b8fd-e9b746e93508"];

    // Parse token and get the tid claim
    const parsedToken = JSON.parse(atob(token.split('.')[1]));
    const tenantId = parsedToken.tid;

    // If tid claim matches either preview or test, return appropriate endpoint
    // otherwise default to PROD.
    if (tenantsForPreview.includes(tenantId)) {
        return "https://make.preview.powerautomate.com/";
    }
    else if (tenantsForTest.includes(tenantId)) {
        return "https://make.test.powerautomate.com/";
    }
    else {
        return "https://make.powerautomate.com/"
    }
}

async function getExcelSource(graphEndpoint, graphHeaders, driveType, siteId) {
    if (driveType?.length > 0 && siteId?.length > 0) {
        if (driveType === "documentLibrary") {
            const resp = await fetch(`${graphEndpoint}/v1.0/sites/${siteId}`, {
                headers: graphHeaders
            });
            if (!resp.ok) {
                return null;
            }

            const respJson = await resp.json();
            if (!respJson?.id) {
                return null;
            }
            return `sites/${respJson?.id}`;
        } else if (driveType === "business") {
            return "me";
        }
    }
    return null;
};
