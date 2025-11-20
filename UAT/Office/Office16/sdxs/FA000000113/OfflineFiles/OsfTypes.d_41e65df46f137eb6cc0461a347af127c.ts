interface IOptionalProperties {
    TaskPaneTitle?: string | null;
    TaskPaneWidth?: TaskpaneWidth;
    SourceLocationOverrideResourceId: ManifestUrlKey | null;
    HeaderCssClass?: string;
    TitleCssClass?: string;
}

interface IDocumentHostInfo {
    ServerDocId: string;
    TenantId: string;
    ClientUrl: string; // user-facing url of the workbook
    BreadcrumbBrandUrl: string; // user-facing url up to the site name of the workbook
}

interface IExtensionIdentity {
    Id: string; // Asset ID for the SDX. Must be in sync with Fabric Internal
    StoreId: string; // Must be inline with the values used in the client code to launch a taskpane from the ribbon
    StoreType: string; // Must be inline with the values used in the client code to launch a taskpane from the ribbon
    AppVersion: string; // This is not currently used and can be set to any string
}

interface IHostProperties {
    HostType: string;
    FormFactor: string;
    Locale: string;
}

interface IExtensionLaunchProperties {
    OptionalProperties: IOptionalProperties;
    DevProperties?: IInitialTaskpaneState;
}

interface IExtensionLifeCycle {
    launchExtensionComponent(
    extId: IExtensionIdentity,
    componentType: string,
    componentId: string,
    hostProps: IHostProperties,
    optionalProps: IExtensionLaunchProperties
    ): any;
}

interface ITaskpaneProperties {
    extId: IExtensionIdentity;
    componentType: string;
    componentId: string;
    hostProperties: IHostProperties;
    optionalProperties: {
    // OptionalProperties are used to set the correct taskpane details including URL, width, and title.
    OptionalProperties: IOptionalProperties;
    // DevProperties can be used to add temporary settings in the form of a dictionary.
    //   DevProperties should be used if a taskpane needs to be launched with an initial state.
    //   The settings set here can then be accessed using Office.context.document.settings.get().
    DevProperties?: any;
    };
}

interface IOptionalPropertiesNew {
    taskpaneTitle?: string;
    taskpaneWidth?: TaskpaneWidth;
    sourceLocationOverride: ManifestUrlKey | null;
    settings: any;
}

interface IRefreshParams {
    operationName: "Publish" | "Delete" | "Attach" | "Detach" | "Open";
    scriptMetadata: StorageScript;
}

interface IRibbonGallery {
    refreshRibbon(refreshParams: IRefreshParams): any;
}

interface IOfficeTheme {
    bodyBackgroundColor: string;
    bodyForegroundColor: string;
    controlBackgroundColor: string;
    controlForegroundColor: string;
}

/* eslint-disable @typescript-eslint/no-namespace */
namespace Office {
    namespace extensionLifeCycle {
    function launchTaskpane(
        launchOptions: TaskpaneLaunchOptions
    ): Promise<void>;
    }

    interface Context {
    extensionLifeCycle: IExtensionLifeCycle;
    ribbonGallery: IRibbonGallery;
    messaging: any;
    }
}

interface IOsfHostInfo {
    osfControlAppCorrelationId: string;
}

declare namespace OSF {
    export interface OfficeAppFactory {
    getHostInfo(): IOsfHostInfo;
    }
    const _OfficeAppFactory: OfficeAppFactory;
}

interface SharedRuntimeMessageActionArgs {
    clickId: string;
}

interface InitializeActionArgs {
    wacFlights: string;
    invocationContext: string;
    documentHostInfo: string;
    storageModePreference: string;
    taskpaneWidth?: string;
    blockExternalCalls?: string;
    headerCssClass?: string;
    titleCssClass?: string;
    clickId?: string;
    ring?: string;
    UserEmail?: string;
    AutomationTest?: string;
}

interface SetSettingsActionArgs
    extends SharedRuntimeMessageActionArgs,
    InitializeActionArgs {}

interface RunFromButtonActionArgs extends SharedRuntimeMessageActionArgs {
    scriptLink: string;
    shapeId: string;
    buttonText: string | undefined;
}

interface ViewScriptActionArgs extends RunFromButtonActionArgs {}

interface ICustomExcelShape extends Excel.Shape {
    scriptLink?: string;
}

interface IBizbarActionArgs {
    clickId: string;
}
