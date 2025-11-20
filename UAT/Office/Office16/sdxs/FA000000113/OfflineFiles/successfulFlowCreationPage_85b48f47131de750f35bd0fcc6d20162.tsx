import React from 'react';
import ReactDOM from 'react-dom';
import { PrimaryButton, IButtonStyles } from "@fluentui/react/lib/Button";
import aiImage from "./assets/aiImage.png";
import styles from "./successfulFlowCreationPageStyles.module.css";
import { Recurrence } from './recurrence';
import { getExcelTheme } from '../../../utils/getExcelTheme';
import { launchCopilotSDX } from '../../../utils/officeJSShim';

type Props = {
    successMessage: string
};

const returnToCopilotButtonId = "ReturnToCopilotButton";

export function renderSuccessfulFlowCreationPage(templateDefinition: string) {
    const parsedDefinition = JSON.parse(templateDefinition);
    const recurrence: Recurrence = parsedDefinition.properties?.definition?.triggers?.Recurrence;
    let successMessage: string;
    if (!recurrence) {
        successMessage = "The flow has been successfully generated";
    } else {
        const { weekDays, hours, minutes } = recurrence.schedule;
        const days = weekDays.join(", ");
        const formattedMinutes = minutes.map((minute => minute < 10 ? `0${minute}` : minute))
        const startTimes = hours.flatMap((hour) => formattedMinutes.flatMap((minute => `${hour}:${minute}`)));
        successMessage = `The flow has been successfully generated. Copilot will execute this flow every ${days} at ${startTimes}.`;
    }

    ReactDOM.render(<SuccessfulFlowCreationPage successMessage={successMessage}/>, document.getElementById('root-div'));
}

function SuccessfulFlowCreationPage({
    successMessage
}: Props) {
    return (
        <div className={styles.successfulFlowCreationPage}>
            <div className={styles.textSummary}>
                {successMessage}
            </div>
            <div className={styles.aiImage}>
                <img src={aiImage} alt="AI Image" />
            </div>
            <div>
                <PrimaryButton
                    text={"Return to Copilot"}
                    ariaLabel={"Return to Copilot"}
                    styles={getPrimaryButtonStyles()}
                    onClick={() => {
                        launchCopilotSDX();
                    }}
                    primary={true}
                    id={returnToCopilotButtonId}
                    theme={getExcelTheme()}
                />
            </div>
        </div>
    );
}

function getPrimaryButtonStyles(): IButtonStyles {
    return {
        root: {
            borderRadius: "2px",
            fontSize: "12px",
            fontWeight: 600,
            height: "26px",
        }
    }
}
