/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */
/// <reference types="@types/office-js" />

import { isCopilotPAIntegrationEnabled } from "./utils/flights";
import { getTaskpaneState } from "./utils/officeJSShim";
import { loadTemplatesWidget } from "./widgets/loadTemplatesWidget/loadTemplatesWidget";
import { loadFlowWidget } from "./widgets/loadFlowWidget";
import { GRAPH_ENDPOINT, getGraphAccessToken, getMakeEndpointForToken, getPowerAutomateAccessToken } from "./widgets/utils/tokenUtils";

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

declare var Office: any;
declare var OfficeFirstPartyAuth: any;


async function getExcelSource(GRAPH_ENDPOINT, graphHeaders, driveType, siteId) {
    if (driveType?.length > 0 && siteId?.length > 0) {
        if (driveType === "documentLibrary") {
            const resp = await fetch(`${GRAPH_ENDPOINT}/v1.0/sites/${siteId}`, {
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
}

Office.onReady(() => {
    document.getElementById('spinner')!.style.display = 'block';
    document.getElementById('spinner-container')!.style.display = 'block';
    document.getElementById('flow-div')!.style.display = 'none';

    OfficeFirstPartyAuth.load(WORKAROUND_REPLY_URL, ["https://service.flow.microsoft.com/"]).then(() => {
        const graphTokenPromise = getGraphAccessToken();

        const flowTokenPromise = getPowerAutomateAccessToken();

        Promise.all([graphTokenPromise, flowTokenPromise]).then(([graphTokenResult, flowTokenResult]) => {
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
                    const graphToken = graphTokenResult.accessToken;
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

                    fetch(`${GRAPH_ENDPOINT}/v1.0${sharedApiPath}`, {
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

                            const excelSource = await getExcelSource(GRAPH_ENDPOINT, graphHeaders, driveType, siteId);
                            if (excelSource !== null) {
                                autoFillParams = {
                                    'parameters.officescripts.source': excelSource,
                                    'parameters.officescripts.drive': hostDriveId,
                                    'parameters.officescripts.fileId': fileId,
                                    'parameters.officescripts.fileName': fileName,
                                }
                            }
                        }

                        // Step 3: Load flow widget
                        const makeEndpoint = getMakeEndpointForToken(flowTokenResult.accessToken);
                        if (getTaskpaneState("LaunchSource") === "ExcelCopilot" && isCopilotPAIntegrationEnabled()) {
                            const templateDefinition = getTaskpaneState("TemplateDefinition");
                            if (!templateDefinition)
                            {
                                throw new Error("Object does not contain a 'TemplateDefinition'.");
                            }

                            loadTemplatesWidget(makeEndpoint, flowTokenResult.accessToken, templateDefinition);
                        }
                        else {
                            loadFlowWidget(makeEndpoint, hostDriveId, fileId, autoFillParams, flowTokenResult.accessToken);
                        }
                    })
                    .catch(e => {
                        // TODO: add logging for exception
                    });
                }
            })
        });
    });
});
