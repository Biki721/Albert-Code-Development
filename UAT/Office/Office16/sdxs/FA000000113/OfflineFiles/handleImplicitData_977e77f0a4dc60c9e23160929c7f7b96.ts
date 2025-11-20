import { WidgetDoneCallback } from "../../types/WidgetDoneCallback";

const FORMATTED_POSTFIX = '_Formatted';

export function handleImplicitData(data: { implicitData?: object }, widgetDoneCallback: WidgetDoneCallback) {
    const columnKeys = Object.keys(data.implicitData || data);
    let rowStartIndex: number;
    let dataRowStartIndex: number;
    let rowCount: number;
    let tableHeaders: string[] = [];
    let rawColumnKeys: string[] = [];
    let formattedColumnKeys: string[] = [];

    Excel.run((context) => {
        let range = context.workbook.getSelectedRange();
        let rangeTables = range.getTables();
        rangeTables.load();
        let table = rangeTables.getFirst();
        table.load();
        range.load('address');
        range.load('rowIndex');
        range.load('rowCount');
        const tableHeaderRowRange = table.getHeaderRowRange();
        tableHeaderRowRange.load('values');
        tableHeaderRowRange.load('rowIndex');
        tableHeaderRowRange.load('columnIndex');

        return context.sync().then(() => {
            tableHeaders = tableHeaderRowRange.values[0];
            rowStartIndex = range.rowIndex;
            // Table row index is relative to table position
            dataRowStartIndex = rowStartIndex - tableHeaderRowRange.rowIndex - 1;
            rowCount = range.rowCount;
            rawColumnKeys = columnKeys.filter((columnKey) => tableHeaders.includes(columnKey));
            formattedColumnKeys = columnKeys.filter(
                (columnKey) => rawColumnKeys.indexOf(columnKey) < 0 && columnKey.endsWith(FORMATTED_POSTFIX)
            );
        });
    })
    .then(() => {
        // No need to do exception handling here when invalid data is selected
        // We won't allow you to run the flow with invalid table selection
        Excel.run((ctx) => {
            let range = ctx.workbook.getSelectedRange();
            let rangeTables = range.getTables();
            rangeTables.load();
            let table = rangeTables.getFirst();

            return sendUserData(
                ctx,
                tableHeaders,
                formattedColumnKeys,
                rawColumnKeys,
                widgetDoneCallback,
                table,
                rowStartIndex,
                dataRowStartIndex,
                rowCount
            );
        });
    })
    .catch((error) => {
        // If there was an issue getting data (for example, the customer has not selected a row in the table),
        // return an empty object to the widget, this will cause the flow to run without any data but will
        // not block any widget usage.
        widgetDoneCallback(null, null);

        console.error(error);
    });
}

function sendUserData(
    ctx: Excel.RequestContext,
    tableHeaders: string[],
    formattedColumnKeys: string[],
    rawColumnKeys: string[],
    widgetDoneCallback: WidgetDoneCallback,
    table: Excel.Table,
    rowStartIndex: number,
    dataRowStartIndex: number,
    rowCount: number
): OfficeExtension.IPromise<void> {

    let rows = table.rows;
    let rowRanges: Excel.Range[] = [];
    // This is for displaying selected rows in the confirmation page
    let selectedRows: number[] = [];
    let boundImplicitData: Array<Record<string, string>> & { selectedRows?: number[] } = [];

    for (let i = 0; i < rowCount; i++) {
        const row = rows.getItemAt(dataRowStartIndex + i);
        selectedRows.push(rowStartIndex + i + 1);
        const rowRange = row.getRange();
        rowRange.load('text');
        rowRange.load('values');
        rowRanges.push(rowRange);
    }
    return ctx
        .sync()
        .then(() => {
            const FORMATTED_POSTFIXRegex = new RegExp(FORMATTED_POSTFIX + '+$');
            boundImplicitData.selectedRows = selectedRows;
            const columnMap: number[] = [];
            rawColumnKeys.forEach((columnKey) => {
                columnMap[columnKey] = tableHeaders.indexOf(columnKey);
            });
            formattedColumnKeys.forEach((columnKey) => {
                columnMap[columnKey] = tableHeaders.indexOf(columnKey.replace(FORMATTED_POSTFIXRegex, ''));
            });
            rowRanges.forEach((currentRow, rowIndex) => {
                // Row data has to be an object to be correctly stringified during flow run
                const rowData = {};
                rawColumnKeys.forEach((rawColumnKey) => {
                    rowData[rawColumnKey] =
                        columnMap[rawColumnKey] !== -1 ? rowRanges[rowIndex].values[0][columnMap[rawColumnKey]] : '';
                });
                formattedColumnKeys.forEach((formattedColumnKey) => {
                    rowData[formattedColumnKey] =
                        columnMap[formattedColumnKey] !== -1
                            ? rowRanges[rowIndex].text[0][columnMap[formattedColumnKey]].trim()
                            : '';
                });
                boundImplicitData.push(rowData);
            });
            widgetDoneCallback(null, { implicitData: boundImplicitData });
        })
        .catch((error) => {
            console.error('SendUserData failed. Error: ' + error);
            widgetDoneCallback(null, { implicitData: boundImplicitData });
        });
}
