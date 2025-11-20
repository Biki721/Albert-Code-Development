// This should be kept in sync with the AutomateCommandConstants defined in:
// //depot/devmainoverride/tenantxl_online/biserver/EwaJs/AutomateCommand/AutomateCommandConstants.cs
const TASKPANE_STORE = "sdxcatalog";

export function getTaskpaneState(name: string): string | undefined {
    if (!Office?.context?.document?.settings?.get) {
        throw new Error("Unable to get initial taskpane state. 'Office.context.document.settings.get' is not defined.");
    }

    return Office.context.document.settings.get(name) ?? undefined;
}

export async function launchCopilotSDX() {
    const devProperties = {
        LaunchSource: "PowerAutomateSDX",
    };
    await launchExtensionComponent("FA000000124", devProperties);
}

async function launchExtensionComponent(
    sdxId: string,
    devProperties: { [key: string]: string } = {}
): Promise<void> {
    if (!Office?.context?.extensionLifeCycle?.launchExtensionComponent) {
        throw new Error("Unable to launch taskpane. 'Office.context.extensionLifeCycle.launchExtensionComponent' is not defined");
    }

    const launchExtensionParams: ITaskpaneProperties = {
        extId: {
            Id: sdxId,
            StoreId: TASKPANE_STORE,
            StoreType: TASKPANE_STORE,
            // AppVersion is not currently used by launchExtensionComponent.
            //    As such, this value does not need to be kept in sync with the AppVersion specified in the manifest
            AppVersion: "1.0.0",
        },
        componentType: "Taskpane",
        componentId: sdxId,
        hostProperties: {
            HostType: "Excel-Online",
            // For now, there are not different FormFactors supported so "Desktop" is the correct value
            // In the future there may be a more accurate value to set here
            FormFactor: "Desktop",
            Locale: Office.context.displayLanguage,
        },
        optionalProperties: {
            OptionalProperties: {
                SourceLocationOverrideResourceId: null,
            },
            DevProperties: devProperties,
        },
    };

    await Office.context.extensionLifeCycle.launchExtensionComponent(
        launchExtensionParams.extId,
        launchExtensionParams.componentType,
        launchExtensionParams.componentId,
        launchExtensionParams.hostProperties,
        launchExtensionParams.optionalProperties,
    );
}
