import { getWidgetTheme } from "../utils/getWidgetTheme";
import { WidgetDoneCallback } from "../../types/WidgetDoneCallback";
import { handleImplicitData } from "../utils/handleImplicitData";
import { renderSuccessfulFlowCreationPage } from "./successfulFlowCreationPage/successfulFlowCreationPage";
import { hideFlowWidget, showFlowWidget } from "../utils/showWidget";
import { getPowerAutomateAccessToken, isTokenExpired } from "../utils/tokenUtils";

declare var MsFlowSdk: any;

export function loadTemplatesWidget(endpoint: string, flowToken: string, templateDefinition: string) {
    const sdk = new MsFlowSdk({
        hostName: endpoint,
        locale: Office.context.displayLanguage || 'en-us',
        hostId: 'ExcelSDX_OfficeCopilotExcel',
        hostLocale: Office.context.displayLanguage,
        hostVersion: Office.context.diagnostics.version,
        hostPlatform: Office.context.platform.toString(),
        enableWidgetV2: true,
    });
    const widgetRenderParams = {
        container: 'flow-div',
        enableOnBehalfOfTokens: true,
        widgetStyleSettings: {
            themeName: getWidgetTheme(),
        }
    };
    const widgetInstance = sdk.renderWidget('flowCreation', widgetRenderParams);

    widgetInstance.listen('GET_ACCESS_TOKEN', async (_requestParams: any, widgetDoneCallback: WidgetDoneCallback) => {
        // If the current token is expired, get a new one
        if (isTokenExpired(flowToken)) {
            const tokenResponse = await getPowerAutomateAccessToken();
            flowToken = tokenResponse.accessToken;
        }

        widgetDoneCallback(null, { token: flowToken });
    });

    widgetInstance.listen('WIDGET_READY', () => {
        showFlowWidget();
        widgetInstance.notify("createFlowFromTemplateDefinition", {
            templateDefinition
        });
    });

    widgetInstance.listen('GET_IMPLICIT_DATA', (requestParam: { data: { implicitData?: object } }, widgetDoneCallback: WidgetDoneCallback) => {
        handleImplicitData(requestParam.data, widgetDoneCallback)
    });

    widgetInstance.listen('FLOW_CREATION_SUCCEEDED', () => {
        hideFlowWidget();
        renderSuccessfulFlowCreationPage(templateDefinition);
    });
}
