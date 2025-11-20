export function getWidgetTheme(): string  {
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
            : '';

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
