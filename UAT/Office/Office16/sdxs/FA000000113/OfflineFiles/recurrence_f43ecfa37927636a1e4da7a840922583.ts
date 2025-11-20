export type Recurrence = {
    frequency: string,
    interval: number,
    timeZone: string,
    startTime: string,
    schedule: {
        weekDays: string[],
        hours: string[],
        minutes: number[]
    }
}
