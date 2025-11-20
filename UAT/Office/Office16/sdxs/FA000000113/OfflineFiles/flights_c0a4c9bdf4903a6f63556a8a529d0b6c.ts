declare namespace OfficeRuntime {
    namespace experimentation {
      function getBooleanFeatureGate(flight: string, defaultValue?: boolean): boolean;
  
      function getStringFeatureGate(
        flight: string,
        defaultValue?: string,
      ): string | undefined;
  
      function getIntFeatureGate(flight: string, defaultValue?: number): number | undefined;
    }
}

function getFlightBase(name: FlightNamesType): boolean | undefined {  
    // if we're inside office, office.js is always loaded.
    // if it's not, we should hard-fail the session here.
    // We've never hit an error around this assumption
    const fixedName = getFlightFixedName(name);
    // Despite its typing, the API returns undefined for features that are not in exp
    return OfficeRuntime.experimentation.getBooleanFeatureGate(fixedName);
}

function getFlightFixedName(name: string): string {
    // SDX Id is lowercase on Win32 and MAC.
    const sdxId = isDesktopHost() ? "fa000000113" : "FA000000113";
    return `Microsoft.Office.Excel.${sdxId}.${name}`;
}

function getPlatform(): Office.PlatformType | undefined {
    return Office.context.platform;
}

function isDesktopHost(): boolean {
    const platform = getPlatform();
    return platform === Office.PlatformType.PC || platform === Office.PlatformType.Mac;
}

export function getFlight(name: FlightNamesType): boolean {
    return !!getFlightBase(name);
}

// key-value pair for what you want to call your flight in code and what value it maps to in exp
// flights are prefixed with: Microsoft.Office.Excel.FA000000013.
enum flightBooleanNamesEnum {
    "PowerAutomatePPUXDevMode",
}

type FlightNamesType = keyof typeof flightBooleanNamesEnum;

export function isCopilotPAIntegrationEnabled() {
    return Office.context.document.settings.get("CopilotPAIntegration");
}
