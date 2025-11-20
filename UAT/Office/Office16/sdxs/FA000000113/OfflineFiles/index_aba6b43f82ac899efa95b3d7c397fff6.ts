/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

declare var Office: any;
declare var dynamicLoadExperiment: any;
declare var serviceWorkerExperiment: any;

import * as OTel from '@ms/oteljs';

class OfficeJsSink implements OTel.TelemetrySink {
    public sendTelemetryEvent(event: OTel.TelemetryEvent) {
        Office.sendTelemetryEvent(event);
    }
}

export let telemetryLogger: OTel.TelemetryLogger;

// Expose global variables
(window as any).telemetryLogger = {};

let dLE;
let sWE;

const officeOnReadyCallback = () => {
    const onReadyTimeStampDate: number = Date.now();
    let onReadyTimeStamp: number = -1;
    const performanceTimingData: any = {};

    if (window.performance !== undefined)
    {
      if (window.performance.now !== undefined)
      {
        onReadyTimeStamp = performance.now();
      }

      if (window.performance.getEntries !== undefined)
      {
        // PerformanceObserver is not supported by IE11 and for TestSDX we don't lose any buffered data without it.
        performanceTimingData.navigation = performance.getEntriesByType('navigation');
        performanceTimingData.resource = performance.getEntriesByType('resource');
        performanceTimingData.paint = performance.getEntriesByType('paint');
        performanceTimingData.frame = performance.getEntriesByType('frame');
      }
    }

    telemetryLogger = new OTel.TelemetryLogger();
    telemetryLogger.addSink(new OfficeJsSink());

    telemetryLogger.setTenantTokens({
      Office: {
        Extensibility: {
          ariaTenantToken: 'db334b301e7b474db5e0f02f07c51a47-a1b5bc36-1bbe-482f-a64a-c2d9cb606706-7439',
          nexusTenantToken: 1755
        }
      }
    });

    (window as any).telemetryLogger = telemetryLogger;

    // SeviceWorker related telemetry is available in window.OnLoad().
    // To avoid race between window.load and office.onReady, we add 10s delay for service worker case.
    let delay;
    try {
      if (serviceWorkerExperiment.isServiceWorkerUsed) {
        delay = 10000;
      }
    }
    catch (e) {
      delay = 0;
    }

    setTimeout(
      () => {
        try {
          sWE = serviceWorkerExperiment;
        }
        catch (e) {
          sWE = {
            registered: false,
            registerTS: -1,
            supported: false,
            registerScope: '',
            isServiceWorkerUsed: false,
            resourcesFromCache: '',
            resourcesFromNetwork: ''
          };
        }

        telemetryLogger.sendTelemetryEvent({
          eventName: 'Office.Extensibility.SDX.Experimentation',
          eventFlags: {
              samplingPolicy: OTel.SamplingPolicy.Diagnostics,
              // tslint:disable-next-line:no-bitwise
              dataCategories: OTel.DataCategories.ProductServiceUsage | OTel.DataCategories.ProductServicePerformance
          },
          dataFields: [
              OTel.makeBooleanDataField('Loaded', true),
              OTel.makeDoubleDataField('onReadyTimeStamp', onReadyTimeStamp),
              OTel.makeStringDataField('URL', window.location.href), // IE doesn't provide URL in perfromance.navigation
              OTel.makeDoubleDataField('onReadyTimeStamp_Date', onReadyTimeStampDate),
              OTel.makeDoubleDataField('contentLoadedTimeStamp', dLE.contentLoadedTS),
              OTel.makeDoubleDataField('scriptFetchedTimeStamp', dLE.scriptFetchedTS),
              OTel.makeDoubleDataField('scriptAddedTimeStamp', dLE.scriptAddedTS),
              OTel.makeDoubleDataField('scriptLoadedTimeStamp', dLE.scriptLoadedTS),
              OTel.makeStringDataField('performanceTimingData', JSON.stringify(performanceTimingData)),
              OTel.makeBooleanDataField('swRegistered', sWE.registered),
              OTel.makeDoubleDataField('swRegisteredTS', sWE.registerTS),
              OTel.makeBooleanDataField('swSupported', sWE.supported),
              OTel.makeStringDataField('swRegisterScope', sWE.registerScope),
              OTel.makeStringDataField('swResourcesFromCache', sWE.resourcesFromCache),
              OTel.makeStringDataField('swResourcesFromNetwork', sWE.resourcesFromNetwork)
          ]
        });
      },
      delay
    );
};

try {
    dLE = dynamicLoadExperiment;
}
catch (e) {
    dLE = {
       dynamic: false,
       scriptLoaded: false,
       contentLoadedTS: -1,
       scriptFetchedTS: -1,
       scriptAddedTS: -1,
       scriptLoadedTS: -1
    };
}

if (dLE.dynamic && !dLE.scriptLoaded) {
    window.addEventListener('WordJSLoaded', () => Office.onReady().then(officeOnReadyCallback), false);
} else {
    debugger;
    Office.onReady()
    .then(officeOnReadyCallback);
}
