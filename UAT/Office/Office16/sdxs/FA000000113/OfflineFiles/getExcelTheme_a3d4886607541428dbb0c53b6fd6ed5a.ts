import { createTheme, ITheme } from "@fluentui/react";

export function getExcelTheme(): ITheme {
    return createTheme({
        palette: {
            themePrimary: "#107c41",
            themeSecondary: "#007c85",
            themeLight: "#CAEAD8",
            themeDark: "#A0D8B9",
            themeDarker: "#37A660",
            themeTertiary: "#0f703b",
            themeLighter: "#42B8B2",
            themeDarkAlt: "#107C41",
            themeLighterAlt: "#DCF51D",
            neutralLighter: "#f5f5f5",
            neutralDark: "#242424",
            black: "#292827",
            white: "#ffffff",
        }
    });
}
